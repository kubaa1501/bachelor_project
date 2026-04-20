import os
import time
import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from torch_geometric.data import HeteroData

# identifier and target columns
USER_COL = "steamid"
GAME_COL = "appid"
TARGET   = "owned"

# numeric user features for the baseline version
USER_NUMERIC_FEATURES = [
    "total_games_owned", "total_playtime_minutes", "median_playtime_minutes",
    "unique_genres_played",
    # "friend_count" <-- NOT IN BASELINE
    "user_playtime_group_Action", "user_playtime_group_Adventure", "user_playtime_group_RPG",
    "user_playtime_group_Casual", "user_playtime_group_Indie", "user_playtime_group_Racing",
    "user_playtime_group_Simulation", "user_playtime_group_Strategy", "user_playtime_group_Sports",
    "user_playtime_group_Violent", "user_playtime_group_Adult",
    "user_playtime_group_Non-gameplay_Tools", "user_playtime_group_Other"
]
# categorical user features
USER_CATEGORICAL_FEATURES = ["country"]

# numeric game features for the baseline version
GAME_NUMERIC_FEATURES = [
    "game_total_playtime_minutes", "user_count", "release_date"
    # game_emb_* <-- NOT IN BASELINE
]
# categorical game features
GAME_CATEGORICAL_FEATURES = ["genres", "developer", "publisher", "platforms"]

#input files (baseline dataset)
files = {
    "train": "/home/jaga/data/sets/without_net_feat/train.csv",
    "val":   "/home/jaga/data/sets/without_net_feat/val.csv",
    "test":  "/home/jaga/data/sets/without_net_feat/test.csv",
}
# input friendship .csv to build graph 
friends_path = "/home/jaga/data/data_final/friends.csv"

# output cache directory 
cache_dir    = "/home/jaga/data/cache_no_net"
os.makedirs(cache_dir, exist_ok=True)

def preprocess_features(df, numeric_features, categorical_features):
    # preprocess numeric and categorical features into one dense tensor
    # numeric:
    # - median imputation
    # - standard scaling
    # categorical:
    # - fill missing values with "MISSING"
    # - one-hot encode categories
    
    X_num = None
    if numeric_features:
        num_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler",  StandardScaler())
        ])
        X_num = num_pipe.fit_transform(df[numeric_features])
    X_cat = None
    if categorical_features:
        cat_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="MISSING")),
            ("ohe",     OneHotEncoder(handle_unknown="ignore"))
        ])
        X_cat = cat_pipe.fit_transform(df[categorical_features]).toarray()
    if X_num is not None and X_cat is not None:
        X = np.hstack([X_num, X_cat])
    elif X_num is not None:
        X = X_num
    else:
        X = X_cat
    return torch.tensor(X, dtype=torch.float)

t0 = time.time()
# load raw csv files
print("Loading CSVs...")
t1 = time.time(); train_df   = pd.read_csv(files["train"], sep=";", low_memory=False); print(f"  train.csv:   {time.time()-t1:.1f}s, shape={train_df.shape}")
t1 = time.time(); val_df     = pd.read_csv(files["val"],   sep=";", low_memory=False); print(f"  val.csv:     {time.time()-t1:.1f}s, shape={val_df.shape}")
t1 = time.time(); test_df    = pd.read_csv(files["test"],  sep=";", low_memory=False); print(f"  test.csv:    {time.time()-t1:.1f}s, shape={test_df.shape}")
t1 = time.time(); friends_df = pd.read_csv(friends_path);                              print(f"  friends.csv: {time.time()-t1:.1f}s, shape={friends_df.shape}")

# build heterogeneous graph object
print("\nBuilding graph...")
data     = HeteroData()

# create user and game index mappings from training data
users    = train_df[USER_COL].unique()
games    = train_df[GAME_COL].unique()
user2idx = {u: i for i, u in enumerate(users)}
game2idx = {g: i for i, g in enumerate(games)}
print(f"  {len(users)} users, {len(games)} games")

# process and store user node features
t1 = time.time()
user_features    = train_df.drop_duplicates(USER_COL).set_index(USER_COL)
data["user"].x   = preprocess_features(user_features, USER_NUMERIC_FEATURES, USER_CATEGORICAL_FEATURES)
print(f"  user features: {data['user'].x.shape} in {time.time()-t1:.1f}s")

# preprocess and store game node features
t1 = time.time()
game_features    = train_df.drop_duplicates(GAME_COL).set_index(GAME_COL)
data["game"].x   = preprocess_features(game_features, GAME_NUMERIC_FEATURES, GAME_CATEGORICAL_FEATURES)
print(f"  game features: {data['game'].x.shape} in {time.time()-t1:.1f}s")

# build user-game interaction edges from positive training interactions only
t1 = time.time()
pos_df = train_df[train_df[TARGET] == 1]
src    = np.array([user2idx[u] for u in pos_df[USER_COL]])
dst    = np.array([game2idx[g] for g in pos_df[GAME_COL]])
data["user", "plays", "game"].edge_index     = torch.tensor(np.stack([src, dst]), dtype=torch.long)
data["game", "rev_plays", "user"].edge_index = torch.tensor(np.stack([dst, src]), dtype=torch.long)
print(f"  user-game edges: {src.shape[0]} in {time.time()-t1:.1f}s")

# add friendship edges between users
# note:
# the no-network version removes network-derived numeric features,
# but still keeps the friendship graph structure
t1 = time.time()
valid_friends = friends_df[
    friends_df["user_steamid"].isin(user2idx) &
    friends_df["friend_steamid"].isin(user2idx)
]
if len(valid_friends) > 0:
    u_src  = valid_friends["user_steamid"].map(user2idx).to_numpy()
    u_dst  = valid_friends["friend_steamid"].map(user2idx).to_numpy()
    edges  = np.concatenate([np.stack([u_src, u_dst]), np.stack([u_dst, u_src])], axis=1)
    data["user", "friend", "user"].edge_index = torch.tensor(edges, dtype=torch.long)
    print(f"  friend edges: {edges.shape[1]} in {time.time()-t1:.1f}s")
else:
    print("  no friend edges found")

# build train and validation edge label tensors
print("\nBuilding edge label tensors...")
# train edge labels contain both positives and negatives
t1           = time.time()
train_pos_df = train_df[train_df[TARGET] == 1]
train_neg_df = train_df[train_df[TARGET] == 0]

train_edge_label_index = torch.cat([
    torch.stack([
        torch.tensor([user2idx[u] for u in train_pos_df[USER_COL]], dtype=torch.long),
        torch.tensor([game2idx[g] for g in train_pos_df[GAME_COL]], dtype=torch.long)
    ], dim=0),
    torch.stack([
        torch.tensor([user2idx[u] for u in train_neg_df[USER_COL]], dtype=torch.long),
        torch.tensor([game2idx[g] for g in train_neg_df[GAME_COL]], dtype=torch.long)
    ], dim=0)
], dim=1)
train_edge_label = torch.cat([
    torch.ones(len(train_pos_df)),
    torch.zeros(len(train_neg_df))
])
print(f"  train edges: {train_edge_label_index.shape[1]} in {time.time()-t1:.1f}s")

# validation edges are filtered to pairs whose users and games exist in the train mapping
t1                = time.time()
val_user_idx_full = torch.tensor([user2idx.get(u, -1) for u in val_df[USER_COL]], dtype=torch.long)
val_game_idx_full = torch.tensor([game2idx.get(g, -1) for g in val_df[GAME_COL]], dtype=torch.long)
val_mask          = (val_user_idx_full >= 0) & (val_game_idx_full >= 0)
val_filtered_df   = val_df[val_mask.numpy()].reset_index(drop=True)
val_edge_label_index = torch.stack([val_user_idx_full[val_mask], val_game_idx_full[val_mask]], dim=0)
val_edge_label       = torch.tensor(val_filtered_df[TARGET].values, dtype=torch.float)
print(f"  val edges: {val_edge_label_index.shape[1]} in {time.time()-t1:.1f}s")


# save cached graph objects, mappings, edge labels, and evaluation dataframes
print("\nSaving cache...")
torch.save(data,                   f"{cache_dir}/graph.pt")
torch.save(user2idx,               f"{cache_dir}/user2idx.pt")
torch.save(game2idx,               f"{cache_dir}/game2idx.pt")
torch.save(train_edge_label_index, f"{cache_dir}/train_edge_label_index.pt")
torch.save(train_edge_label,       f"{cache_dir}/train_edge_label.pt")
torch.save(val_edge_label_index,   f"{cache_dir}/val_edge_label_index.pt")
torch.save(val_edge_label,         f"{cache_dir}/val_edge_label.pt")
val_filtered_df.to_parquet(f"{cache_dir}/val_filtered_df.parquet")
test_df.to_parquet(f"{cache_dir}/test_df.parquet")

print(f"\nAll done! Total time: {time.time()-t0:.1f}s")
print(f"Cache saved to: {cache_dir}")
