import os
import random
import torch
import pandas as pd
import numpy as np
from collections import defaultdict
 
BASE          = "/home/jaga"
GRAPH_PT      = f"{BASE}/data/cache/graph.pt"
GAME2IDX_PT   = f"{BASE}/data/cache/game2idx.pt"
USER2IDX_PT   = f"{BASE}/data/cache/user2idx.pt"
PER_GAME_FULL = f"{BASE}/results/thesis_analysis/per_game_full.csv"
OUTDIR        = f"{BASE}/results/graph_structure"
os.makedirs(OUTDIR, exist_ok=True)
 
# ── Load graph + mappings ─────────────────────────────────────────────────
print("Loading graph...", flush=True)
graph    = torch.load(GRAPH_PT, map_location="cpu")
game2idx = torch.load(GAME2IDX_PT, map_location="cpu")
user2idx = torch.load(USER2IDX_PT, map_location="cpu")
idx2game = {v: int(k) for k, v in game2idx.items()}
 
# ── Load per-game base table ──────────────────────────────────────────────
game_df  = pd.read_csv(PER_GAME_FULL)
print(f"Loaded per_game_full.csv: {game_df.shape}", flush=True)
 
# ── Extract edges ─────────────────────────────────────────────────────────
plays             = graph[("user", "plays", "game")].edge_index.numpy()
friends           = graph[("user", "friend", "user")].edge_index.numpy()
user_plays, game_plays = plays
n_games           = len(game2idx)
 
# ── Build owner and friend adjacency ─────────────────────────────────────
print("Building adjacency structures...", flush=True)
game_owners = defaultdict(set)
user_games  = defaultdict(set)
for u, g in zip(user_plays, game_plays):
    game_owners[g].add(u)
    user_games[u].add(g)
 
friend_adj = defaultdict(set)
for u, v in zip(friends[0], friends[1]):
    friend_adj[u].add(v)
    friend_adj[v].add(u)
 
# ── Compute metrics ───────────────────────────────────────────────────────
print("Computing graph metrics...", flush=True)
clustering    = {}
second_order  = {}
friend_reach2 = {}
 
random.seed(42)
 
for g in range(n_games):
    owners = game_owners.get(g, set())
 
    # 2nd-order neighborhood size
    nbrs = set()
    for u in owners:
        nbrs.update(user_games[u])
    nbrs.discard(g)
    second_order[g] = len(nbrs)
 
    # Clustering coefficient
    nbr_list = list(nbrs)
    k = len(nbr_list)
    if k < 2:
        clustering[g] = 0.0
    else:
        hits = 0
        if k <= 300:
            for i in range(k):
                for j in range(i + 1, k):
                    if game_owners[nbr_list[i]] & game_owners[nbr_list[j]]:
                        hits += 1
            clustering[g] = hits / (k * (k - 1) / 2)
        else:
            # sample pairs for very high-degree games to keep runtime manageable
            sub   = nbr_list[:100]
            pairs = [(sub[i], sub[j])
                     for i in range(len(sub))
                     for j in range(i + 1, len(sub))]
            n_sample   = min(5000, len(pairs))
            sample_pairs = random.sample(pairs, n_sample) if n_sample < len(pairs) else pairs
            for a, b in sample_pairs:
                if game_owners[a] & game_owners[b]:
                    hits += 1
            clustering[g] = hits / len(sample_pairs)
 
    # 2-hop friend reach
    hop1 = set()
    for u in owners:
        hop1.update(friend_adj[u])
    hop1 -= owners
    hop2 = set()
    for u in hop1:
        hop2.update(friend_adj[u])
    hop2 -= owners
    hop2 -= hop1
    friend_reach2[g] = len(hop1) + len(hop2)
 
    if g % 2000 == 0:
        print(f"  {g:,} / {n_games:,} games processed...", flush=True)
 
# ── Assemble and save ─────────────────────────────────────────────────────
print("Saving output...", flush=True)
struct_df = pd.DataFrame([
    {
        "appid"             : idx2game[g],
        "clustering_coeff"  : clustering[g],
        "second_order_size" : second_order[g],
        "friend_reach_2hop" : friend_reach2[g],
    }
    for g in range(n_games)
])
 
full_df = game_df.merge(struct_df, on="appid", how="left")
full_df.to_csv(f"{OUTDIR}/per_game_with_structure.csv", index=False)
print(f"Saved: {OUTDIR}/per_game_with_structure.csv  (shape: {full_df.shape})", flush=True)