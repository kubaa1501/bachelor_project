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
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

# global seed 
SEED = 42
np.random.seed(SEED)

# paths
BASE_DIR = Path("/home/anci/new")
DATA_DIR = BASE_DIR / "correct_splits" / "with_genre_groups_network_fixed"
OUT_DIR = BASE_DIR / "models_new" / "xgb_network"

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

# additional config for XGB experiments
LC_MAX_ROWS = int(os.getenv("LC_MAX_ROWS", "1000000"))
XGB_NJOBS = int(os.getenv("XGB_NJOBS", "8"))
OHE_MAX_CATS = int(os.getenv("OHE_MAX_CATS", "100"))
OHE_MIN_FREQ = int(os.getenv("OHE_MIN_FREQ", "50"))

# fractions used for learning-curve experiments
LC_FRACTIONS = [0.05, 0.10, 0.20, 0.40, 0.70, 1.00]


def read_split(path: Path, max_rows: int = 0) -> pd.DataFrame:
    # load one split file (and optionally trim it to the first max_rows rows)
    print(f"Loading {path} ...")
    df = pd.read_csv(path, sep=";", usecols=USECOLS)
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

    # aggregate metrics across users
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


def build_pipeline(params):
    # build a full sklearn pipeline:
    # - numeric preprocessing: median imputation
    # - categorical preprocessing: missing-value fill + one-hot encoding
    # - final classifier: XGBClassifier

    # note:
    # numeric scaling is not used here because tree-based boosting models do not require feature scaling
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

    model = XGBClassifier(
        n_estimators=params["n_estimators"],
        max_depth=params["max_depth"],
        learning_rate=params["learning_rate"],
        min_child_weight=params["min_child_weight"],
        subsample=params["subsample"],
        colsample_bytree=params["colsample_bytree"],
        reg_lambda=params["reg_lambda"],
        reg_alpha=params["reg_alpha"],
        objective="binary:logistic",
        eval_metric="logloss",
        tree_method="hist",
        random_state=SEED,
        n_jobs=XGB_NJOBS,
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])
    return pipe


def make_learning_curve(best_params, train_df, val_df, out_dir: Path):
    # train the best XGB configuration on increasing fractions of train data
    # and measure:
    # - train ROC-AUC
    # - validation ROC-AUC
    # - validation ranking metrics
    # save curves and plots
    positives_df = train_df[train_df[TARGET] == 1]
    negatives_df = train_df[train_df[TARGET] == 0]
    
    # optionally reduce the data used for learning curves
    # this keeps XGB training time manageable on large splits
    if LC_MAX_ROWS > 0 and len(train_df) > LC_MAX_ROWS:
        pos_target = max(1, int(LC_MAX_ROWS * (len(positives_df) / len(train_df))))
        neg_target = max(1, LC_MAX_ROWS - pos_target)

        pos_part = positives_df.iloc[:min(pos_target, len(positives_df))]
        neg_part = negatives_df.iloc[:min(neg_target, len(negatives_df))]
        train_df = pd.concat([pos_part, neg_part], axis=0).sample(frac=1.0, random_state=SEED).reset_index(drop=True)
        positives_df = train_df[train_df[TARGET] == 1]
        negatives_df = train_df[train_df[TARGET] == 0]

    print(f"[LC] Using {len(train_df)} rows for learning curve")

    rows = []
    X_val = val_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y_val = val_df[TARGET].astype(int).copy()

    for frac in LC_FRACTIONS:
        n_total = max(2, int(len(train_df) * frac))
        pos_rate = len(positives_df) / len(train_df)
        n_pos = max(1, int(n_total * pos_rate))
        n_neg = max(1, n_total - n_pos)

        part_pos = positives_df.iloc[:min(n_pos, len(positives_df))]
        part_neg = negatives_df.iloc[:min(n_neg, len(negatives_df))]
        part = pd.concat([part_pos, part_neg], axis=0).sample(frac=1.0, random_state=SEED)

        X_part = part[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
        y_part = part[TARGET].astype(int).copy()

        pipe = build_pipeline(best_params)
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
            "fit_seconds": fit_seconds,
            "train_roc_auc": train_auc,
            "val_roc_auc": val_auc,
            **val_metrics,
        }
        rows.append(row)
        print(f"[LC] fraction={frac:.2f} rows={len(part)} val_ndcg10={val_metrics['NDCG@10']:.6f}")

    lc_df = pd.DataFrame(rows)
    lc_df.to_csv(out_dir / "learning_curve.csv", index=False)

    # plot train/validation ROC-AUC as a function of training set size
    plt.figure(figsize=(8, 5))
    plt.plot(lc_df["n_rows"], lc_df["train_roc_auc"], marker="o", label="Train ROC-AUC")
    plt.plot(lc_df["n_rows"], lc_df["val_roc_auc"], marker="o", label="Val ROC-AUC")
    plt.xlabel("Training rows")
    plt.ylabel("ROC-AUC")
    plt.title("Learning Curve — XGB Network")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_roc_auc.png", dpi=200)
    plt.close()

    # plot validation ranking metrics as a function of training set size
    plt.figure(figsize=(8, 5))
    plt.plot(lc_df["n_rows"], lc_df["NDCG@10"], marker="o", label="Val NDCG@10")
    plt.plot(lc_df["n_rows"], lc_df["Recall@10"], marker="o", label="Val Recall@10")
    plt.xlabel("Training rows")
    plt.ylabel("Score")
    plt.title("Learning Curve — XGB Network Ranking")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_ranking.png", dpi=200)
    plt.close()


def main():
    # train, validate, test, and save XGB network model
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

    # hyperparameter grid for model selection
    grid = [
        {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.05, "min_child_weight": 3, "subsample": 0.8, "colsample_bytree": 0.8, "reg_lambda": 1.0, "reg_alpha": 0.0},
        {"n_estimators": 300, "max_depth": 4, "learning_rate": 0.05, "min_child_weight": 3, "subsample": 0.8, "colsample_bytree": 0.8, "reg_lambda": 1.0, "reg_alpha": 0.0},
        {"n_estimators": 300, "max_depth": 6, "learning_rate": 0.05, "min_child_weight": 5, "subsample": 0.8, "colsample_bytree": 0.8, "reg_lambda": 1.0, "reg_alpha": 0.1},
        {"n_estimators": 300, "max_depth": 6, "learning_rate": 0.10, "min_child_weight": 5, "subsample": 0.8, "colsample_bytree": 0.8, "reg_lambda": 2.0, "reg_alpha": 0.1},
        {"n_estimators": 400, "max_depth": 6, "learning_rate": 0.05, "min_child_weight": 5, "subsample": 1.0, "colsample_bytree": 1.0, "reg_lambda": 2.0, "reg_alpha": 0.1},
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

        pipe = build_pipeline(params)
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
            **params,
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

    # save all validation trials
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

    # final summary .json
    final_results = {
        "model_type": "xgb",
        "dataset_type": "network",
        "seed": SEED,
        "train_rows": int(len(train_df)),
        "val_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "xgb_njobs": XGB_NJOBS,
        "ohe_max_categories": OHE_MAX_CATS,
        "ohe_min_frequency": OHE_MIN_FREQ,
        "learning_curve_max_rows": LC_MAX_ROWS,
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