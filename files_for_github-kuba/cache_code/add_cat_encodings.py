"""
Adds integer-encoded categorical features to existing caches.
Does NOT rebuild the graph or edge tensors.
"""
import os
import json
import time
import numpy as np
import pandas as pd
import torch

CAT_EMBED_COLS = ["genres", "developer", "publisher", "platforms"]
CAT_SEPARATOR  = ";"
MAX_LENS = {
    "genres":    13,
    "developer": 16,
    "publisher": 6,
    "platforms": 3,
}

CONFIGS = {
    "with_net": {
        "train":    "/home/jaga/data/sets/with_net_feat/train.csv",
        "cache":    "/home/jaga/data/cache",
        "numeric_game": [
            "game_total_playtime_minutes", "user_count", "release_date"
        ] + [f"game_emb_{i}" for i in range(32)],
        "numeric_user": [
            "total_games_owned", "total_playtime_minutes",
            "median_playtime_minutes", "unique_genres_played", "friend_count",
            "user_playtime_group_Action", "user_playtime_group_Adventure",
            "user_playtime_group_RPG", "user_playtime_group_Casual",
            "user_playtime_group_Indie", "user_playtime_group_Racing",
            "user_playtime_group_Simulation", "user_playtime_group_Strategy",
            "user_playtime_group_Sports", "user_playtime_group_Violent",
            "user_playtime_group_Adult", "user_playtime_group_Non-gameplay_Tools",
            "user_playtime_group_Other"
        ],
    },
    "no_net": {
        "train":    "/home/jaga/data/sets/without_net_feat/train.csv",
        "cache":    "/home/jaga/data/cache_no_net",
        "numeric_game": [
            "game_total_playtime_minutes", "user_count", "release_date"
        ],
        "numeric_user": [
            "total_games_owned", "total_playtime_minutes",
            "median_playtime_minutes", "unique_genres_played",
            "user_playtime_group_Action", "user_playtime_group_Adventure",
            "user_playtime_group_RPG", "user_playtime_group_Casual",
            "user_playtime_group_Indie", "user_playtime_group_Racing",
            "user_playtime_group_Simulation", "user_playtime_group_Strategy",
            "user_playtime_group_Sports", "user_playtime_group_Violent",
            "user_playtime_group_Adult", "user_playtime_group_Non-gameplay_Tools",
            "user_playtime_group_Other"
        ],
    },
}


def build_vocab(series):
    all_values = set()
    for val in series.dropna():
        for v in str(val).split(CAT_SEPARATOR):
            v = v.strip()
            if v:
                all_values.add(v)
    vocab = {"<PAD>": 0, "<UNK>": 1}
    for i, v in enumerate(sorted(all_values), start=2):
        vocab[v] = i
    return vocab


def encode_multihot(series, vocab, max_len):
    result = np.zeros((len(series), max_len), dtype=np.int64)
    for i, val in enumerate(series):
        if pd.isna(val):
            continue
        tokens = [v.strip() for v in str(val).split(CAT_SEPARATOR) if v.strip()]
        for j, token in enumerate(tokens[:max_len]):
            result[i, j] = vocab.get(token, vocab["<UNK>"])
    return result


t_total = time.time()

for config_name, cfg in CONFIGS.items():
    print(f"\n{'='*50}")
    print(f"Adding categorical encodings: {config_name}")
    print(f"Cache dir: {cfg['cache']}")
    t0 = time.time()

    # Load only the columns we need
    print("Reading train CSV (game columns only)...")
    t1 = time.time()
    train_df = pd.read_csv(
        cfg["train"], sep=";", low_memory=False,
        usecols=["appid"] + CAT_EMBED_COLS
    )
    print(f"  done in {time.time()-t1:.1f}s, shape={train_df.shape}")

    # Get unique games
    game_features_df = train_df.drop_duplicates("appid").set_index("appid")
    print(f"  unique games: {len(game_features_df)}")

    # Load existing graph to get game ordering
    print("Loading existing graph to get game order...")
    game2idx = torch.load(f"{cfg['cache']}/game2idx.pt", weights_only=False)
    print(f"  {len(game2idx)} games in cache")

    # Reindex game_features_df to match game2idx order
    idx2game = {v: k for k, v in game2idx.items()}
    ordered_games = [idx2game[i] for i in range(len(game2idx))]
    game_features_ordered = game_features_df.reindex(ordered_games)

    # Build vocabularies
    print("\nBuilding vocabularies...")
    vocabs = {}
    for col in CAT_EMBED_COLS:
        if col not in game_features_ordered.columns:
            print(f"  {col}: NOT FOUND")
            continue
        vocab = build_vocab(game_features_ordered[col])
        vocabs[col] = vocab
        print(f"  {col}: {len(vocab)} tokens")

    # Encode and save each categorical
    print("\nEncoding and saving...")
    for col in CAT_EMBED_COLS:
        if col not in vocabs:
            continue
        t1 = time.time()
        encoded = encode_multihot(
            game_features_ordered[col], vocabs[col], MAX_LENS[col]
        )
        torch.save(
            torch.tensor(encoded, dtype=torch.long),
            f"{cfg['cache']}/game_{col}_idx.pt"
        )
        print(f"  {col}: {encoded.shape} saved in {time.time()-t1:.1f}s")

    # Load existing graph and add categorical indices to it
    print("\nUpdating graph.pt with categorical indices...")
    data = torch.load(f"{cfg['cache']}/graph.pt", weights_only=False)
    for col in CAT_EMBED_COLS:
        if col not in vocabs:
            continue
        encoded = torch.load(
            f"{cfg['cache']}/game_{col}_idx.pt", weights_only=False
        )
        setattr(data["game"], f"{col}_idx", encoded)
    torch.save(data, f"{cfg['cache']}/graph.pt")
    print("  graph.pt updated")

    # Save vocabularies
    with open(f"{cfg['cache']}/cat_vocabs.json", "w") as f:
        json.dump(vocabs, f)
    print("  cat_vocabs.json saved")

    # Save metadata
    # Load existing graph to get dims
    user_in_dim      = data["user"].x.size(1)
    game_numeric_dim = data["game"].x.size(1)

    meta = {
        "user_in_dim":      user_in_dim,
        "game_numeric_dim": game_numeric_dim,
        "cat_embed_cols":   CAT_EMBED_COLS,
        "max_lens":         MAX_LENS,
        "cat_vocab_sizes":  {col: len(v) for col, v in vocabs.items()},
        "numeric_user":     cfg["numeric_user"],
        "numeric_game":     cfg["numeric_game"],
    }
    with open(f"{cfg['cache']}/meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("  meta.json saved")

    print(f"\nDone {config_name} in {time.time()-t0:.1f}s")

print(f"\nAll done in {time.time()-t_total:.1f}s")
