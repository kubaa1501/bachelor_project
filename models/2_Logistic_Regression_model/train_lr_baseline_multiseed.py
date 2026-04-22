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

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# run final model with multiple seeds to report mean ± std
SEEDS = [42, 0, 1]

# best hyperparameters selected earlier during search (code: train_lr_baseline.py)
BEST_PARAMS = {
    "C": 1.0,
    "class_weight": "balanced",
}

# paths
BASE_DIR = Path("/home/anci/new")
DATA_DIR = BASE_DIR / "correct_splits" / "with_genre_groups"
OUT_DIR = BASE_DIR / "models_new" / "lr_baseline_multiseed"

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

# fractions used for learning-curve experiments
LC_FRACTIONS = [0.10, 0.50, 1.00]


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



def build_pipeline(seed: int):
    # build a full sklearn pipeline:
    # - numeric preprocessing: median imputation + standard scaling
    # - categorical preprocessing: missing-value fill + one-hot encoding
    # - final classifier: Logistic Regression
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="MISSING")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
        sparse_threshold=1.0,
    )

    model = LogisticRegression(
        C=BEST_PARAMS["C"],
        class_weight=BEST_PARAMS["class_weight"],
        solver="saga",
        penalty="l2",
        max_iter=300,
        random_state=seed,
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])
    return pipe



# train and evaluate one seed 
def train_and_evaluate_for_seed(seed, train_df, val_df, test_df, save_model=True):
    print("\n" + "=" * 100)
    print(f"SEED {seed} | BEST_PARAMS={BEST_PARAMS}")
    print("=" * 100)

    set_seed(seed)

    X_train = train_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_train = train_df[TARGET].astype(int).copy()

    X_val = val_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_val = val_df[TARGET].astype(int).copy()

    X_test = test_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_test = test_df[TARGET].astype(int).copy()

    pipe = build_pipeline(seed)
    
    # fit model on train split
    t0 = time.time()
    pipe.fit(X_train, y_train)
    fit_seconds = time.time() - t0

    # predict on validation and test
    val_scores = pipe.predict_proba(X_val)[:, 1]
    test_scores = pipe.predict_proba(X_test)[:, 1]

    # compute classification ROC-AUC
    val_auc = float(roc_auc_score(y_val, val_scores))
    test_auc = float(roc_auc_score(y_test, test_scores))

    # evaluate validation ranking + ROC-AUC
    val_score_df = val_df[["steamid", "appid", TARGET]].copy()
    val_score_df["score"] = val_scores
    val_metrics, _ = evaluate_ranking(val_score_df.rename(columns={TARGET: "owned"}))
    val_metrics = {"ROC-AUC": val_auc, **val_metrics}

    # evaluate test ranking + ROC-AUC
    test_score_df = test_df[["steamid", "appid", TARGET]].copy()
    test_score_df["score"] = test_scores
    test_metrics, per_user_metrics = evaluate_ranking(test_score_df.rename(columns={TARGET: "owned"}))
    test_metrics = {"ROC-AUC": test_auc, **test_metrics}


    # save fitted pipeline and detailed test outputs for current seed
    if save_model:
        joblib.dump(pipe, OUT_DIR / f"best_model_seed{seed}.joblib")
        test_score_df.to_csv(
            OUT_DIR / f"test_scores_seed{seed}.csv.gz",
            index=False,
            compression="gzip",
        )
        per_user_metrics.to_csv(
            OUT_DIR / f"test_per_user_metrics_seed{seed}.csv",
            index=False,
        )

    print(f"[seed={seed}] fit_seconds={fit_seconds:.2f}")
    print(f"[seed={seed}] val ROC-AUC={val_auc:.6f}, val NDCG@10={val_metrics['NDCG@10']:.6f}")
    print(f"[seed={seed}] test ROC-AUC={test_auc:.6f}, test NDCG@10={test_metrics['NDCG@10']:.6f}")

    return {
        "seed": seed,
        "fit_seconds": float(fit_seconds),
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
    }


# multi-seed learning curve
def make_learning_curve_multiseed(train_df, val_df, out_dir: Path):
    # train the best LR configuration on increasing fractions of train data
    # for multiple seeds and measure:
    # - train ROC-AUC
    # - validation ROC-AUC
    # - validation ranking metrics
    # save per-seed curves, aggregated curves, and plots
    print("\n" + "=" * 100)
    print("MULTI-SEED LEARNING CURVE")
    print("=" * 100)

    X_val = val_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_val = val_df[TARGET].astype(int).copy()

    positives_df = train_df[train_df[TARGET] == 1].copy()
    negatives_df = train_df[train_df[TARGET] == 0].copy()

    all_rows = []

    for seed in SEEDS:
        set_seed(seed)
        print(f"\n[LC] seed={seed}")

        for frac in LC_FRACTIONS:
            n_total = int(len(train_df) * frac)
            n_pos = max(1, int(len(positives_df) * frac))
            n_neg = max(1, n_total - n_pos)

            part_pos = positives_df.iloc[:min(n_pos, len(positives_df))]
            part_neg = negatives_df.iloc[:min(n_neg, len(negatives_df))]
            part = pd.concat([part_pos, part_neg], axis=0).sample(frac=1.0, random_state=seed)

            X_part = part[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
            y_part = part[TARGET].astype(int).copy()

            pipe = build_pipeline(seed)

            # fit model on one training fraction
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
            all_rows.append(row)

            print(
                f"[LC] seed={seed} fraction={frac:.2f} rows={len(part)} "
                f"val_auc={val_auc:.6f} val_ndcg10={val_metrics['NDCG@10']:.6f}"
            )

    lc_df = pd.DataFrame(all_rows)
    lc_df.to_csv(out_dir / "learning_curve_per_seed.csv", index=False)

    # aggregate learning-curve statistics across seeds
    agg_df = (
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
    )

    agg_df = agg_df.fillna(0.0)
    agg_df.to_csv(out_dir / "learning_curve_aggregated.csv", index=False)

    # plot aggregated ROC-AUC learning curve with std shading
    plt.figure(figsize=(8, 5))
    plt.plot(agg_df["n_rows"], agg_df["train_roc_auc_mean"], marker="o", label="Train ROC-AUC")
    plt.fill_between(
        agg_df["n_rows"],
        agg_df["train_roc_auc_mean"] - agg_df["train_roc_auc_std"],
        agg_df["train_roc_auc_mean"] + agg_df["train_roc_auc_std"],
        alpha=0.2,
    )
    plt.plot(agg_df["n_rows"], agg_df["val_roc_auc_mean"], marker="o", label="Val ROC-AUC")
    plt.fill_between(
        agg_df["n_rows"],
        agg_df["val_roc_auc_mean"] - agg_df["val_roc_auc_std"],
        agg_df["val_roc_auc_mean"] + agg_df["val_roc_auc_std"],
        alpha=0.2,
    )
    plt.xlabel("Training rows")
    plt.ylabel("ROC-AUC")
    plt.title("Learning Curve — LR Baseline (multi-seed)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_roc_auc_multiseed.png", dpi=200)
    plt.close()

    # plot aggregated ranking learning curve with std shading
    plt.figure(figsize=(8, 5))
    plt.plot(agg_df["n_rows"], agg_df["ndcg10_mean"], marker="o", label="Val NDCG@10")
    plt.fill_between(
        agg_df["n_rows"],
        agg_df["ndcg10_mean"] - agg_df["ndcg10_std"],
        agg_df["ndcg10_mean"] + agg_df["ndcg10_std"],
        alpha=0.2,
    )
    plt.plot(agg_df["n_rows"], agg_df["recall10_mean"], marker="o", label="Val Recall@10")
    plt.fill_between(
        agg_df["n_rows"],
        agg_df["recall10_mean"] - agg_df["recall10_std"],
        agg_df["recall10_mean"] + agg_df["recall10_std"],
        alpha=0.2,
    )
    plt.xlabel("Training rows")
    plt.ylabel("Score")
    plt.title("Learning Curve — LR Baseline Ranking (multi-seed)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_ranking_multiseed.png", dpi=200)
    plt.close()

    return lc_df, agg_df



# main
def main():
    # train, validate, test, and save LR baseline multi-seed model
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    train_df = read_split(TRAIN_CSV, MAX_TRAIN_ROWS)
    val_df   = read_split(VAL_CSV, MAX_VAL_ROWS)
    test_df  = read_split(TEST_CSV, MAX_TEST_ROWS)

    all_seed_runs = []
    per_seed_val = []
    per_seed_test = []
    
    # train and evaluate final model for each seed
    for seed in SEEDS:
        run = train_and_evaluate_for_seed(
            seed=seed,
            train_df=train_df,
            val_df=val_df,
            test_df=test_df,
            save_model=True,
        )
        all_seed_runs.append(run)

        per_seed_val.append({
            "seed": seed,
            **run["val_metrics"],
        })
        per_seed_test.append({
            "seed": seed,
            **run["test_metrics"],
        })
    # aggregate validation and test metrics across seeds
    val_metrics_agg = aggregate_metrics([r["val_metrics"] for r in all_seed_runs])
    test_metrics_agg = aggregate_metrics([r["test_metrics"] for r in all_seed_runs])

    # build multi-seed learning curves for the best config
    make_learning_curve_multiseed(train_df, val_df, OUT_DIR)

    # final summary .json
    final_results = {
        "model_type": "lr",
        "dataset_type": "baseline",
        "config": {
            "solver": "saga",
            "penalty": "l2",
            "max_iter": 300,
            "seeds": SEEDS,
            "best_params": BEST_PARAMS,
        },
        "train_rows": int(len(train_df)),
        "val_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "features_numeric": NUMERIC_FEATURES,
        "features_categorical": CATEGORICAL_FEATURES,
        "val_metrics": val_metrics_agg,
        "test_metrics": test_metrics_agg,
        "per_seed_val": per_seed_val,
        "per_seed_test": per_seed_test,
    }

    with open(OUT_DIR / "results.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2)

    print("\n" + "=" * 100)
    print("FINAL MULTI-SEED RESULTS")
    print("=" * 100)
    print(json.dumps(final_results, indent=2))
    print(f"\nSaved to: {OUT_DIR}")


if __name__ == "__main__":
    main()