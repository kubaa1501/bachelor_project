#!/usr/bin/env python3
import os
import json
import time
import random
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
from torch.optim import Adam
from sklearn.metrics import roc_auc_score


# multiseed setup 
SEEDS = [int(x) for x in os.getenv("SEEDS", "0,1,42").split(",")]

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# paths
BASE_DIR = Path("/home/anci/new")
DATA_DIR = BASE_DIR / "correct_splits" / "with_genre_groups"
OUT_DIR = BASE_DIR / "models_new" / "lightGCN_multiseed"

TRAIN_CSV = DATA_DIR / "train.csv"
VAL_CSV = DATA_DIR / "val.csv"
TEST_CSV = DATA_DIR / "test.csv"

# columns
USER_COL = "steamid"
GAME_COL = "appid"
TARGET = "owned"
USECOLS = [USER_COL, GAME_COL, TARGET]

# optional row limits for debugging / faster experiments
MAX_TRAIN_ROWS = int(os.getenv("MAX_TRAIN_ROWS", "0"))
MAX_VAL_ROWS = int(os.getenv("MAX_VAL_ROWS", "0"))
MAX_TEST_ROWS = int(os.getenv("MAX_TEST_ROWS", "0"))

# best config from previous small-grid search
BEST_CONFIG = {
    "hidden_channels": 256,
    "lr": 0.001,
    "num_layers": 1,
}

# training setup copied from the best previous LightGCN search
NUM_EPOCHS = int(os.getenv("NUM_EPOCHS", "30"))
MIN_EPOCHS = int(os.getenv("MIN_EPOCHS", "5"))
EARLY_STOPPING_PATIENCE = int(os.getenv("EARLY_STOPPING_PATIENCE", "5"))

WEIGHT_DECAY = float(os.getenv("WEIGHT_DECAY", "1e-6"))
BPR_REG = float(os.getenv("BPR_REG", "1e-6"))
POS_BATCH_SIZE = int(os.getenv("POS_BATCH_SIZE", "8192"))
NEG_PER_POS = int(os.getenv("NEG_PER_POS", "10"))

EVAL_BATCH_SIZE = int(os.getenv("EVAL_BATCH_SIZE", "262144"))
TRAIN_ROC_SAMPLE_POS = int(os.getenv("TRAIN_ROC_SAMPLE_POS", "200000"))

# learning curve settings
RUN_LEARNING_CURVE = int(os.getenv("RUN_LEARNING_CURVE", "1")) == 1
LC_MAX_POS = int(os.getenv("LC_MAX_POS", "1000000"))
LC_FRACTIONS = [float(x) for x in os.getenv("LC_FRACTIONS", "0.05,0.10,0.20,0.40,0.70,1.00").split(",")]


# utils
def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def stringify(obj: Any) -> Any:
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, Path):
        return str(obj)
    return obj


def save_json(data: dict[str, Any], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=stringify)

#  data loading
def read_split(path: Path, max_rows: int = 0) -> pd.DataFrame:
    print(f"Loading {path} ...", flush=True)

    df = pd.read_csv(path, sep=";", usecols=USECOLS, low_memory=False)

    if max_rows > 0:
        df = df.iloc[:max_rows].copy()
        print(f"Trimmed to {len(df):,} rows", flush=True)

    df[TARGET] = df[TARGET].astype(int)

    print(f"Loaded {len(df):,} rows from {path}", flush=True)
    return df


# metrics
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

    for steamid, g in df_scores.groupby(USER_COL, sort=False):
        g = g.sort_values("score", ascending=False)
        y = g[TARGET].astype(int).tolist()
        positives = int(np.sum(y))

        if positives == 0:
            continue

        row = {USER_COL: steamid}

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


# graph construction
def build_mappings(train_df: pd.DataFrame):
    users = train_df[USER_COL].dropna().unique()
    games = train_df[GAME_COL].dropna().unique()

    user2idx = {u: i for i, u in enumerate(users)}
    game2idx = {g: i for i, g in enumerate(games)}

    idx2user = {i: u for u, i in user2idx.items()}
    idx2game = {i: g for g, i in game2idx.items()}

    return user2idx, game2idx, idx2user, idx2game


def build_edge_index(train_pos_df: pd.DataFrame, user2idx: dict, game2idx: dict, num_users: int):
    src = np.array([user2idx[u] for u in train_pos_df[USER_COL]], dtype=np.int64)
    dst = np.array([game2idx[g] for g in train_pos_df[GAME_COL]], dtype=np.int64) + num_users

    edge_index = torch.tensor(
        np.vstack([
            np.concatenate([src, dst]),
            np.concatenate([dst, src]),
        ]),
        dtype=torch.long,
        device=DEVICE,
    )

    return edge_index


def build_norm_adj(edge_index: torch.Tensor, num_nodes: int) -> torch.Tensor:
    row, col = edge_index[0], edge_index[1]

    deg = torch.bincount(row, minlength=num_nodes).float()
    deg_inv_sqrt = deg.pow(-0.5)
    deg_inv_sqrt[torch.isinf(deg_inv_sqrt)] = 0.0

    values = deg_inv_sqrt[row] * deg_inv_sqrt[col]

    adj = torch.sparse_coo_tensor(
        edge_index,
        values,
        (num_nodes, num_nodes),
        device=DEVICE,
    )

    return adj.coalesce()


# model
class LightGCN(nn.Module):
    def __init__(
        self,
        num_users: int,
        num_games: int,
        hidden_channels: int,
        num_layers: int,
        norm_adj: torch.Tensor,
    ):
        super().__init__()

        self.num_users = num_users
        self.num_games = num_games
        self.num_layers = num_layers
        self.norm_adj = norm_adj

        self.user_embedding = nn.Embedding(num_users, hidden_channels)
        self.game_embedding = nn.Embedding(num_games, hidden_channels)

        nn.init.xavier_uniform_(self.user_embedding.weight)
        nn.init.xavier_uniform_(self.game_embedding.weight)

    def forward(self):
        x = torch.cat(
            [self.user_embedding.weight, self.game_embedding.weight],
            dim=0,
        )

        embeddings = [x]

        for _ in range(self.num_layers):
            x = torch.sparse.mm(self.norm_adj, x)
            embeddings.append(x)

        x = torch.stack(embeddings, dim=0).mean(dim=0)

        user_emb, game_emb = torch.split(
            x,
            [self.num_users, self.num_games],
            dim=0,
        )

        return user_emb, game_emb


def score_pairs(
    user_emb: torch.Tensor,
    game_emb: torch.Tensor,
    user_idx: torch.Tensor,
    game_idx: torch.Tensor,
) -> torch.Tensor:
    return (user_emb[user_idx] * game_emb[game_idx]).sum(dim=-1)


# bpr arrays and sampling
def build_bpr_arrays(train_df: pd.DataFrame, user2idx: dict, game2idx: dict):
    train_pos_df = train_df[train_df[TARGET] == 1].copy()
    train_neg_df = train_df[train_df[TARGET] == 0].copy()

    pos_users = np.array(
        [user2idx[u] for u in train_pos_df[USER_COL]],
        dtype=np.int64,
    )

    pos_games = np.array(
        [game2idx[g] for g in train_pos_df[GAME_COL]],
        dtype=np.int64,
    )

    neg_lists = [[] for _ in range(len(user2idx))]

    for u, games in train_neg_df.groupby(USER_COL)[GAME_COL].apply(list).items():
        if u not in user2idx:
            continue

        ui = user2idx[u]
        neg_lists[ui] = [game2idx[g] for g in games if g in game2idx]

    usable_mask = np.array([len(neg_lists[u]) > 0 for u in pos_users], dtype=bool)

    pos_users = pos_users[usable_mask]
    pos_games = pos_games[usable_mask]

    usable_users = int(len(set(pos_users.tolist())))

    return train_pos_df, pos_users, pos_games, neg_lists, usable_users


def sample_bpr_batch(
    pos_users: np.ndarray,
    pos_games: np.ndarray,
    neg_lists: list[list[int]],
    batch_indices: np.ndarray,
):
    batch_users = pos_users[batch_indices]
    batch_pos_games = pos_games[batch_indices]

    u_out = np.repeat(batch_users, NEG_PER_POS)
    pos_out = np.repeat(batch_pos_games, NEG_PER_POS)
    neg_out = np.empty(len(u_out), dtype=np.int64)

    ptr = 0

    for u in batch_users:
        negs = neg_lists[int(u)]
        sampled = np.random.choice(negs, size=NEG_PER_POS, replace=True)
        neg_out[ptr:ptr + NEG_PER_POS] = sampled
        ptr += NEG_PER_POS

    return (
        torch.tensor(u_out, dtype=torch.long, device=DEVICE),
        torch.tensor(pos_out, dtype=torch.long, device=DEVICE),
        torch.tensor(neg_out, dtype=torch.long, device=DEVICE),
    )


def bpr_loss(scores_pos: torch.Tensor, scores_neg: torch.Tensor, model: LightGCN) -> torch.Tensor:
    base_loss = -torch.log(torch.sigmoid(scores_pos - scores_neg) + 1e-8).mean()

    reg = (
        model.user_embedding.weight.norm(2).pow(2)
        + model.game_embedding.weight.norm(2).pow(2)
    ) / (model.num_users + model.num_games)

    return base_loss + BPR_REG * reg


# eval
def score_dataframe(
    df: pd.DataFrame,
    model: LightGCN,
    user2idx: dict,
    game2idx: dict,
) -> pd.DataFrame:
    model.eval()

    user_idx_np = np.array(
        [user2idx.get(u, -1) for u in df[USER_COL]],
        dtype=np.int64,
    )

    game_idx_np = np.array(
        [game2idx.get(g, -1) for g in df[GAME_COL]],
        dtype=np.int64,
    )

    mask = (user_idx_np >= 0) & (game_idx_np >= 0)

    filtered = df.loc[mask, [USER_COL, GAME_COL, TARGET]].copy()
    user_idx_np = user_idx_np[mask]
    game_idx_np = game_idx_np[mask]

    scores_all = []

    with torch.no_grad():
        user_emb, game_emb = model()

        for start in range(0, len(filtered), EVAL_BATCH_SIZE):
            end = min(start + EVAL_BATCH_SIZE, len(filtered))

            u = torch.tensor(
                user_idx_np[start:end],
                dtype=torch.long,
                device=DEVICE,
            )

            g = torch.tensor(
                game_idx_np[start:end],
                dtype=torch.long,
                device=DEVICE,
            )

            scores = score_pairs(user_emb, game_emb, u, g).detach().cpu().numpy()
            scores_all.append(scores)

    filtered["score"] = np.concatenate(scores_all) if scores_all else np.array([])

    return filtered


def evaluate_split(df: pd.DataFrame, model: LightGCN, user2idx: dict, game2idx: dict):
    score_df = score_dataframe(df, model, user2idx, game2idx)

    roc_auc = float(
        roc_auc_score(
            score_df[TARGET].astype(int),
            score_df["score"],
        )
    )

    metrics, per_user = evaluate_ranking(score_df)

    return roc_auc, metrics, per_user, score_df


def train_roc_sample(
    model: LightGCN,
    pos_users: np.ndarray,
    pos_games: np.ndarray,
    neg_lists: list[list[int]],
) -> float:
    n = min(TRAIN_ROC_SAMPLE_POS, len(pos_users))
    idx = np.random.choice(len(pos_users), size=n, replace=False)

    u, pos_g, neg_g = sample_bpr_batch(pos_users, pos_games, neg_lists, idx)

    model.eval()

    with torch.no_grad():
        user_emb, game_emb = model()

        pos_scores = score_pairs(user_emb, game_emb, u, pos_g)
        neg_scores = score_pairs(user_emb, game_emb, u, neg_g)

        scores = torch.cat([pos_scores, neg_scores]).detach().cpu().numpy()
        labels = np.concatenate([
            np.ones(len(pos_scores)),
            np.zeros(len(neg_scores)),
        ])

    return float(roc_auc_score(labels, scores))


# training
def train_one_seed(
    seed: int,
    norm_adj: torch.Tensor,
    pos_users: np.ndarray,
    pos_games: np.ndarray,
    neg_lists: list[list[int]],
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    user2idx: dict,
    game2idx: dict,
    num_users: int,
    num_games: int,
    train_rows: int,
    val_rows: int,
    test_rows: int,
    train_pos_edges: int,
    usable_users: int,
):
    set_seed(seed)

    seed_out = OUT_DIR / f"seed_{seed}"
    seed_out.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 80, flush=True)
    print(f"Seed {seed}", flush=True)
    print(f"Output directory: {seed_out}", flush=True)
    print(f"Config: {BEST_CONFIG}", flush=True)

    model = LightGCN(
        num_users=num_users,
        num_games=num_games,
        hidden_channels=BEST_CONFIG["hidden_channels"],
        num_layers=BEST_CONFIG["num_layers"],
        norm_adj=norm_adj,
    ).to(DEVICE)

    optimizer = Adam(
        model.parameters(),
        lr=BEST_CONFIG["lr"],
        weight_decay=WEIGHT_DECAY,
    )

    history_rows = []

    best_state = None
    best_epoch = -1
    best_val_ndcg10 = -np.inf
    best_val_roc = np.nan
    best_val_metrics = None
    bad_epochs = 0

    indices = np.arange(len(pos_users))
    total_start = time.time()

    for epoch in range(1, NUM_EPOCHS + 1):
        model.train()
        np.random.shuffle(indices)

        epoch_loss = 0.0
        n_batches = 0
        t0 = time.time()

        for start in range(0, len(indices), POS_BATCH_SIZE):
            batch_idx = indices[start:start + POS_BATCH_SIZE]

            if len(batch_idx) == 0:
                continue

            u, pos_g, neg_g = sample_bpr_batch(
                pos_users,
                pos_games,
                neg_lists,
                batch_idx,
            )

            optimizer.zero_grad(set_to_none=True)

            user_emb, game_emb = model()

            pos_scores = score_pairs(user_emb, game_emb, u, pos_g)
            neg_scores = score_pairs(user_emb, game_emb, u, neg_g)

            loss = bpr_loss(pos_scores, neg_scores, model)
            loss.backward()
            optimizer.step()

            epoch_loss += float(loss.item())
            n_batches += 1

        epoch_loss = epoch_loss / max(1, n_batches)
        fit_seconds = time.time() - t0

        train_auc = train_roc_sample(model, pos_users, pos_games, neg_lists)
        val_roc, val_metrics, _, _ = evaluate_split(val_df, model, user2idx, game2idx)
        val_ndcg10 = val_metrics["NDCG@10"]

        row = {
            "seed": seed,
            "epoch": epoch,
            **BEST_CONFIG,
            "fit_seconds": fit_seconds,
            "loss": epoch_loss,
            "train_roc_auc": train_auc,
            "val_roc_auc": val_roc,
            **val_metrics,
        }

        history_rows.append(row)

        print(
            f"Epoch {epoch:02d} | loss={epoch_loss:.6f} | "
            f"train_auc={train_auc:.6f} | val_auc={val_roc:.6f} | "
            f"val_NDCG@10={val_ndcg10:.6f}",
            flush=True,
        )

        pd.DataFrame(history_rows).to_csv(seed_out / "training_history.csv", index=False)

        if val_ndcg10 > best_val_ndcg10:
            best_val_ndcg10 = val_ndcg10
            best_val_roc = val_roc
            best_val_metrics = val_metrics
            best_epoch = epoch
            best_state = {
                k: v.detach().cpu().clone()
                for k, v in model.state_dict().items()
            }
            bad_epochs = 0
        else:
            bad_epochs += 1

        if epoch >= MIN_EPOCHS and bad_epochs >= EARLY_STOPPING_PATIENCE:
            print(
                f"Early stopping at epoch {epoch} "
                f"(best epoch {best_epoch})",
                flush=True,
            )
            break

    fit_seconds_total = time.time() - total_start

    best_model = LightGCN(
        num_users=num_users,
        num_games=num_games,
        hidden_channels=BEST_CONFIG["hidden_channels"],
        num_layers=BEST_CONFIG["num_layers"],
        norm_adj=norm_adj,
    ).to(DEVICE)

    best_model.load_state_dict({k: v.to(DEVICE) for k, v in best_state.items()})
    best_model.eval()

    torch.save(
        {
            "model_state_dict": {
                k: v.cpu()
                for k, v in best_model.state_dict().items()
            },
            "config": BEST_CONFIG,
            "num_users": num_users,
            "num_games": num_games,
            "user2idx": user2idx,
            "game2idx": game2idx,
            "seed": seed,
        },
        seed_out / "best_model_state.pt",
    )

    print("\nFinal validation evaluation...", flush=True)
    val_roc, val_metrics, val_per_user, val_scores = evaluate_split(
        val_df,
        best_model,
        user2idx,
        game2idx,
    )

    print("\nFinal test evaluation...", flush=True)
    test_roc, test_metrics, test_per_user, test_scores = evaluate_split(
        test_df,
        best_model,
        user2idx,
        game2idx,
    )

    val_scores.to_csv(seed_out / "val_scores.csv.gz", index=False, compression="gzip")
    test_scores.to_csv(seed_out / "test_scores.csv.gz", index=False, compression="gzip")

    val_per_user.to_csv(seed_out / "val_per_user_metrics.csv", index=False)
    test_per_user.to_csv(seed_out / "test_per_user_metrics.csv", index=False)

    history_df = pd.DataFrame(history_rows)
    plot_training_curves(history_df, seed_out, seed)

    if RUN_LEARNING_CURVE:
        make_learning_curve(
            seed=seed,
            norm_adj=norm_adj,
            pos_users=pos_users,
            pos_games=pos_games,
            neg_lists=neg_lists,
            val_df=val_df,
            user2idx=user2idx,
            game2idx=game2idx,
            num_users=num_users,
            num_games=num_games,
            out_dir=seed_out,
        )

    seed_results = {
        "model_type": "lightgcn_multiseed",
        "dataset_type": "with_genre_groups",
        "seed": seed,
        "device": DEVICE,
        "train_rows": int(train_rows),
        "val_rows": int(val_rows),
        "test_rows": int(test_rows),
        "num_users": int(num_users),
        "num_games": int(num_games),
        "num_train_rows": int(train_rows),
        "num_train_positive_edges": int(train_pos_edges),
        "usable_positive_pairs": int(len(pos_users)),
        "usable_users": int(usable_users),
        "config": BEST_CONFIG,
        "num_epochs": NUM_EPOCHS,
        "min_epochs": MIN_EPOCHS,
        "early_stopping_patience": EARLY_STOPPING_PATIENCE,
        "weight_decay": WEIGHT_DECAY,
        "regularization": BPR_REG,
        "pos_batch_size": POS_BATCH_SIZE,
        "neg_per_pos": NEG_PER_POS,
        "best_epoch": int(best_epoch),
        "best_selection_metric": "val_NDCG@10",
        "best_val_ndcg10": float(best_val_ndcg10),
        "best_val_roc_auc": float(best_val_roc),
        "fit_seconds_total": float(fit_seconds_total),
        "val_roc_auc": float(val_roc),
        **{f"val_{k}": v for k, v in val_metrics.items()},
        "test_roc_auc": float(test_roc),
        **{f"test_{k}": v for k, v in test_metrics.items()},
    }

    save_json(seed_results, seed_out / "results.json")

    print("\nSEED FINAL RESULTS", flush=True)
    print(json.dumps(seed_results, indent=2, default=stringify), flush=True)

    return seed_results


# plots
def plot_training_curves(history_df: pd.DataFrame, out_dir: Path, seed: int):
    plt.figure(figsize=(8, 5))
    plt.plot(history_df["epoch"], history_df["train_roc_auc"], marker="o", label="Train ROC-AUC")
    plt.plot(history_df["epoch"], history_df["val_roc_auc"], marker="o", label="Validation ROC-AUC")
    plt.xlabel("Epoch")
    plt.ylabel("ROC-AUC")
    plt.title(f"Training vs Validation ROC-AUC — LightGCN seed {seed}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "train_val_roc_curve.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(history_df["epoch"], history_df["NDCG@10"], marker="o", label="Validation NDCG@10")
    plt.plot(history_df["epoch"], history_df["Recall@10"], marker="o", label="Validation Recall@10")
    plt.xlabel("Epoch")
    plt.ylabel("Score")
    plt.title(f"Validation ranking metrics — LightGCN seed {seed}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "ranking_curve.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(history_df["epoch"], history_df["loss"], marker="o")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title(f"Training loss — LightGCN seed {seed}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / "training_loss.png", dpi=200)
    plt.close()


def make_learning_curve(
    seed: int,
    norm_adj: torch.Tensor,
    pos_users: np.ndarray,
    pos_games: np.ndarray,
    neg_lists: list[list[int]],
    val_df: pd.DataFrame,
    user2idx: dict,
    game2idx: dict,
    num_users: int,
    num_games: int,
    out_dir: Path,
):
    if LC_MAX_POS > 0 and len(pos_users) > LC_MAX_POS:
        base_idx = np.random.choice(len(pos_users), size=LC_MAX_POS, replace=False)
        lc_pos_users = pos_users[base_idx]
        lc_pos_games = pos_games[base_idx]
    else:
        lc_pos_users = pos_users
        lc_pos_games = pos_games

    print(f"[LC] Using {len(lc_pos_users):,} positive pairs for learning curve", flush=True)

    rows = []

    for frac in LC_FRACTIONS:
        n_pos = max(1, int(len(lc_pos_users) * frac))
        idx = np.random.choice(len(lc_pos_users), size=n_pos, replace=False)

        part_users = lc_pos_users[idx]
        part_games = lc_pos_games[idx]

        model = LightGCN(
            num_users=num_users,
            num_games=num_games,
            hidden_channels=BEST_CONFIG["hidden_channels"],
            num_layers=BEST_CONFIG["num_layers"],
            norm_adj=norm_adj,
        ).to(DEVICE)

        optimizer = Adam(
            model.parameters(),
            lr=BEST_CONFIG["lr"],
            weight_decay=WEIGHT_DECAY,
        )

        t0 = time.time()
        indices = np.arange(len(part_users))

        for _ in range(max(1, MIN_EPOCHS)):
            model.train()
            np.random.shuffle(indices)

            for start in range(0, len(indices), POS_BATCH_SIZE):
                batch_idx = indices[start:start + POS_BATCH_SIZE]

                u, pos_g, neg_g = sample_bpr_batch(
                    part_users,
                    part_games,
                    neg_lists,
                    batch_idx,
                )

                optimizer.zero_grad(set_to_none=True)

                user_emb, game_emb = model()

                loss = bpr_loss(
                    score_pairs(user_emb, game_emb, u, pos_g),
                    score_pairs(user_emb, game_emb, u, neg_g),
                    model,
                )

                loss.backward()
                optimizer.step()

        fit_seconds = time.time() - t0
        train_auc = train_roc_sample(model, part_users, part_games, neg_lists)
        val_auc, val_metrics, _, _ = evaluate_split(val_df, model, user2idx, game2idx)

        row = {
            "fraction": frac,
            "n_positive_pairs": int(len(part_users)),
            "fit_seconds": fit_seconds,
            "train_roc_auc": train_auc,
            "val_roc_auc": val_auc,
            **val_metrics,
        }

        rows.append(row)

        print(
            f"[LC] fraction={frac:.2f} "
            f"pos_pairs={len(part_users):,} "
            f"val_NDCG@10={val_metrics['NDCG@10']:.6f}",
            flush=True,
        )

    lc_df = pd.DataFrame(rows)
    lc_df.to_csv(out_dir / "learning_curve.csv", index=False)

    plt.figure(figsize=(8, 5))
    plt.plot(lc_df["n_positive_pairs"], lc_df["train_roc_auc"], marker="o", label="Train ROC-AUC")
    plt.plot(lc_df["n_positive_pairs"], lc_df["val_roc_auc"], marker="o", label="Validation ROC-AUC")
    plt.xlabel("Training positive pairs")
    plt.ylabel("ROC-AUC")
    plt.title(f"Learning curve ROC-AUC — LightGCN seed {seed}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_roc_auc.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(lc_df["n_positive_pairs"], lc_df["NDCG@10"], marker="o", label="Validation NDCG@10")
    plt.plot(lc_df["n_positive_pairs"], lc_df["Recall@10"], marker="o", label="Validation Recall@10")
    plt.xlabel("Training positive pairs")
    plt.ylabel("Score")
    plt.title(f"Learning curve ranking — LightGCN seed {seed}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "learning_curve_ranking.png", dpi=200)
    plt.close()


# multiseeds results
def aggregate_results(seed_results: list[dict[str, Any]]):
    save_json({"results": seed_results}, OUT_DIR / "results_all_seeds.json")

    rows = []

    for res in seed_results:
        rows.append({
            "seed": res["seed"],
            "best_epoch": res["best_epoch"],
            "val_roc_auc": res["val_roc_auc"],
            "val_NDCG@10": res["val_NDCG@10"],
            "val_HitRate@10": res["val_HitRate@10"],
            "val_MRR": res["val_MRR"],
            "test_roc_auc": res["test_roc_auc"],
            "test_NDCG@10": res["test_NDCG@10"],
            "test_HitRate@10": res["test_HitRate@10"],
            "test_MRR": res["test_MRR"],
            "fit_seconds_total": res["fit_seconds_total"],
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "summary_per_seed.csv", index=False)

    numeric_cols = [
        "best_epoch",
        "val_roc_auc",
        "val_NDCG@10",
        "val_HitRate@10",
        "val_MRR",
        "test_roc_auc",
        "test_NDCG@10",
        "test_HitRate@10",
        "test_MRR",
        "fit_seconds_total",
    ]

    summary = {}

    for col in numeric_cols:
        summary[col] = {
            "mean": float(df[col].mean()),
            "std": float(df[col].std(ddof=1)) if len(df) > 1 else 0.0,
            "min": float(df[col].min()),
            "max": float(df[col].max()),
        }

    final_summary = {
        "model_type": "lightgcn_multiseed",
        "dataset_type": "with_genre_groups",
        "seeds": SEEDS,
        "num_seeds": len(SEEDS),
        "config": BEST_CONFIG,
        "num_epochs": NUM_EPOCHS,
        "min_epochs": MIN_EPOCHS,
        "early_stopping_patience": EARLY_STOPPING_PATIENCE,
        "weight_decay": WEIGHT_DECAY,
        "regularization": BPR_REG,
        "pos_batch_size": POS_BATCH_SIZE,
        "neg_per_pos": NEG_PER_POS,
        "summary": summary,
    }

    save_json(final_summary, OUT_DIR / "summary_mean_std.json")

    print("\n" + "=" * 80, flush=True)
    print("MULTISEED SUMMARY", flush=True)
    print(json.dumps(final_summary, indent=2, default=stringify), flush=True)


# main
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Device: {DEVICE}", flush=True)
    print(f"Output directory: {OUT_DIR}", flush=True)
    print(f"Seeds: {SEEDS}", flush=True)
    print(f"Config: {BEST_CONFIG}", flush=True)

    train_df = read_split(TRAIN_CSV, MAX_TRAIN_ROWS)
    val_df = read_split(VAL_CSV, MAX_VAL_ROWS)
    test_df = read_split(TEST_CSV, MAX_TEST_ROWS)

    user2idx, game2idx, idx2user, idx2game = build_mappings(train_df)

    num_users = len(user2idx)
    num_games = len(game2idx)

    train_pos_df, pos_users, pos_games, neg_lists, usable_users = build_bpr_arrays(
        train_df,
        user2idx,
        game2idx,
    )

    edge_index = build_edge_index(train_pos_df, user2idx, game2idx, num_users)
    norm_adj = build_norm_adj(edge_index, num_users + num_games)

    print(f"num_users={num_users:,}", flush=True)
    print(f"num_games={num_games:,}", flush=True)
    print(f"num_train_positive_edges={len(train_pos_df):,}", flush=True)
    print(f"usable_positive_pairs={len(pos_users):,}", flush=True)
    print(f"usable_users={usable_users:,}", flush=True)

    seed_results = []

    for seed in SEEDS:
        result = train_one_seed(
            seed=seed,
            norm_adj=norm_adj,
            pos_users=pos_users,
            pos_games=pos_games,
            neg_lists=neg_lists,
            val_df=val_df,
            test_df=test_df,
            user2idx=user2idx,
            game2idx=game2idx,
            num_users=num_users,
            num_games=num_games,
            train_rows=len(train_df),
            val_rows=len(val_df),
            test_rows=len(test_df),
            train_pos_edges=len(train_pos_df),
            usable_users=usable_users,
        )

        seed_results.append(result)

    aggregate_results(seed_results)

    print(f"Saved to: {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
