#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import defaultdict

# Paths
BASE = Path("/home/anci/new")

# Inputs
INPUTS = {
    "train": BASE / "correct_splits" / "train.csv",
    "val":   BASE / "correct_splits" / "val.csv",
    "test":  BASE / "correct_splits" / "test.csv",
}

# Outputs
OUTPUT_DIR = BASE / "correct_splits" / "with_genre_groups"

DELIMITER = ";"

# Genres mapping from RAW to genre groups 
GENRE_GROUPS = {
    "Action": ['Action', 'Acción', 'Akcja', 'Aksiyon', 'Actie', 'Akční', 'Экшены', '動作'],
    "Adventure": ['Adventure', 'Aventura', 'Avontuur', '冒险', 'Приключенческие gry', 'Приключенческие игры', 'Macera'],
    "RPG": ['RPG', 'RYO', 'Rol', 'Ролевые игры', '角色扮演'],
    "Casual": ['Casual', 'Occasionnel', 'Казуальные игры'],
    "Indie": ['Indie', 'Indépendant', '独立', 'Инди'],
    "Racing": ['Racing'],
    "Simulation": ['Simulation', 'Simuladores', 'Symulacje', 'Симуляторы'],
    "Strategy": ['Strategy', 'Strategie', 'Стратегии'],
    "Sports": ['Sport', 'Sports'],
    "Violent": ['Gore', 'Violent'],
    "Adult": ['Nudity', 'Sexual Content'],
    "Non-gameplay_Tools": [
        'Education', 'Documentary', 'Movie', 'Tutorial', 'Accounting', 'Audio Production',
        'Video Production', 'Photo Editing', 'Design & Illustration', 'Web Publishing',
        'Utilities', 'Software Training', 'Game Development', 'Animation & Modeling'
    ],
    "Other": ['Early Access', 'Episodic', 'Free To Play', 'Massively Multiplayer', 'Бесплатные']
}

# new features columns to replace the single user_game_playtime column
GROUP_COLUMNS = [f"user_playtime_group_{g}" for g in GENRE_GROUPS.keys()]

# Reverse lookup - RAW genre token -> genre groups 
TOKEN_TO_GROUP = {}
for group_name, tokens in GENRE_GROUPS.items():
    for tok in tokens:
        TOKEN_TO_GROUP[tok.strip().strip('"').strip().lower()] = group_name

# Parse float values; 0 for missing/invalid
def parse_float(value: str) -> float:
    if value is None:
        return 0.0
    value = str(value).strip()
    if value == "":
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0

# Parse int values; 0 for missing/invalid
def parse_int(value: str) -> int:
    if value is None:
        return 0
    value = str(value).strip()
    if value == "":
        return 0
    try:
        return int(float(value))
    except ValueError:
        return 0


def normalize_genre_token(token: str) -> str:
    return token.strip().strip('"').strip()

#Convert raw semicolon-separated genres into a list of merged genres
#    Example: 'Action;RPG' -> ['Action', 'RPG']
def get_merged_groups(genres_value: str):
    if genres_value is None:
        return []

    raw = str(genres_value).strip()
    if not raw:
        return []

    groups = []
    seen = set()

    for part in raw.split(";"):
        tok = normalize_genre_token(part)
        if not tok:
            continue
        key = tok.lower()
        group = TOKEN_TO_GROUP.get(key)
        if group is None:
            continue
        if group not in seen:
            seen.add(group)
            groups.append(group)

    return groups

#Build user-level historical playtime profiles from the training split only
#
#   For each user, aggregate playtime across merged genre groups
#   If a game belongs to multiple groups-> split evenly

def build_user_group_profile(train_path: Path):
    user_group_minutes = defaultdict(lambda: defaultdict(float))
    total_rows = 0
    positive_rows = 0
    missing_genre_rows = 0

    with train_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=DELIMITER)
        for row in reader:
            total_rows += 1

            owned = parse_int(row.get("owned"))
            if owned != 1:
                continue

            positive_rows += 1
            steamid = row.get("steamid", "").strip()
            playtime = parse_float(row.get("user_game_playtime"))
            groups = get_merged_groups(row.get("genres"))

            if not groups:
                missing_genre_rows += 1
                continue

            share = playtime / len(groups) if groups else 0.0
            for group in groups:
                user_group_minutes[steamid][group] += share

    print(f"[PROFILE] Built from: {train_path}")
    print(f"[PROFILE] Total rows: {total_rows}")
    print(f"[PROFILE] Positive rows (owned=1): {positive_rows}")
    print(f"[PROFILE] Positive rows with no mapped groups: {missing_genre_rows}")
    print(f"[PROFILE] Users in profile: {len(user_group_minutes)}")

    return user_group_minutes

#Replace user_game_playtime with multiple group-level user playtime features.
#
#   For each row:
#    - keep all original columns except user_game_playtime
#    - add one feature per merged genre group
#    - for positive train rows, subtract the current game's own contribution to avoid leakage-from-self

def transform_dataset(input_path: Path, output_path: Path, user_group_minutes, is_train: bool):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows_written = 0
    rows_missing_groups = 0

    with input_path.open("r", encoding="utf-8", newline="") as f_in, \
         output_path.open("w", encoding="utf-8", newline="") as f_out:

        reader = csv.DictReader(f_in, delimiter=DELIMITER)
        in_fields = reader.fieldnames
        if in_fields is None:
            raise ValueError(f"Missing header in {input_path}")
        # Remove user_game_playtime and replace it with group-level features
        out_fields = [c for c in in_fields if c != "user_game_playtime"] + GROUP_COLUMNS

        writer = csv.DictWriter(
            f_out,
            fieldnames=out_fields,
            delimiter=DELIMITER,
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()

        for row in reader:
            steamid = row.get("steamid", "").strip()
            owned = parse_int(row.get("owned"))
            playtime = parse_float(row.get("user_game_playtime"))
            groups = get_merged_groups(row.get("genres"))

            if not groups:
                rows_missing_groups += 1
            # Start from the users historical profile built on train positives
            profile = user_group_minutes.get(steamid, {})

            new_values = {}
            for group_name in GENRE_GROUPS.keys():
                col = f"user_playtime_group_{group_name}"
                new_values[col] = float(profile.get(group_name, 0.0))

            # for train and owned=1 substract wthe games own contribution (avoid leaking)
            if is_train and owned == 1 and groups:
                share = playtime / len(groups) if groups else 0.0
                for group in groups:
                    col = f"user_playtime_group_{group}"
                    adjusted = new_values[col] - share
                    if adjusted < 0:
                        adjusted = 0.0
                    new_values[col] = adjusted
            # Keep all original fields except user_game_playtime
            out_row = {k: v for k, v in row.items() if k != "user_game_playtime"}
            
            # Append new genre-group playtime features
            for col in GROUP_COLUMNS:
                out_row[col] = f"{new_values[col]:.6f}"

            writer.writerow(out_row)
            rows_written += 1

    print(f"[WRITE] Input : {input_path}")
    print(f"[WRITE] Output: {output_path}")
    print(f"[WRITE] Rows written: {rows_written}")
    print(f"[WRITE] Rows with no mapped groups: {rows_missing_groups}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    user_group_minutes = build_user_group_profile(INPUTS["train"])

    for split, in_path in INPUTS.items():
        out_path = OUTPUT_DIR / f"{split}.csv"
        transform_dataset(
            input_path=in_path,
            output_path=out_path,
            user_group_minutes=user_group_minutes,
            is_train=(split == "train"),
        )

    print("Done. Created:")
    print(f" - {OUTPUT_DIR}")


if __name__ == "__main__":
    main()