import pandas as pd
import networkx as nx
from pathlib import Path

# ==============================
# PATHS
# ==============================
data_path = Path(
    r"C:\Users\jkgas\OneDrive\Desktop\data_science\Spring_2026\bachelor_project\data"
)

checkpoint_path = data_path / "checkpoint"

users_path = checkpoint_path / "users.csv"
friends_path = checkpoint_path / "friends.csv"
user_games_path = checkpoint_path / "user_games.csv"
games_path = data_path / "enriched_games.csv"

final_data_path = data_path / "final_data"
final_data_path.mkdir(parents=True, exist_ok=True)

# ==============================
# LOAD
# ==============================
users = pd.read_csv(users_path)
friends = pd.read_csv(friends_path)
user_games = pd.read_csv(user_games_path)
games = pd.read_csv(games_path)

# ==============================
# CLEAN TYPES
# ==============================
users["steamid"] = users["steamid"].astype(str)
friends["user_steamid"] = friends["user_steamid"].astype(str)
friends["friend_steamid"] = friends["friend_steamid"].astype(str)
user_games["steamid"] = user_games["steamid"].astype(str)

user_games["appid"] = pd.to_numeric(user_games["appid"], errors="coerce")
games["appid"] = pd.to_numeric(games["appid"], errors="coerce")

user_games = user_games.dropna(subset=["appid"])
games = games.dropna(subset=["appid"])

user_games["appid"] = user_games["appid"].astype(int)
games["appid"] = games["appid"].astype(int)

# ==============================
# KEEP FRIEND EDGES BETWEEN KNOWN USERS
# ==============================
valid_users = set(users["steamid"])

friends = friends[
    friends["user_steamid"].isin(valid_users)
    & friends["friend_steamid"].isin(valid_users)
].copy()

friends = friends[friends["user_steamid"] != friends["friend_steamid"]].copy()

# Convert directed friendship rows to undirected edges
friends["source"] = friends[["user_steamid", "friend_steamid"]].min(axis=1)
friends["target"] = friends[["user_steamid", "friend_steamid"]].max(axis=1)

edges = friends[["source", "target"]].drop_duplicates().copy()

# ==============================
# BUILD GRAPH + FIND LCC
# ==============================
G = nx.Graph()
G.add_edges_from(edges[["source", "target"]].itertuples(index=False, name=None))

if G.number_of_nodes() == 0:
    raise ValueError("Graph is empty. Check checkpoint/friends.csv.")

lcc_users = set(max(nx.connected_components(G), key=len))

print("Users in users.csv:", len(users))
print("Users in graph:", G.number_of_nodes())
print("Users in LCC:", len(lcc_users))

# ==============================
# FILTER USERS
# ==============================
users_lcc = users[users["steamid"].isin(lcc_users)].copy()

# ==============================
# FILTER EDGES TO LCC
# ==============================
edges_lcc = edges[
    edges["source"].isin(lcc_users)
    & edges["target"].isin(lcc_users)
].copy()

# ==============================
# FILTER USER_GAMES TO LCC USERS
# ==============================
user_games_lcc = user_games[user_games["steamid"].isin(lcc_users)].copy()

user_games_lcc = user_games_lcc.drop_duplicates(
    subset=["steamid", "appid"]
).copy()

# ==============================
# FILTER GAMES TO GAMES OWNED BY LCC USERS
# ==============================
valid_appids = set(user_games_lcc["appid"])

games_lcc = games[games["appid"].isin(valid_appids)].copy()

# Recompute user_count from LCC only
game_user_counts_lcc = (
    user_games_lcc.groupby("appid")["steamid"]
    .nunique()
    .rename("user_count")
    .reset_index()
)

games_lcc = games_lcc.drop(columns=["user_count"], errors="ignore")

games_lcc = games_lcc.merge(
    game_user_counts_lcc,
    on="appid",
    how="left"
)

valid_final_appids = set(games_lcc["appid"])
user_games_lcc = user_games_lcc[
    user_games_lcc["appid"].isin(valid_final_appids)
].copy()

# ==============================
# SAVE OUTPUTS FOR creating_baseline.py
# ==============================
users_lcc.to_csv(final_data_path / "users.csv", index=False)
user_games_lcc.to_csv(final_data_path / "user_games.csv", index=False)
games_lcc.to_csv(final_data_path / "games.csv", index=False)

# Extra output for network / graph work
edges_lcc.to_csv(final_data_path / "edges.csv", index=False)

# ==============================
# SUMMARY
# ==============================
print("\n===== LCC FILTERING SUMMARY =====")
print(f"Users before:        {len(users)}")
print(f"Users after LCC:     {len(users_lcc)}")

print(f"Edges before:        {len(edges)}")
print(f"Edges after LCC:     {len(edges_lcc)}")

print(f"User-games before:   {len(user_games)}")
print(f"User-games after:    {len(user_games_lcc)}")

print(f"Games before:        {len(games)}")
print(f"Games after LCC:     {len(games_lcc)}")

print("\nSaved:")
print(final_data_path / "users.csv")
print(final_data_path / "user_games.csv")
print(final_data_path / "games.csv")
print(final_data_path / "edges.csv")
