import pandas as pd
import numpy as np
import os

# ---------------------------
# Paths
# ---------------------------
final_data_path = r"C:\Users\jkgas\OneDrive\Desktop\data_science\Spring_2026\bachelor_project\data\final_data"

users_file = os.path.join(final_data_path, "users.csv")
user_games_file = os.path.join(final_data_path, "user_games.csv")
games_file = os.path.join(final_data_path, "games.csv")

baseline_output = os.path.join(final_data_path, "baseline_dataset.csv")

# ---------------------------
# Load data
# ---------------------------
users = pd.read_csv(users_file)
user_games = pd.read_csv(user_games_file)
games = pd.read_csv(games_file)

original_rows = len(user_games)

# ---------------------------
# Account age features
# ---------------------------
users["account_created"] = pd.to_datetime(
    users["account_created"], unit="s", errors="coerce"
)

now = pd.Timestamp.now()

users["account_age_minutes"] = (
    (now - users["account_created"]).dt.total_seconds() / 60
)

# Keep country for baseline
# ---------------------------
# Merge account age into interactions
# ---------------------------
user_games = user_games.merge(
    users[["steamid", "account_age_minutes", "country"]],
    on="steamid",
    how="left"
)

# ---------------------------
# Cap individual playtime
# ---------------------------
user_games["playtime_minutes_capped"] = np.minimum(
    user_games["playtime_minutes"],
    user_games["account_age_minutes"]
)

# ---------------------------
# USER AGGREGATE FEATURES
# ---------------------------
user_agg = user_games.groupby("steamid").agg(
    total_games_owned=("appid", "nunique"),
    total_playtime_minutes=("playtime_minutes_capped", "sum"),
    median_playtime_minutes=("playtime_minutes_capped", "median")
)

# Cap lifetime total_playtime by account age
user_agg = user_agg.join(users.set_index("steamid")["account_age_minutes"])
user_agg["total_playtime_minutes"] = np.minimum(
    user_agg["total_playtime_minutes"],
    user_agg["account_age_minutes"]
)
user_agg.drop(columns="account_age_minutes", inplace=True)

# ---------------------------
# UNIQUE GENRES PER USER
# ---------------------------
user_games_genres = user_games.merge(
    games[["appid", "genres"]],
    on="appid",
    how="left"
)

user_games_genres["genres"] = (
    user_games_genres["genres"]
    .fillna("")
    .str.split(";")
)

user_genres = (
    user_games_genres.explode("genres")
    .groupby("steamid")["genres"]
    .nunique()
    .rename("unique_genres_played")
)

user_agg = user_agg.join(user_genres)

# ---------------------------
# GAME FEATURES
# ---------------------------
games["release_date"] = pd.to_datetime(
    games["release_date"], errors="coerce"
)

game_agg = user_games.groupby("appid")["playtime_minutes_capped"] \
    .sum().rename("game_total_playtime_minutes")

games = games.set_index("appid").join(game_agg).reset_index()

# ---------------------------
# BUILD FINAL BASELINE DATASET
# ---------------------------
baseline = user_games.merge(
    user_agg.reset_index(),
    on="steamid",
    how="left"
)

baseline = baseline.merge(
    games,
    on="appid",
    how="left"
)

# ---------------------------
# DROP REDUNDANT COLUMNS
# ---------------------------
baseline = baseline.drop(columns=[
    "playtime_minutes",
    "account_age_minutes",
    "release_year",
    "playtime_minutes_capped"
], errors="ignore")

# ---------------------------
# Final checks
# ---------------------------
print("Original rows:", original_rows)
print("Baseline rows:", len(baseline))

print("\n===== BASELINE HEAD =====")
print(baseline.head())

print("\n===== BASELINE DESCRIBE =====")
print(baseline.describe(include="all"))

# ---------------------------
# Save baseline dataset
# ---------------------------
baseline.to_csv(baseline_output, index=False)
print("Baseline dataset saved to:", baseline_output)