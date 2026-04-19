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
    MODEL_PATH   = "/home/jaga/results/models/nn_bpr_with_net_best.pt"
    METRICS_PATH = "/home/jaga/results/metrics/nn_bpr_with_net_metrics.json"
    PLOT_PATH    = "/home/jaga/results/plots/nn_bpr_with_net_roc.png"
else:
    CACHE_DIR    = "/home/jaga/data/cache_no_net"
    MODEL_PATH   = "/home/jaga/results/models/nn_bpr_no_net_best.pt"
    METRICS_PATH = "/home/jaga/results/metrics/nn_bpr_no_net_metrics.json"
    PLOT_PATH    = "/home/jaga/results/plots/nn_bpr_no_net_roc.png"

# ---------------------------
# Reproducibility
# ---------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark     = False

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
# Load cache
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

# Extract feature tensors
user_features = data["user"].x   # (n_users, user_in_dim)
game_features = data["game"].x   # (n_games, game_numeric_dim)

# Extract categorical indices
game_cat_idx = {}
for col in cat_embed_cols:
    key = f"{col}_idx"
    if hasattr(data["game"], key):
        game_cat_idx[col] = getattr(data["game"], key)

print(f"  user_in_dim={user_in_dim}, game_numeric_dim={game_numeric_dim}")
print(f"  cat_vocab_sizes={cat_vocab_sizes}")
print(f"  n_users={user_features.shape[0]}, n_games={game_features.shape[0]}")
print(f"  grouped train edges: {grouped_ei.shape[1]}")

# ---------------------------
# Dataset
# ---------------------------
class InteractionDataset(Dataset):
    """Returns groups of (1 pos + N_NEG neg) as flat tensors."""
    def __init__(self, edge_index, edge_label, n_neg=N_NEG):
        self.edge_index = edge_index
        self.edge_label = edge_label
        self.n_neg      = n_neg
        self.group_size = n_neg + 1
        self.n_groups   = edge_index.shape[1] // self.group_size

    def __len__(self):
        return self.n_groups

    def __getitem__(self, idx):
        start = idx * self.group_size
        end   = start + self.group_size
        user_idx = self.edge_index[0, start:end]
        game_idx = self.edge_index[1, start:end]
        labels   = self.edge_label[start:end]
        return user_idx, game_idx, labels


def collate_fn(batch):
    user_idx = torch.stack([b[0] for b in batch])  # (batch, group_size)
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
    """Simple MLP: concat(user_emb, game_emb) -> score."""
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

        # MLP layers after concatenation
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
        """
        user_idx: (batch, group_size)
        game_idx: (batch, group_size)
        Returns scores: (batch * group_size,)
        """
        batch_size = user_idx.shape[0]
        group_size = user_idx.shape[1]

        # Flatten
        u_flat = user_idx.reshape(-1)  # (batch * group_size,)
        g_flat = game_idx.reshape(-1)

        u_feat = user_features[u_flat]
        g_feat = game_features[g_flat]
        g_cats = {col: game_cat_idx[col][g_flat] for col in game_cat_idx}

        u_emb = self.encode_user(u_feat)
        g_emb = self.encode_game(g_feat, g_cats)

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
            dcg      = sum(1/math.log2(i+1) for i,y in enumerate(topk,1) if y==1)
            idcg     = sum(1/math.log2(i+1) for i in range(1, min(n_pos,k)+1))
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


# ---------------------------
# Auto batch size
# ---------------------------
if torch.cuda.is_available():
    gpu_mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"GPU: {torch.cuda.get_device_name(0)}, Memory: {gpu_mem_gb:.1f}GB")
    batch_size = 2048
else:
    batch_size = 512
print(f"Using batch_size={batch_size}")

# Move features to device
user_features = user_features.to(DEVICE)
game_features = game_features.to(DEVICE)
game_cat_idx  = {col: idx.to(DEVICE) for col, idx in game_cat_idx.items()}

# ---------------------------
# Hyperparameters
# ---------------------------
hidden_channels_list = [64, 128, 256]
num_layers_list      = [2, 3, 4]
learning_rates       = [1e-3, 5e-4]
num_epochs           = 20
N_GROUPS_SAMPLE      = 200_000

best_val_score   = -np.inf
best_model_state = None
best_config      = None
best_train_roc   = None
best_val_roc     = None

def fmt_time(s):
    return time.strftime("%H:%M:%S", time.gmtime(s))

configs        = list(itertools.product(
    hidden_channels_list, num_layers_list, learning_rates
))
n_configs      = len(configs)
t_search_start = time.time()

print(f"\n{n_configs} hyperparameter combinations to try")
print(f"{num_epochs} epochs each\n")

config_bar = tqdm(configs, desc="Hyperparam search", unit="config", position=0)

for config_idx, (hidden_channels, num_layers, lr) in enumerate(config_bar):
    print(f"\n--- Config {config_idx+1}/{n_configs}: "
          f"hidden={hidden_channels}, layers={num_layers}, lr={lr} ---")

    model = MLPBPR(
        user_in_dim      = user_in_dim,
        game_numeric_dim = game_numeric_dim,
        cat_vocab_sizes  = cat_vocab_sizes,
        cat_embed_cols   = cat_embed_cols,
        max_lens         = max_lens,
        cat_emb_dims     = CAT_EMB_DIMS,
        hidden_channels  = hidden_channels,
        num_layers       = num_layers,
    ).to(DEVICE)

    optimizer = Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=3, verbose=False
    )

    train_roc_list = []
    val_roc_list   = []
    epoch_times    = []

    epoch_bar = tqdm(range(num_epochs), desc="  Epochs",
                     unit="epoch", position=1, leave=False)

    for epoch in epoch_bar:
        t_epoch_start = time.time()

        # Subsample groups
        n_total_groups = grouped_ei.shape[1] // (N_NEG + 1)
        group_idx      = torch.randperm(n_total_groups)[:N_GROUPS_SAMPLE]
        edge_idx       = (group_idx.unsqueeze(1) * (N_NEG + 1) +
                          torch.arange(N_NEG + 1).unsqueeze(0)).flatten()
        sampled_ei     = grouped_ei[:, edge_idx]
        sampled_el     = grouped_el[edge_idx]

        dataset = InteractionDataset(sampled_ei, sampled_el)
        loader  = DataLoader(
            dataset,
            batch_size = batch_size // (N_NEG + 1),
            shuffle    = True,
            num_workers= 4,
            pin_memory = True,
            collate_fn = collate_fn,
        )

        # --- Train ---
        model.train()
        epoch_loss  = 0.0
        total_edges = 0

        train_bar = tqdm(loader, desc=f"    Train ep{epoch:02d}",
                         unit="batch", position=2, leave=False)
        for user_idx_b, game_idx_b, labels_b in train_bar:
            user_idx_b = user_idx_b.to(DEVICE)
            game_idx_b = game_idx_b.to(DEVICE)

            optimizer.zero_grad()
            scores = model(
                user_idx_b, game_idx_b,
                user_features, game_features, game_cat_idx
            )
            loss = bpr_loss(scores)
            loss.backward()
            optimizer.step()

            epoch_loss  += loss.item() * scores.size(0)
            total_edges += scores.size(0)
            train_bar.set_postfix(loss=f"{loss.item():.4f}")

        epoch_loss /= max(total_edges, 1)

        # --- Evaluate ROC ---
        model.eval()
        with torch.no_grad():
            # Train ROC — 5 batches
            all_scores, all_labels = [], []
            for i, (u, g, lbl) in enumerate(loader):
                if i >= 5: break
                u = u.to(DEVICE); g = g.to(DEVICE)
                s = model(u, g, user_features, game_features, game_cat_idx)
                all_scores.append(s.cpu())
                all_labels.append(lbl.reshape(-1))
            train_roc = roc_auc_score(
                torch.cat(all_labels).numpy(),
                torch.cat(all_scores).numpy()
            ) if all_scores else np.nan
            train_roc_list.append(train_roc)

            # Val ROC
            _, val_scores = get_val_scores(
                model, val_filtered_df, user2idx, game2idx,
                user_features, game_features, game_cat_idx
            )
            val_labels = val_filtered_df[TARGET].values
            val_roc    = roc_auc_score(val_labels, val_scores)
            val_roc_list.append(val_roc)

        scheduler.step(val_roc)

        t_epoch = time.time() - t_epoch_start
        epoch_times.append(t_epoch)
        avg_t   = sum(epoch_times) / len(epoch_times)
        eta     = avg_t * (num_epochs - (epoch + 1))

        epoch_bar.set_postfix(
            loss=f"{epoch_loss:.4f}",
            troc=f"{train_roc:.4f}",
            vroc=f"{val_roc:.4f}",
        )
        print(
            f"  Ep {epoch:02d} | Loss {epoch_loss:.4f} | "
            f"TrainROC {train_roc:.4f} | ValROC {val_roc:.4f} | "
            f"Epoch {t_epoch:.0f}s | ETA {fmt_time(eta)}"
        )

    avg_val_roc = np.nanmean(val_roc_list)
    config_bar.set_postfix(best=f"{best_val_score:.4f}", this=f"{avg_val_roc:.4f}")

    if avg_val_roc > best_val_score:
        best_val_score   = avg_val_roc
        best_model_state = {k: v.cpu() for k, v in model.state_dict().items()}
        best_config      = {
            "hidden_channels": hidden_channels,
            "num_layers":      num_layers,
            "lr":              lr,
            "loss":            "bpr",
            "mode":            MODE,
        }
        best_train_roc = train_roc_list
        best_val_roc   = val_roc_list
        print(f"  *** New best val ROC: {best_val_score:.4f} ***")

total_time = time.time() - t_search_start
print(f"\nSearch complete in {fmt_time(total_time)}")
print(f"Best config: {best_config}")
print(f"Best val ROC: {best_val_score:.4f}")

# ---------------------------
# Save best model
# ---------------------------
torch.save({
    "state_dict":       best_model_state,
    "best_val_roc":     float(best_val_score),
    "user_in_dim":      user_in_dim,
    "game_numeric_dim": game_numeric_dim,
    "cat_vocab_sizes":  cat_vocab_sizes,
    "cat_embed_cols":   cat_embed_cols,
    "max_lens":         max_lens,
    "cat_emb_dims":     CAT_EMB_DIMS,
    "config":           best_config,
}, MODEL_PATH)
print(f"Saved to: {MODEL_PATH}")

# ---------------------------
# Plot
# ---------------------------
epochs_range = range(1, len(best_train_roc) + 1)
plt.figure(figsize=(8, 5))
plt.plot(epochs_range, best_train_roc, marker='o', label="Train ROC-AUC")
plt.plot(epochs_range, best_val_roc,   marker='o', label="Val ROC-AUC")
plt.xlabel("Epoch"); plt.ylabel("ROC-AUC")
plt.title(f"NN BPR — {MODE}")
plt.grid(True, alpha=0.3); plt.legend(); plt.tight_layout()
plt.savefig(PLOT_PATH)
plt.close()

# ---------------------------
# Final evaluation
# ---------------------------
best_model = MLPBPR(
    user_in_dim      = user_in_dim,
    game_numeric_dim = game_numeric_dim,
    cat_vocab_sizes  = cat_vocab_sizes,
    cat_embed_cols   = cat_embed_cols,
    max_lens         = max_lens,
    cat_emb_dims     = CAT_EMB_DIMS,
    hidden_channels  = best_config["hidden_channels"],
    num_layers       = best_config["num_layers"],
).to(DEVICE)
best_model.load_state_dict({k: v.to(DEVICE) for k, v in best_model_state.items()})
best_model.eval()

print("\nEvaluating on val and test sets...")
val_df_f, val_scores   = get_val_scores(
    best_model, val_filtered_df, user2idx, game2idx,
    user_features, game_features, game_cat_idx
)
test_df_f, test_scores = get_val_scores(
    best_model, test_df, user2idx, game2idx,
    user_features, game_features, game_cat_idx
)

val_metrics  = evaluate_ranking_df(val_df_f,  val_scores)
test_metrics = evaluate_ranking_df(test_df_f, test_scores)
print("Val metrics: ",  val_metrics)
print("Test metrics:", test_metrics)

metrics_dict = {
    "best_config":    best_config,
    "best_val_roc":   float(best_val_score),
    "best_train_roc": [float(x) for x in best_train_roc],
    "best_val_roc_history": [float(x) for x in best_val_roc],
    "val_metrics":    val_metrics,
    "test_metrics":   test_metrics,
}
with open(METRICS_PATH, "w") as f:
    json.dump(metrics_dict, f, indent=2)
print(f"Saved metrics to {METRICS_PATH}")
