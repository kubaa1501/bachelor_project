#!/usr/bin/env python3
import argparse
import json
import os
import random
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
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer
from xgboost import XGBClassifier

# ============================================================
# Multi-seed XGBoost experiment runner
# Trains selected/all XGB experiments models on seeds [42, 0, 1] 
# on each models best hyperparameters and writes results compatible
# with paired significance tests:
#   - val_metrics mean/std
#   - test_metrics mean/std
#   - per_seed_val
#   - per_seed_test
#   - learning_curve.csv
#   - learning_curve_per_seed.csv
# ============================================================

SEEDS = [42, 0, 1]

BASE_DIR = Path(os.getenv("BASE_DIR", "/home/anci/new"))
MODELS_DIR = BASE_DIR / "models_new"

TARGET = "owned"
ID_COLS = ["steamid", "appid"]

MAX_TRAIN_ROWS = int(os.getenv("MAX_TRAIN_ROWS", "0"))
MAX_VAL_ROWS = int(os.getenv("MAX_VAL_ROWS", "0"))
MAX_TEST_ROWS = int(os.getenv("MAX_TEST_ROWS", "0"))

LC_MAX_ROWS = int(os.getenv("LC_MAX_ROWS", "1000000"))
XGB_NJOBS = int(os.getenv("XGB_NJOBS", "8"))
OHE_MAX_CATS = int(os.getenv("OHE_MAX_CATS", "100"))
OHE_MIN_FREQ = int(os.getenv("OHE_MIN_FREQ", "50"))
FAKE_EMB_TARGET_CORR = float(os.getenv("FAKE_EMB_TARGET_CORR", "0.97"))

LC_FRACTIONS = [0.05, 0.10, 0.20, 0.40, 0.70, 1.00]

STANDARD_XGB_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.10,
    "min_child_weight": 5,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "reg_lambda": 2.0,
    "reg_alpha": 0.1,
}

EMBEDDINGS_ONLY_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "min_child_weight": 5,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "reg_lambda": 1.0,
    "reg_alpha": 0.1,
}

USERCOUNT_EMB0_ONLY_PARAMS = {
    "n_estimators": 500,
    "max_depth": 5,
    "learning_rate": 0.03,
    "min_child_weight": 5,
    "subsample": 1.0,
    "colsample_bytree": 1.0,
    "reg_lambda": 2.0,
    "reg_alpha": 0.1,
}

BASELINE_NUMERIC = [
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

BASELINE_WITHOUT_USER_COUNT_NUMERIC = [
    "total_games_owned",
    "total_playtime_minutes",
    "median_playtime_minutes",
    "unique_genres_played",
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

NETWORK_BASIC_NUMERIC_PREFIX = [
    "total_games_owned",
    "total_playtime_minutes",
    "median_playtime_minutes",
    "unique_genres_played",
    "user_count",
    "game_total_playtime_minutes",
    "release_date",
    "friend_count",
]

GENRE_GROUP_NUMERIC = [
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

EMB_COLS = [f"game_emb_{i}" for i in range(32)]

CATEGORICAL = ["country", "genres", "developer", "publisher", "platforms"]

FAKE_EMB_SOURCE_COL = "user_count"
FAKE_EMB_COL = "fake_emb_0_from_user_count"

EXPERIMENTS = {
    # original ablations based on non-network split
    "baseline_without_user_count": {
        "dataset_type": "baseline_without_user_count",
        "data_subdir": "correct_splits/with_genre_groups",
        "out_subdir": "xgb_baseline_without_user_count_multiseed",
        "numeric_features": BASELINE_WITHOUT_USER_COUNT_NUMERIC,
        "categorical_features": CATEGORICAL,
        "best_params": STANDARD_XGB_PARAMS,
        "uses_log_user_count": False,
        "uses_fake_emb": False,
        "title": "XGB Baseline without user_count",
    },
    "baseline_log_user_count": {
        "dataset_type": "baseline_log_user_count",
        "data_subdir": "correct_splits/with_genre_groups",
        "out_subdir": "xgb_baseline_log_user_count_multiseed",
        "numeric_features": BASELINE_WITHOUT_USER_COUNT_NUMERIC,
        "categorical_features": CATEGORICAL,
        "best_params": STANDARD_XGB_PARAMS,
        "uses_log_user_count": True,
        "uses_fake_emb": False,
        "title": "XGB Baseline log(user_count)",
    },
    "baseline_fake_emb_corr97": {
        "dataset_type": "baseline_fake_emb_corr97",
        "data_subdir": "correct_splits/with_genre_groups",
        "out_subdir": "xgb_baseline_fake_emb_corr97_multiseed",
        "numeric_features": BASELINE_NUMERIC + [FAKE_EMB_COL],
        "categorical_features": CATEGORICAL,
        "best_params": STANDARD_XGB_PARAMS,
        "uses_log_user_count": False,
        "uses_fake_emb": True,
        "title": "XGB Baseline + fake embedding corr97",
    },
    # ablations based on network split
    "one_embedding": {
        "dataset_type": "one_embedding",
        "data_subdir": "correct_splits/with_genre_groups_network_fixed",
        "out_subdir": "xgb_one_embedding_multiseed",
        "numeric_features": NETWORK_BASIC_NUMERIC_PREFIX + ["game_emb_0"] + GENRE_GROUP_NUMERIC,
        "categorical_features": CATEGORICAL,
        "best_params": STANDARD_XGB_PARAMS,
        "uses_log_user_count": False,
        "uses_fake_emb": False,
        "title": "XGB One Embedding",
    },
    "emb0_without_user_count": {
        "dataset_type": "emb0_without_user_count",
        "data_subdir": "correct_splits/with_genre_groups_network_fixed",
        "out_subdir": "xgb_emb0_without_user_count_multiseed",
        "numeric_features": [
            "total_games_owned",
            "total_playtime_minutes",
            "median_playtime_minutes",
            "unique_genres_played",
            "game_total_playtime_minutes",
            "release_date",
            "friend_count",
            "game_emb_0",
        ] + GENRE_GROUP_NUMERIC,
        "categorical_features": CATEGORICAL,
        "best_params": STANDARD_XGB_PARAMS,
        "uses_log_user_count": False,
        "uses_fake_emb": False,
        "title": "XGB emb0 without user_count",
    },
    "usercount_emb0_only": {
        "dataset_type": "usercount_emb0_only",
        "data_subdir": "correct_splits/with_genre_groups_network_fixed",
        "out_subdir": "xgb_usercount_emb0_only_multiseed",
        "numeric_features": ["user_count", "game_emb_0"],
        "categorical_features": [],
        "best_params": USERCOUNT_EMB0_ONLY_PARAMS,
        "uses_log_user_count": False,
        "uses_fake_emb": False,
        "title": "XGB user_count + emb0 only",
    },
    "embeddings_only": {
        "dataset_type": "embeddings_only",
        "data_subdir": "correct_splits/with_genre_groups_network_fixed",
        "out_subdir": "xgb_embeddings_only_multiseed",
        "numeric_features": EMB_COLS,
        "categorical_features": [],
        "best_params": EMBEDDINGS_ONLY_PARAMS,
        "uses_log_user_count": False,
        "uses_fake_emb": False,
        "title": "XGB Embeddings Only",
    },
    "embeddings_and_basic_info": {
        "dataset_type": "embeddings_and_basic_info",
        "data_subdir": "correct_splits/with_genre_groups_network_fixed",
        "out_subdir": "xgb_embeddings_and_basic_info_multiseed",
        "numeric_features": ["unique_genres_played", "total_playtime_minutes"] + EMB_COLS,
        "categorical_features": [],
        "best_params": STANDARD_XGB_PARAMS,
        "uses_log_user_count": False,
        "uses_fake_emb": False,
        "title": "XGB Embeddings and Basic Info",
    },
}


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)


def zscore_series(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    mean = s.mean()
    std = s.std(ddof=0)
    if pd.isna(std) or std == 0:
        raise ValueError("Cannot z-score a column with zero variance or only missing values.")
    return (s - mean) / std


def build_fake_feature_with_target_corr(x: pd.Series, rho: float, seed: int) -> pd.Series:
    if not (-0.999 < rho < 0.999):
        raise ValueError("rho must be between -0.999 and 0.999")

    xz = zscore_series(x).to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    noise = rng.normal(loc=0.0, scale=1.0, size=len(xz))

    denom = np.dot(xz, xz)
    if denom == 0:
        raise ValueError("Cannot orthogonalize noise because source variance is zero.")

    proj = np.dot(noise, xz) / denom
    noise_orth = noise - proj * xz
    noise_std = noise_orth.std(ddof=0)
    if noise_std == 0:
        raise ValueError("Noise collapsed to zero; try a different seed.")

    noise_orth = noise_orth / noise_std
    fake_z = rho * xz + np.sqrt(1.0 - rho ** 2) * noise_orth

    x_std = pd.to_numeric(x, errors="coerce").std(ddof=0)
    if pd.isna(x_std) or x_std == 0:
        x_std = 1.0

    return pd.Series(fake_z * x_std, index=x.index, name=FAKE_EMB_COL)


def add_fake_embedding_feature(df: pd.DataFrame, split_name: str, seed: int) -> pd.DataFrame:
    df = df.copy()
    if FAKE_EMB_SOURCE_COL not in df.columns:
        raise KeyError(f"Column '{FAKE_EMB_SOURCE_COL}' not found in dataframe.")

    split_offsets = {"train": 101, "val": 202, "test": 303}
    fake_seed = seed + split_offsets.get(split_name.lower(), 999)

    source = pd.to_numeric(df[FAKE_EMB_SOURCE_COL], errors="coerce")
    valid_mask = source.notna()
    if valid_mask.sum() < 3:
        raise ValueError(f"Need at least 3 non-null rows in '{FAKE_EMB_SOURCE_COL}' to build fake embedding.")

    fake_valid = build_fake_feature_with_target_corr(
        source.loc[valid_mask],
        rho=FAKE_EMB_TARGET_CORR,
        seed=fake_seed,
    )

    df[FAKE_EMB_COL] = np.nan
    df.loc[valid_mask, FAKE_EMB_COL] = fake_valid
    df[FAKE_EMB_COL] = df[FAKE_EMB_COL].fillna(df[FAKE_EMB_COL].median())

    corr = df[[FAKE_EMB_SOURCE_COL, FAKE_EMB_COL]].corr(method="pearson").iloc[0, 1]
    print(
        f"[FAKE_EMB] seed={seed} split={split_name} "
        f"corr({FAKE_EMB_SOURCE_COL}, {FAKE_EMB_COL})={corr:.6f} "
        f"target={FAKE_EMB_TARGET_CORR:.4f}"
    )
    return df


def read_split(path: Path, usecols, max_rows: int = 0) -> pd.DataFrame:
    print(f"Loading {path} ...")
    df = pd.read_csv(path, sep=";", usecols=usecols)
    if max_rows > 0:
        df = df.iloc[:max_rows].copy()
        print(f"Trimmed to {len(df)} rows")
    print(f"Loaded {len(df)} rows from {path}")
    return df


def dcg_at_k(relevances, k):
    vals = np.asarray(relevances[:k], dtype=float)
    if vals.size == 0:
        return 0.0
    discounts = np.log2(np.arange(2, vals.size + 2))
    return float(np.sum(vals / discounts))


def ndcg_at_k(y_true_sorted, k):
    ideal = sorted(y_true_sorted, reverse=True)
    best = dcg_at_k(ideal, k)
    if best == 0.0:
        return 0.0
    return dcg_at_k(y_true_sorted, k) / best


def evaluate_ranking(df_scores: pd.DataFrame):
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

    metrics = {"n_users_evaluated": int(len(per_user))}
    for k in [1, 5, 10, 20]:
        metrics[f"HitRate@{k}"] = float(per_user[f"HitRate@{k}"].mean())
        metrics[f"Recall@{k}"] = float(per_user[f"Recall@{k}"].mean())
        metrics[f"NDCG@{k}"] = float(per_user[f"NDCG@{k}"].mean())
    metrics["MRR"] = float(per_user["MRR"].mean())
    return metrics, per_user


def build_pipeline(cfg, seed: int):
    numeric_features = cfg["numeric_features"]
    categorical_features = cfg["categorical_features"]
    params = cfg["best_params"]

    transformers = []

    if numeric_features:
        numeric_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
        ])
        transformers.append(("num", numeric_transformer, numeric_features))

    if cfg.get("uses_log_user_count", False):
        log_user_count_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("log1p", FunctionTransformer(np.log1p, validate=False)),
        ])
        transformers.append(("log_user_count", log_user_count_transformer, ["user_count"]))

    if categorical_features:
        categorical_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="MISSING")),
            ("onehot", OneHotEncoder(
                handle_unknown="infrequent_if_exist",
                max_categories=OHE_MAX_CATS,
                min_frequency=OHE_MIN_FREQ,
            )),
        ])
        transformers.append(("cat", categorical_transformer, categorical_features))

    preprocessor = ColumnTransformer(
        transformers=transformers,
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
        random_state=seed,
        n_jobs=XGB_NJOBS,
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])


def aggregate_metrics(list_of_dicts):
    keys = [k for k in list_of_dicts[0] if k != "n_users_evaluated"]
    result = {}
    for k in keys:
        vals = [d[k] for d in list_of_dicts]
        result[k] = {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
        }
    result["n_users_evaluated"] = list_of_dicts[0]["n_users_evaluated"]
    return result


def get_feature_cols(cfg):
    cols = list(cfg["numeric_features"]) + list(cfg["categorical_features"])
    if cfg.get("uses_log_user_count", False):
        cols = ["user_count"] + cols
    # stable unique order
    return list(dict.fromkeys(cols))


def make_learning_curve(cfg, train_df, val_df, out_dir: Path):
    best_params = cfg["best_params"]
    feature_cols = get_feature_cols(cfg)

    positives_df = train_df[train_df[TARGET] == 1]
    negatives_df = train_df[train_df[TARGET] == 0]

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
    X_val = val_df[feature_cols].copy()
    y_val = val_df[TARGET].astype(int).copy()

    for seed in SEEDS:
        set_seed(seed)
        print("\n" + "=" * 80)
        print(f"[LC] SEED {seed}")

        for frac in LC_FRACTIONS:
            n_total = max(2, int(len(train_df) * frac))
            pos_rate = len(positives_df) / len(train_df)
            n_pos = max(1, int(n_total * pos_rate))
            n_neg = max(1, n_total - n_pos)

            part_pos = positives_df.iloc[:min(n_pos, len(positives_df))]
            part_neg = negatives_df.iloc[:min(n_neg, len(negatives_df))]
            part = pd.concat([part_pos, part_neg], axis=0).sample(frac=1.0, random_state=seed)

            X_part = part[feature_cols].copy()
            y_part = part[TARGET].astype(int).copy()

            pipe = build_pipeline(cfg, seed)
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
    lc_agg.to_csv(out_dir / "learning_curve.csv", index=False)

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
    plt.title(f"Learning Curve — {cfg['title']}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_roc_auc.png", dpi=200)
    plt.close()

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
    plt.title(f"Learning Curve — {cfg['title']} Ranking")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_ranking.png", dpi=200)
    plt.close()


def train_experiment(name: str, cfg: dict):
    print("\n" + "#" * 90)
    print(f"# EXPERIMENT: {name}")
    print("#" * 90)

    data_dir = BASE_DIR / cfg["data_subdir"]
    out_dir = MODELS_DIR / cfg["out_subdir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    train_csv = data_dir / "train.csv"
    val_csv = data_dir / "val.csv"
    test_csv = data_dir / "test.csv"

    # Columns read from disk. For fake feature, source column is read and fake column is generated later.
    read_cols = ID_COLS + [TARGET] + list(cfg["numeric_features"]) + list(cfg["categorical_features"])
    if cfg.get("uses_log_user_count", False):
        read_cols.append("user_count")
    if cfg.get("uses_fake_emb", False):
        read_cols = [c for c in read_cols if c != FAKE_EMB_COL]
        read_cols.append(FAKE_EMB_SOURCE_COL)
    read_cols = list(dict.fromkeys(read_cols))

    base_train_df = read_split(train_csv, read_cols, MAX_TRAIN_ROWS)
    base_val_df = read_split(val_csv, read_cols, MAX_VAL_ROWS)
    base_test_df = read_split(test_csv, read_cols, MAX_TEST_ROWS)

    feature_cols = get_feature_cols(cfg)
    all_seeds_val_metrics = []
    all_seeds_test_metrics = []

    for seed in SEEDS:
        print("\n" + "=" * 80)
        print(f"{name} | SEED {seed}")
        print(f"Best params: {cfg['best_params']}")
        set_seed(seed)

        if cfg.get("uses_fake_emb", False):
            train_df = add_fake_embedding_feature(base_train_df, "train", seed)
            val_df = add_fake_embedding_feature(base_val_df, "val", seed)
            test_df = add_fake_embedding_feature(base_test_df, "test", seed)
        else:
            train_df = base_train_df
            val_df = base_val_df
            test_df = base_test_df

        X_train = train_df[feature_cols].copy()
        y_train = train_df[TARGET].astype(int).copy()
        X_val = val_df[feature_cols].copy()
        y_val = val_df[TARGET].astype(int).copy()
        X_test = test_df[feature_cols].copy()
        y_test = test_df[TARGET].astype(int).copy()

        pipe = build_pipeline(cfg, seed)
        t0 = time.time()
        pipe.fit(X_train, y_train)
        fit_seconds = time.time() - t0

        val_scores = pipe.predict_proba(X_val)[:, 1]
        val_score_df = val_df[["steamid", "appid", TARGET]].copy()
        val_score_df["score"] = val_scores
        val_metrics, _ = evaluate_ranking(val_score_df.rename(columns={TARGET: "owned"}))
        val_auc = float(roc_auc_score(y_val, val_scores))

        val_row = {
            "seed": seed,
            "fit_seconds": fit_seconds,
            "val_roc_auc": val_auc,
            **val_metrics,
        }
        all_seeds_val_metrics.append(val_row)
        print("VAL")
        print(json.dumps(val_row, indent=2))

        test_scores = pipe.predict_proba(X_test)[:, 1]
        test_score_df = test_df[["steamid", "appid", TARGET]].copy()
        test_score_df["score"] = test_scores
        test_metrics, per_user_metrics = evaluate_ranking(test_score_df.rename(columns={TARGET: "owned"}))
        test_auc = float(roc_auc_score(y_test, test_scores))

        test_row = {
            "seed": seed,
            "test_roc_auc": test_auc,
            **test_metrics,
        }
        all_seeds_test_metrics.append(test_row)
        print("TEST")
        print(json.dumps(test_row, indent=2))

        test_score_df.to_csv(out_dir / f"test_scores_seed{seed}.csv.gz", index=False, compression="gzip")
        per_user_metrics.to_csv(out_dir / f"test_per_user_metrics_seed{seed}.csv", index=False)
        joblib.dump(pipe, out_dir / f"best_model_seed{seed}.joblib")

    val_metrics_agg = aggregate_metrics([
        {k: v for k, v in row.items() if k not in ("seed", "fit_seconds")}
        for row in all_seeds_val_metrics
    ])
    test_metrics_agg = aggregate_metrics([
        {k: v for k, v in row.items() if k != "seed"}
        for row in all_seeds_test_metrics
    ])

    print("\n--- Val metrics (mean ± std) ---")
    for k, v in val_metrics_agg.items():
        if isinstance(v, dict):
            print(f"  {k}: {v['mean']:.4f} ± {v['std']:.4f}")

    print("\n--- Test metrics (mean ± std) ---")
    for k, v in test_metrics_agg.items():
        if isinstance(v, dict):
            print(f"  {k}: {v['mean']:.4f} ± {v['std']:.4f}")

    # Learning curve uses the base data; fake embeddings are generated with seed 42 for LC input,
    # then model training still runs across all SEEDS.
    if cfg.get("uses_fake_emb", False):
        lc_train_df = add_fake_embedding_feature(base_train_df, "train", 42)
        lc_val_df = add_fake_embedding_feature(base_val_df, "val", 42)
    else:
        lc_train_df = base_train_df
        lc_val_df = base_val_df
    make_learning_curve(cfg, lc_train_df, lc_val_df, out_dir)

    final_results = {
        "model_type": "xgb",
        "dataset_type": cfg["dataset_type"],
        "experiment_name": name,
        "dataset_dir": str(data_dir),
        "seeds": SEEDS,
        "train_rows": int(len(base_train_df)),
        "val_rows": int(len(base_val_df)),
        "test_rows": int(len(base_test_df)),
        "xgb_njobs": XGB_NJOBS,
        "ohe_max_categories": OHE_MAX_CATS,
        "ohe_min_frequency": OHE_MIN_FREQ,
        "learning_curve_max_rows": LC_MAX_ROWS,
        "numeric_features": cfg["numeric_features"],
        "categorical_features": cfg["categorical_features"],
        "best_params": cfg["best_params"],
        "val_metrics": val_metrics_agg,
        "test_metrics": test_metrics_agg,
        "per_seed_val": all_seeds_val_metrics,
        "per_seed_test": all_seeds_test_metrics,
    }

    if cfg.get("uses_fake_emb", False):
        final_results.update({
            "fake_embedding_source_col": FAKE_EMB_SOURCE_COL,
            "fake_embedding_col": FAKE_EMB_COL,
            "fake_embedding_target_corr": FAKE_EMB_TARGET_CORR,
        })

    with open(out_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2)

    alias_name = f"results_xgb_{name}_multiseed.json"
    with open(out_dir / alias_name, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2)

    print("\nFINAL RESULTS")
    print(json.dumps(final_results, indent=2))
    print(f"Saved to: {out_dir}")


def parse_args():
    parser = argparse.ArgumentParser(description="Train XGB ablation models on 3 seeds.")
    parser.add_argument(
        "--experiment",
        default="all",
        choices=["all"] + sorted(EXPERIMENTS.keys()),
        help="Which experiment to run. Use 'all' to run every ablation sequentially.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available experiments and exit.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list:
        print("Available experiments:")
        for name in sorted(EXPERIMENTS):
            print(f"  - {name}")
        return

    if args.experiment == "all":
        for name, cfg in EXPERIMENTS.items():
            train_experiment(name, cfg)
    else:
        train_experiment(args.experiment, EXPERIMENTS[args.experiment])


if __name__ == "__main__":
    main()
