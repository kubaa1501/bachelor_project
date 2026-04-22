import os
import sys
import json
import random
import math
import time
from collections import defaultdict

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.optim import Adam
from tqdm import tqdm
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt

from torch_geometric.nn import SAGEConv, to_hetero
from torch_geometric.loader import LinkNeighborLoader

# ---------------------------
# Mode: with_net or no_net
# ---------------------------
MODE = sys.argv[1] if len(sys.argv) > 1 else "with_net"
assert MODE in ("with_net", "no_net"), f"MODE must be with_net or no_net, got {MODE}"
print(f"Running in mode: {MODE}")

if MODE == "with_net":
    CACHE_DIR    = "/home/jaga/data/cache"
    MODEL_PATH   = "/home/jaga/results/models/gsage_with_net_seed{seed}.pt"
    METRICS_PATH = "/home/jaga/results/metrics/gsage_with_net_metrics.json"
    PLOT_PATH    = "/home/jaga/results/plots/gsage_with_net_learning_curve.png"
else:
    CACHE_DIR    = "/home/jaga/data/cache_no_net"
    MODEL_PATH   = "/home/jaga/results/models/gsage_no_net_seed{seed}.pt"
    METRICS_PATH = "/home/jaga/results/metrics/gsage_no_net_metrics.json"
    PLOT_PATH    = "/home/jaga/results/plots/gsage_no_net_learning_curve.png"

# ---------------------------
# Multi-seed setup
# ---------------------------
SEEDS = [42, 0, 1]

# ---------------------------
# Best hyperparameters (fixed — search already done)
# ---------------------------
# gsage_no_net:   hidden=128, layers=2, lr=5e-4
# gsage_with_net: hidden=128, layers=2, lr=5e-4
HIDDEN_CHANNELS = 128
NUM_LAYERS      = 2
LR              = 5e-4

# # Commented out — other configs tried during search
# hidden_channels_list = [64, 128]
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

NUM_EPOCHS      = 20
N_GROUPS_SAMPLE = 200_000

# ---------------------------
# Load cache (once, outside seed loop)
# ---------------------------
print(f"\nLoading cache from {CACHE_DIR}...")
t0 = time.time()

data                 = torch.load(f"{CACHE_DIR}/graph.pt",                          weights_only=False)
user2idx             = torch.load(f"{CACHE_DIR}/user2idx.pt",                       weights_only=False)
game2idx             = torch.load(f"{CACHE_DIR}/game2idx.pt",                       weights_only=False)
val_edge_label_index = torch.load(f"{CACHE_DIR}/val_edge_label_index.pt",           weights_only=False)
val_edge_label       = torch.load(f"{CACHE_DIR}/val_edge_label.pt",                 weights_only=False)
grouped_ei           = torch.load(f"{CACHE_DIR}/grouped_train_edge_label_index.pt", weights_only=False)
grouped_el           = torch.load(f"{CACHE_DIR}/grouped_train_edge_label.pt",       weights_only=False)
val_filtered_df      = pd.read_parquet(f"{CACHE_DIR}/val_filtered_df.parquet")
test_df              = pd.read_parquet(f"{CACHE_DIR}/test_df.parquet")

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

if torch.cuda.is_available():
    gpu_mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"GPU: {torch.cuda.get_device_name(0)}, Memory: {gpu_mem_gb:.1f}GB")
    if gpu_mem_gb >= 40:
        base = 1024
    elif gpu_mem_gb >= 20:
        base = 512
    elif gpu_mem_gb >= 16:
        base = 256
    else:
        base = 128
else:
    base = 32
batch_size = base * (N_NEG + 1)
print(f"Using batch_size={batch_size}")

data = data.to(DEVICE)

nn_dict    = {et: [10, 10] for et in data.edge_types}
val_loader = LinkNeighborLoader(
    data=data,
    num_neighbors=nn_dict,
    edge_label_index=(("user", "plays", "game"), val_edge_label_index),
    edge_label=val_edge_label,
    neg_sampling=None,
    batch_size=batch_size,
    shuffle=False,
    num_workers=4,
    persistent_workers=True,
    pin_memory=True,
)


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


class GraphSAGENet(nn.Module):
    def __init__(self, hidden_channels, num_layers=2):
        super().__init__()
        self.convs = nn.ModuleList([
            SAGEConv((-1, -1), hidden_channels) for _ in range(num_layers)
        ])
        self.dropout = nn.Dropout(0.3)

    def forward(self, x, edge_index):
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index).relu()
            if i < len(self.convs) - 1:
                x = self.dropout(x)
        return x


class LinkPredictor(nn.Module):
    def __init__(self, hidden_channels, metadata, num_layers,
                 user_in_dim, game_numeric_dim,
                 cat_vocab_sizes, cat_embed_cols, max_lens, cat_emb_dims):
        super().__init__()
        self.cat_embed_cols = cat_embed_cols
        self.user_proj = nn.Linear(user_in_dim, hidden_channels)
        self.game_encoder = GameFeatureEncoder(
            numeric_dim=game_numeric_dim, vocab_sizes=cat_vocab_sizes,
            max_lens=max_lens, cat_embed_cols=cat_embed_cols,
            cat_emb_dims=cat_emb_dims, hidden_dim=hidden_channels,
        )
        self.gnn = to_hetero(
            GraphSAGENet(hidden_channels, num_layers=num_layers),
            metadata, aggr='sum'
        )
        self.decoder = nn.Sequential(
            nn.Linear(hidden_channels * 2, hidden_channels),
            nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(hidden_channels, 1)
        )

    def _get_cats(self, batch_or_data):
        cats = {}
        for col in self.cat_embed_cols:
            key = f"{col}_idx"
            if hasattr(batch_or_data["game"], key):
                cats[col] = getattr(batch_or_data["game"], key)
        return cats

    def _encode(self, x_dict, batch_or_data):
        user_x = self.user_proj(x_dict["user"]).relu()
        cats   = self._get_cats(batch_or_data)
        game_x = self.game_encoder(x_dict["game"], cats)
        return {"user": user_x, "game": game_x}

    def forward_batch(self, batch):
        etype  = ("user", "plays", "game")
        x_dict = self._encode(batch.x_dict, batch)
        x_dict = self.gnn(x_dict, batch.edge_index_dict)
        u_emb  = x_dict["user"][batch[etype].edge_label_index[0]]
        g_emb  = x_dict["game"][batch[etype].edge_label_index[1]]
        return self.decoder(torch.cat([u_emb, g_emb], dim=-1)).squeeze(-1)

    def forward_full(self, data):
        x_dict = self._encode(data.x_dict, data)
        return self.gnn(x_dict, data.edge_index_dict)


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


def fmt_time(s):
    return time.strftime("%H:%M:%S", time.gmtime(s))


# ---------------------------
# Multi-seed training loop
# ---------------------------
etype = ("user", "plays", "game")

all_seeds_train_roc    = []
all_seeds_val_roc      = []
all_seeds_val_ndcg     = []
all_seeds_val_recall   = []
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

    model = LinkPredictor(
        hidden_channels=HIDDEN_CHANNELS, metadata=data.metadata(),
        num_layers=NUM_LAYERS, user_in_dim=user_in_dim,
        game_numeric_dim=game_numeric_dim, cat_vocab_sizes=cat_vocab_sizes,
        cat_embed_cols=cat_embed_cols, max_lens=max_lens, cat_emb_dims=CAT_EMB_DIMS,
    ).to(DEVICE)

    optimizer = Adam(model.parameters(), lr=LR, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=3, verbose=False
    )

    train_roc_list  = []
    val_roc_list    = []
    val_ndcg_list   = []
    val_recall_list = []
    best_val_roc_seed = -np.inf
    best_model_state  = None
    epoch_times       = []

    for epoch in range(NUM_EPOCHS):
        t_epoch_start = time.time()

        # Subsample groups
        n_total_groups = grouped_ei.shape[1] // (N_NEG + 1)
        group_idx      = torch.randperm(n_total_groups)[:N_GROUPS_SAMPLE]
        edge_idx       = (group_idx.unsqueeze(1) * (N_NEG + 1) +
                          torch.arange(N_NEG + 1).unsqueeze(0)).flatten()
        sampled_ei = grouped_ei[:, edge_idx]
        sampled_el = grouped_el[edge_idx]

        epoch_loader = LinkNeighborLoader(
            data=data, num_neighbors=nn_dict,
            edge_label_index=(etype, sampled_ei),
            edge_label=sampled_el, neg_sampling=None,
            batch_size=batch_size, shuffle=False,
            num_workers=4, persistent_workers=False, pin_memory=True,
        )

        # Train
        model.train()
        epoch_loss  = 0.0
        total_edges = 0
        for batch in tqdm(epoch_loader, desc=f"  Train ep{epoch:02d}", leave=False):
            batch = batch.to(DEVICE)
            optimizer.zero_grad()
            scores = model.forward_batch(batch)
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
            for i, batch in enumerate(epoch_loader):
                if i >= 5: break
                batch = batch.to(DEVICE)
                all_s.append(model.forward_batch(batch).cpu())
                all_l.append(batch[etype].edge_label.cpu())
            train_roc = roc_auc_score(
                torch.cat(all_l).numpy(), torch.cat(all_s).numpy()
            ) if all_s else np.nan
            train_roc_list.append(train_roc)

            # Val ROC
            all_s, all_l = [], []
            for batch in tqdm(val_loader, desc=f"  Val ep{epoch:02d}", leave=False):
                batch = batch.to(DEVICE)
                all_s.append(model.forward_batch(batch).cpu())
                all_l.append(batch[etype].edge_label.cpu())
            ep_val_scores = torch.cat(all_s).numpy()
            val_roc = roc_auc_score(
                torch.cat(all_l).numpy(), torch.cat(all_s).numpy()
            ) if all_s else np.nan
            val_roc_list.append(val_roc)

            # Val ranking metrics — reuse val_loader scores already computed above
            val_df_f = val_filtered_df.iloc[:len(ep_val_scores)].reset_index(drop=True)
            val_rank = evaluate_ranking_df(val_df_f, ep_val_scores)
            val_ndcg_list.append(val_rank["NDCG@10"])
            val_recall_list.append(val_rank["Recall@10"])

        scheduler.step(val_roc)

        if val_roc > best_val_roc_seed:
            best_val_roc_seed = val_roc
            best_model_state  = {k: v.cpu() for k, v in model.state_dict().items()}

        t_epoch = time.time() - t_epoch_start
        epoch_times.append(t_epoch)
        eta = (sum(epoch_times) / len(epoch_times)) * (NUM_EPOCHS - (epoch + 1))
        print(f"  Ep {epoch:02d} | Loss {epoch_loss:.4f} | "
              f"TrainROC {train_roc:.4f} | ValROC {val_roc:.4f} | "
              f"NDCG@10 {val_rank['NDCG@10']:.4f} | "
              f"{t_epoch:.0f}s | ETA {fmt_time(eta)}")

    # Save best model for this seed
    seed_model_path = MODEL_PATH.format(seed=seed)
    torch.save({
        "state_dict": best_model_state, "seed": seed,
        "config": {"hidden_channels": HIDDEN_CHANNELS, "num_layers": NUM_LAYERS,
                   "lr": LR, "loss": "bpr", "mode": MODE},
    }, seed_model_path)
    print(f"  Saved: {seed_model_path}")

    # Final evaluation with best model
    best_model = LinkPredictor(
        hidden_channels=HIDDEN_CHANNELS, metadata=data.metadata(),
        num_layers=NUM_LAYERS, user_in_dim=user_in_dim,
        game_numeric_dim=game_numeric_dim, cat_vocab_sizes=cat_vocab_sizes,
        cat_embed_cols=cat_embed_cols, max_lens=max_lens, cat_emb_dims=CAT_EMB_DIMS,
    ).to(DEVICE)
    best_model.load_state_dict({k: v.to(DEVICE) for k, v in best_model_state.items()})
    best_model.eval()

    with torch.no_grad():
        full_x = best_model.forward_full(data)
    user_emb_full = full_x["user"].cpu()
    game_emb_full = full_x["game"].cpu()

    def score_df(df, batch_size=4096):
        u_idx = torch.tensor(
            [user2idx.get(u, -1) for u in df[USER_COL]], dtype=torch.long
        )
        g_idx = torch.tensor(
            [game2idx.get(g, -1) for g in df[GAME_COL]], dtype=torch.long
        )
        mask = (u_idx >= 0) & (g_idx >= 0)
        fdf  = df[mask.numpy()].reset_index(drop=True)
        u_idx_valid = u_idx[mask]
        g_idx_valid = g_idx[mask]
        all_scores  = []
        with torch.no_grad():
            for start in range(0, len(u_idx_valid), batch_size):
                u_emb = user_emb_full[u_idx_valid[start:start+batch_size]].to(DEVICE)
                g_emb = game_emb_full[g_idx_valid[start:start+batch_size]].to(DEVICE)
                scores = best_model.decoder(
                    torch.cat([u_emb, g_emb], dim=-1)
                ).squeeze(-1).cpu()
                all_scores.append(scores)
        return fdf, torch.cat(all_scores).numpy()

    val_df_f,  val_scores  = score_df(val_filtered_df)
    test_df_f, test_scores = score_df(test_df)

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
train_roc_arr  = np.array(all_seeds_train_roc)
val_roc_arr    = np.array(all_seeds_val_roc)
val_ndcg_arr   = np.array(all_seeds_val_ndcg)
val_recall_arr = np.array(all_seeds_val_recall)

epochs = np.arange(1, NUM_EPOCHS + 1)

mean_train_roc  = train_roc_arr.mean(axis=0)
std_train_roc   = train_roc_arr.std(axis=0)
mean_val_roc    = val_roc_arr.mean(axis=0)
std_val_roc     = val_roc_arr.std(axis=0)
mean_val_ndcg   = val_ndcg_arr.mean(axis=0)
std_val_ndcg    = val_ndcg_arr.std(axis=0)
mean_val_recall = val_recall_arr.mean(axis=0)
std_val_recall  = val_recall_arr.std(axis=0)

model_name = f"GraphSAGE ({'with' if MODE == 'with_net' else 'no'} network features)"

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