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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer


# run final model with multiple seeds to report mean ± std
SEEDS = [42, 0, 1]

# best hyperparameters selected earlier during search (code: train_rf_network.py)
BEST_PARAMS = {
    "n_estimators": 120,
    "max_depth": 30,
    "min_samples_split": 20,
    "min_samples_leaf": 10,
    "max_features": "sqrt",
}

# paths
BASE_DIR = Path("/home/anci/new")
DATA_DIR = BASE_DIR / "correct_splits" / "with_genre_groups_network_fixed"
OUT_DIR = BASE_DIR / "models_new" / "rf_network_multiseed"

TRAIN_CSV = DATA_DIR / "train.csv"
VAL_CSV   = DATA_DIR / "val.csv"
TEST_CSV  = DATA_DIR / "test.csv"

# target column: 1 = positive interaction, 0 = negative
TARGET = "owned"
# user-game pair identifier columns

ID_COLS = ["steamid", "appid"]

# numeric input features used by the model
NUMERIC_FEATURES = [
    "total_games_owned",
    "total_playtime_minutes",
    "median_playtime_minutes",
    "unique_genres_played",
    "user_count",
    "game_total_playtime_minutes",
    "release_date",
    "friend_count",
    "game_emb_0", "game_emb_1", "game_emb_2", "game_emb_3",
    "game_emb_4", "game_emb_5", "game_emb_6", "game_emb_7",
    "game_emb_8", "game_emb_9", "game_emb_10", "game_emb_11",
    "game_emb_12", "game_emb_13", "game_emb_14", "game_emb_15",
    "game_emb_16", "game_emb_17", "game_emb_18", "game_emb_19",
    "game_emb_20", "game_emb_21", "game_emb_22", "game_emb_23",
    "game_emb_24", "game_emb_25", "game_emb_26", "game_emb_27",
    "game_emb_28", "game_emb_29", "game_emb_30", "game_emb_31",
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

# categorical input features used by the model
CATEGORICAL_FEATURES = [
    "country",
    "genres",
    "developer",
    "publisher",
    "platforms",
]
# columns loaded from the csv splits
USECOLS = ID_COLS + [TARGET] + NUMERIC_FEATURES + CATEGORICAL_FEATURES

# optional row limits for debugging / faster experiments
MAX_TRAIN_ROWS = int(os.getenv("MAX_TRAIN_ROWS", "0"))
MAX_VAL_ROWS   = int(os.getenv("MAX_VAL_ROWS", "0"))
MAX_TEST_ROWS  = int(os.getenv("MAX_TEST_ROWS", "0"))

# configs for RF experiments
LC_MAX_ROWS = int(os.getenv("LC_MAX_ROWS", "300000"))
RF_NJOBS = int(os.getenv("RF_NJOBS", "8"))
OHE_MAX_CATS = int(os.getenv("OHE_MAX_CATS", "100"))
OHE_MIN_FREQ = int(os.getenv("OHE_MIN_FREQ", "50"))

# fractions used for learning-curve experiments
LC_FRACTIONS = [0.10, 0.30, 0.60, 1.00]


def set_seed(seed: int):
    # set randomness for numpy / python
    random.seed(seed)
    np.random.seed(seed)


def read_split(path: Path, max_rows: int = 0) -> pd.DataFrame:
    # load one split file (and optionally trim it to the first max_rows rows)
    print(f"Loading {path} ...")
    df = pd.read_csv(path, sep=";", usecols=USECOLS, low_memory=False)
    if max_rows > 0:
        df = df.iloc[:max_rows].copy()
        print(f"Trimmed to {len(df)} rows")
    print(f"Loaded {len(df)} rows from {path}")
    return df


# compute Discounted Cumulative Gain at rank k
def dcg_at_k(relevances, k):
    vals = np.asarray(relevances[:k], dtype=float)
    if vals.size == 0:
        return 0.0
    discounts = np.log2(np.arange(2, vals.size + 2))
    return float(np.sum(vals / discounts))


# compute normalized DCG at rank k using the ideal ranking as reference
def ndcg_at_k(y_true_sorted, k):
    ideal = sorted(y_true_sorted, reverse=True)
    best = dcg_at_k(ideal, k)
    if best == 0.0:
        return 0.0
    return dcg_at_k(y_true_sorted, k) / best


def evaluate_ranking(df_scores: pd.DataFrame):
    # evaluate ranking quality per user
    # for each user:
    # - sort candidate games by predicted score
    # - compute ranking metrics on the ordered labels
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


def sparse_to_dense(X):
    # RandomForest in sklearn expects dense input
    # convert sparse matrices produced by preprocessing to dense arrays
    if sparse.issparse(X):
        return X.toarray()
    return X


def build_pipeline(seed: int):
    # build a full sklearn pipeline:
    # - numeric preprocessing: median imputation
    # - categorical preprocessing: missing-value fill + one-hot encoding
    # - sparse-to-dense conversion for RandomForest
    # - final classifier: RandomForestClassifier
    
     # note:
    # numeric scaling is not used here because tree-based models do not require feature scaling
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])
    # use constrained one-hot encoding to limit feature explosion from rare categories
    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="MISSING")),
        ("onehot", OneHotEncoder(
            handle_unknown="infrequent_if_exist",
            max_categories=OHE_MAX_CATS,
            min_frequency=OHE_MIN_FREQ,
        )),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
        sparse_threshold=0.3,
    )

    model = RandomForestClassifier(
        n_estimators=BEST_PARAMS["n_estimators"],
        max_depth=BEST_PARAMS["max_depth"],
        min_samples_split=BEST_PARAMS["min_samples_split"],
        min_samples_leaf=BEST_PARAMS["min_samples_leaf"],
        max_features=BEST_PARAMS["max_features"],
        bootstrap=True,
        class_weight="balanced_subsample",
        random_state=seed,
        n_jobs=RF_NJOBS,
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("to_dense", FunctionTransformer(sparse_to_dense, accept_sparse=True)),
        ("model", model),
    ])
    return pipe


def evaluate_dataset(pipe, df: pd.DataFrame, split_name: str):
    # evaluate the trained model on one split
    # produce ROC-AUC, ranking metrics and scored dataframe
    print("\n" + "=" * 80)
    print(f"Evaluating on {split_name}...")

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_true = df[TARGET].astype(int).to_numpy()

    scores = pipe.predict_proba(X)[:, 1]
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


def make_learning_curve_multiseed(train_df, val_df, out_dir: Path):
    # train the final RF configuration on increasing fractions of train data
    # and measure:
    # - train ROC-AUC
    # - validation ROC-AUC
    # - validation ranking metrics
    # across multiple seeds
    positives_df = train_df[train_df[TARGET] == 1]
    negatives_df = train_df[train_df[TARGET] == 0]

    # optionally reduce the data used for learning curves
    # this keeps RF training time manageable on large splits
    if LC_MAX_ROWS > 0 and len(train_df) > LC_MAX_ROWS:
        pos_target = max(1, int(LC_MAX_ROWS * (len(positives_df) / len(train_df))))
        neg_target = max(1, LC_MAX_ROWS - pos_target)

        pos_part = positives_df.iloc[:min(pos_target, len(positives_df))]
        neg_part = negatives_df.iloc[:min(neg_target, len(negatives_df))]
        train_df = pd.concat([pos_part, neg_part], axis=0).sample(frac=1.0, random_state=42).reset_index(drop=True)
        positives_df = train_df[train_df[TARGET] == 1]
        negatives_df = train_df[train_df[TARGET] == 0]

    print(f"[LC] Using {len(train_df)} rows for learning curve")

    rows = []
    X_val = val_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_val = val_df[TARGET].astype(int).copy()

    for seed in SEEDS:
        print("\n" + "=" * 80)
        print(f"Learning curve for seed={seed}")

        for frac in LC_FRACTIONS:
            n_total = max(2, int(len(train_df) * frac))
            pos_rate = len(positives_df) / len(train_df)
            n_pos = max(1, int(n_total * pos_rate))
            n_neg = max(1, n_total - n_pos)

            part_pos = positives_df.iloc[:min(n_pos, len(positives_df))]
            part_neg = negatives_df.iloc[:min(n_neg, len(negatives_df))]
            part = pd.concat([part_pos, part_neg], axis=0).sample(frac=1.0, random_state=seed)

            X_part = part[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
            y_part = part[TARGET].astype(int).copy()

            pipe = build_pipeline(seed)
            t0 = time.time()
            pipe.fit(X_part, y_part)
            fit_seconds = time.time() - t0

            train_scores = pipe.predict_proba(X_part)[:, 1]
            val_scores = pipe.predict_proba(X_val)[:, 1]

            train_auc = float(roc_auc_score(y_part, train_scores))
            val_auc = float(roc_auc_score(y_val, val_scores))

            val_score_df = val_df[["steamid", "appid", TARGET]].copy()
            val_score_df["score"] = val_scores
            val_metrics, _ = evaluate_ranking(val_score_df.rename(columns={TARGET: "owned"}))

            row = {
                "seed": seed,
                "fraction": frac,
                "n_rows": int(len(part)),
                "fit_seconds": fit_seconds,
                "train_roc_auc": train_auc,
                "val_roc_auc": val_auc,
                "NDCG@10": float(val_metrics["NDCG@10"]),
                "Recall@10": float(val_metrics["Recall@10"]),
            }
            rows.append(row)
            print(f"[LC] seed={seed} fraction={frac:.2f} rows={len(part)} val_ndcg10={val_metrics['NDCG@10']:.6f}")

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

    # plot learning curve ROC-AUC
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
    plt.title("Learning Curve — RF Network (multi-seed)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_roc_auc_multiseed.png", dpi=200)
    plt.close()

    # plot learning curve ranking
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
    plt.title("Learning Curve — RF Network Ranking (multi-seed)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_ranking_multiseed.png", dpi=200)
    plt.close()


def main():
    # train, validate, test, and save RF network model across multiple seeds
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    train_df = read_split(TRAIN_CSV, MAX_TRAIN_ROWS)
    val_df   = read_split(VAL_CSV, MAX_VAL_ROWS)
    test_df  = read_split(TEST_CSV, MAX_TEST_ROWS)

    X_train = train_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_train = train_df[TARGET].astype(int).copy()

    all_seed_runs = []
    per_seed_val = []
    per_seed_test = []

    # train one model per seed using fixed best hyperparameters
    for seed in SEEDS:
        print("\n" + "=" * 80)
        print(f"FINAL RUN FOR SEED {seed}")
        print("=" * 80)

        set_seed(seed)

        pipe = build_pipeline(seed)

        t0 = time.time()
        pipe.fit(X_train, y_train)
        fit_seconds = time.time() - t0

        val_auc, val_metrics, _, _ = evaluate_dataset(pipe, val_df, "val")
        test_auc, test_metrics, per_user_metrics, test_score_df = evaluate_dataset(pipe, test_df, "test")

        joblib.dump(pipe, OUT_DIR / f"best_model_seed{seed}.joblib")
        test_score_df.to_csv(OUT_DIR / f"test_scores_seed{seed}.csv.gz", index=False, compression="gzip")
        per_user_metrics.to_csv(OUT_DIR / f"test_per_user_metrics_seed{seed}.csv", index=False)

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

    make_learning_curve_multiseed(train_df, val_df, OUT_DIR)

    final_results = {
        "model_type": "rf",
        "dataset_type": "network",
        "train_rows": int(len(train_df)),
        "val_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "rf_njobs": RF_NJOBS,
        "ohe_max_categories": OHE_MAX_CATS,
        "ohe_min_frequency": OHE_MIN_FREQ,
        "learning_curve_max_rows": LC_MAX_ROWS,
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