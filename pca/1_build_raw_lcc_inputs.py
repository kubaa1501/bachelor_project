import pickle
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

# paths 
DATA_DIR = Path("/home/anci/new/data")
OUT_DIR = Path("/home/anci/node_distance/data_for_micheles_algorithm/michele_safe")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# inputs
FRIENDS_CSV = DATA_DIR / "friends.csv"
USER_GAMES_CSV = DATA_DIR / "user_games.csv"

# outputs 
GRAPH_OUT = OUT_DIR / "user_edge_graph_steamid_LCC31021.pkl"
MATRIX_OUT = OUT_DIR / "user_game_01_steam_users_appid_games.pkl"
OLD_TO_NEW_OUT = OUT_DIR / "old_to_new_node_id.csv"

LCC_USERS_OUT = OUT_DIR / "lcc_steamids_31021.csv"


def save_pickle(obj, path):
    # save object aspickle using highest protocol 
    with open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def main():
    # load friendship edges
    # each row is one user-user friendship relation
    print("Loading friends:", FRIENDS_CSV)
    friends = pd.read_csv(FRIENDS_CSV, dtype=str)

    # expected columns in friends.csv
    required = {"user_steamid", "friend_steamid"}
    if not required.issubset(friends.columns):
        raise ValueError(f"friends.csv columns wrong. Have: {friends.columns.tolist()}")

    # keep only the two needed columns and normalize ids as strings
    friends = friends[["user_steamid", "friend_steamid"]].dropna()
    friends["user_steamid"] = friends["user_steamid"].astype(str)
    friends["friend_steamid"] = friends["friend_steamid"].astype(str)

    # build full user-user graph from Steam friendships
    # nodes = steam ids
    # edges = friendship links
    print("Building full user-user graph...")
    G = nx.Graph()
    G.add_edges_from(
        zip(friends["user_steamid"], friends["friend_steamid"])
    )

    print("Full graph:")
    print("  nodes:", G.number_of_nodes())
    print("  edges:", G.number_of_edges())

    # keep only the largest connected component
    # this is the user set used later in the algorithm
    print("Extracting largest connected component...")
    lcc_nodes = max(nx.connected_components(G), key=len)
    lcc_nodes = sorted(str(x) for x in lcc_nodes)

    # graph restricted to users in the LCC
    G_lcc = G.subgraph(lcc_nodes).copy()

    print("LCC graph:")
    print("  nodes:", G_lcc.number_of_nodes())
    print("  edges:", G_lcc.number_of_edges())

    # save LCC friendship graph with steam ids as node labels
    save_pickle(G_lcc, GRAPH_OUT)
    print("Saved graph:", GRAPH_OUT)

    # create deterministic old->new mapping
    old_to_new = pd.DataFrame({
        "old_node_id": np.arange(len(lcc_nodes), dtype=np.int64),
        "new_node_id": np.arange(len(lcc_nodes), dtype=np.int64),
    })
    old_to_new.to_csv(OLD_TO_NEW_OUT, index=False)
    print("Saved mapping:", OLD_TO_NEW_OUT)

    # save the exact user set used in the LCC
    pd.DataFrame({"steam_id": lcc_nodes}).to_csv(LCC_USERS_OUT, index=False)
    print("Saved LCC steam ids:", LCC_USERS_OUT)

    # load user-game ownership/playtime data
    # only steamid and appid are needed here
    print("Loading user_games:", USER_GAMES_CSV)
    ug = pd.read_csv(
        USER_GAMES_CSV,
        usecols=["steamid", "appid"],
        dtype={"steamid": str, "appid": np.int64},
    ).dropna()

    ug["steamid"] = ug["steamid"].astype(str)
    ug["appid"] = ug["appid"].astype(np.int64)

    # keep only user-game rows where the user belongs to the LCC
    print("Filtering user_games to LCC users...")
    lcc_set = set(lcc_nodes)
    ug = ug[ug["steamid"].isin(lcc_set)].drop_duplicates(["steamid", "appid"])

    print("Filtered user-game pairs:", len(ug))

    # deterministic game order
    game_ids = sorted(ug["appid"].unique().tolist())
    print("Number of games:", len(game_ids))

    # maps used only to build the dense matrix
    user_to_row = {sid: i for i, sid in enumerate(lcc_nodes)}
    game_to_col = {appid: j for j, appid in enumerate(game_ids)}

    # build binary user-game matrix
    # rows = steam ids from LCC
    # columns = app ids
    # value = 1 if user owns/has the game, else 0
    print("Building dense 0/1 user-game matrix...")
    X = np.zeros((len(lcc_nodes), len(game_ids)), dtype=np.uint8)

    rows = ug["steamid"].map(user_to_row).to_numpy()
    cols = ug["appid"].map(game_to_col).to_numpy()

    # keep only successfully mapped pairs
    ok = pd.notna(rows) & pd.notna(cols)
    rows = rows[ok].astype(np.int64)
    cols = cols[ok].astype(np.int64)
    # set observed user-game pairs to 1
    X[rows, cols] = 1

    # convert matrix to DataFrame because the next pipeline step expects pandas
    df = pd.DataFrame(X, index=lcc_nodes, columns=game_ids)
    df.index = df.index.astype(str)
    df.columns = df.columns.astype(int)

    print("Matrix shape:", df.shape)
    print("Matrix index head:", list(df.index[:5]))
    print("Matrix columns head:", list(df.columns[:5]))

    # save final raw LCC user-game matrix
    save_pickle(df, MATRIX_OUT)
    print("Saved matrix:", MATRIX_OUT)

    print("DONE")


if __name__ == "__main__":
    main()