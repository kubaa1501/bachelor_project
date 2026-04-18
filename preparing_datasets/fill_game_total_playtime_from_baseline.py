#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

BASE = Path("/home/anci/new")

SOURCE_PATH = BASE / "data" / "baseline_features_playtime_capped_owned_semicolon.csv"

TARGET_FILES = [
    BASE / "correct_splits" / "with_genre_groups" / "train.csv",
    BASE / "correct_splits" / "with_genre_groups" / "val.csv",
    BASE / "correct_splits" / "with_genre_groups" / "test.csv",
    BASE / "correct_splits" / "with_genre_groups_network" / "train.csv",
    BASE / "correct_splits" / "with_genre_groups_network" / "val.csv",
    BASE / "correct_splits" / "with_genre_groups_network" / "test.csv",
]

KEY_COL = "appid"
FILL_COL = "game_total_playtime_minutes"


def build_appid_map(source_path: Path) -> pd.Series:
    print(f"Loading source: {source_path}")
    src = pd.read_csv(source_path, sep=";", usecols=[KEY_COL, FILL_COL], low_memory=False)

    src[KEY_COL] = pd.to_numeric(src[KEY_COL], errors="coerce")
    src[FILL_COL] = pd.to_numeric(src[FILL_COL], errors="coerce")
    src = src.dropna(subset=[KEY_COL])
    src[KEY_COL] = src[KEY_COL].astype("int64")

    src_nonnull = src.dropna(subset=[FILL_COL]).copy()
    appid_map = src_nonnull.drop_duplicates(subset=[KEY_COL]).set_index(KEY_COL)[FILL_COL]

    print(f"Unique appids with non-null {FILL_COL}: {len(appid_map):,}")
    return appid_map


def fill_file(path: Path, appid_map: pd.Series):
    print(f"\nProcessing: {path}")
    df = pd.read_csv(path, sep=";", low_memory=False)

    if KEY_COL not in df.columns:
        raise ValueError(f"{path} has no column {KEY_COL}")
    if FILL_COL not in df.columns:
        raise ValueError(f"{path} has no column {FILL_COL}")

    df[KEY_COL] = pd.to_numeric(df[KEY_COL], errors="coerce")
    before_missing = int(df[FILL_COL].isna().sum())

    fill_values = df[KEY_COL].map(appid_map)
    df[FILL_COL] = df[FILL_COL].fillna(fill_values)

    after_missing = int(df[FILL_COL].isna().sum())
    filled = before_missing - after_missing

    print(f"Missing before: {before_missing:,}")
    print(f"Filled:         {filled:,}")
    print(f"Missing after:  {after_missing:,}")

    # backup
    backup_path = path.with_suffix(path.suffix + ".bak")
    if not backup_path.exists():
        path.rename(backup_path)
        print(f"Backup created: {backup_path}")
    else:
        print(f"Backup exists:  {backup_path}")

    df.to_csv(path, sep=";", index=False)
    print(f"Saved:          {path}")


def main():
    appid_map = build_appid_map(SOURCE_PATH)
    for path in TARGET_FILES:
        fill_file(path, appid_map)


if __name__ == "__main__":
    main()