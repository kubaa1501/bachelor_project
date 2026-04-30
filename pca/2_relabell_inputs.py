import pickle
from pathlib import Path

import networkx as nx
import pandas as pd

BASE = Path("/home/anci/node_distance/data_for_micheles_algorithm/michele_safe")

GRAPH_IN = BASE / "user_edge_graph_steamid_LCC31021.pkl"
MATRIX_IN = BASE / "user_game_01_steam_users_appid_games.pkl"
OLD_NODE_MAP_IN = BASE / "old_to_new_node_id.csv"

GRAPH_OUT = BASE / "user_edge_graph_relabelled.pkl"
MATRIX_OUT = BASE / "user_game_01_relabelled.pkl"
STEAM_MAP_OUT = BASE / "steamid_to_newnodeid_LCC31021.csv"
GAME_MAP_OUT = BASE / "game_index_to_gameid_20988.csv"

with open(GRAPH_IN, "rb") as f:
    G = pickle.load(f)

with open(MATRIX_IN, "rb") as f:
    df = pickle.load(f)

# normalize ids
df.index = df.index.astype(str)
df.columns = df.columns.astype(int)

# preserve original order from the user-game matrix
steam_ids = list(df.index)
game_ids = list(df.columns)

# create user mapping: steam_id -> new_node_id
steamid_to_new = {sid: i for i, sid in enumerate(steam_ids)}

# relabel graph nodes from steam_id to new_node_id
G_rel = nx.relabel_nodes(G, steamid_to_new, copy=True)

# relabel only matrix rows; columns stay as appid
df_rel = df.copy()
df_rel.index = range(len(steam_ids))

# save relabelled graph
with open(GRAPH_OUT, "wb") as f:
    pickle.dump(G_rel, f, protocol=pickle.HIGHEST_PROTOCOL)

# save relabelled user-game matrix
with open(MATRIX_OUT, "wb") as f:
    pickle.dump(df_rel, f, protocol=pickle.HIGHEST_PROTOCOL)

# rebuild steam_id mapping using original old_node_id values
old_map = pd.read_csv(OLD_NODE_MAP_IN)

steam_map = pd.DataFrame({
    "steam_id": steam_ids,
    "new_node_id": range(len(steam_ids)),
})

steam_map = steam_map.merge(
    old_map,
    on="new_node_id",
    how="left",
)

steam_map = steam_map[["steam_id", "old_node_id", "new_node_id"]]
steam_map.to_csv(STEAM_MAP_OUT, index=False)

# save game index mapping
pd.DataFrame({
    "matrix_index": range(len(game_ids)),
    "game_id": game_ids,
}).to_csv(GAME_MAP_OUT, index=False)

print("saved:")
print(GRAPH_OUT)
print(MATRIX_OUT)
print(STEAM_MAP_OUT)
print(GAME_MAP_OUT)

print("graph:", G_rel.number_of_nodes(), G_rel.number_of_edges())
print("matrix:", df_rel.shape)
print("matrix columns head:", list(df_rel.columns[:5]))