import re
from pathlib import Path

import numpy as np
import pandas as pd
import dateparser

# paths 
BASE = Path("/home/anci/new/correct_splits/with_genre_groups_network")
# files to change
FILES = ["train.csv", "val.csv", "test.csv"]
# ref time (game age until this date)
REFERENCE_DATE = pd.Timestamp("2026-03-12")
# max age of a game 
MAX_AGE_MONTHS = 600
# reading in chunks
CHUNKSIZE = 300_000

# quaters of a year mapping
QUARTER_MONTH = {
    "1": 1,
    "2": 4,
    "3": 7,
    "4": 10,
}

# handling quaters - returns 1st day of the first month of the quarter
def parse_quarter_string(s: str):
    m = re.fullmatch(r"Q([1-4])\s+(\d{4})", s.strip(), flags=re.IGNORECASE)
    if not m:
        return None
    q, year = m.groups()
    return pd.Timestamp(year=int(year), month=QUARTER_MONTH[q], day=1)

# handling cheneese formatting
def parse_chinese_date(s: str):
    m = re.fullmatch(r"\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日\s*", s)
    if not m:
        return None
    year, month, day = map(int, m.groups())
    return pd.Timestamp(year=year, month=month, day=day)


def parse_one_date(s: str):
  # changing release_date into timestamp in Pandas
    if s is None:
        return pd.NaT

    s = str(s).strip()
    if s == "":
        return pd.NaT
      
  # games without specified data are treated as 0 
    s_lower = s.lower()
    if s_lower in {"coming soon", "to be announced"}:
        return None

    qdt = parse_quarter_string(s)
    if qdt is not None:
        return qdt

    cdt = parse_chinese_date(s)
    if cdt is not None:
        return cdt

    dt = pd.to_datetime(s, format="mixed", errors="coerce")
    if pd.notna(dt):
        return dt

    # additional parsing 
    dt2 = dateparser.parse(
        s,
        settings={
            "DATE_ORDER": "DMY",
            "PREFER_DAY_OF_MONTH": "first",
            "PREFER_MONTH_OF_YEAR": "first",
            "STRICT_PARSING": False,
            "PREFER_LOCALE_DATE_ORDER": True,
        },
    )
    if dt2 is not None:
        return pd.Timestamp(dt2)

    # return nan if not possible to convert the date 
    return pd.NaT


def transform_release_date(series: pd.Series) -> pd.Series:
  # tranfroming release_date into a numeric age in mothns 
    out = pd.Series(np.nan, index=series.index, dtype="float32")

    for idx, val in series.items():
        if pd.isna(val):
            continue

        s = str(val).strip()
        if s == "":
            continue

        # 0 for not specified dates 
        s_lower = s.lower()
        if s_lower in {"coming soon", "to be announced"}:
            out.at[idx] = 0
            continue

        dt = parse_one_date(s)
        if pd.isna(dt):
            continue
        # calculating age 
        months = (REFERENCE_DATE.year - dt.year) * 12 + (REFERENCE_DATE.month - dt.month)
        months = max(months, 0)

        if months > MAX_AGE_MONTHS:
            out.at[idx] = np.nan
        else:
            out.at[idx] = months

    return out


def process_file(path: Path) -> None:
    print(f"\nProcessing: {path}", flush=True)

    backup_path = path.with_suffix(path.suffix + ".bak_release_date")
    fallback_backup = path.with_suffix(path.suffix + ".bak")

    if backup_path.exists():
        source_path = backup_path
    elif fallback_backup.exists():
        source_path = fallback_backup
    else:
        source_path = path
   # tmp file to save the output 
    temp_path = path.with_suffix(path.suffix + ".tmp_release_date")

    if temp_path.exists():
        temp_path.unlink()

    total_rows = 0
    total_nan_before = 0
    total_tba_before = 0
    total_soon_before = 0
    total_nan_after = 0
    total_zero_after = 0

    first_chunk = True

    for chunk_id, chunk in enumerate(
        pd.read_csv(source_path, sep=";", low_memory=False, chunksize=CHUNKSIZE),
        start=1
    ):
        s = chunk["release_date"].astype("string").str.strip().str.lower()

        total_rows += len(chunk)
        total_nan_before += int(chunk["release_date"].isna().sum())
        total_tba_before += int(s.eq("to be announced").sum())
        total_soon_before += int(s.eq("coming soon").sum())

        chunk["release_date"] = transform_release_date(chunk["release_date"])

        total_nan_after += int(chunk["release_date"].isna().sum())
        total_zero_after += int((chunk["release_date"] == 0).sum())

        chunk.to_csv(
            temp_path,
            sep=";",
            index=False,
            mode="w" if first_chunk else "a",
            header=first_chunk
        )
        first_chunk = False

        print(
            f"chunk {chunk_id}: rows={len(chunk)}, total_rows={total_rows}, "
            f"nan_after_so_far={total_nan_after}, zero_after_so_far={total_zero_after}",
            flush=True
        )

    # replace temporary to the acctual file 
    temp_path.replace(path)

    print(f"NaN before: {total_nan_before}", flush=True)
    print(f"'to be announced' before: {total_tba_before}", flush=True)
    print(f"'coming soon' before: {total_soon_before}", flush=True)
    print(f"NaN after: {total_nan_after}", flush=True)
    print(f"zero count after: {total_zero_after}", flush=True)
    print(f"Saved: {path}", flush=True)


def main():
    for fname in FILES:
        process_file(BASE / fname)
    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
