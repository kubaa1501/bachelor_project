import os
import sys
import json
import random
import math
import time
import itertools
from collections import defaultdict

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt

# ---------------------------
# Mode
# ---------------------------
MODE = sys.argv[1] if len(sys.argv) > 1 else "with_net"
assert MODE in ("with_net", "no_net"), f"MODE must be with_net or no_net, got {MODE}"
print(f"Running in mode: {MODE}")

if MODE == "with_net":
    CACHE_DIR    = "/home/jaga/data/cache"
    MODEL_PATH   = "/home/jaga/results/models/nn_with_net_best_seed{seed}.pt"
    METRICS_PATH = "/home/jaga/results/metrics/nn_with_net_metrics.json"
    PLOT_PATH    = "/home/jaga/results/plots/nn_with_net_learning_curve.png"
else:
    CACHE_DIR    = "/home/jaga/data/cache_no_net"
    MODEL_PATH   = "/home/jaga/results/models/nn_no_net_best_seed{seed}.pt"
    METRICS_PATH = "/home/jaga/results/metrics/nn_no_net_metrics.json"
    PLOT_PATH    = "/home/jaga/results/plots/nn_no_net_learning_curve.png"

# ---------------------------
# Multi-seed setup
# ---------------------------
SEEDS = [42, 0, 1]

# ---------------------------
# Best hyperparameters (fixed — search already done)
# ---------------------------
# nn_no_net:  hidden=256, layers=4, lr=5e-4
# nn_with_net: hidden=256, layers=4, lr=5e-4
HIDDEN_CHANNELS = 256
NUM_LAYERS      = 4
LR              = 5e-4

# # Commented out — other configs tried during search
# hidden_channels_list = [64, 128, 256]
# num_layers_list      = [2, 3, 4]
# learning_rates       = [1e-3, 5e-4]

DEVICE   = "cuda" if torch.cuda.is_available() else "cpu"
USER_COL = "steamid"
GAME_COL = "appid"
TARGET   = "owned"
N_NEG    = 10
print(f"Using device: {DEVICE}")

os.makedirs("/home/jaga/results/metrics", exist_ok=True)
os.makedirs("/home/jaga/results/models",  exist_ok=True)
os.makedirs("/home/jaga/results/plots",   exist_ok=True)

CAT_EMB_DIMS = {
    "genres":    16,
    "developer": 64,
    "publisher": 64,
    "platforms": 4,
}

# ---------------------------
# Load cache (once, outside seed loop)
# ---------------------------
print(f"\nLoading cache from {CACHE_DIR}...")
t0 = time.time()

data     = torch.load(f"{CACHE_DIR}/graph.pt",     weights_only=False)
user2idx = torch.load(f"{CACHE_DIR}/user2idx.pt",  weights_only=False)
game2idx = torch.load(f"{CACHE_DIR}/game2idx.pt",  weights_only=False)
grouped_ei = torch.load(f"{CACHE_DIR}/grouped_train_edge_label_index.pt", weights_only=False)
grouped_el = torch.load(f"{CACHE_DIR}/grouped_train_edge_label.pt",       weights_only=False)
val_filtered_df = pd.read_parquet(f"{CACHE_DIR}/val_filtered_df.parquet")
test_df         = pd.read_parquet(f"{CACHE_DIR}/test_df.parquet")

with open(f"{CACHE_DIR}/cat_vocabs.json") as f:
    vocabs = json.load(f)
with open(f"{CACHE_DIR}/meta.json") as f:
    meta = json.load(f)

print(f"Cache loaded in {time.time()-t0:.1f}s")

cat_embed_cols   = meta["cat_embed_cols"]
max_lens         = meta["max_lens"]
cat_vocab_sizes  = meta["cat_vocab_sizes"]
user_in_dim      = meta["user_in_dim"]
game_numeric_dim = meta["game_numeric_dim"]

user_features = data["user"].x
game_features = data["game"].x

game_cat_idx = {}
for col in cat_embed_cols:
    key = f"{col}_idx"
    if hasattr(data["game"], key):
        game_cat_idx[col] = getattr(data["game"], key)

print(f"  user_in_dim={user_in_dim}, game_numeric_dim={game_numeric_dim}")
print(f"  n_users={user_features.shape[0]}, n_games={game_features.shape[0]}")

if torch.cuda.is_available():
    gpu_mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"GPU: {torch.cuda.get_device_name(0)}, Memory: {gpu_mem_gb:.1f}GB")
    batch_size = 2048
else:
    batch_size = 512
print(f"Using batch_size={batch_size}")

user_features = user_features.to(DEVICE)
game_features = game_features.to(DEVICE)
game_cat_idx  = {col: idx.to(DEVICE) for col, idx in game_cat_idx.items()}

num_epochs      = 20
N_GROUPS_SAMPLE = 200_000

# ---------------------------
# Dataset
# ---------------------------
class InteractionDataset(Dataset):
    def __init__(self, edge_index, edge_label, n_neg=N_NEG):
        self.edge_index = edge_index
        self.edge_label = edge_label
        self.n_neg      = n_neg
        self.group_size = n_neg + 1
        self.n_groups   = edge_index.shape[1] // self.group_size

    def __len__(self):
        return self.n_groups

    def __getitem__(self, idx):
        start    = idx * self.group_size
        end      = start + self.group_size
        user_idx = self.edge_index[0, start:end]
        game_idx = self.edge_index[1, start:end]
        labels   = self.edge_label[start:end]
        return user_idx, game_idx, labels


def collate_fn(batch):
    user_idx = torch.stack([b[0] for b in batch])
    game_idx = torch.stack([b[1] for b in batch])
    labels   = torch.stack([b[2] for b in batch])
    return user_idx, game_idx, labels


# ---------------------------
# Model
# ---------------------------
class GameFeatureEncoder(nn.Module):
    def __init__(self, numeric_dim, vocab_sizes, max_lens,
                 cat_embed_cols, cat_emb_dims, hidden_dim):
        super().__init__()
        self.cat_embed_cols = cat_embed_cols
        self.embeddings = nn.ModuleDict({
            col: nn.Embedding(vocab_sizes[col], cat_emb_dims[col], padding_idx=0)
            for col in cat_embed_cols if col in vocab_sizes
        })
        self.numeric_proj = nn.Linear(numeric_dim, hidden_dim)
        cat_total = sum(cat_emb_dims[col] for col in cat_embed_cols if col in vocab_sizes)
        self.final_proj = nn.Linear(hidden_dim + cat_total, hidden_dim)

    def forward(self, x_numeric, x_cats):
        num_out  = self.numeric_proj(x_numeric).relu()
        cat_outs = []
        for col in self.cat_embed_cols:
            if col not in self.embeddings:
                continue
            idx  = x_cats[col]
            emb  = self.embeddings[col](idx)
            mask = (idx != 0).float().unsqueeze(-1)
            emb  = (emb * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
            cat_outs.append(emb)
        cat_out = torch.cat(cat_outs, dim=-1)
        return self.final_proj(torch.cat([num_out, cat_out], dim=-1)).relu()


class MLPBPR(nn.Module):
    def __init__(self, user_in_dim, game_numeric_dim,
                 cat_vocab_sizes, cat_embed_cols, max_lens, cat_emb_dims,
                 hidden_channels, num_layers, dropout=0.3):
        super().__init__()
        self.user_proj = nn.Linear(user_in_dim, hidden_channels)
        self.game_encoder = GameFeatureEncoder(
            numeric_dim    = game_numeric_dim,
            vocab_sizes    = cat_vocab_sizes,
            max_lens       = max_lens,
            cat_embed_cols = cat_embed_cols,
            cat_emb_dims   = cat_emb_dims,
            hidden_dim     = hidden_channels,
        )
        layers = []
        in_dim = hidden_channels * 2
        for i in range(num_layers):
            out_dim = hidden_channels if i < num_layers - 1 else hidden_channels // 2
            layers += [nn.Linear(in_dim, out_dim), nn.ReLU(), nn.Dropout(dropout)]
            in_dim = out_dim
        layers.append(nn.Linear(in_dim, 1))
        self.mlp = nn.Sequential(*layers)

    def encode_user(self, user_feat):
        return self.user_proj(user_feat).relu()

    def encode_game(self, game_feat, game_cats):
        return self.game_encoder(game_feat, game_cats)

    def score(self, user_emb, game_emb):
        return self.mlp(torch.cat([user_emb, game_emb], dim=-1)).squeeze(-1)

    def forward(self, user_idx, game_idx,
                user_features, game_features, game_cat_idx):
        u_flat = user_idx.reshape(-1)
        g_flat = game_idx.reshape(-1)
        u_feat = user_features[u_flat]
        g_feat = game_features[g_flat]
        g_cats = {col: game_cat_idx[col][g_flat] for col in game_cat_idx}
        u_emb  = self.encode_user(u_feat)
        g_emb  = self.encode_game(g_feat, g_cats)
        return self.score(u_emb, g_emb)


# ---------------------------
# BPR loss
# ---------------------------
def bpr_loss(scores, n_neg=N_NEG):
    group_size = n_neg + 1
    n_groups   = scores.size(0) // group_size
    if n_groups == 0:
        return torch.tensor(0.0, device=scores.device, requires_grad=True)
    scores     = scores[:n_groups * group_size].view(n_groups, group_size)
    pos_scores = scores[:, 0]
    neg_scores = scores[:, 1:]
    diff       = pos_scores.unsqueeze(1) - neg_scores
    return -torch.log(torch.sigmoid(diff) + 1e-8).mean()


# ---------------------------
# Ranking metrics
# ---------------------------
def evaluate_ranking_df(df, scores, ks=(1, 5, 10, 20)):
    user_items = defaultdict(list)
    for u, y, s in zip(df[USER_COL].values, df[TARGET].values, scores):
        user_items[u].append((float(s), int(y)))

    metrics = {f"HitRate@{k}": 0.0 for k in ks}
    metrics.update({f"Recall@{k}": 0.0 for k in ks})
    metrics.update({f"NDCG@{k}": 0.0 for k in ks})
    metrics["MRR"] = 0.0
    n_users_eval   = 0

    for u, items in user_items.items():
        items.sort(key=lambda x: x[0], reverse=True)
        labels = [y for _, y in items]
        n_pos  = sum(labels)
        if n_pos == 0:
            continue
        n_users_eval += 1
        for rank, y in enumerate(labels, start=1):
            if y == 1:
                metrics["MRR"] += 1.0 / rank
                break
        for k in ks:
            topk     = labels[:k]
            hits_k   = 1.0 if any(topk) else 0.0
            recall_k = sum(topk) / n_pos
            dcg      = sum(1/math.log2(i+1) for i, y in enumerate(topk, 1) if y == 1)
            idcg     = sum(1/math.log2(i+1) for i in range(1, min(n_pos, k)+1))
            metrics[f"HitRate@{k}"] += hits_k
            metrics[f"Recall@{k}"]  += recall_k
            metrics[f"NDCG@{k}"]    += dcg/idcg if idcg > 0 else 0.0

    if n_users_eval == 0:
        return {k: 0.0 for k in metrics} | {"n_users_evaluated": 0}
    for k in metrics:
        if k != "n_users_evaluated":
            metrics[k] /= n_users_eval
    metrics["n_users_evaluated"] = n_users_eval
    return metrics


def get_val_scores(model, val_df, user2idx, game2idx,
                   user_features, game_features, game_cat_idx,
                   batch_size=4096):
    user_idx = torch.tensor(
        [user2idx.get(u, -1) for u in val_df[USER_COL]], dtype=torch.long
    )
    game_idx = torch.tensor(
        [game2idx.get(g, -1) for g in val_df[GAME_COL]], dtype=torch.long
    )
    mask        = (user_idx >= 0) & (game_idx >= 0)
    filtered_df = val_df[mask.numpy()].reset_index(drop=True)
    u_idx       = user_idx[mask]
    g_idx       = game_idx[mask]

    all_scores = []
    model.eval()
    with torch.no_grad():
        for start in range(0, len(u_idx), batch_size):
            end    = min(start + batch_size, len(u_idx))
            u_flat = u_idx[start:end].to(DEVICE)
            g_flat = g_idx[start:end].to(DEVICE)
            u_feat = user_features[u_flat]
            g_feat = game_features[g_flat]
            g_cats = {col: game_cat_idx[col][g_flat] for col in game_cat_idx}
            u_emb  = model.encode_user(u_feat)
            g_emb  = model.encode_game(g_feat, g_cats)
            scores = model.score(u_emb, g_emb)
            all_scores.append(scores.cpu())

    return filtered_df, torch.cat(all_scores).numpy()


def fmt_time(s):
    return time.strftime("%H:%M:%S", time.gmtime(s))


# ---------------------------
# Multi-seed training loop
# ---------------------------
all_seeds_train_roc = []   # (n_seeds, n_epochs)
all_seeds_val_roc   = []
all_seeds_val_ndcg  = []   # (n_seeds, n_epochs) — tracked per epoch for ranking curve
all_seeds_val_recall= []
all_seeds_val_metrics  = []
all_seeds_test_metrics = []

for seed in SEEDS:
    print(f"\n{'='*60}")
    print(f"SEED {seed}  |  hidden={HIDDEN_CHANNELS}, layers={NUM_LAYERS}, lr={LR}")
    print(f"{'='*60}")

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark     = False

    model = MLPBPR(
        user_in_dim      = user_in_dim,
        game_numeric_dim = game_numeric_dim,
        cat_vocab_sizes  = cat_vocab_sizes,
        cat_embed_cols   = cat_embed_cols,
        max_lens         = max_lens,
        cat_emb_dims     = CAT_EMB_DIMS,
        hidden_channels  = HIDDEN_CHANNELS,
        num_layers       = NUM_LAYERS,
    ).to(DEVICE)

    optimizer = Adam(model.parameters(), lr=LR, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=3, verbose=False
    )

    train_roc_list  = []
    val_roc_list    = []
    val_ndcg_list   = []
    val_recall_list = []
    best_val_roc_seed    = -np.inf
    best_model_state     = None

    for epoch in range(num_epochs):
        t_epoch_start = time.time()

        # Subsample groups
        n_total_groups = grouped_ei.shape[1] // (N_NEG + 1)
        group_idx      = torch.randperm(n_total_groups)[:N_GROUPS_SAMPLE]
        edge_idx       = (group_idx.unsqueeze(1) * (N_NEG + 1) +
                          torch.arange(N_NEG + 1).unsqueeze(0)).flatten()
        sampled_ei = grouped_ei[:, edge_idx]
        sampled_el = grouped_el[edge_idx]

        dataset = InteractionDataset(sampled_ei, sampled_el)
        loader  = DataLoader(
            dataset,
            batch_size  = batch_size // (N_NEG + 1),
            shuffle     = True,
            num_workers = 4,
            pin_memory  = True,
            collate_fn  = collate_fn,
        )

        # Train
        model.train()
        epoch_loss  = 0.0
        total_edges = 0
        for user_idx_b, game_idx_b, labels_b in tqdm(loader, desc=f"  Train ep{epoch:02d}", leave=False):
            user_idx_b = user_idx_b.to(DEVICE)
            game_idx_b = game_idx_b.to(DEVICE)
            optimizer.zero_grad()
            scores = model(user_idx_b, game_idx_b, user_features, game_features, game_cat_idx)
            loss   = bpr_loss(scores)
            loss.backward()
            optimizer.step()
            epoch_loss  += loss.item() * scores.size(0)
            total_edges += scores.size(0)
        epoch_loss /= max(total_edges, 1)

        # Evaluate
        model.eval()
        with torch.no_grad():
            # Train ROC (5 batches)
            all_s, all_l = [], []
            for i, (u, g, lbl) in enumerate(loader):
                if i >= 5: break
                u = u.to(DEVICE); g = g.to(DEVICE)
                s = model(u, g, user_features, game_features, game_cat_idx)
                all_s.append(s.cpu()); all_l.append(lbl.reshape(-1))
            train_roc = roc_auc_score(
                torch.cat(all_l).numpy(), torch.cat(all_s).numpy()
            ) if all_s else np.nan
            train_roc_list.append(train_roc)

            # Val ROC + ranking metrics
            val_df_f, val_scores = get_val_scores(
                model, val_filtered_df, user2idx, game2idx,
                user_features, game_features, game_cat_idx
            )
            val_labels = val_filtered_df[TARGET].values
            val_roc    = roc_auc_score(val_labels, val_scores)
            val_roc_list.append(val_roc)

            val_rank = evaluate_ranking_df(val_df_f, val_scores)
            val_ndcg_list.append(val_rank["NDCG@10"])
            val_recall_list.append(val_rank["Recall@10"])

        scheduler.step(val_roc)

        if val_roc > best_val_roc_seed:
            best_val_roc_seed = val_roc
            best_model_state  = {k: v.cpu() for k, v in model.state_dict().items()}

        t_epoch = time.time() - t_epoch_start
        print(f"  Ep {epoch:02d} | Loss {epoch_loss:.4f} | "
              f"TrainROC {train_roc:.4f} | ValROC {val_roc:.4f} | "
              f"NDCG@10 {val_rank['NDCG@10']:.4f} | {t_epoch:.0f}s")

    # Save best model for this seed
    seed_model_path = MODEL_PATH.format(seed=seed)
    torch.save({
        "state_dict": best_model_state,
        "seed": seed,
        "config": {"hidden_channels": HIDDEN_CHANNELS, "num_layers": NUM_LAYERS,
                   "lr": LR, "loss": "bpr", "mode": MODE},
    }, seed_model_path)
    print(f"  Saved: {seed_model_path}")

    # Final evaluation with best model
    best_model = MLPBPR(
        user_in_dim=user_in_dim, game_numeric_dim=game_numeric_dim,
        cat_vocab_sizes=cat_vocab_sizes, cat_embed_cols=cat_embed_cols,
        max_lens=max_lens, cat_emb_dims=CAT_EMB_DIMS,
        hidden_channels=HIDDEN_CHANNELS, num_layers=NUM_LAYERS,
    ).to(DEVICE)
    best_model.load_state_dict({k: v.to(DEVICE) for k, v in best_model_state.items()})
    best_model.eval()

    val_df_f,  val_scores  = get_val_scores(best_model, val_filtered_df, user2idx, game2idx,
                                             user_features, game_features, game_cat_idx)
    test_df_f, test_scores = get_val_scores(best_model, test_df, user2idx, game2idx,
                                             user_features, game_features, game_cat_idx)

    all_seeds_val_metrics.append(evaluate_ranking_df(val_df_f, val_scores))
    all_seeds_test_metrics.append(evaluate_ranking_df(test_df_f, test_scores))
    all_seeds_train_roc.append(train_roc_list)
    all_seeds_val_roc.append(val_roc_list)
    all_seeds_val_ndcg.append(val_ndcg_list)
    all_seeds_val_recall.append(val_recall_list)


# ---------------------------
# Aggregate metrics: mean ± std
# ---------------------------
def aggregate_metrics(list_of_dicts):
    keys = [k for k in list_of_dicts[0] if k != "n_users_evaluated"]
    result = {}
    for k in keys:
        vals = [d[k] for d in list_of_dicts]
        result[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}
    result["n_users_evaluated"] = list_of_dicts[0]["n_users_evaluated"]
    return result

val_metrics_agg  = aggregate_metrics(all_seeds_val_metrics)
test_metrics_agg = aggregate_metrics(all_seeds_test_metrics)

print("\n--- Val metrics (mean ± std) ---")
for k, v in val_metrics_agg.items():
    if isinstance(v, dict):
        print(f"  {k}: {v['mean']:.4f} ± {v['std']:.4f}")

print("\n--- Test metrics (mean ± std) ---")
for k, v in test_metrics_agg.items():
    if isinstance(v, dict):
        print(f"  {k}: {v['mean']:.4f} ± {v['std']:.4f}")


# ---------------------------
# Plots
# ---------------------------
# Arrays: (n_seeds, n_epochs)
train_roc_arr  = np.array(all_seeds_train_roc)   # (3, 20)
val_roc_arr    = np.array(all_seeds_val_roc)
val_ndcg_arr   = np.array(all_seeds_val_ndcg)
val_recall_arr = np.array(all_seeds_val_recall)

epochs = np.arange(1, num_epochs + 1)

mean_train_roc  = train_roc_arr.mean(axis=0)
std_train_roc   = train_roc_arr.std(axis=0)
mean_val_roc    = val_roc_arr.mean(axis=0)
std_val_roc     = val_roc_arr.std(axis=0)
mean_val_ndcg   = val_ndcg_arr.mean(axis=0)
std_val_ndcg    = val_ndcg_arr.std(axis=0)
mean_val_recall = val_recall_arr.mean(axis=0)
std_val_recall  = val_recall_arr.std(axis=0)

model_name = f"MLP ({'with' if MODE == 'with_net' else 'no'} network features)"

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
fig.suptitle(f"Learning Curve — {model_name}", fontsize=13)

# Top: ROC-AUC
ax1.plot(epochs, mean_train_roc, marker='o', label="Train ROC-AUC")
ax1.fill_between(epochs, mean_train_roc - std_train_roc,
                          mean_train_roc + std_train_roc, alpha=0.2)
ax1.plot(epochs, mean_val_roc, marker='o', label="Val ROC-AUC")
ax1.fill_between(epochs, mean_val_roc - std_val_roc,
                          mean_val_roc + std_val_roc, alpha=0.2)
ax1.set_xlabel("Epoch")
ax1.set_ylabel("ROC-AUC")
ax1.legend()
ax1.grid(True, alpha=0.3)

# Bottom: Ranking metrics
ax2.plot(epochs, mean_val_ndcg, marker='o', label="Val NDCG@10")
ax2.fill_between(epochs, mean_val_ndcg - std_val_ndcg,
                          mean_val_ndcg + std_val_ndcg, alpha=0.2)
ax2.plot(epochs, mean_val_recall, marker='o', label="Val Recall@10")
ax2.fill_between(epochs, mean_val_recall - std_val_recall,
                          mean_val_recall + std_val_recall, alpha=0.2)
ax2.set_xlabel("Epoch")
ax2.set_ylabel("Score")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(PLOT_PATH, dpi=150)
plt.close()
print(f"\nPlot saved to: {PLOT_PATH}")


# ---------------------------
# Save all metrics
# ---------------------------
metrics_dict = {
    "config": {
        "hidden_channels": HIDDEN_CHANNELS,
        "num_layers":      NUM_LAYERS,
        "lr":              LR,
        "loss":            "bpr",
        "mode":            MODE,
        "seeds":           SEEDS,
    },
    "val_metrics":        val_metrics_agg,
    "test_metrics":       test_metrics_agg,
    "per_seed_val":       [
        {k: float(v) if not isinstance(v, dict) else v
         for k, v in m.items()} for m in all_seeds_val_metrics
    ],
    "per_seed_test":      [
        {k: float(v) if not isinstance(v, dict) else v
         for k, v in m.items()} for m in all_seeds_test_metrics
    ],
    "train_roc_history":  train_roc_arr.tolist(),
    "val_roc_history":    val_roc_arr.tolist(),
    "val_ndcg_history":   val_ndcg_arr.tolist(),
    "val_recall_history": val_recall_arr.tolist(),
}
with open(METRICS_PATH, "w") as f:
    json.dump(metrics_dict, f, indent=2)
print(f"Metrics saved to: {METRICS_PATH}")