import requests
import time
import random
import json
import os
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

# configuration 
# load the api key from the enviroment variable 
API_KEY = os.getenv("STEAM_API_KEY")
# stop the script if the api key is missing
if not API_KEY:
    raise ValueError("Missing STEAM_API_KEY env var. Put it in secrets.env and source it in the job.")

# starting user for the crawl
SUPERVISOR_ID = "76561198064675174"

# base url for steam web api requests
BASE_URL = "https://api.steampowered.com"

# delay between api requests to avoid hitting rate limits
RATE_LIMIT = 1.2  

# maximum number of users to visit
MAX_USERS = 100000

# save intermediate results every n visited users
CHECKPOINT_INTERVAL = 500

# fixed seed for reproducible random user selection
RANDOM_SEED = 42

random.seed(RANDOM_SEED)

# load checkpoint if it already exists
# this allows the crawler to resume after interruption
if os.path.exists("checkpoint/visited.json"):
    tqdm.write("Loading checkpoint...")
    
    # load already visited users
    with open("checkpoint/visited.json") as f:
        visited = set(json.load(f))
    # load discovered users that may still be visited
    with open("checkpoint/discovered.json") as f:
        discovered = set(json.load(f))
    # load collected user metadata
    users_df = pd.read_csv("checkpoint/users.csv")
    users = {u["steamid"]: u for u in users_df.to_dict("records")}
    
    # load collected friendship edges
    edges_df = pd.read_csv("checkpoint/friends.csv")
    edges = [(e["user_steamid"], e["friend_steamid"]) for e in edges_df.to_dict("records")]
    
    # load collected user-game interactions
    games_df = pd.read_csv("checkpoint/user_games.csv")
    user_games = [(g["steamid"], g["appid"], g["playtime_minutes"]) for g in games_df.to_dict("records")]
    
    # rebuild game popularity counts from saved user-game data
    game_counts = defaultdict(int)
    for g in user_games:
        game_counts[g[1]] += 1
else:
    # initialize empty crawl state when no checkpoint exists
    visited = set()
    discovered = set([SUPERVISOR_ID])
    users = {}
    edges = []
    user_games = []
    game_counts = defaultdict(int)

# create checkpoint directory if it does not exist
os.makedirs("checkpoint", exist_ok=True)



# api function: fetch basic steam profile information for one user
def get_player_summary(steamid):
    url = f"{BASE_URL}/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": API_KEY, "steamids": steamid}
    r = requests.get(url, params=params)
    # return none if the request failed
    if r.status_code != 200:
        return None
    # extract the player object from the api response
    players = r.json().get("response", {}).get("players", [])
    # return the first player if present
    return players[0] if players else None

# api function: fetch friends of one steam user
def get_friends(steamid):
    url = f"{BASE_URL}/ISteamUser/GetFriendList/v1/"
    params = {"key": API_KEY, "steamid": steamid}
    r = requests.get(url, params=params)
    # return an empty list if friends cannot be fetched
    if r.status_code != 200:
        return []
    
    # extract friend steam ids from the response
    return [f["steamid"] for f in r.json().get("friendslist", {}).get("friends", [])]

# api function: fetch owned games for one steam user
def get_games(steamid):
    url = f"{BASE_URL}/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": API_KEY,
        "steamid": steamid,
        "include_appinfo": False
    }
    r = requests.get(url, params=params)
    # return none if games cannot be fetched
    if r.status_code != 200:
        return None
    # return the list of owned games from the response
    return r.json().get("response", {}).get("games")

# save current crawl state to checkpoint files
def save_checkpoint():
    # save visited users
    with open("checkpoint/visited.json", "w") as f:
        json.dump(list(visited), f)

    # save discovered users
    with open("checkpoint/discovered.json", "w") as f:
        json.dump(list(discovered), f)
        
    # save collected user metadata
    pd.DataFrame(users.values()).to_csv("checkpoint/users.csv", index=False)
    
     # save friendship edges
    edges_df = pd.DataFrame(edges, columns=["user_steamid", "friend_steamid"])
    edges_df.to_csv("checkpoint/friends.csv", index=False)

    # save user-game playtime records
    games_df = pd.DataFrame(user_games, columns=["steamid", "appid", "playtime_minutes"])
    games_df.to_csv("checkpoint/user_games.csv", index=False)

# initialize progress bar for the crawling process
progress = tqdm(total=MAX_USERS, desc="Crawling users", unit="users", ncols=100)
# resume progress bar from the number of already visited users
progress.n = len(visited)
progress.last_print_n = len(visited)
progress.refresh()

# main crawling loop
# continue until the user limit is reached or there are no more discovered users
while len(visited) < MAX_USERS and discovered:
    # choose a random user that has been discovered but not yet visited
    steamid = random.choice(tuple(discovered - visited))

    # fetch basic profile information
    summary = get_player_summary(steamid)
    time.sleep(RATE_LIMIT)

    # mark user as visited
    visited.add(steamid)
    
    # update progress bar
    progress.update(1)
    progress.refresh()

    # skip user if no profile summary was returned
    if not summary:
        continue

    # get profile visibility status
    visibility = summary.get("communityvisibilitystate", 1)

    # store basic user metadata
    users[steamid] = {
        "steamid": steamid,
        "public": visibility == 3,
        "country": summary.get("loccountrycode"),
        "account_created": summary.get("timecreated"),
        "last_logoff": summary.get("lastlogoff")
    }

    # skip private users because friends and games are not available
    if visibility != 3:
        continue

    # fetch friends for public users
    friends = get_friends(steamid)
    time.sleep(RATE_LIMIT)

    # store friendship edges and add friends to discovered users
    for f in friends:
        edges.append((steamid, f))
        discovered.add(f)

    # fetch owned games for public users
    games = get_games(steamid)
    time.sleep(RATE_LIMIT)

    # store user-game interactions and update game popularity counts
    if games:
        for g in games:
            appid = g["appid"]
            playtime = g.get("playtime_forever", 0)
            user_games.append((steamid, appid, playtime))
            game_counts[appid] += 1

    # save checkpoint periodically to avoid losing progress
    if len(visited) % CHECKPOINT_INTERVAL == 0:
        save_checkpoint()
    
# close progress bar after crawling is finished
progress.close()

# save final checkpoint
save_checkpoint()

# print completion message
tqdm.write("Done :D")

# create final game popularity table
all_games = sorted(game_counts.items(), key=lambda x: x[1], reverse=True)
# convert game counts to dataframe
games_df = pd.DataFrame(all_games, columns=["appid", "user_count"])
# store appid as string for safer csv handling
games_df["appid"] = games_df["appid"].astype(str)
# save final game-level output
games_df.to_csv("games.csv", index=False)