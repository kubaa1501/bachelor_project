import requests
import pandas as pd
import time
import os
from tqdm import tqdm
import json

# =====================
# CONFIGURATION
# =====================
GAMES_CSV = "games.csv"  # CSV from your crawler
CHECKPOINT_DIR = "checkpoint_games"
RATE_LIMIT = 0.5  # seconds between API calls
CHECKPOINT_INTERVAL = 50  # save every 50 games

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# =====================
# LOAD GAMES
# =====================
games_df = pd.read_csv(GAMES_CSV)
# Only unique appids
games_df = games_df.drop_duplicates(subset="appid")

# =====================
# LOAD CHECKPOINT IF EXISTS
# =====================
checkpoint_file = os.path.join(CHECKPOINT_DIR, "enriched_games.csv")
visited_file = os.path.join(CHECKPOINT_DIR, "visited_games.json")

# Initialize
enriched_df = pd.DataFrame(columns=["appid", "name", "genres", "developer", "publisher",
                                    "platforms", "release_date", "user_count"])
visited_appids = set()

# Load existing CSV if exists
if os.path.exists(checkpoint_file):
    enriched_df = pd.read_csv(checkpoint_file, sep=";", quoting=1)

# Load visited_appids safely
if os.path.exists(visited_file) and os.path.getsize(visited_file) > 0:
    try:
        with open(visited_file) as f:
            visited_appids = set(int(a) for a in json.load(f))
        tqdm.write(f"Resuming from checkpoint, {len(visited_appids)} games already processed")
    except Exception:
        tqdm.write("Warning: visited_games.json corrupted, starting fresh")

# =====================
# MAIN LOOP
# =====================
for idx, row in tqdm(games_df.iterrows(), total=len(games_df),
                      desc="Fetching game metadata", ncols=100):

    appid = int(row["appid"])  # ensure it's a plain int
    user_count = row["user_count"]

    if appid in visited_appids:
        continue  # skip already fetched games

    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if not data[str(appid)]["success"]:
            continue
        info = data[str(appid)]["data"]

        name = info.get("name")
        genres = ";".join([g["description"] for g in info.get("genres", [])]) if info.get("genres") else ""
        developer = ";".join(info.get("developers", [])) if info.get("developers") else ""
        publisher = ";".join(info.get("publishers", [])) if info.get("publishers") else ""
        platforms = ";".join([k for k,v in info.get("platforms", {}).items() if v]) if info.get("platforms") else ""
        release_date = info.get("release_date", {}).get("date", "")

        # Replace tabs with semicolons to avoid CSV issues
        for col in ["genres", "developer", "publisher", "platforms"]:
            val = locals()[col]
            locals()[col] = val.replace("\t", ";") if val else val

        enriched_df = pd.concat([enriched_df, pd.DataFrame([{
            "appid": appid,
            "name": name,
            "genres": genres,
            "developer": developer,
            "publisher": publisher,
            "platforms": platforms,
            "release_date": release_date,
            "user_count": user_count
        }])], ignore_index=True)

        visited_appids.add(appid)

    except Exception as e:
        print(f"Error fetching {appid}: {e}")

    # Save checkpoint periodically
    if len(visited_appids) % CHECKPOINT_INTERVAL == 0:
        enriched_df.to_csv(checkpoint_file, sep=";", index=False, quoting=1)
        with open(visited_file, "w") as f:
            json.dump([int(a) for a in visited_appids], f)

    time.sleep(RATE_LIMIT)

# Final save
enriched_df.to_csv(checkpoint_file, sep=";", index=False, quoting=1)
with open(visited_file, "w") as f:
    json.dump([int(a) for a in visited_appids], f)

tqdm.write("Finished!")