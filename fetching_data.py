import requests
import time
import random
import json
import os
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

# =====================
# CONFIGURATION
# =====================
API_KEY = os.getenv("STEAM_API_KEY")
if not API_KEY:
    raise ValueError("Missing STEAM_API_KEY env var. Put it in secrets.env and source it in the job.")
SUPERVISOR_ID = "76561198064675174"

BASE_URL = "https://api.steampowered.com"
RATE_LIMIT = 1.2  # seconds between API calls
MAX_USERS = 100000  
CHECKPOINT_INTERVAL = 500
RANDOM_SEED = 42

random.seed(RANDOM_SEED)

# =====================
# LOAD CHECKPOINT IF EXISTS
# =====================
if os.path.exists("checkpoint/visited.json"):
    tqdm.write("Loading checkpoint...")
    with open("checkpoint/visited.json") as f:
        visited = set(json.load(f))
    with open("checkpoint/discovered.json") as f:
        discovered = set(json.load(f))
    users_df = pd.read_csv("checkpoint/users.csv")
    users = {u["steamid"]: u for u in users_df.to_dict("records")}
    edges_df = pd.read_csv("checkpoint/friends.csv")
    edges = [(e["user_steamid"], e["friend_steamid"]) for e in edges_df.to_dict("records")]
    games_df = pd.read_csv("checkpoint/user_games.csv")
    user_games = [(g["steamid"], g["appid"], g["playtime_minutes"]) for g in games_df.to_dict("records")]
    # Rebuild game_counts
    game_counts = defaultdict(int)
    for g in user_games:
        game_counts[g[1]] += 1
else:
    visited = set()
    discovered = set([SUPERVISOR_ID])
    users = {}
    edges = []
    user_games = []
    game_counts = defaultdict(int)

# Ensure checkpoint directory exists
os.makedirs("checkpoint", exist_ok=True)

# =====================
# API FUNCTIONS
# =====================
def get_player_summary(steamid):
    url = f"{BASE_URL}/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": API_KEY, "steamids": steamid}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return None
    players = r.json().get("response", {}).get("players", [])
    return players[0] if players else None

def get_friends(steamid):
    url = f"{BASE_URL}/ISteamUser/GetFriendList/v1/"
    params = {"key": API_KEY, "steamid": steamid}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return []
    return [f["steamid"] for f in r.json().get("friendslist", {}).get("friends", [])]

def get_games(steamid):
    url = f"{BASE_URL}/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": API_KEY,
        "steamid": steamid,
        "include_appinfo": False
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return None
    return r.json().get("response", {}).get("games")

# =====================
# CHECKPOINT FUNCTION
# =====================
def save_checkpoint():
    with open("checkpoint/visited.json", "w") as f:
        json.dump(list(visited), f)
    with open("checkpoint/discovered.json", "w") as f:
        json.dump(list(discovered), f)
    pd.DataFrame(users.values()).to_csv("checkpoint/users.csv", index=False)
    edges_df = pd.DataFrame(edges, columns=["user_steamid", "friend_steamid"])
    edges_df.to_csv("checkpoint/friends.csv", index=False)
    games_df = pd.DataFrame(user_games, columns=["steamid", "appid", "playtime_minutes"])
    games_df.to_csv("checkpoint/user_games.csv", index=False)

# =====================
# MAIN CRAWLER
# =====================
progress = tqdm(total=MAX_USERS, desc="Crawling users", unit="users", ncols=100)
progress.n = len(visited)
progress.last_print_n = len(visited)
progress.refresh()

while len(visited) < MAX_USERS and discovered:
    # Pick random unvisited user
    steamid = random.choice(tuple(discovered - visited))

    # Get user summary
    summary = get_player_summary(steamid)
    time.sleep(RATE_LIMIT)

    # Mark as visited and update progress
    visited.add(steamid)
    progress.update(1)
    progress.refresh()

    if not summary:
        continue

    visibility = summary.get("communityvisibilitystate", 1)

    # Store user info
    users[steamid] = {
        "steamid": steamid,
        "public": visibility == 3,
        "country": summary.get("loccountrycode"),
        "account_created": summary.get("timecreated"),
        "last_logoff": summary.get("lastlogoff")
    }

    # PRIVATE USER → do not expand
    if visibility != 3:
        continue

    # PUBLIC USER → expand friends
    friends = get_friends(steamid)
    time.sleep(RATE_LIMIT)
    for f in friends:
        edges.append((steamid, f))
        discovered.add(f)

    # Get games
    games = get_games(steamid)
    time.sleep(RATE_LIMIT)

    if games:
        for g in games:
            appid = g["appid"]
            playtime = g.get("playtime_forever", 0)
            user_games.append((steamid, appid, playtime))
            game_counts[appid] += 1

    # Periodic checkpoint
    if len(visited) % CHECKPOINT_INTERVAL == 0:
        save_checkpoint()

progress.close()
save_checkpoint()
tqdm.write("Done :D")

# =====================
# FINAL GAME DATA
# =====================
all_games = sorted(game_counts.items(), key=lambda x: x[1], reverse=True)
games_df = pd.DataFrame(all_games, columns=["appid", "user_count"])
games_df["appid"] = games_df["appid"].astype(str)
games_df.to_csv("games.csv", index=False)