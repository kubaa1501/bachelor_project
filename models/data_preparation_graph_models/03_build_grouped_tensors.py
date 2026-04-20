"""
Builds and caches grouped edge tensors (pos, neg*10 structure)
for use with softmax loss. Only needs to run once.
Saves to both cache dirs since tensors are identical for both.
"""
import time
import torch
import pandas as pd

# identifier and target columns
USER_COL = "steamid"
GAME_COL = "appid"
TARGET   = "owned"

# both cache variants use the same grouped interaction tensors
cache_dirs = [
    "/home/jaga/data/cache",
    "/home/jaga/data/cache_no_net",
]

# load index mappings from one cache
# user2idx and game2idx are assumed to be identical across both variants
user2idx = torch.load("/home/jaga/data/cache/user2idx.pt", weights_only=False)
game2idx = torch.load("/home/jaga/data/cache/game2idx.pt", weights_only=False)

# load raw training data
print("Reading train CSV...")
t0 = time.time()
train_df = pd.read_csv(
    "/home/jaga/data/sets/with_net_feat/train.csv",
    sep=";", low_memory=False
)
print(f"  done in {time.time()-t0:.1f}s, shape={train_df.shape}")

# filter to interactions whose users and games exist in the cache mappings
# then convert identifiers to index tensors
print("Filtering and building grouped tensors...")
t1 = time.time()
mask = (
    train_df[USER_COL].isin(user2idx) &
    train_df[GAME_COL].isin(game2idx)
)
train_df = train_df[mask].reset_index(drop=True)

train_user_idx = torch.tensor(
    [user2idx[u] for u in train_df[USER_COL]], dtype=torch.long
)
train_game_idx = torch.tensor(
    [game2idx[g] for g in train_df[GAME_COL]], dtype=torch.long
)
train_edge_label       = torch.tensor(train_df[TARGET].values, dtype=torch.float)
train_edge_label_index = torch.stack([train_user_idx, train_game_idx], dim=0)

print(f"  done in {time.time()-t1:.1f}s")
print(f"  edges: {train_edge_label_index.shape[1]}")
print(f"  pos: {int(train_edge_label.sum())}, neg: {int((train_edge_label==0).sum())}")
print(f"  first 22 labels: {train_edge_label[:22].int().tolist()}")
print(f"  (should be: 1,0,0,0,0,0,0,0,0,0,0 repeating)")

# verify that the grouped training structure is correct:
# each group should contain:
# - 1 positive interaction
# - followed by 10 negative interactions
assert train_edge_label[0] == 1, "First label should be positive!"
assert all(train_edge_label[1:11] == 0), "Labels 1-10 should be negative!"
print("  Group structure verified OK")

# save grouped tensors to both cache directories
# these tensors are shared by the with_net and no_net variants
print("\nSaving to both cache dirs...")
for cache_dir in cache_dirs:
    torch.save(train_edge_label_index, f"{cache_dir}/grouped_train_edge_label_index.pt")
    torch.save(train_edge_label,       f"{cache_dir}/grouped_train_edge_label.pt")
    print(f"  saved to {cache_dir}")

print(f"\nAll done! Total time: {time.time()-t0:.1f}s")
