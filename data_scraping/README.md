# data_scraping

This folder contains scripts used to collect Steam user, friendship, user-game interaction, and game metadata data.

The scraping pipeline has two main steps:

1. crawl Steam users, friends, owned games, and playtime
2. enrich the game list with metadata from the Steam Store API

---

<details>
<summary>STEP 1: Crawl Steam users, friends and owned games</summary>

### CODE: `steam_crawl.py`

This script is the main Steam crawler.

It starts from one selected Steam user and expands the dataset by visiting discovered friends.  
For every visited user, the script attempts to collect:

- basic Steam profile information
- country
- account creation timestamp
- public/private profile status
- friend connections
- owned games
- playtime per owned game

The script uses the Steam Web API and requires the `STEAM_API_KEY` environment variable.

-----------------------------------

#### Configuration

Main parameters:

- `SUPERVISOR_ID = "76561198064675174"`
- `MAX_USERS = 100000`
- `RATE_LIMIT = 1.2`
- `CHECKPOINT_INTERVAL = 500`
- `RANDOM_SEED = 42`

The crawler uses a fixed random seed to make the random user selection reproducible.

-----------------------------------

#### Checkpointing

The script supports checkpointing.

If checkpoint files already exist, the crawler resumes from the previous state instead of starting from scratch.

Checkpoint files are saved every `500` visited users.

This is important because crawling can take a long time and may be interrupted by job time limits, API issues, or cluster problems.

-----------------------------------

#### Crawling strategy

The crawler keeps two user sets:

- `visited` — users that were already processed
- `discovered` — users found through friend lists but not necessarily visited yet

At every iteration, the script randomly selects one user from:
`discovered` ->  moved to `visited` later  
  
Then it fetches the user profile.  
  
If the user is private, only basic profile information is saved.  
If the user is public, the script also fetches:  
- friend list
- owned games
- playtime for each owned game

-------------------------------------

#### Steam API endpoints used
  
The script uses:  

- `ISteamUser/GetPlayerSummaries/v2/` - to fetch user profile information.
- `ISteamUser/GetFriendList/v1/` - to fetch user friends.
- `IPlayerService/GetOwnedGames/v1/` - to fetch owned games and playtime.

-------------------------------------

#### Outputs
  
The script creates checkpoint outputs inside:    
`checkpoint/`   
and a final game popularity file:  
`games.csv`
  
Main output files:  
- `checkpoint/visited.json`
- `checkpoint/discovered.json`
- `checkpoint/users.csv`
- `checkpoint/friends.csv`
- `checkpoint/user_games.csv`
- `games.csv`

-------------------------------------
  
<details> 
<summary>Show users.csv</summary>

| steamid           | public | country | account_created | last_logoff |
| ----------------- | ------ | ------- | --------------- | ----------- |
| 76561198064675174 | True   | IT      | 1338657689.0    |             |
| 76561198109425210 | True   | BE      | 1380726267.0    |             |
| 76561198281198045 | True   |         | 1454511095.0    |             |
| 76561197994839969 | True   | BE      | 1197478136.0    |             |
  
</details>

<details> 
<summary>Show friends.csv</summary>

| user_steamid      | friend_steamid    |
| ----------------- | ----------------- |
| 76561198064675174 | 76561197972380369 |
| 76561198064675174 | 76561198109425210 |
| 76561198109425210 | 76561198064675174 |
| 76561198109425210 | 76561198281198045 |

</details>

<details> 
<summary>Show user_games.csv</summary>

| steamid           | appid | playtime_minutes |
| ----------------- | ----- | ---------------- |
| 76561198064675174 | 400   | 367              |
| 76561198064675174 | 500   | 117              |
| 76561198064675174 | 550   | 0                |
| 76561198064675174 | 620   | 710              |

</details>

<details> 
<summary>Show raw games.csv</summary>

| appid  | user_count |
| ------ | ---------- |
| 730    | 38752      |
| 550    | 26253      |
| 218620 | 24022      |
| 431960 | 21856      |


*Important note:*
  
*The raw `games.csv` from this step contains only:*
- `appid`, `user_count`
*It does not contain game names, genres, developers, publishers, platforms, or release dates.*  
*Those fields are added in the next step.*
    
</details>
</details>   
  
  
<details> <summary>STEP 2: Enrich games with Steam Store metadata</summary>  
    
### CODE: scraping_games_enrich.py

This script enriches the raw game popularity file created by the crawler.  
It reads:  
- `games.csv`
  
where each row contains:  
- `appid`, `user_count`
  
Then, for every unique appid, it queries the Steam Store API and collects game metadata.
  
-------------------------------------
  
 Input  
- `games.csv`

Expected input columns:  
- `appid`, `user_count`

-------------------------------------

#### Steam Store API endpoint used

The script queries:
  
`https://store.steampowered.com/api/appdetails?appids={appid}`

For every game, it attempts to extract:  
- game name
- genres
- developer
- publisher
- supported platforms
- release date

-------------------------------------

#### Checkpointing
  
The script saves progress inside:  
- checkpoint_games/
  
Checkpoint files:  
- `checkpoint_games/enriched_games.csv`
- `checkpoint_games/visited_games.json`

*The checkpoint is saved every 50 processed games.  
This makes the script safe to resume if the job stops before all games are processed.* 
  
-------------------------------------

#### Processing strategy

The script first removes duplicate appids:  

`games_df = games_df.drop_duplicates(subset="appid")`

Then it skips every appid that already exists in:  
- checkpoint_games/visited_games.json
  
*This prevents duplicated work when resuming from checkpoint.*
  
------------------------------------- 
  
#### Metadata extraction

For every successfully fetched game, the script stores:  
- `appid`
- `name`
- `genres`
- `developer`
- `publisher`
- `platforms`
- `release_date`
- `user_count`
   
Multiple values, such as genres or developers, are joined with semicolons.  
  
Example:  
  
`Action;RPG`
`windows;linux`

-------------------------------------

#### Outputs:
    
The script writes the enriched output to:
- `checkpoint_games/enriched_games.csv`

<details> 
<summary>Show enriched games.csv</summary>

| appid  | name             | genres                                                                          | developer                       | publisher                | platforms     | release_date | user_count |
| ------ | ---------------- | ------------------------------------------------------------------------------- | ------------------------------- | ------------------------ | ------------- | ------------ | ---------- |
| 730    | Counter-Strike 2 | Action;Free To Play                                                             | Valve                           | Valve                    | windows;linux | 21 Aug, 2012 | 38752      |
| 550    | Left 4 Dead 2    | Action                                                                          | Valve                           | Valve                    | windows;linux | 16 Nov, 2009 | 26253      |
| 218620 | PAYDAY 2         | Action;RPG                                                                      | OVERKILL - a Starbreeze Studio. | Starbreeze Entertainment | windows;linux | 13 Aug, 2013 | 24022      |
| 431960 | Wallpaper Engine | Casual;Indie;Animation & Modeling;Design & Illustration;Photo Editing;Utilities | Wallpaper Engine Team           | Wallpaper Engine Team    | windows       | 16 Nov, 2018 | 21856      |

</details>
</details> 

# Data cleaning and LCC 
  
The next step is to filter our scraped datasets to LCC.

<details>
<summary>STEP 3: Data cleaning and LCC filtering</summary>

### CODE: `filtering_LCC.py`

This script filters the scraped Steam network to the Largest Connected Component (LCC).

The goal is to keep only users that belong to the largest connected part of the friendship graph.  
This makes the final dataset consistent for later network-based experiments.

-------------------------------------

#### Inputs

The script reads:

- `checkpoint/users.csv`
- `checkpoint/friends.csv`
- `checkpoint/user_games.csv`
- `enriched_games.csv`

`enriched_games.csv` is the enriched game metadata file produced after querying the Steam Store API.

-------------------------------------

#### Processing steps

The script first cleans identifier types:

- `steamid` values are converted to strings
- `appid` values are converted to integers

Then it keeps only friendship edges where both users exist in `users.csv`.

The friendship data originally contains directed rows:

- `user_steamid`
- `friend_steamid`

These rows are converted into undirected edges:

- `source`
- `target`

Duplicate undirected edges and self-loops are removed.

-------------------------------------

#### Largest Connected Component filtering

The script builds an undirected graph from the friendship edges using NetworkX.

It then finds the largest connected component:

`lcc_users = set(max(nx.connected_components(G), key=len))`
  
**Only users inside this component are kept.**  

------------------------------------- 
  
#### Filtered outputs

The script creates the cleaned final datasets:  
  
Output files:  
- `users.csv`      - Contains only users that belong to the LCC
- `user_games.csv` - Contains only user-game interactions for users in the LCC
- `games.csv`      - Contains only games that appear in the LCC-filtered user-game interactions
- `edges.csv`      - Contains only friendship edges where both endpoints are inside the LCC

</details>
<details> <summary>STEP 4: Create initial baseline dataset</summary>

CODE: `creating_baseline.py`
  
This script builds the initial positive-interaction baseline dataset from the LCC-filtered data.  
It uses the cleaned files created by filtering_LCC.py.  

-------------------------------------

#### Inputs:
- `users.csv`  
- `user_games.csv`
- `games.csv`

-------------------------------------

#### Account age features

The script converts the Steam account creation timestamp into a datetime value:  

`users["account_created"] = pd.to_datetime(  
    users["account_created"], unit="s", errors="coerce"  
)`    
Then it computes:
- `account_age_minutes`
  
*This is used to control unrealistic playtime values.*

-------------------------------------

#### Playtime capping
  
For each user-game interaction, the script caps playtime by the user's account age:  
  
`playtime_minutes_capped = min(playtime_minutes, account_age_minutes)`  
*This prevents impossible cases where a user has more recorded playtime than the account could physically allow.*

-------------------------------------

#### User-level features
  
The script computes user aggregate features:  
- `total_games_owned`
- `total_playtime_minutes`
- `median_playtime_minutes`
- `unique_genres_played`
  
*`total_playtime_minutes` is also capped by account age.*

-------------------------------------

#### Game-level features
  
The script computes:  
- `game_total_playtime_minutes`
  
*This is the total capped playtime for each game across the LCC-filtered interactions.*
  
The script also parses:  
- `release_date`
from the enriched game metadata.

-------------------------------------

#### Final baseline construction

The final dataset is created by merging:  
- user-game interactions
- user-level aggregate features
- enriched game metadata
- game-level aggregate features 
    
The output contains one row per positive user-game interaction.  

-------------------------------------

#### Output:
  
- `baseline_dataset.csv`

This file is used as the input for the next stage of dataset preparation (`dataset_preparation` folder) 

*Important note*
*`baseline_dataset.csv` is still a full positive-interaction dataset.
Later train-only feature recomputation and leakage-safe train/validation/test splitting are handled in the next folder:
`preparing_datasets/`*

</details>

