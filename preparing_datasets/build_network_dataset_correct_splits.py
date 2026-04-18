#!/usr/bin/env python3
import csv
from pathlib import Path

# base project dir:
BASE = Path("/home/anci/new")

# input from the previous step of a pipeline
INPUT_DIR = BASE / "correct_splits" / "with_genre_groups"
# ourput 
OUTPUT_DIR = BASE / "correct_splits" / "with_genre_groups_network"

# additional input for new features 
FRIEND_COUNTS_PATH = BASE / "data" / "users_friend_counts.csv"
EMBEDDINGS_PATH = BASE / "pca_k32_trainonly" / "game_pca_embeddings_k32_trainonly.csv"

INPUTS = {
    "train": INPUT_DIR / "train.csv",
    "val":   INPUT_DIR / "val.csv",
    "test":  INPUT_DIR / "test.csv",
}

DELIM_IN = ";"
DELIM_OUT = ";"


def detect_delimiter(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as f:
        first = f.readline()
    return ";" if first.count(";") > first.count(",") else ","

# new columns friends_count
def load_friend_counts(path: Path):
    delim = detect_delimiter(path)
    out = {}

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header in {path}")

        fields = set(reader.fieldnames)

        # steamid is required to join friend counts with split rows
        if "steamid" not in fields:
            raise ValueError(f"{path} must contain a steamid column")

        candidate_friend_cols = [
            "friend_count",
            "friends_count",
            "num_friends",
            "friends",
            "count",
        ]
        friend_col = None
        for c in candidate_friend_cols:
            if c in fields:
                friend_col = c
                break

        if friend_col is None:
            raise ValueError(
                f"Could not find a friend-count column in {path}. "
                f"Columns: {reader.fieldnames}"
            )

        for row in reader:
            steamid = str(row["steamid"]).strip()
            val = str(row.get(friend_col, "")).strip()
            out[steamid] = val if val != "" else ""

    print(f"[FRIENDS] Loaded {len(out):,} users from {path}")
    print(f"[FRIENDS] Using friend count column: {friend_col}")
    return out

# Load game embedding vectors into a dictionary
#  appid -> {embedding_column_name: value}
def load_embeddings(path: Path):
    delim = detect_delimiter(path)
    out = {}
    emb_cols = None

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        if reader.fieldnames is None:
            raise ValueError(f"Lacking header in {path}")

        fields = reader.fieldnames
        if "appid" not in fields:
            raise ValueError(f"{path} Must contain  appid column")

        emb_cols = [c for c in fields if c.startswith("game_emb_")]
        if not emb_cols:
            # Fallback: PCA-style names such as pca_0, pca_1, ...
            pca_cols = [c for c in fields if c.startswith("pca_")]
            if pca_cols:
                emb_cols = pca_cols

        if not emb_cols:
            raise ValueError(
                f"Could not find embedding columns in {path}. "
                f"Columns: {fields}"
            )

        # If the file uses pca_* columns, rename them on load
        rename_needed = emb_cols[0].startswith("pca_")

        for row in reader:
            appid = str(row["appid"]).strip()
            if rename_needed:
                values = {}
                for i, c in enumerate(emb_cols):
                    values[f"game_emb_{i}"] = str(row.get(c, "")).strip()
            else:
                values = {c: str(row.get(c, "")).strip() for c in emb_cols}
            out[appid] = values

    final_emb_cols = list(next(iter(out.values())).keys()) if out else (
        [f"game_emb_{i}" for i in range(len(emb_cols))]
        if emb_cols and emb_cols[0].startswith("pca_")
        else emb_cols
    )

    print(f"[EMB] Loaded {len(out):,} games from {path}")
    print(f"[EMB] Number of embedding columns: {len(final_emb_cols)}")
    return out, final_emb_cols


# enrich split file with friend_count and embeddings
def transform_split(input_path: Path, output_path: Path, friend_counts, embeddings, emb_cols):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows_written = 0
    missing_friend_count = 0
    missing_embedding = 0

    with input_path.open("r", encoding="utf-8", newline="") as f_in, \
         output_path.open("w", encoding="utf-8", newline="") as f_out:

        reader = csv.DictReader(f_in, delimiter=DELIM_IN)
        in_fields = reader.fieldnames
        if in_fields is None:
            raise ValueError(f"Lacking header in {input_path}")

        out_fields = list(in_fields)
        if "friend_count" not in out_fields:
            out_fields.append("friend_count")
        for c in emb_cols:
            if c not in out_fields:
                out_fields.append(c)

        writer = csv.DictWriter(
            f_out,
            fieldnames=out_fields,
            delimiter=DELIM_OUT,
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()

        for row in reader:
            steamid = str(row.get("steamid", "")).strip()
            appid = str(row.get("appid", "")).strip()

            fc = friend_counts.get(steamid, "")
            if fc == "":
                missing_friend_count += 1
            row["friend_count"] = fc

            emb = embeddings.get(appid)
            if emb is None:
                missing_embedding += 1
                for c in emb_cols:
                    row[c] = ""
            else:
                for c in emb_cols:
                    row[c] = emb.get(c, "")

            writer.writerow(row)
            rows_written += 1

    print(f"[WRITE] Input : {input_path}")
    print(f"[WRITE] Output: {output_path}")
    print(f"[WRITE] Rows written: {rows_written:,}")
    print(f"[WRITE] Rows missing friend_count: {missing_friend_count:,}")
    print(f"[WRITE] Rows missing embeddings : {missing_embedding:,}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    friend_counts = load_friend_counts(FRIEND_COUNTS_PATH)
    embeddings, emb_cols = load_embeddings(EMBEDDINGS_PATH)

    for split, in_path in INPUTS.items():
        out_path = OUTPUT_DIR / f"{split}.csv"
        transform_split(
            input_path=in_path,
            output_path=out_path,
            friend_counts=friend_counts,
            embeddings=embeddings,
            emb_cols=emb_cols,
        )

    print("Done.")
    print(f"Created: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()