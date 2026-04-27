import pandas as pd
from pathlib import Path

# ==============================
# PATHS
# ==============================
user_games_path = r"C:\Users\jkgas\OneDrive\Desktop\data_science\Spring_2026\bachelor_project\data\final_data\user_games.csv"
baseline_path = r"C:\Users\jkgas\OneDrive\Desktop\data_science\Spring_2026\bachelor_project\data\baseline\baseline_dataset.csv"
val_pairs_path = Path.cwd() / "validation_user_game_pairs.csv"
test_pairs_path = Path.cwd() / "test_user_game_pairs.csv"
output_path = Path.cwd() / "baseline_features_train_only.csv"

# ==============================
# LOAD DATA
# ==============================
print("Loading user-game interactions...")
user_games = pd.read_csv(user_games_path)

val_pairs = pd.read_csv(val_pairs_path)
test_pairs = pd.read_csv(test_pairs_path)

# ==============================
# FILTER TRAIN INTERACTIONS
# ==============================
exclude_pairs = pd.concat([val_pairs, test_pairs], ignore_index=True)

user_games = user_games.merge(
    exclude_pairs.assign(exclude=1),
    on=["steamid", "appid"],
    how="left"
)

train_games = user_games[user_games["exclude"].isna()].drop(columns=["exclude"])

print(f"Training interactions remaining: {len(train_games)}")

# ==============================
# LOAD BASELINE
# ==============================
baseline_df = pd.read_csv(baseline_path)

print(f"Baseline rows BEFORE update: {len(baseline_df)}")

# SAVE ORIGINAL COLUMN ORDER
original_columns = baseline_df.columns.tolist()

# ==============================
# REMOVE OLD FEATURES
# ==============================
features_to_replace = [
    "total_games_owned",
    "total_playtime_minutes",
    "median_playtime_minutes",
    "unique_genres_played",
    "user_count",
    "game_total_playtime_minutes",
]

baseline_df = baseline_df.drop(columns=features_to_replace, errors="ignore")

# ==============================
# USER FEATURES (TRAIN ONLY)
# ==============================
print("Computing user features...")

user_features = (
    train_games.groupby("steamid")
    .agg(
        total_games_owned=("appid", "nunique"),
        total_playtime_minutes=("playtime_minutes", "sum"),
        median_playtime_minutes=("playtime_minutes", "median"),
    )
    .reset_index()
)

# ==============================
# GAME FEATURES (TRAIN ONLY)
# ==============================
print("Computing game features...")

game_features = (
    train_games.groupby("appid")
    .agg(
        user_count=("steamid", "nunique"),
        game_total_playtime_minutes=("playtime_minutes", "sum"),
    )
    .reset_index()
)

# ==============================
# MERGE FEATURES
# ==============================
baseline_df = baseline_df.merge(user_features, on="steamid", how="left")
baseline_df = baseline_df.merge(game_features, on="appid", how="left")

# ==============================
# UNIQUE GENRES PLAYED
# ==============================
print("Computing unique genres...")

train_with_genres = train_games.merge(
    baseline_df[["appid", "genres"]].drop_duplicates(),
    on="appid",
    how="left",
)

train_with_genres["genres"] = train_with_genres["genres"].fillna("")
train_with_genres["genres_list"] = train_with_genres["genres"].str.split(";")

user_unique_genres = (
    train_with_genres.explode("genres_list")
    .groupby("steamid")["genres_list"]
    .nunique()
    .rename("unique_genres_played")
    .reset_index()
)

baseline_df = baseline_df.merge(user_unique_genres, on="steamid", how="left")

# ==============================
# RESTORE ORIGINAL COLUMN ORDER
# ==============================
baseline_df = baseline_df[original_columns]

# ==============================
# CHECK RESULTS
# ==============================
print("\nUpdated baseline head:")
print(baseline_df.head())

print(f"\nRows AFTER update: {len(baseline_df)}")

# ==============================
# SAVE
# ==============================
baseline_df.to_csv(output_path, index=False)

print(f"\nSaved file:\n{output_path}")