import pandas as pd
from pathlib import Path

# ==============================
# PATH TO DATASET
# ==============================
input_path = r"C:\Users\jkgas\OneDrive\Desktop\data_science\Spring_2026\bachelor_project\data\baseline\baseline_dataset.csv"

# ==============================
# LOAD DATA
# ==============================
print("Loading dataset...")
df = pd.read_csv(input_path, usecols=["steamid", "appid"])
print(f"Total rows in original file: {len(df)}")
initial_users = df["steamid"].nunique()
print(f"Unique users in original file: {initial_users}")

# ==============================
# REMOVE DUPLICATES
# ==============================
df = df.drop_duplicates(["steamid", "appid"])

# ==============================
# FILTER USERS WITH ENOUGH GAMES
# ==============================
MIN_GAMES = 5
user_counts = df.groupby("steamid").size()
valid_users = user_counts[user_counts >= MIN_GAMES].index
df = df[df["steamid"].isin(valid_users)]
print(f"Users kept (>= {MIN_GAMES} games): {len(valid_users)}")

# ==============================
# LEAVE-TWO-OUT SPLIT: VALIDATION & TEST
# ==============================
print("Selecting validation and test interactions...")

def leave_two_out(x):
    """Randomly select 1 validation and 1 test per user."""
    steamid = x.name  # the group key
    if len(x) < 2:
        return pd.DataFrame(columns=["steamid", "appid", "split"])
    
    sampled = x.sample(n=2, random_state=None)
    val  = sampled.iloc[0:1].copy()
    test = sampled.iloc[1:2].copy()
    
    val["split"] = "validation"
    test["split"] = "test"
    
    val["steamid"] = steamid
    test["steamid"] = steamid
    
    return pd.concat([val, test])

pairs = df.groupby("steamid", group_keys=False).apply(leave_two_out).reset_index(drop=True)

# ==============================
# EXTRACT VALIDATION & TEST
# ==============================
validation_pairs = pairs[pairs["split"] == "validation"][["steamid", "appid"]]
test_pairs       = pairs[pairs["split"] == "test"][["steamid", "appid"]]

# ==============================
# PRINT SOME INFO
# ==============================
print("\nValidation pairs:")
print(validation_pairs.shape)
print(validation_pairs.head())
print("Unique users in validation:", validation_pairs["steamid"].nunique())

print("\nTest pairs:")
print(test_pairs.shape)
print(test_pairs.head())
print("Unique users in test:", test_pairs["steamid"].nunique())

# ==============================
# SAVING
# ==============================
output_val_path = "validation_user_game_pairs.csv"
output_test_path = "test_user_game_pairs.csv"

validation_pairs.to_csv(output_val_path, index=False)
test_pairs.to_csv(output_test_path, index=False)

print(f"\nSaved validation file to: {output_val_path}")
print(f"Saved test file to: {output_test_path}")