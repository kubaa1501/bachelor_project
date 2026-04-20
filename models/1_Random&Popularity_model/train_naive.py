#!/usr/bin/env python3
import os
import json
from pathlib import Path

import numpy as np
import pandas as pd

# global seed 
SEED = 42
np.random.seed(SEED)

# base dir
BASE_DIR = Path("/home/anci/new")

# which dataset used: 
DATASET_NAME = os.getenv("DATASET_NAME", "baseline")  # baseline | network
if DATASET_NAME not in {"baseline", "network"}:
    raise ValueError("DATASET_NAME must be 'baseline' or 'network'")

if DATASET_NAME == "baseline":
    DATA_DIR = BASE_DIR / "correct_splits" / "with_genre_groups"
    OUT_DIR = BASE_DIR / "models_new" / "naive_baseline"
else:
    DATA_DIR = BASE_DIR / "correct_splits" / "with_genre_groups_network"
    OUT_DIR = BASE_DIR / "models_new" / "naive_network"

# train, val and test splt files
TRAIN_CSV = DATA_DIR / "train.csv"
VAL_CSV   = DATA_DIR / "val.csv"
TEST_CSV  = DATA_DIR / "test.csv"

# target column, 1=positive interraction, 0= negative
TARGET = "owned"
ID_COLS = ["steamid", "appid"]

# used columns- steamid, appid, owned (target), user_count (for popularity)
USECOLS = ID_COLS + [TARGET, "user_count"]

# repeated runs for random baseline
N_RANDOM_RUNS = int(os.getenv("N_RANDOM_RUNS", "100"))


def read_split(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", usecols=USECOLS)
    return df

# compute Discounted Cumulative Gain at rank k.
# higher relevance near the top of the ranking gets more weight.

def dcg_at_k(relevances, k):
    vals = np.asarray(relevances[:k], dtype=float)
    if vals.size == 0:
        return 0.0
    discounts = np.log2(np.arange(2, vals.size + 2))
    return float(np.sum(vals / discounts))

# compute Normalized DCG at rank k.
# the predicted ranking is compared against the ideal ranking.
def ndcg_at_k(y_true_sorted, k):
    ideal = sorted(y_true_sorted, reverse=True)
    best = dcg_at_k(ideal, k)
    if best == 0.0:
        return 0.0
    return dcg_at_k(y_true_sorted, k) / best

# Evaluate ranking quality per user.
#
#   For each user:
#    - sort candidate games by predicted score (descending)
#    - compute ranking metrics on the ordered relevance labels
#
#    Metrics:
#    - HitRate@10 / HitRate@20
#    - Recall@10 / Recall@20
#    - NDCG@10 / NDCG@20
#    - MRR

def evaluate_ranking(df_scores: pd.DataFrame):
    rows = []

    for steamid, g in df_scores.groupby("steamid", sort=False):
        g = g.sort_values("score", ascending=False)
        y = g[TARGET].astype(int).tolist()
        positives = int(np.sum(y))
        if positives == 0:
            continue

        row = {"steamid": steamid}

        for k in [10, 20]:
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
        "HitRate@10": float(per_user["HitRate@10"].mean()),
        "Recall@10": float(per_user["Recall@10"].mean()),
        "NDCG@10": float(per_user["NDCG@10"].mean()),
        "HitRate@20": float(per_user["HitRate@20"].mean()),
        "Recall@20": float(per_user["Recall@20"].mean()),
        "NDCG@20": float(per_user["NDCG@20"].mean()),
        "MRR": float(per_user["MRR"].mean()),
    }
    return metrics, per_user

# score each candidate game by its global popularity.
#
# popularity is computed from train only and mapped by appid.
#  if a game is unseen, assign score 0.0.

def apply_popularity(df: pd.DataFrame, global_popularity: pd.Series) -> pd.DataFrame:
    out = df[[*ID_COLS, TARGET]].copy()
    out["score"] = out["appid"].map(global_popularity).fillna(0.0).astype(float)
    return out

# assign a random score to each candidate game.
# used as a naive random baseline.

def apply_random(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    out = df[[*ID_COLS, TARGET]].copy()
    rng = np.random.default_rng(seed)
    out["score"] = rng.random(len(out))
    return out



# run the random baseline multiple times and average metrics across runs.
#
# additionally keep:
#    - per-run metrics
#    - the best-scoring run (by MRR)
#    - its scored rows and per-user metrics

def evaluate_random_many(df: pd.DataFrame, n_runs: int):
    metrics_accum = []
    best_scores_df = None
    best_per_user = None
    best_mrr = -1.0

    for run in range(n_runs):
        df_random = apply_random(df, seed=SEED + run)
        metrics, per_user = evaluate_ranking(df_random)

        row = {"run": run, **metrics}
        metrics_accum.append(row)

        if metrics["MRR"] > best_mrr:
            best_mrr = metrics["MRR"]
            best_scores_df = df_random.copy()
            best_per_user = per_user.copy()

    avg_metrics = {
        "n_runs": int(n_runs),
        "HitRate@10": float(np.mean([m["HitRate@10"] for m in metrics_accum])),
        "Recall@10": float(np.mean([m["Recall@10"] for m in metrics_accum])),
        "NDCG@10": float(np.mean([m["NDCG@10"] for m in metrics_accum])),
        "HitRate@20": float(np.mean([m["HitRate@20"] for m in metrics_accum])),
        "Recall@20": float(np.mean([m["Recall@20"] for m in metrics_accum])),
        "NDCG@20": float(np.mean([m["NDCG@20"] for m in metrics_accum])),
        "MRR": float(np.mean([m["MRR"] for m in metrics_accum])),
        "n_users_evaluated": int(np.mean([m["n_users_evaluated"] for m in metrics_accum])),
    }

    runs_df = pd.DataFrame(metrics_accum)
    return avg_metrics, runs_df, best_scores_df, best_per_user

# save 
def save_outputs(
    out_dir: Path,
    prefix: str,
    scores_df: pd.DataFrame,
    per_user_df: pd.DataFrame,
    metrics: dict,
):
    scores_df.to_csv(out_dir / f"{prefix}_scores.csv.gz", index=False, compression="gzip")
    per_user_df.to_csv(out_dir / f"{prefix}_per_user_metrics.csv", index=False)

    with open(out_dir / f"{prefix}_results.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # train and evaluate two naive baselines: popularity and random.
    train_df = read_split(TRAIN_CSV)
    val_df   = read_split(VAL_CSV)
    test_df  = read_split(TEST_CSV)

     # Popularity baseline:
    # compute game popularity using TRAIN ONLY
    # Here popularity = sum of user_count over rows grouped by appid
    global_popularity = train_df.groupby("appid")["user_count"].sum()

    # -------------------------
    # Popularity baseline
    # -------------------------
    val_pop_scores = apply_popularity(val_df, global_popularity)
    val_pop_metrics, val_pop_per_user = evaluate_ranking(val_pop_scores)

    test_pop_scores = apply_popularity(test_df, global_popularity)
    test_pop_metrics, test_pop_per_user = evaluate_ranking(test_pop_scores)

    save_outputs(
        OUT_DIR,
        "val_popularity",
        val_pop_scores,
        val_pop_per_user,
        val_pop_metrics,
    )
    save_outputs(
        OUT_DIR,
        "test_popularity",
        test_pop_scores,
        test_pop_per_user,
        test_pop_metrics,
    )

    # -------------------------
    # Random baseline
    # -------------------------
    # repeat random scoring many (defined) times and average the metrics
    val_rand_metrics, val_rand_runs, val_rand_best_scores, val_rand_best_per_user = evaluate_random_many(
        val_df, N_RANDOM_RUNS
    )
    test_rand_metrics, test_rand_runs, test_rand_best_scores, test_rand_best_per_user = evaluate_random_many(
        test_df, N_RANDOM_RUNS
    )

    val_rand_runs.to_csv(OUT_DIR / "val_random_runs.csv", index=False)
    test_rand_runs.to_csv(OUT_DIR / "test_random_runs.csv", index=False)

    save_outputs(
        OUT_DIR,
        "val_random_best_run",
        val_rand_best_scores,
        val_rand_best_per_user,
        val_rand_metrics,
    )
    save_outputs(
        OUT_DIR,
        "test_random_best_run",
        test_rand_best_scores,
        test_rand_best_per_user,
        test_rand_metrics,
    )

    final_results = {
        "model_type": "naive",
        "dataset_type": DATASET_NAME,
        "seed": SEED,
        "train_rows": int(len(train_df)),
        "val_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "n_random_runs": int(N_RANDOM_RUNS),
        "popularity_val": val_pop_metrics,
        "popularity_test": test_pop_metrics,
        "random_val_avg": val_rand_metrics,
        "random_test_avg": test_rand_metrics,
    }

    with open(OUT_DIR / "results.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2)


if __name__ == "__main__":
    main()