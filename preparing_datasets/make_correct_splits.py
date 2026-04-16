#!/usr/bin/env python3
import csv
import bisect
import random
from pathlib import Path
from collections import defaultdict, Counter

SEED = 42
rng = random.Random(SEED)

# Paths
BASE = Path("/home/anci/new")
DATA_DIR = BASE / "data"
OUT_DIR = BASE / "correct_splits"

# Input 
TRAIN_POS_PATH = DATA_DIR / "train_positive.csv"
VAL_POS_PATH   = DATA_DIR / "val_positive.csv"
TEST_POS_PATH  = DATA_DIR / "test_positive.csv"
GAMES_PATH     = DATA_DIR / "games.csv"

#Output
TRAIN_OUT = OUT_DIR / "train.csv"
VAL_OUT   = OUT_DIR / "val.csv"
TEST_OUT  = OUT_DIR / "test.csv"

POS_DELIM = ";"
GAMES_DELIM = ","

# Ratios of negatives to positives form data 
NEG_PER_POS = {
    "train": 10,
    "val": 100,
    "test": 100,
}

# Popularity fraction used for sampling negatives 
POPULAR_FRAC = 0.30


def load_games_catalog(path: Path):
    games = {}
    popularity = []

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=GAMES_DELIM)
        for row in reader:
            appid = str(row["appid"]).strip()

            raw_user_count = row.get("user_count", "")
            try:
                user_count_num = float(raw_user_count) if str(raw_user_count).strip() != "" else 0.0
            except ValueError:
                user_count_num = 0.0

            games[appid] = {
                "appid": appid,
                "name": row.get("name", ""),
                "genres": row.get("genres", ""),
                "developer": row.get("developer", ""),
                "publisher": row.get("publisher", ""),
                "platforms": row.get("platforms", ""),
                "release_date": row.get("release_date", ""),
                "user_count": str(row.get("user_count", "")),
                "user_count_num": user_count_num,
            }
            popularity.append((appid, user_count_num))

    if not games:
        raise ValueError("games.csv is empty or failed to load.")

    popularity.sort(key=lambda x: x[1], reverse=True)

    all_appids = [appid for appid, _ in popularity]

    # top 30% games as a popular subset 
    top_n = max(1, int(len(popularity) * 0.30))
    popular_subset = popularity[:top_n]

    pop_appids = [appid for appid, _ in popular_subset]
    pop_weights = [max(1.0, cnt) for _, cnt in popular_subset]

    cum_weights = []
    total = 0.0
    for w in pop_weights:
        total += w
        cum_weights.append(total)

    return games, all_appids, pop_appids, cum_weights


def load_positive_rows(path: Path):
    rows_by_user = defaultdict(list)

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=POS_DELIM)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise ValueError(f"Lack of header in {path}")

        for row in reader:
            row["steamid"] = str(row["steamid"]).strip()
            row["appid"] = str(row["appid"]).strip()
            rows_by_user[row["steamid"]].append(row)

    return fieldnames, rows_by_user


def pick_random_app(all_appids, forbidden_appids, max_tries=5000):
    for _ in range(max_tries):
        appid = rng.choice(all_appids)
        if appid not in forbidden_appids:
            return appid
    return None


def pick_popular_app(pop_appids, cum_weights, forbidden_appids, max_tries=8000):
    total = cum_weights[-1]
    for _ in range(max_tries):
        x = rng.random() * total
        idx = bisect.bisect_left(cum_weights, x)
        appid = pop_appids[idx]
        if appid not in forbidden_appids:
            return appid
    return None


def build_negative_row(pos_row, game_info):
    return {
        "steamid": pos_row["steamid"],
        "appid": game_info["appid"],
        "country": pos_row.get("country", ""),
        "total_games_owned": pos_row.get("total_games_owned", ""),
        "total_playtime_minutes": pos_row.get("total_playtime_minutes", ""),
        "median_playtime_minutes": pos_row.get("median_playtime_minutes", ""),
        "unique_genres_played": pos_row.get("unique_genres_played", ""),
        "name": game_info.get("name", ""),
        "genres": game_info.get("genres", ""),
        "developer": game_info.get("developer", ""),
        "publisher": game_info.get("publisher", ""),
        "platforms": game_info.get("platforms", ""),
        "release_date": game_info.get("release_date", ""),
        "user_count": game_info.get("user_count", ""),
        # games.csv doesnt have this column
        "game_total_playtime_minutes": "",
        "owned": "0",
        "user_game_playtime": "0",
    }


def sample_negatives_for_positive(
    pos_row,
    split_name,
    split_forbidden_appids,
    user_all_positive_appids,
    games,
    all_appids,
    pop_appids,
    cum_weights,
):
    """
    split_forbidden_appids:
      Games already used for this user in diffrent splits + all positives of the user
      but DOES NOT block repeating inside of the current split
    """
    total_neg = NEG_PER_POS[split_name]
    n_pop_target = int(total_neg * POPULAR_FRAC)

    chosen = []

    current_forbidden = set(split_forbidden_appids) | set(user_all_positive_appids)

    # popular-weighted
    for _ in range(n_pop_target):
        appid = pick_popular_app(pop_appids, cum_weights, current_forbidden)
        if appid is None:
            break
        chosen.append(appid)

    # random fallback / fill
    while len(chosen) < total_neg:
        appid = pick_random_app(all_appids, current_forbidden)
        if appid is None:
            break
        chosen.append(appid)

    return [build_negative_row(pos_row, games[a]) for a in chosen], chosen


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    games, all_appids, pop_appids, cum_weights = load_games_catalog(GAMES_PATH)

    fieldnames_train, train_by_user = load_positive_rows(TRAIN_POS_PATH)
    fieldnames_val, val_by_user = load_positive_rows(VAL_POS_PATH)
    fieldnames_test, test_by_user = load_positive_rows(TEST_POS_PATH)

    if fieldnames_train != fieldnames_val or fieldnames_train != fieldnames_test:
        raise ValueError("Headers in train/val/test positive are not identical.")

    out_fieldnames = fieldnames_train

    all_users = sorted(set(train_by_user) | set(val_by_user) | set(test_by_user))

    warnings = []
    stats = {
        "train_pos": 0, "train_neg": 0,
        "val_pos": 0,   "val_neg": 0,
        "test_pos": 0,  "test_neg": 0,
    }

    # used to prevent leakage between splits for the same user
    used_by_user_split = {
        "train": defaultdict(set),
        "val": defaultdict(set),
        "test": defaultdict(set),
    }

    with TRAIN_OUT.open("w", encoding="utf-8", newline="") as f_train, \
         VAL_OUT.open("w", encoding="utf-8", newline="") as f_val, \
         TEST_OUT.open("w", encoding="utf-8", newline="") as f_test:

        train_writer = csv.DictWriter(f_train, fieldnames=out_fieldnames, delimiter=POS_DELIM, quoting=csv.QUOTE_MINIMAL)
        val_writer   = csv.DictWriter(f_val,   fieldnames=out_fieldnames, delimiter=POS_DELIM, quoting=csv.QUOTE_MINIMAL)
        test_writer  = csv.DictWriter(f_test,  fieldnames=out_fieldnames, delimiter=POS_DELIM, quoting=csv.QUOTE_MINIMAL)

        train_writer.writeheader()
        val_writer.writeheader()
        test_writer.writeheader()

        split_to_writer = {
            "train": train_writer,
            "val": val_writer,
            "test": test_writer,
        }

        for user_idx, steamid in enumerate(all_users, start=1):
            train_rows = train_by_user.get(steamid, [])
            val_rows   = val_by_user.get(steamid, [])
            test_rows  = test_by_user.get(steamid, [])

            user_all_positive_appids = set()
            for row in train_rows + val_rows + test_rows:
                user_all_positive_appids.add(row["appid"])

            # round-robin in splits for user
            queues = {
                "train": list(train_rows),
                "val": list(val_rows),
                "test": list(test_rows),
            }

            max_len = max(len(queues["train"]), len(queues["val"]), len(queues["test"]))

            for i in range(max_len):
                for split_name in ["train", "val", "test"]:
                    if i >= len(queues[split_name]):
                        continue

                    pos_row = queues[split_name][i]

                    # save positives
                    split_to_writer[split_name].writerow(pos_row)
                    stats[f"{split_name}_pos"] += 1

                    # block games form diffrent splits + users positives
                    other_splits = [s for s in ["train", "val", "test"] if s != split_name]
                    forbidden = set()
                    for s in other_splits:
                        forbidden |= used_by_user_split[s][steamid]
                    forbidden |= user_all_positive_appids

                    neg_rows, chosen_appids = sample_negatives_for_positive(
                        pos_row=pos_row,
                        split_name=split_name,
                        split_forbidden_appids=forbidden,
                        user_all_positive_appids=user_all_positive_appids,
                        games=games,
                        all_appids=all_appids,
                        pop_appids=pop_appids,
                        cum_weights=cum_weights,
                    )

                    # save negatives
                    for neg_row in neg_rows:
                        split_to_writer[split_name].writerow(neg_row)
                    stats[f"{split_name}_neg"] += len(neg_rows)

                    # after save we block those games for the rest of the splits 
                    used_by_user_split[split_name][steamid].update(chosen_appids)

                    expected = NEG_PER_POS[split_name]
                    if len(chosen_appids) < expected:
                        warnings.append(
                            f"user={steamid} split={split_name} pos_appid={pos_row['appid']} "
                            f"expected_neg={expected} got={len(chosen_appids)}"
                        )

            if user_idx % 5000 == 0:
                print(
                    f"Processed users: {user_idx:,}/{len(all_users):,} | "
                    f"train_total={stats['train_pos'] + stats['train_neg']:,} | "
                    f"val_total={stats['val_pos'] + stats['val_neg']:,} | "
                    f"test_total={stats['test_pos'] + stats['test_neg']:,}"
                )

    print("\nDone.")
    print(f"Saved to: {OUT_DIR}")
    print()
    print(f"Train positives: {stats['train_pos']:,}")
    print(f"Train negatives: {stats['train_neg']:,}")
    print(f"Train total:     {stats['train_pos'] + stats['train_neg']:,}")
    print()
    print(f"Val positives:   {stats['val_pos']:,}")
    print(f"Val negatives:   {stats['val_neg']:,}")
    print(f"Val total:       {stats['val_pos'] + stats['val_neg']:,}")
    print()
    print(f"Test positives:  {stats['test_pos']:,}")
    print(f"Test negatives:  {stats['test_neg']:,}")
    print(f"Test total:      {stats['test_pos'] + stats['test_neg']:,}")
    print()

    print("Expected target ratios:")
    print("  train: 1:10")
    print("  val:   1:100")
    print("  test:  1:100")
    print()

    print(f"Warnings (insufficient negatives): {len(warnings):,}")
    if warnings:
        warn_path = OUT_DIR / "warnings_insufficient_negatives.txt"
        with warn_path.open("w", encoding="utf-8") as f:
            for w in warnings:
                f.write(w + "\n")
        print(f"Saved warnings to: {warn_path}")
        print("First 20 warnings:")
        for w in warnings[:20]:
            print("  " + w)


if __name__ == "__main__":
    main()