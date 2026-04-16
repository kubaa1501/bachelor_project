#!/usr/bin/env python3
import csv
from pathlib import Path

#Input paths 
BASELINE_PATH = Path("/home/anci/new/data/baseline_features_playtime_capped_owned_semicolon.csv")
VAL_PAIRS_PATH = Path("/home/anci/new/data/validation_user_game_pairs.csv")
TEST_PAIRS_PATH = Path("/home/anci/new/data/test_user_game_pairs.csv")

#Path to outputs and output 
OUT_DIR = Path("/home/anci/new/data")
TRAIN_OUT = OUT_DIR / "train_positive.csv"
VAL_OUT   = OUT_DIR / "val_positive.csv"
TEST_OUT  = OUT_DIR / "test_positive.csv"

DELIM = ";"


def load_pairs(path: Path, delimiter=","):
    pairs = set()
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError(f"lacking header {path}")
        if "steamid" not in reader.fieldnames or "appid" not in reader.fieldnames:
            raise ValueError(f"{path} needs to have columns: steamid, appid")

        for row in reader:
            pairs.add((str(row["steamid"]).strip(), str(row["appid"]).strip()))
    return pairs


def detect_delimiter(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        first = f.readline()
    if first.count(";") > first.count(","):
        return ";"
    return ","


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    val_delim = detect_delimiter(VAL_PAIRS_PATH)
    test_delim = detect_delimiter(TEST_PAIRS_PATH)

    val_pairs = load_pairs(VAL_PAIRS_PATH, delimiter=val_delim)
    test_pairs = load_pairs(TEST_PAIRS_PATH, delimiter=test_delim)

    overlap = val_pairs & test_pairs
    print(f"validation pairs: {len(val_pairs):,}")
    print(f"test pairs:       {len(test_pairs):,}")
    print(f"overlap:          {len(overlap):,}")

    if overlap:
        print("ERROR: validation and test pairs overlap!")
        print("sample:", list(overlap)[:10])
        raise SystemExit(1)

    all_holdout_pairs = val_pairs | test_pairs

    train_rows = []
    val_rows = []
    test_rows = []

    total_rows = 0
    total_positive_rows = 0
    skipped_non_positive = 0
    missing_in_holdouts = 0

    with BASELINE_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=DELIM)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise ValueError("Lack of header in Baseline")
        if "steamid" not in fieldnames or "appid" not in fieldnames or "owned" not in fieldnames:
            raise ValueError("Baseline needs to have headers steamid, appid, owned")

        for row in reader:
            total_rows += 1
            if str(row["owned"]).strip() != "1":
                skipped_non_positive += 1
                continue

            total_positive_rows += 1
            pair = (str(row["steamid"]).strip(), str(row["appid"]).strip())

            if pair in val_pairs:
                val_rows.append(row)
            elif pair in test_pairs:
                test_rows.append(row)
            else:
                train_rows.append(row)

    # Save
    for path, rows in [
        (TRAIN_OUT, train_rows),
        (VAL_OUT, val_rows),
        (TEST_OUT, test_rows),
    ]:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
                delimiter=DELIM,
                quoting=csv.QUOTE_MINIMAL
            )
            writer.writeheader()
            writer.writerows(rows)

    # Final checks
    train_pairs = {(r["steamid"], r["appid"]) for r in train_rows}
    val_pairs_written = {(r["steamid"], r["appid"]) for r in val_rows}
    test_pairs_written = {(r["steamid"], r["appid"]) for r in test_rows}

    print()
    print("Saved:")
    print(f"  train_positive: {len(train_rows):,} -> {TRAIN_OUT}")
    print(f"  val_positive:   {len(val_rows):,} -> {VAL_OUT}")
    print(f"  test_positive:  {len(test_rows):,} -> {TEST_OUT}")
    print()
    print("Intersections after write:")
    print(f"  train ∩ val : {len(train_pairs & val_pairs_written):,}")
    print(f"  train ∩ test: {len(train_pairs & test_pairs_written):,}")
    print(f"  val ∩ test  : {len(val_pairs_written & test_pairs_written):,}")
    print()
    print("Counts:")
    print(f"  total rows in baseline:     {total_rows:,}")
    print(f"  total positive in baseline: {total_positive_rows:,}")
    print(f"  skipped non-positive rows:  {skipped_non_positive:,}")


if __name__ == "__main__":
    main()