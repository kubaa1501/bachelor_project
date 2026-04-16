import pandas as pd
import numpy as np
from pathlib import Path
import time
import csv

# Paths 
BASE = Path("/home/anci/new")

user_games_path = BASE / "user_games.csv"
users_path      = BASE / "users.csv"
baseline_path   = BASE / "baseline_dataset.csv"

val_pairs_path  = BASE / "validation_user_game_pairs.csv"
test_pairs_path = BASE / "test_user_game_pairs.csv"

output_path     = BASE / "baseline_features_playtime_capped_owned_semicolon.csv"

# Read 
read_opts = dict(sep=",", low_memory=False)  # input files are comma-separated
DT_ID = {"steamid": "string", "appid": "Int64"}

print("Loading datasets...")
user_games  = pd.read_csv(user_games_path, dtype=DT_ID, **read_opts)
users       = pd.read_csv(users_path, dtype={"steamid": "string"}, **read_opts)
baseline_df = pd.read_csv(baseline_path, dtype=DT_ID, **read_opts)
val_pairs   = pd.read_csv(val_pairs_path, dtype=DT_ID, **read_opts)
test_pairs  = pd.read_csv(test_pairs_path, dtype=DT_ID, **read_opts)


# Check : baseline must have 15 columns 
assert baseline_df.shape[1] == 15, f"baseline has {baseline_df.shape[1]} columns, expected 15"
original_columns = baseline_df.columns.tolist()
assert len(original_columns) == 15

# Normalize steamid (remove trailing .0 if any)
for df in (user_games, users, baseline_df, val_pairs, test_pairs):
    df["steamid"] = df["steamid"].astype("string").str.replace(r"\.0$", "", regex=True)

# Enforce appid as Int64 everywhere
for df in (user_games, baseline_df, val_pairs, test_pairs):
    df["appid"] = pd.to_numeric(df["appid"], errors="coerce").astype("Int64")

# Compute account age
print("Computing account age in minutes...")
NOW_TS = time.time()
users["account_created"] = pd.to_numeric(users.get("account_created"), errors="coerce")
users["account_age_minutes"] = (NOW_TS - users["account_created"]) / 60

user_games = user_games.merge(
    users[["steamid", "account_age_minutes"]],
    on="steamid",
    how="left",
    validate="m:1"
)

# Cap individual playtime
print("Capping individual playtime by account age...")
user_games["playtime_minutes"] = pd.to_numeric(user_games.get("playtime_minutes"), errors="coerce")
global_cap = user_games["playtime_minutes"].quantile(0.999)

user_games["playtime_capped"] = np.where(
    user_games["account_age_minutes"].notna(),
    np.minimum(user_games["playtime_minutes"], user_games["account_age_minutes"]),
    np.minimum(user_games["playtime_minutes"], global_cap)
)

# Exclude test and val from train
exclude_pairs = pd.concat([val_pairs, test_pairs], ignore_index=True)[["steamid", "appid"]].drop_duplicates()
exclude_pairs["_exclude"] = 1

user_games = user_games.merge(exclude_pairs, on=["steamid", "appid"], how="left", validate="m:1")
train_games = user_games[user_games["_exclude"].isna()].drop(columns=["_exclude"]).copy()
print(f"Training interactions remaining: {len(train_games)}")

# Remove old features- to be replaced
features_to_replace = [
    "total_games_owned",
    "total_playtime_minutes",
    "median_playtime_minutes",
    "unique_genres_played",
    "user_count",
    "game_total_playtime_minutes",
]
baseline_df = baseline_df.drop(columns=features_to_replace, errors="ignore")

# User Features
print("Computing user aggregates...")
user_features = (
    train_games.groupby("steamid", sort=False)
    .agg(
        total_games_owned=("appid", "nunique"),
        total_playtime_minutes=("playtime_capped", "sum"),
        median_playtime_minutes=("playtime_capped", "median"),
    )
    .reset_index()
)

# Game Features
print("Computing game aggregates...")
game_features = (
    train_games.groupby("appid", sort=False)
    .agg(
        user_count=("steamid", "nunique"),
        game_total_playtime_minutes=("playtime_capped", "sum"),
    )
    .reset_index()
)

# Merge features into baseline
baseline_df = baseline_df.merge(user_features, on="steamid", how="left", validate="m:1")
baseline_df = baseline_df.merge(game_features, on="appid", how="left", validate="m:1")

# Unique genres played (user level)
print("Computing unique genres played...")
game_genres = baseline_df[["appid", "genres"]].drop_duplicates("appid")
train_with_genres = train_games.merge(game_genres, on="appid", how="left", validate="m:1")

train_with_genres["genres"] = train_with_genres["genres"].fillna("")
train_with_genres["genres_list"] = train_with_genres["genres"].astype(str).str.split(";")

user_unique_genres = (
    train_with_genres
    .explode("genres_list")
    .groupby("steamid")["genres_list"]
    .nunique()
    .rename("unique_genres_played")
    .reset_index()
)

baseline_df = baseline_df.merge(user_unique_genres, on="steamid", how="left", validate="m:1")

# Add user- game playtime feature
print("Adding user_game_playtime feature...")
playtime_map = train_games[["steamid", "appid", "playtime_capped"]].copy()

baseline_df = baseline_df.merge(playtime_map, on=["steamid", "appid"], how="left", validate="m:1")

# Set 0 for holdout pairs (val/test)
baseline_df = baseline_df.merge(
    exclude_pairs[["steamid", "appid"]].assign(_holdout=1),
    on=["steamid", "appid"],
    how="left",
    validate="m:1"
)
baseline_df.loc[baseline_df["_holdout"].eq(1), "playtime_capped"] = 0
baseline_df = baseline_df.drop(columns=["_holdout"])

baseline_df = baseline_df.rename(columns={"playtime_capped": "user_game_playtime"})
baseline_df["user_game_playtime"] = pd.to_numeric(baseline_df["user_game_playtime"], errors="coerce").fillna(0.0)

# owned = 1 
baseline_df["owned"] = 1


# TAB CLEANUP: Replace tabs with comma INSIDE FIELDS (so "windows<TAB>linux" becomes "windows,linux" but stays in ONE column)
print("Replacing TABs in text fields with commas...")
TEXT_COLS = ["name", "genres", "developer", "publisher", "platforms", "country", "release_date"]
for c in TEXT_COLS:
    if c in baseline_df.columns:
        baseline_df[c] = (
            baseline_df[c].astype(str)
            .str.replace("\t", ",", regex=False)
            .str.replace("\r", " ", regex=False)
            .str.replace("\n", " ", regex=False)
        )

# Final Structure
expected_cols = original_columns + ["owned", "user_game_playtime"]
baseline_df = baseline_df.reindex(columns=expected_cols)

# Final check
assert baseline_df.shape[1] == 17, f"output has {baseline_df.shape[1]} cols, expected 17"
assert (baseline_df["owned"] == 1).all(), "owned is not 1 everywhere!"

print("Saving with separator ';' ...")
baseline_df.to_csv(
    output_path,
    index=False,
    sep=";",
    quoting=csv.QUOTE_MINIMAL
)

print(f"Saved to: {output_path}")