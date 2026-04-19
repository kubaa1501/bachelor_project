#!/usr/bin/env python3
import os
import json
import time
import joblib
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

# global seed 
SEED = 42
np.random.seed(SEED)

# paths
BASE_DIR = Path("/home/anci/new")
DATA_DIR = BASE_DIR / "correct_splits" / "with_genre_groups"
OUT_DIR = BASE_DIR / "models_new" / "lr_baseline"

TRAIN_CSV = DATA_DIR / "train.csv"
VAL_CSV   = DATA_DIR / "val.csv"
TEST_CSV  = DATA_DIR / "test.csv"

# target, 1- positive interaction, 0- negative
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

# optional row limits for debugging / faster experiments
MAX_TRAIN_ROWS = int(os.getenv("MAX_TRAIN_ROWS", "0"))
MAX_VAL_ROWS   = int(os.getenv("MAX_VAL_ROWS", "0"))
MAX_TEST_ROWS  = int(os.getenv("MAX_TEST_ROWS", "0"))

# fractions used for learning-curve experiments
LC_FRACTIONS = [0.10, 0.50, 1.00]

# load one split file (and optionally trim it to the first max_rows rows)
def read_split(path: Path, max_rows: int = 0) -> pd.DataFrame:
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
    # evaluate ranking quality per user.
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


def build_pipeline(C: float, class_weight):
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
        C=C,
        class_weight=class_weight,
        solver="saga",
        penalty="l2",
        max_iter=300,
        random_state=SEED,
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])
    return pipe


def make_learning_curve(best_params, train_df, val_df, out_dir: Path):
    # train the best LR configuration on increasing fractions of train data
    # and measure:
    # - train ROC-AUC
    # - validation ROC-AUC
    # - validation ranking metrics
    # save curves and plots 
    rows = []
    X_val = val_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_val = val_df[TARGET].astype(int).copy()

    positives_df = train_df[train_df[TARGET] == 1]
    negatives_df = train_df[train_df[TARGET] == 0]

    for frac in LC_FRACTIONS:
        n_total = int(len(train_df) * frac)
        n_pos = max(1, int(len(positives_df) * frac))
        n_neg = max(1, n_total - n_pos)

        part_pos = positives_df.iloc[:min(n_pos, len(positives_df))]
        part_neg = negatives_df.iloc[:min(n_neg, len(negatives_df))]
        part = pd.concat([part_pos, part_neg], axis=0).sample(frac=1.0, random_state=SEED)

        X_part = part[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
        y_part = part[TARGET].astype(int).copy()

        pipe = build_pipeline(best_params["C"], best_params["class_weight"])
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
            "fraction": frac,
            "n_rows": int(len(part)),
            "n_pos": int((y_part == 1).sum()),
            "n_neg": int((y_part == 0).sum()),
            "fit_seconds": fit_seconds,
            "train_roc_auc": train_auc,
            "val_roc_auc": val_auc,
            **val_metrics,
        }
        rows.append(row)
        print(f"[LC] fraction={frac:.2f} rows={len(part)} val_ndcg10={val_metrics['NDCG@10']:.6f}")

    lc_df = pd.DataFrame(rows)
    lc_df.to_csv(out_dir / "learning_curve.csv", index=False)

    plt.figure(figsize=(8, 5))
    plt.plot(lc_df["n_rows"], lc_df["train_roc_auc"], marker="o", label="Train ROC-AUC")
    plt.plot(lc_df["n_rows"], lc_df["val_roc_auc"], marker="o", label="Val ROC-AUC")
    plt.xlabel("Training rows")
    plt.ylabel("ROC-AUC")
    plt.title("Learning Curve — LR Baseline")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_roc_auc.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(lc_df["n_rows"], lc_df["NDCG@10"], marker="o", label="Val NDCG@10")
    plt.plot(lc_df["n_rows"], lc_df["Recall@10"], marker="o", label="Val Recall@10")
    plt.xlabel("Training rows")
    plt.ylabel("Score")
    plt.title("Learning Curve — LR Baseline Ranking")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_ranking.png", dpi=200)
    plt.close()

    return lc_df


def main():
    # train, validate, test, and save LR baseline model
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    train_df = read_split(TRAIN_CSV, MAX_TRAIN_ROWS)
    val_df   = read_split(VAL_CSV, MAX_VAL_ROWS)
    test_df  = read_split(TEST_CSV, MAX_TEST_ROWS)

    X_train = train_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_train = train_df[TARGET].astype(int).copy()

    X_val = val_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_val = val_df[TARGET].astype(int).copy()

    X_test = test_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_test = test_df[TARGET].astype(int).copy()
# small hyperparameter grid for model selection
    grid = [
        {"C": 0.1, "class_weight": None},
        {"C": 1.0, "class_weight": "balanced"},
    ]

    all_trials = []
    best_model = None
    best_params = None
    best_val_ndcg10 = -1.0
    best_val_row = None
    # train and evaluate each hyperparameter setting
    for i, params in enumerate(grid, start=1):
        print("\n" + "=" * 80)
        print(f"Trial {i}/{len(grid)}: {params}")

        pipe = build_pipeline(params["C"], params["class_weight"])
        # fit model on train
        t0 = time.time()
        pipe.fit(X_train, y_train)
        fit_seconds = time.time() - t0
        # predict on validation
        val_scores = pipe.predict_proba(X_val)[:, 1]
        val_score_df = val_df[["steamid", "appid", TARGET]].copy()
        val_score_df["score"] = val_scores
        # evaluate validation ranking + ROC-AUC
        val_metrics, _ = evaluate_ranking(val_score_df.rename(columns={TARGET: "owned"}))
        val_auc = float(roc_auc_score(y_val, val_scores))

        row = {
            "trial": i,
            "C": params["C"],
            "class_weight": params["class_weight"],
            "fit_seconds": fit_seconds,
            "val_roc_auc": val_auc,
            **val_metrics,
        }
        all_trials.append(row)

        print(json.dumps(row, indent=2))
        # select best model using NDCG@10
        if val_metrics["NDCG@10"] > best_val_ndcg10:
            best_val_ndcg10 = val_metrics["NDCG@10"]
            best_model = pipe
            best_params = params
            best_val_row = row
    # save all val trials 
    pd.DataFrame(all_trials).to_csv(OUT_DIR / "val_trials.csv", index=False)

    print("\nBest params:")
    print(best_params)
    print("Best VAL NDCG@10:", best_val_ndcg10)
    # evaluate best model on test 
    test_scores = best_model.predict_proba(X_test)[:, 1]
    test_score_df = test_df[["steamid", "appid", TARGET]].copy()
    test_score_df["score"] = test_scores

    test_metrics, per_user_metrics = evaluate_ranking(
        test_score_df.rename(columns={TARGET: "owned"})
    )
    test_auc = float(roc_auc_score(y_test, test_scores))
    # save test predictions and per-user ranking metrics 
    test_score_df.to_csv(OUT_DIR / "test_scores.csv.gz", index=False, compression="gzip")
    per_user_metrics.to_csv(OUT_DIR / "test_per_user_metrics.csv", index=False)
    # save the full fitted sklearn pipeline 
    joblib.dump(best_model, OUT_DIR / "best_model.joblib")
    # final summay .json 
    final_results = {
        "model_type": "lr",
        "dataset_type": "baseline",
        "seed": SEED,
        "train_rows": int(len(train_df)),
        "val_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "features_numeric": NUMERIC_FEATURES,
        "features_categorical": CATEGORICAL_FEATURES,
        "best_params": best_params,
        "best_val": best_val_row,
        "test_roc_auc": test_auc,
        **test_metrics,
    }

    with open(OUT_DIR / "results.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2)
    # build learning curves for the best config
    make_learning_curve(best_params, train_df, val_df, OUT_DIR)

    print("\nFINAL TEST RESULTS")
    print(json.dumps(final_results, indent=2))
    print(f"Saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()