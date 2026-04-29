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
#           mode
# ---------------------------
MODE = sys.argv[1] if len(sys.argv) > 1 else "with_net"
assert MODE in ("with_net", "no_net"), f"MODE must be with_net or no_net, got {MODE}"
print(f"Running in mode: {MODE}")


# paths depend on selected mode:
# - with_net   -> use network-enriched cached data and output files
# - no_net     -> use baseline / no-network cached data and output files

if MODE == "with_net":
    CACHE_DIR    = "/home/jaga/data/cache"
    MODEL_PATH   = "/home/jaga/results/models/gsage_bpr_v2_with_net.pt"
    METRICS_PATH = "/home/jaga/results/metrics/gsage_bpr_v2_with_net.json"
    PLOT_PATH    = "/home/jaga/results/plots/gsage_bpr_v2_with_net_roc.png"
else:
    CACHE_DIR    = "/home/jaga/data/cache_no_net"
    MODEL_PATH   = "/home/jaga/results/models/gsage_bpr_v2_no_net.pt"
    METRICS_PATH = "/home/jaga/results/metrics/gsage_bpr_v2_no_net.json"
    PLOT_PATH    = "/home/jaga/results/plots/gsage_bpr_v2_no_net_roc.png"

# ---------------------------
#      reproducibility
# --------------------------- 
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark     = False

# device and task settings
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

USER_COL = "steamid"
GAME_COL = "appid"
TARGET   = "owned"
# number of negatives paired with each positive in BPR training groups
N_NEG    = 10

# create optupt dirs
os.makedirs("/home/jaga/results/metrics", exist_ok=True)
os.makedirs("/home/jaga/results/models",  exist_ok=True)
os.makedirs("/home/jaga/results/plots",   exist_ok=True)

# embedding dimentions for categorical game features
CAT_EMB_DIMS = {
    "genres":    16,
    "developer": 64,
    "publisher": 64,
    "platforms": 4,
}

# ---------------------------
#         load cache
# ---------------------------
print(f"\nLoading cache from {CACHE_DIR}...")
t0 = time.time()

# load cached heterogeneous graph, mappings, train groups and validation/test data
data                 = torch.load(f"{CACHE_DIR}/graph.pt",                          weights_only=False)
user2idx             = torch.load(f"{CACHE_DIR}/user2idx.pt",                       weights_only=False)
game2idx             = torch.load(f"{CACHE_DIR}/game2idx.pt",                       weights_only=False)
val_edge_label_index = torch.load(f"{CACHE_DIR}/val_edge_label_index.pt",           weights_only=False)
val_edge_label       = torch.load(f"{CACHE_DIR}/val_edge_label.pt",                 weights_only=False)
grouped_ei           = torch.load(f"{CACHE_DIR}/grouped_train_edge_label_index.pt", weights_only=False)
grouped_el           = torch.load(f"{CACHE_DIR}/grouped_train_edge_label.pt",       weights_only=False)
val_filtered_df      = pd.read_parquet(f"{CACHE_DIR}/val_filtered_df.parquet")
test_df              = pd.read_parquet(f"{CACHE_DIR}/test_df.parquet")


# load categorical vocabularies and feature metadata
with open(f"{CACHE_DIR}/cat_vocabs.json") as f:
    vocabs = json.load(f)
with open(f"{CACHE_DIR}/meta.json") as f:
    meta = json.load(f)

print(f"Cache loaded in {time.time()-t0:.1f}s")
print(f"  Graph: {data}")
print(f"  Grouped train edges: {grouped_ei.shape[1]}")
print(f"  Val edges: {val_edge_label_index.shape[1]}")

# metadata describing feature layout 
cat_embed_cols   = meta["cat_embed_cols"]
max_lens         = meta["max_lens"]
cat_vocab_sizes  = meta["cat_vocab_sizes"]
user_in_dim      = meta["user_in_dim"]
game_numeric_dim = meta["game_numeric_dim"]

print(f"  user_in_dim={user_in_dim}, game_numeric_dim={game_numeric_dim}")
print(f"  cat_vocab_sizes={cat_vocab_sizes}")
print(f"  cat_emb_dims={CAT_EMB_DIMS}")

# move graph data to selected device
data = data.to(DEVICE)

# ---------------------------
#      auto batch size
# ---------------------------
# choose batch size based on available GPU memory
# batch size is kept as a multiple of group size: 1 positive + n negatives
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

# ---------------------------
#          model
# ---------------------------
class GameFeatureEncoder(nn.Module):
    # encode game features from:
    # - numeric game features
    # - multi-value categorical game features via embeddings
    def __init__(self, numeric_dim, vocab_sizes, max_lens,
                 cat_embed_cols, cat_emb_dims, hidden_dim):
        super().__init__()
        self.cat_embed_cols = cat_embed_cols

        # create one embedding table per categorical game feature
        self.embeddings = nn.ModuleDict({
            col: nn.Embedding(vocab_sizes[col], cat_emb_dims[col], padding_idx=0)
            for col in cat_embed_cols if col in vocab_sizes
        })
        
        # project numeric game features to hidden dimension
        self.numeric_proj = nn.Linear(numeric_dim, hidden_dim)
        
        # combine numeric and categorical game representations
        cat_total = sum(cat_emb_dims[col] for col in cat_embed_cols if col in vocab_sizes)
        self.final_proj = nn.Linear(hidden_dim + cat_total, hidden_dim)

    def forward(self, x_numeric, x_cats):
        # encode numeric game features
        num_out  = self.numeric_proj(x_numeric).relu()
        # average non-padding embeddings for each categorical field
        cat_outs = []
        for col in self.cat_embed_cols:
            if col not in self.embeddings:
                continue
            idx  = x_cats[col]                          # (n_games, max_len)
            emb  = self.embeddings[col](idx)             # (n_games, max_len, emb_dim)
            mask = (idx != 0).float().unsqueeze(-1)      # (n_games, max_len, 1)
            emb  = (emb * mask).sum(dim=1)               # (n_games, emb_dim)
            emb  = emb / mask.sum(dim=1).clamp(min=1)   # mean pool
            cat_outs.append(emb)
        cat_out = torch.cat(cat_outs, dim=-1)
        # return final game representation
        return self.final_proj(torch.cat([num_out, cat_out], dim=-1)).relu()


class GraphSAGENet(nn.Module):
    # graph encoder based on stacked GraphSAGE convolution layers
    def __init__(self, hidden_channels, num_layers=2):
        super().__init__()
        self.convs = nn.ModuleList([
            SAGEConv((-1, -1), hidden_channels)
            for _ in range(num_layers)
        ])
        self.dropout = nn.Dropout(0.3)

    def forward(self, x, edge_index):
        # apply GraphSAGE layers with dropout between hidden layers
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index).relu()
            if i < len(self.convs) - 1:
                x = self.dropout(x)
        return x


class LinkPredictor(nn.Module):
    # full link prediction model:
    # - projects user features
    # - encodes game numeric/categorical features
    # - applies heterogeneous GraphSAGE
    # - scores user-game pairs with an MLP decoder
    def __init__(self, hidden_channels, metadata, num_layers,
                 user_in_dim, game_numeric_dim,
                 cat_vocab_sizes, cat_embed_cols, max_lens, cat_emb_dims):
        super().__init__()
        self.cat_embed_cols = cat_embed_cols

        # project user features to hidden dimension
        self.user_proj = nn.Linear(user_in_dim, hidden_channels)

        # encode game numeric and categorical features
        self.game_encoder = GameFeatureEncoder(
            numeric_dim    = game_numeric_dim,
            vocab_sizes    = cat_vocab_sizes,
            max_lens       = max_lens,
            cat_embed_cols = cat_embed_cols,
            cat_emb_dims   = cat_emb_dims,
            hidden_dim     = hidden_channels,
        )

        # convert homogeneous GraphSAGE definition into heterogeneous graph model
        self.gnn = to_hetero(
            GraphSAGENet(hidden_channels, num_layers=num_layers),
            metadata, aggr='sum'
        )

        # decode final user-game score from concatenated node embeddings
        self.decoder = nn.Sequential(
            nn.Linear(hidden_channels * 2, hidden_channels),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_channels, 1)
        )

    def _get_cats(self, batch_or_data):
        # collect categorical game tensors stored in the batch/data object
        cats = {}
        for col in self.cat_embed_cols:
            key = f"{col}_idx"
            if hasattr(batch_or_data["game"], key):
                cats[col] = getattr(batch_or_data["game"], key)
        return cats

    def _encode(self, x_dict, batch_or_data):
        # encode raw user and game features before graph propagation
        user_x = self.user_proj(x_dict["user"]).relu()
        cats   = self._get_cats(batch_or_data)
        game_x = self.game_encoder(x_dict["game"], cats)
        return {"user": user_x, "game": game_x}

    def forward_batch(self, batch):
        # score user-game edges from a mini-batch
        etype  = ("user", "plays", "game")
        x_dict = self._encode(batch.x_dict, batch)
        x_dict = self.gnn(x_dict, batch.edge_index_dict)
        u_emb  = x_dict["user"][batch[etype].edge_label_index[0]]
        g_emb  = x_dict["game"][batch[etype].edge_label_index[1]]
        return self.decoder(torch.cat([u_emb, g_emb], dim=-1)).squeeze(-1)

    def forward_full(self, data):
        # compute full-graph user and game embeddings
        x_dict = self._encode(data.x_dict, data)
        return self.gnn(x_dict, data.edge_index_dict)


# ---------------------------
#         BPR loss 
# ---------------------------
def bpr_loss(scores, n_neg=N_NEG):
    # compute Bayesian Personalized Ranking loss:
    # - first score in each group is positive
    # - remaining scores are negatives
    # - optimize positive score to be higher than negative scores
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
#        Val loader
# ---------------------------
# validation loader uses fixed candidate edges and does not perform additional negative sampling
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
#      hyperparameters
# ---------------------------
HIDDEN_CHANNELS  = 128
NUM_LAYERS       = 2
LR               = 5e-4
NUM_EPOCHS       = 20
N_GROUPS_SAMPLE  = 200_000

print(f"\nConfig: hidden={HIDDEN_CHANNELS}, layers={NUM_LAYERS}, "
      f"lr={LR}, neighbors=[10,10], epochs={NUM_EPOCHS}")

# ---------------------------
# model + optimizer + scheduler
# ---------------------------
model = LinkPredictor(
    hidden_channels  = HIDDEN_CHANNELS,
    metadata         = data.metadata(),
    num_layers       = NUM_LAYERS,
    user_in_dim      = user_in_dim,
    game_numeric_dim = game_numeric_dim,
    cat_vocab_sizes  = cat_vocab_sizes,
    cat_embed_cols   = cat_embed_cols,
    max_lens         = max_lens,
    cat_emb_dims     = CAT_EMB_DIMS,
).to(DEVICE)

optimizer = Adam(model.parameters(), lr=LR, weight_decay=1e-5)
# reduce learning rate when validation ROC stops improving
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='max', factor=0.5, patience=3, verbose=True
)

etype            = ("user", "plays", "game")

# store training history and best checkpoint
train_roc_list   = []
val_roc_list     = []
epoch_times      = []
best_val_roc     = -np.inf
best_model_state = None

def fmt_time(s):
    # format seconds as hh:mm:ss
    return time.strftime("%H:%M:%S", time.gmtime(s))

# ---------------------------
#        training loop
# ---------------------------
t_start = time.time()
print("\nStarting training...\n")

for epoch in range(NUM_EPOCHS):
    t_epoch_start = time.time()

    # sample complete BPR groups so that positive-negative structure is preserved
    n_total_groups = grouped_ei.shape[1] // (N_NEG + 1)
    group_idx      = torch.randperm(n_total_groups)[:N_GROUPS_SAMPLE]
    edge_idx       = (group_idx.unsqueeze(1) * (N_NEG + 1) +
                      torch.arange(N_NEG + 1).unsqueeze(0)).flatten()
    sampled_ei     = grouped_ei[:, edge_idx]
    sampled_el     = grouped_el[edge_idx]

    # build epoch loader from sampled training groups
    epoch_loader = LinkNeighborLoader(
        data=data,
        num_neighbors=nn_dict,
        edge_label_index=(etype, sampled_ei),
        edge_label=sampled_el,
        neg_sampling=None,
        batch_size=batch_size,
        shuffle=False,  # CRITICAL — preserve group structure
        num_workers=4,
        persistent_workers=False,
        pin_memory=True,
    )

    # train one epoch using BPR loss
    model.train()
    epoch_loss  = 0.0
    total_edges = 0

    train_bar = tqdm(epoch_loader, desc=f"Train ep{epoch:02d}",
                     unit="batch", leave=False)
    for batch in train_bar:
        batch  = batch.to(DEVICE)
        optimizer.zero_grad()
        scores = model.forward_batch(batch)
        loss   = bpr_loss(scores)
        loss.backward()
        optimizer.step()
        epoch_loss  += loss.item() * scores.size(0)
        total_edges += scores.size(0)
        train_bar.set_postfix(loss=f"{loss.item():.4f}")

    epoch_loss /= max(total_edges, 1)

    # evaluate train and validation ROC
    model.eval()
    with torch.no_grad():
        # approximate train ROC using a few batches
        all_scores, all_labels = [], []
        for i, batch in enumerate(epoch_loader):
            if i >= 5: break
            batch = batch.to(DEVICE)
            all_scores.append(model.forward_batch(batch).cpu())
            all_labels.append(batch[etype].edge_label.cpu())
        train_roc = roc_auc_score(
            torch.cat(all_labels).numpy(),
            torch.cat(all_scores).numpy()
        ) if all_scores else np.nan
        train_roc_list.append(train_roc)

        # compute validation ROC on the full validation loader
        all_scores, all_labels = [], []
        for batch in tqdm(val_loader, desc=f"Val ep{epoch:02d}",
                          unit="batch", leave=False):
            batch = batch.to(DEVICE)
            all_scores.append(model.forward_batch(batch).cpu())
            all_labels.append(batch[etype].edge_label.cpu())
        val_roc = roc_auc_score(
            torch.cat(all_labels).numpy(),
            torch.cat(all_scores).numpy()
        ) if all_scores else np.nan
        val_roc_list.append(val_roc)

    scheduler.step(val_roc)
    
    # keep best model according to validation ROC
    if val_roc > best_val_roc:
        best_val_roc     = val_roc
        best_model_state = {k: v.cpu() for k, v in model.state_dict().items()}
        print(f"  *** New best val ROC: {best_val_roc:.4f} ***")

    t_epoch = time.time() - t_epoch_start
    epoch_times.append(t_epoch)
    eta = (sum(epoch_times) / len(epoch_times)) * (NUM_EPOCHS - (epoch + 1))
    print(
        f"Ep {epoch:02d} | Loss {epoch_loss:.4f} | "
        f"TrainROC {train_roc:.4f} | ValROC {val_roc:.4f} | "
        f"Epoch {t_epoch:.0f}s | ETA {fmt_time(eta)}"
    )

print(f"\nTraining complete in {fmt_time(time.time()-t_start)}")
print(f"Best val ROC: {best_val_roc:.4f}")

# ---------------------------
#          save
# ---------------------------
# save best model state and all metadata required for reloading
torch.save({
    "state_dict":       best_model_state,
    "best_val_roc":     float(best_val_roc),
    "user_in_dim":      user_in_dim,
    "game_numeric_dim": game_numeric_dim,
    "cat_vocab_sizes":  cat_vocab_sizes,
    "cat_embed_cols":   cat_embed_cols,
    "max_lens":         max_lens,
    "cat_emb_dims":     CAT_EMB_DIMS,
    "config": {
        "hidden_channels": HIDDEN_CHANNELS,
        "num_layers":      NUM_LAYERS,
        "lr":              LR,
        "loss":            "bpr",
        "mode":            MODE,
    }
}, MODEL_PATH)
print(f"Saved to: {MODEL_PATH}")

# ---------------------------
#    plot learning curve
# ---------------------------
# plot train and validation ROC-AUC over epochs
epochs_range = range(1, len(train_roc_list) + 1)

plt.figure(figsize=(8, 5))
plt.plot(epochs_range, train_roc_list, marker='o', label="Train ROC-AUC")
plt.plot(epochs_range, val_roc_list,   marker='o', label="Val ROC-AUC")
plt.xlabel("Epoch"); plt.ylabel("ROC-AUC")
plt.title(f"GraphSAGE BPR v2 — {MODE}")
plt.grid(True, alpha=0.3); plt.legend(); plt.tight_layout()
plt.savefig(PLOT_PATH)
plt.close()

# ---------------------------
#      final evaluation
# ---------------------------
# reload best checkpoint before final validation/test evaluation
best_model = LinkPredictor(
    hidden_channels  = HIDDEN_CHANNELS,
    metadata         = data.metadata(),
    num_layers       = NUM_LAYERS,
    user_in_dim      = user_in_dim,
    game_numeric_dim = game_numeric_dim,
    cat_vocab_sizes  = cat_vocab_sizes,
    cat_embed_cols   = cat_embed_cols,
    max_lens         = max_lens,
    cat_emb_dims     = CAT_EMB_DIMS,
).to(DEVICE)
best_model.load_state_dict({k: v.to(DEVICE) for k, v in best_model_state.items()})
best_model.eval()

# compute full graph embeddings once and reuse them for scoring
print("\nRunning full-graph inference...")
with torch.no_grad():
    full_x = best_model.forward_full(data)

user_emb_full = full_x["user"]
game_emb_full = full_x["game"]


def evaluate_ranking_df(df, scores, ks=(1, 5, 10, 20)):
    # evaluate ranking quality per user on scored candidates
    user_items = defaultdict(list)
    for u, y, s in zip(df[USER_COL].values, df[TARGET].values, scores):
        user_items[u].append((float(s), int(y)))

    metrics = {f"HitRate@{k}": 0.0 for k in ks}
    metrics.update({f"Recall@{k}": 0.0 for k in ks})
    metrics.update({f"NDCG@{k}": 0.0 for k in ks})
    metrics["MRR"] = 0.0
    n_users_eval = 0

    for u, items in user_items.items():
        # sort candidate games by descending score
        items.sort(key=lambda x: x[0], reverse=True)
        labels = [y for _, y in items]
        n_pos  = sum(labels)
        if n_pos == 0:
            continue
        n_users_eval += 1

        # reciprocal rank
        for rank, y in enumerate(labels, start=1):
            if y == 1:
                metrics["MRR"] += 1.0 / rank
                break

        # top-k ranking metrics
        for k in ks:
            topk     = labels[:k]
            hits_k   = 1.0 if any(topk) else 0.0
            recall_k = sum(topk) / n_pos
            dcg      = sum(1/math.log2(i+1) for i, y in enumerate(topk, 1) if y==1)
            idcg     = sum(1/math.log2(i+1) for i in range(1, min(n_pos, k)+1))
            metrics[f"HitRate@{k}"] += hits_k
            metrics[f"Recall@{k}"]  += recall_k
            metrics[f"NDCG@{k}"]    += dcg/idcg if idcg > 0 else 0.0

   
    if n_users_eval == 0:
        return {k: 0.0 for k in metrics} | {"n_users_evaluated": 0}
     # aggregate metrics across evaluated users
    for k in metrics:
        if k != "n_users_evaluated":
            metrics[k] /= n_users_eval
    metrics["n_users_evaluated"] = n_users_eval
    return metrics


def evaluate_df(df, name):
    # score valid user-game pairs using learned user and game embeddings
    print(f"Evaluating {name}...")
    user_idx = torch.tensor(
        [user2idx.get(u, -1) for u in df[USER_COL]], dtype=torch.long, device=DEVICE
    )
    game_idx = torch.tensor(
        [game2idx.get(g, -1) for g in df[GAME_COL]], dtype=torch.long, device=DEVICE
    )
    mask = (user_idx >= 0) & (game_idx >= 0)
    if mask.sum().item() == 0:
        print(f"  {name}: no overlapping nodes.")
        return None
    filtered_df = df[mask.cpu().numpy()]
    with torch.no_grad():
        u_emb  = user_emb_full[user_idx[mask]]
        g_emb  = game_emb_full[game_idx[mask]]
        scores = best_model.decoder(
            torch.cat([u_emb, g_emb], dim=-1)
        ).squeeze(-1).cpu().numpy()
    return evaluate_ranking_df(filtered_df, scores, ks=(1, 5, 10, 20))


val_metrics  = evaluate_df(val_filtered_df, "Validation")
test_metrics = evaluate_df(test_df, "Test")
print("Val metrics: ", val_metrics)
print("Test metrics:", test_metrics)


# save final metrics and learning history
metrics_dict = {
    "config": {
        "hidden_channels": HIDDEN_CHANNELS,
        "num_layers":      NUM_LAYERS,
        "lr":              LR,
        "loss":            "bpr",
        "mode":            MODE,
    },
    "best_val_roc":  float(best_val_roc),
    "train_roc":     [float(x) for x in train_roc_list],
    "val_roc":       [float(x) for x in val_roc_list],
    "val_metrics":   val_metrics,
    "test_metrics":  test_metrics,
}
with open(METRICS_PATH, "w") as f:
    json.dump(metrics_dict, f, indent=2)
print(f"Saved metrics to {METRICS_PATH}")