#!/usr/bin/env python3
import os
import json
import time
import joblib
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from scipy import sparse
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# run final model with multiple seeds to report mean ± std
SEEDS = [42, 0, 1]

# best hyperparameters selected earlier during search (code: train_lr_network.py)
BEST_PARAMS = {
    "C": 1.0,
    "class_weight": "balanced",
}

# paths
BASE_DIR = Path("/home/anci/new")
DATA_DIR = BASE_DIR / "correct_splits" / "with_genre_groups_network_fixed"
OUT_DIR = BASE_DIR / "models_new" / "lr_network_multiseed"

TRAIN_CSV = DATA_DIR / "train.csv"
VAL_CSV   = DATA_DIR / "val.csv"
TEST_CSV  = DATA_DIR / "test.csv"

# target, 1 - positive interaction, 0 - negative
TARGET = "owned"

# user-game pairs (identifier columns)
ID_COLS = ["steamid", "appid"]

# numeric input features used by model
NUMERIC_FEATURES = [
    "total_games_owned",
    "total_playtime_minutes",
    "median_playtime_minutes",
    "unique_genres_played",
    "user_count",
    "game_total_playtime_minutes",
    "release_date",
    "friend_count",
    "game_emb_0",
    "game_emb_1",
    "game_emb_2",
    "game_emb_3",
    "game_emb_4",
    "game_emb_5",
    "game_emb_6",
    "game_emb_7",
    "game_emb_8",
    "game_emb_9",
    "game_emb_10",
    "game_emb_11",
    "game_emb_12",
    "game_emb_13",
    "game_emb_14",
    "game_emb_15",
    "game_emb_16",
    "game_emb_17",
    "game_emb_18",
    "game_emb_19",
    "game_emb_20",
    "game_emb_21",
    "game_emb_22",
    "game_emb_23",
    "game_emb_24",
    "game_emb_25",
    "game_emb_26",
    "game_emb_27",
    "game_emb_28",
    "game_emb_29",
    "game_emb_30",
    "game_emb_31",
    "user_playtime_group_Action",
    "user_playtime_group_Adventure",
    "user_playtime_group_RPG",
    "user_playtime_group_Casual",
    "user_playtime_group_Indie",
    "user_playtime_group_Racing",
    "user_playtime_group_Simulation",
    "user_playtime_group_Strategy",
    "user_playtime_group_Sports",
    "user_playtime_group_Violent",
    "user_playtime_group_Adult",
    "user_playtime_group_Non-gameplay_Tools",
    "user_playtime_group_Other",
]

# categorical input features used by model
CATEGORICAL_FEATURES = [
    "country",
    "genres",
    "developer",
    "publisher",
    "platforms",
]

# columns to load from csv files
USECOLS = ID_COLS + [TARGET] + NUMERIC_FEATURES + CATEGORICAL_FEATURES
FEATURE_COLS = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# optional row limits for debugging / faster experiments
MAX_TRAIN_ROWS = int(os.getenv("MAX_TRAIN_ROWS", "0"))
MAX_VAL_ROWS   = int(os.getenv("MAX_VAL_ROWS", "0"))
MAX_TEST_ROWS  = int(os.getenv("MAX_TEST_ROWS", "0"))

# preprocessor is fit only on a sample of the training split to reduce memory
PREPROCESSOR_SAMPLE_ROWS = int(os.getenv("PREPROCESSOR_SAMPLE_ROWS", "5000000"))
CHUNKSIZE = int(os.getenv("CHUNKSIZE", "200000"))
EPOCHS = int(os.getenv("EPOCHS", "3"))

# fractions used for learning-curve experiments
LC_FRACTIONS = [0.10, 0.50, 1.00]

# limits for one-hot encoding in the large network setting
# rare categories are grouped as "infrequent"
OHE_MAX_CATS = int(os.getenv("OHE_MAX_CATS", "100"))
OHE_MIN_FREQ = int(os.getenv("OHE_MIN_FREQ", "50"))


def set_seed(seed: int):
    # set randomness for numpy / python
    random.seed(seed)
    np.random.seed(seed)


def iter_split(path: Path, max_rows: int = 0, chunksize: int = 200_000):
    # read a CSV file in chunks
    # this is used for large-scale training so we do not need to load the entire split into memory at once
    rows_read = 0
    for chunk in pd.read_csv(path, sep=";", usecols=USECOLS, chunksize=chunksize, low_memory=False):
        if max_rows > 0:
            remaining = max_rows - rows_read
            if remaining <= 0:
                break
            if len(chunk) > remaining:
                chunk = chunk.iloc[:remaining].copy()
        rows_read += len(chunk)
        yield chunk
        if max_rows > 0 and rows_read >= max_rows:
            break


def read_split(path: Path, max_rows: int = 0) -> pd.DataFrame:
    # load a full split into memory (and optionally trim it)
    print(f"Loading {path} ...")
    df = pd.read_csv(path, sep=";", usecols=USECOLS, low_memory=False)
    if max_rows > 0:
        df = df.iloc[:max_rows].copy()
        print(f"Trimmed to {len(df)} rows")
    print(f"Loaded {len(df)} rows from {path}")
    return df


def count_rows(path: Path) -> int:
    total = 0
    for chunk in pd.read_csv(path, sep=";", usecols=[TARGET], chunksize=1_000_000, low_memory=False):
        total += len(chunk)
    return total


# compute Discounted Cumulative Gain at rank k
def dcg_at_k(relevances, k):
    vals = np.asarray(relevances[:k], dtype=float)
    if vals.size == 0:
        return 0.0
    discounts = np.log2(np.arange(2, vals.size + 2))
    return float(np.sum(vals / discounts))


# compute normalized DCG at rank k
def ndcg_at_k(y_true_sorted, k):
    ideal = sorted(y_true_sorted, reverse=True)
    best = dcg_at_k(ideal, k)
    if best == 0.0:
        return 0.0
    return dcg_at_k(y_true_sorted, k) / best


def evaluate_ranking(df_scores: pd.DataFrame):
    # evaluate ranking quality per user.
    #
    # For each user:
    # - sort candidate games by predicted score
    # - compute ranking metrics on ordered labels
    # metrics:
    # - HitRate@1/5/10/20
    # - Recall@1/5/10/20
    # - NDCG@1/5/10/20
    # - MRR
    rows = []

    for steamid, g in df_scores.groupby("steamid", sort=False):
        g = g.sort_values("score", ascending=False)
        y = g["owned"].astype(int).tolist()
        positives = int(np.sum(y))
        if positives == 0:
            continue

        row = {"steamid": steamid}

        for k in [1, 5, 10, 20]:
            topk = y[:k]
            hits = int(np.sum(topk))
            row[f"HitRate@{k}"] = 1.0 if hits > 0 else 0.0
            row[f"Recall@{k}"] = hits / positives
            row[f"NDCG@{k}"] = ndcg_at_k(y, k)

        rr = 0.0
        for i, val in enumerate(y, start=1):
            if val == 1:
                rr = 1.0 / i
                break
        row["MRR"] = rr
        rows.append(row)

    per_user = pd.DataFrame(rows)
    if per_user.empty:
        raise RuntimeError("No users with positives found during ranking evaluation.")

    # agragate metrics across users
    metrics = {
        "n_users_evaluated": int(len(per_user)),
        "HitRate@1": float(per_user["HitRate@1"].mean()),
        "Recall@1": float(per_user["Recall@1"].mean()),
        "NDCG@1": float(per_user["NDCG@1"].mean()),
        "HitRate@5": float(per_user["HitRate@5"].mean()),
        "Recall@5": float(per_user["Recall@5"].mean()),
        "NDCG@5": float(per_user["NDCG@5"].mean()),
        "HitRate@10": float(per_user["HitRate@10"].mean()),
        "Recall@10": float(per_user["Recall@10"].mean()),
        "NDCG@10": float(per_user["NDCG@10"].mean()),
        "HitRate@20": float(per_user["HitRate@20"].mean()),
        "Recall@20": float(per_user["Recall@20"].mean()),
        "NDCG@20": float(per_user["NDCG@20"].mean()),
        "MRR": float(per_user["MRR"].mean()),
    }
    return metrics, per_user


def sparse_to_csr_int32(X):
    # ensure that a sparse matrix is stored in CSR format with int32 indices
    # (technical safeguard for large sparse feature matrices)
    if sparse.issparse(X):
        X = X.tocsr(copy=False)

        print(
            f"[DEBUG] sparse matrix shape={X.shape}, nnz={X.nnz}, "
            f"indices_dtype={X.indices.dtype}, indptr_dtype={X.indptr.dtype}"
        )
        print(f"[DEBUG] indptr[-1]={X.indptr[-1]}, int32_max={np.iinfo(np.int32).max}")

        if X.indices.dtype != np.int32:
            max_idx = int(X.indices.max()) if X.indices.size else 0
            if max_idx > np.iinfo(np.int32).max:
                raise ValueError("CSR indices exceed int32 range.")
            X.indices = X.indices.astype(np.int32, copy=False)

        if X.indptr.dtype != np.int32:
            max_int32 = np.iinfo(np.int32).max
            max_indptr = int(X.indptr.max()) if X.indptr.size else 0
            if max_indptr > max_int32:
                raise ValueError(
                    "CSR indptr exceeds int32 range; matrix is too large for sklearn sparse input. "
                    f"shape={X.shape}, nnz={X.nnz}, indptr[-1]={X.indptr[-1]}"
                )
            X.indptr = X.indptr.astype(np.int32, copy=False)

        return X
    return X


def make_preprocessor():
    # build the preprocessing pipeline.
    # - numeric preprocessing: median imputation + standard scaling
    # - categorical preprocessing: missing-value fill + one-hot encoding
    #
    # the network version uses stricter OHE settings to control feature explosion
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="MISSING")),
        ("onehot", OneHotEncoder(
            handle_unknown="infrequent_if_exist",
            max_categories=OHE_MAX_CATS,
            min_frequency=OHE_MIN_FREQ,
        )),
    ])

    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
        sparse_threshold=1.0,
    )


def build_model(seed: int):
    # build the LR model for chunked training
    # max_iter=1 + warm_start=True means:
    # - each call to fit() performs one optimization pass
    # - parameters are reused across chunks and epochs
    return LogisticRegression(
        C=BEST_PARAMS["C"],
        class_weight=BEST_PARAMS["class_weight"],
        solver="saga",
        max_iter=1,
        warm_start=True,
        random_state=seed,
    )


def fit_preprocessor(train_csv: Path, max_train_rows: int = 0):
    # fit preprocessor on a sample of the training split
    print("\n" + "=" * 80)
    print("Fitting preprocessor on sample...")

    sample_limit = PREPROCESSOR_SAMPLE_ROWS
    if max_train_rows > 0:
        sample_limit = min(sample_limit, max_train_rows)

    sample_df = pd.read_csv(
        train_csv,
        sep=";",
        usecols=USECOLS,
        nrows=sample_limit,
        low_memory=False,
    )
    X_sample = sample_df[FEATURE_COLS].copy()

    preprocessor = make_preprocessor()

    t0 = time.time()
    preprocessor.fit(X_sample)
    dt = time.time() - t0

    # transform a small preview for inspection
    sample_preview = sparse_to_csr_int32(preprocessor.transform(X_sample.iloc[:min(10000, len(X_sample))]))
    n_features_out = int(sample_preview.shape[1])

    print(f"Preprocessor fitted on {len(sample_df)} rows in {dt:.2f}s")
    print(f"Output feature dimension: {n_features_out}")

    return preprocessor, n_features_out


def transform_features(preprocessor, df: pd.DataFrame):
    # apply the fitted preprocessor and convert to safe CSR format
    X = df[FEATURE_COLS].copy()
    Xt = preprocessor.transform(X)
    Xt = sparse_to_csr_int32(Xt)
    return Xt


def fit_model_chunked(preprocessor, train_csv: Path, seed: int, max_train_rows: int = 0):
    # train the LR model in chunks over multiple epochs
    # workflow:
    # - read train.csv chunk by chunk
    # - transform each chunk with the fitted preprocessor
    # - fit the model repeatedly using warm_start
    # - log training progress per chunk
    #
    # this is used because the network dataset is too large for a standard full-data fit
    model = build_model(seed)
    fit_log = []

    for epoch in range(1, EPOCHS + 1):
        print("\n" + "=" * 80)
        print(
            f"Training epoch {epoch}/{EPOCHS} | "
            f"seed={seed} | C={BEST_PARAMS['C']}, class_weight={BEST_PARAMS['class_weight']}"
        )

        epoch_rows = 0
        epoch_chunks = 0
        epoch_start = time.time()

        for chunk_idx, chunk in enumerate(iter_split(train_csv, max_rows=max_train_rows, chunksize=CHUNKSIZE), start=1):
            y_chunk = chunk[TARGET].astype(int).to_numpy()
            if np.unique(y_chunk).size < 2:
                print(f"[TRAIN] skipping chunk {chunk_idx} because it has one class only")
                continue

            Xt = transform_features(preprocessor, chunk)

            t0 = time.time()
            model.fit(Xt, y_chunk)
            dt = time.time() - t0

            epoch_rows += len(chunk)
            epoch_chunks += 1

            chunk_log = {
                "seed": seed,
                "epoch": epoch,
                "chunk": chunk_idx,
                "rows": int(len(chunk)),
                "fit_seconds": float(dt),
                "coef_norm": float(np.linalg.norm(model.coef_)),
                "intercept": float(model.intercept_[0]),
            }
            fit_log.append(chunk_log)

            print(
                f"[TRAIN] seed={seed} epoch={epoch} chunk={chunk_idx} rows={len(chunk)} "
                f"fit_seconds={dt:.2f} coef_norm={chunk_log['coef_norm']:.6f}"
            )

        epoch_dt = time.time() - epoch_start
        print(
            f"[TRAIN] seed={seed} epoch {epoch} done: chunks={epoch_chunks}, rows={epoch_rows}, "
            f"elapsed={epoch_dt:.2f}s"
        )

    return model, pd.DataFrame(fit_log)


# transform features and return predicted probabilities for positive class
def predict_scores(preprocessor, model, df: pd.DataFrame):
    Xt = transform_features(preprocessor, df)
    return model.predict_proba(Xt)[:, 1]


def evaluate_dataset(preprocessor, model, df: pd.DataFrame, split_name: str):
    # evaluate the trained model on one split
    # produce ROC-AUC, ranking metrics and scored dataframe
    print("\n" + "=" * 80)
    print(f"Evaluating on {split_name}...")

    y_true = df[TARGET].astype(int).to_numpy()
    scores = predict_scores(preprocessor, model, df)
    auc = float(roc_auc_score(y_true, scores))

    score_df = df[["steamid", "appid", TARGET]].copy()
    score_df["score"] = scores
    ranking_metrics, per_user_metrics = evaluate_ranking(score_df.rename(columns={TARGET: "owned"}))

    result = {"split": split_name, "roc_auc": auc, **ranking_metrics}
    print(json.dumps(result, indent=2))
    return auc, ranking_metrics, per_user_metrics, score_df


def aggregate_metrics(list_of_dicts):
    # aggregate scalar metrics across seeds
    keys = [k for k in list_of_dicts[0].keys() if k != "n_users_evaluated"]
    result = {}
    for k in keys:
        vals = [float(d[k]) for d in list_of_dicts]
        result[k] = {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
        }
    result["n_users_evaluated"] = int(list_of_dicts[0]["n_users_evaluated"])
    return result


def make_learning_curve_multiseed(preprocessor, train_df, val_df, out_dir: Path):
    # build learning curves for the final model across multiple seeds
    rows = []

    X_val = val_df[FEATURE_COLS].copy()
    y_val = val_df[TARGET].astype(int).to_numpy()
    Xt_val = sparse_to_csr_int32(preprocessor.transform(X_val))

    positives_df = train_df[train_df[TARGET] == 1]
    negatives_df = train_df[train_df[TARGET] == 0]

    for seed in SEEDS:
        print("\n" + "=" * 80)
        print(f"Learning curve for seed={seed}")

        for frac in LC_FRACTIONS:
            n_total = int(len(train_df) * frac)
            n_pos = max(1, int(len(positives_df) * frac))
            n_neg = max(1, n_total - n_pos)

            part_pos = positives_df.iloc[:min(n_pos, len(positives_df))]
            part_neg = negatives_df.iloc[:min(n_neg, len(negatives_df))]
            part = pd.concat([part_pos, part_neg], axis=0).sample(frac=1.0, random_state=seed)

            X_part = part[FEATURE_COLS].copy()
            y_part = part[TARGET].astype(int).to_numpy()
            Xt_part = sparse_to_csr_int32(preprocessor.transform(X_part))

            # for learning curves, fit a standard LR model
            model = LogisticRegression(
                C=BEST_PARAMS["C"],
                class_weight=BEST_PARAMS["class_weight"],
                solver="saga",
                max_iter=300,
                random_state=seed,
            )

            t0 = time.time()
            model.fit(Xt_part, y_part)
            fit_seconds = time.time() - t0

            train_scores = model.predict_proba(Xt_part)[:, 1]
            val_scores = model.predict_proba(Xt_val)[:, 1]

            train_auc = float(roc_auc_score(y_part, train_scores))
            val_auc = float(roc_auc_score(y_val, val_scores))

            val_score_df = val_df[["steamid", "appid", TARGET]].copy()
            val_score_df["score"] = val_scores
            val_metrics, _ = evaluate_ranking(val_score_df.rename(columns={TARGET: "owned"}))

            row = {
                "seed": seed,
                "fraction": float(frac),
                "n_rows": int(len(part)),
                "n_pos": int((y_part == 1).sum()),
                "n_neg": int((y_part == 0).sum()),
                "fit_seconds": float(fit_seconds),
                "train_roc_auc": train_auc,
                "val_roc_auc": val_auc,
                "NDCG@10": float(val_metrics["NDCG@10"]),
                "Recall@10": float(val_metrics["Recall@10"]),
            }
            rows.append(row)
            print(
                f"[LC] seed={seed} fraction={frac:.2f} rows={len(part)} "
                f"val_ndcg10={val_metrics['NDCG@10']:.6f}"
            )

    lc_df = pd.DataFrame(rows)
    lc_df.to_csv(out_dir / "learning_curve_per_seed.csv", index=False)

    lc_agg = (
        lc_df.groupby(["fraction", "n_rows"], as_index=False)
        .agg(
            train_roc_auc_mean=("train_roc_auc", "mean"),
            train_roc_auc_std=("train_roc_auc", "std"),
            val_roc_auc_mean=("val_roc_auc", "mean"),
            val_roc_auc_std=("val_roc_auc", "std"),
            ndcg10_mean=("NDCG@10", "mean"),
            ndcg10_std=("NDCG@10", "std"),
            recall10_mean=("Recall@10", "mean"),
            recall10_std=("Recall@10", "std"),
        )
        .sort_values("n_rows")
        .fillna(0.0)
    )
    lc_agg.to_csv(out_dir / "learning_curve_aggregated.csv", index=False)

    # plot train/val ROC-AUC vs training size
    plt.figure(figsize=(8, 5))
    plt.plot(lc_agg["n_rows"], lc_agg["train_roc_auc_mean"], marker="o", label="Train ROC-AUC")
    plt.fill_between(
        lc_agg["n_rows"],
        lc_agg["train_roc_auc_mean"] - lc_agg["train_roc_auc_std"],
        lc_agg["train_roc_auc_mean"] + lc_agg["train_roc_auc_std"],
        alpha=0.2,
    )
    plt.plot(lc_agg["n_rows"], lc_agg["val_roc_auc_mean"], marker="o", label="Val ROC-AUC")
    plt.fill_between(
        lc_agg["n_rows"],
        lc_agg["val_roc_auc_mean"] - lc_agg["val_roc_auc_std"],
        lc_agg["val_roc_auc_mean"] + lc_agg["val_roc_auc_std"],
        alpha=0.2,
    )
    plt.xlabel("Training rows")
    plt.ylabel("ROC-AUC")
    plt.title("Learning Curve — LR Network (multi-seed)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_roc_auc_multiseed.png", dpi=200)
    plt.close()

    # plot validation ranking metrics vs training size
    plt.figure(figsize=(8, 5))
    plt.plot(lc_agg["n_rows"], lc_agg["ndcg10_mean"], marker="o", label="Val NDCG@10")
    plt.fill_between(
        lc_agg["n_rows"],
        lc_agg["ndcg10_mean"] - lc_agg["ndcg10_std"],
        lc_agg["ndcg10_mean"] + lc_agg["ndcg10_std"],
        alpha=0.2,
    )
    plt.plot(lc_agg["n_rows"], lc_agg["recall10_mean"], marker="o", label="Val Recall@10")
    plt.fill_between(
        lc_agg["n_rows"],
        lc_agg["recall10_mean"] - lc_agg["recall10_std"],
        lc_agg["recall10_mean"] + lc_agg["recall10_std"],
        alpha=0.2,
    )
    plt.xlabel("Training rows")
    plt.ylabel("Score")
    plt.title("Learning Curve — LR Network Ranking (multi-seed)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_ranking_multiseed.png", dpi=200)
    plt.close()

    return lc_df, lc_agg


def main():
    # train, evaluate and save the final LR network model across multiple seeds
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # fit one shared preprocessor
    preprocessor, n_features_out = fit_preprocessor(TRAIN_CSV, max_train_rows=MAX_TRAIN_ROWS)

    # load validation / test once
    val_df = read_split(VAL_CSV, max_rows=MAX_VAL_ROWS)
    test_df = read_split(TEST_CSV, max_rows=MAX_TEST_ROWS)

    all_seed_runs = []
    per_seed_val = []
    per_seed_test = []

    # train one chunked model per seed using fixed best hyperparameters
    for seed in SEEDS:
        print("\n" + "=" * 80)
        print(f"FINAL RUN FOR SEED {seed}")
        print("=" * 80)

        set_seed(seed)

        t0 = time.time()
        model, fit_log_df = fit_model_chunked(
            preprocessor=preprocessor,
            train_csv=TRAIN_CSV,
            seed=seed,
            max_train_rows=MAX_TRAIN_ROWS,
        )
        fit_seconds = time.time() - t0

        val_auc, val_metrics, _, _ = evaluate_dataset(preprocessor, model, val_df, "val")
        test_auc, test_metrics, per_user_metrics, test_score_df = evaluate_dataset(preprocessor, model, test_df, "test")

        fit_log_df.to_csv(OUT_DIR / f"fit_log_seed_{seed}.csv", index=False)
        test_score_df.to_csv(OUT_DIR / f"test_scores_seed{seed}.csv.gz", index=False, compression="gzip")
        per_user_metrics.to_csv(OUT_DIR / f"test_per_user_metrics_seed{seed}.csv", index=False)

        joblib.dump(model, OUT_DIR / f"best_model_seed{seed}.joblib")

        run = {
            "seed": seed,
            "fit_seconds": float(fit_seconds),
            "val_metrics": {"ROC-AUC": val_auc, **val_metrics},
            "test_metrics": {"ROC-AUC": test_auc, **test_metrics},
        }
        all_seed_runs.append(run)

        per_seed_val.append({
            "seed": seed,
            "fit_seconds": float(fit_seconds),
            "ROC-AUC": val_auc,
            **val_metrics,
        })
        per_seed_test.append({
            "seed": seed,
            "ROC-AUC": test_auc,
            **test_metrics,
        })

    # save shared preprocessor once
    joblib.dump(preprocessor, OUT_DIR / "preprocessor.joblib")

    # aggregate mean ± std across seeds
    val_metrics_agg = aggregate_metrics([r["val_metrics"] for r in all_seed_runs])
    test_metrics_agg = aggregate_metrics([r["test_metrics"] for r in all_seed_runs])

    print("\n--- Val metrics (mean ± std) ---")
    for k, v in val_metrics_agg.items():
        if isinstance(v, dict):
            print(f"  {k}: {v['mean']:.4f} ± {v['std']:.4f}")

    print("\n--- Test metrics (mean ± std) ---")
    for k, v in test_metrics_agg.items():
        if isinstance(v, dict):
            print(f"  {k}: {v['mean']:.4f} ± {v['std']:.4f}")

    # learning curve is computed on a smaller train subset
    lc_train_rows = 2_000_000
    print("\nLoading subsets for learning curve...")
    train_df_lc = read_split(TRAIN_CSV, max_rows=lc_train_rows)
    val_df_lc = val_df.copy()
    make_learning_curve_multiseed(preprocessor, train_df_lc, val_df_lc, OUT_DIR)

    # final summary .json
    final_results = {
        "model_type": "lr",
        "dataset_type": "network",
        "training_mode": "full_chunked_warm_start_multiseed",
        "train_rows": int(MAX_TRAIN_ROWS) if MAX_TRAIN_ROWS > 0 else int(count_rows(TRAIN_CSV)),
        "val_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "features_numeric": NUMERIC_FEATURES,
        "features_categorical": CATEGORICAL_FEATURES,
        "n_features_out": int(n_features_out),
        "chunksize": CHUNKSIZE,
        "epochs": EPOCHS,
        "preprocessor_sample_rows": PREPROCESSOR_SAMPLE_ROWS,
        "best_params": BEST_PARAMS,
        "seeds": SEEDS,
        "val_metrics": val_metrics_agg,
        "test_metrics": test_metrics_agg,
        "per_seed_val": per_seed_val,
        "per_seed_test": per_seed_test,
    }

    with open(OUT_DIR / "results.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2)

    print("\nFINAL TEST RESULTS")
    print(json.dumps(final_results, indent=2))
    print(f"Saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()