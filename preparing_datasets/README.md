<details>
<summary>STEP 1. Selecting positives for validation & training splits</summary>

### CODE: `selecting_pos_pairs_for_val_test_split.py`

This script selects positive user–game interaction pairs that will later be used as validation and test holdout pairs.

The goal of this script is to create a leave-two-out split at the user level, where each eligible user contributes:

- 1 positive interaction to validation
- 1 positive interaction to test

These pairs are later excluded when recomputing training-based features, so they act as true holdout interactions and help prevent leakage.

-----------------------------------

Inputs:
- `baseline_dataset.csv` (output from last step from folder `data_scraping/`)

Only the following columns are loaded:

- `steamid`
- `appid`

-----------------------------------

#### Duplicate removal

The script first removes duplicate `(steamid, appid)` pairs.

This ensures that each user–game interaction is represented only once before sampling validation and test pairs.

-----------------------------------

#### User filtering

The script keeps only users with at least:

- `MIN_GAMES = 5`

positive interactions.

Users with fewer than 5 games are removed from the holdout-pair selection process.

This makes sure that after selecting one validation and one test interaction, each user still has enough remaining interactions for training.

-----------------------------------

#### Leave-two-out holdout selection

For every eligible user, the script randomly samples two owned games:

- the first sampled game becomes the validation pair
- the second sampled game becomes the test pair

This produces exactly one validation and one test positive interaction per user.

The sampling is random and uses:

- `random_state=None`

so the selected pairs may differ between script runs unless a fixed seed is added.

-----------------------------------

#### Outputs:

- `validation_user_game_pairs.csv`
- `test_user_game_pairs.csv`

These files contain only:

- `steamid`
- `appid`

They are later used by `make_baseline_features_playtime_capped_owned_semicolon.py` to exclude validation and test interactions from training-based feature computation.

-----------------------------------

</details>
  
<details>
<summary>STEP 2: create dataset</summary>
    
### CODE: `make_baseline_features_playtime_capped_owned_semicolon.py`  
  
It creates the enriched baseline dataset `baseline_features_playtime_capped_owned_semicolon.csv` by recomputing user- and game-level features from training interactions only, capping playtime values, and adding owned and user_game_playtime.
  
The goal of this script is to prepare a cleaner feature-based baseline dataset while avoiding leakage from validation and test interactions.  
  
Inputs:  
- `user_games.csv`
-  `users.csv`
-  `baseline_dataset.csv`
  (outputs from folder `data_scraping/`)
  
-----------------------------------       
-  `validation_user_game_pairs.csv`
-  `test_user_game_pairs.csv`
  
 *These holdout pairs are excluded when computing training-based features, so validation and test interactions do not contribute to aggregate or interaction-level feature values.*
   
-----------------------------------   
#### Playtime capping strategy
The script computes `account_age_minutes` from `users.csv` and uses it to cap unrealistic playtime values.    
For each interaction:    
- if account age is known → playtime_minutes is capped by account_age_minutes  
- otherwise → playtime_minutes is capped by the global 99.9th percentile of playtime  
      
This produces a cleaned playtime feature.    
The purpose is to reduce the impact of unrealistic or corrupted playtime values.  
  
-----------------------------------     
  
#### Feature recomputation strategy
    
Before computing new features, the script removes the original aggregate columns from `baseline_dataset.csv` and recalculates them using only training interactions.    
  
Recomputed user-level features:    
  
`total_games_owned`  
`total_playtime_minutes`  
`median_playtime_minutes`  
`unique_genres_played`  
  
Recomputed game-level features:  
  
`user_count`  
`game_total_playtime_minutes`  
  
This ensures that feature values are based only on the training portion of the interaction data.    
  
-----------------------------------    
  
#### user_game_playtime
  
The script also adds a user–game-specific feature:  
  
`user_game_playtime`
  
This value is taken from the capped playtime of a given (steamid, appid) interaction in training data.  
  
For validation and test holdout pairs:  
  
`user_game_playtime = 0`  
    
This prevents leakage of true holdout interaction strength into downstream datasets.   
  
-----------------------------------   
  
#### owned
  
The script adds:  
  
`owned = 1`  
for every row in the output dataset.  

This means the resulting file still contains only positive interactions, now enriched with recomputed features.  
  
#### Leakage prevention
The script is careful not to use validation and test interactions when building features.  
  
It explicitly excludes:  
- all pairs from `validation_user_game_pairs.csv`  
- all pairs from `test_user_game_pairs.csv`    
when computing:  
  
- user aggregates  
- game aggregates  
- user genre diversity  
- user–game playtime
  
-----------------------------------   
  
Output:
  
- `baseline_features_playtime_capped_owned_semicolon.csv`
  
-----------------------------------      
</details>
<details>
<summary>STEP 3: Create positive train, validation & test</summary>
    
### CODE: `make_positive_splits_from_pairs.py`
    
This script creates positive-only train, validation, and test split files from the enriched baseline dataset.   
  
-----------------------------------  
  
Inputs:  
- `baseline_features_playtime_capped_owned_semicolon.csv`

<details>
<summary>Show baseline_features_playtime_capped_owned_semicolon.csv</summary>  
  
| steamid           | appid | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name          | genres | developer | publisher | platforms     | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|-------|---------|-------------------|------------------------|-------------------------|----------------------|---------------|--------|-----------|-----------|---------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561198064675174 | 400   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Portal        | Action | Valve     | Valve     | windows;linux | 2007-10-10   | 7807.0     | 2544088.0                   | 1     | 367.0              |
| 76561198064675174 | 500   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Left 4 Dead   | Action | Valve     | Valve     | windows       | 2008-11-17   | 6018.0     | 7031495.0                   | 1     | 117.0              |
| 76561198064675174 | 550   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Left 4 Dead 2 | Action | Valve     | Valve     | windows;linux | 2009-11-16   | 16225.0    | 67545173.0                  | 1     | 0.0                |

</details>
  
- `validation_user_game_pairs.csv`

<details>
<summary>Show validation_user_game_pairs.csv</summary>  
  
| steamid           | appid  | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name                    | genres                | developer                                                                 | publisher                                   | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|--------|---------|-------------------|------------------------|-------------------------|----------------------|-------------------------|-----------------------|---------------------------------------------------------------------------|---------------------------------------------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561198064675174 | 383870 | IT      | 168               | 498693.0               | 588.0                   | 15                   | Firewatch               | Adventure;Indie       | Campo Santo                                                             | Panic; Campo Santo                          | windows;mac;linux | 2016-02-09   | 1965.0     | 657036.0                    | 1     | 0.0                |
| 76561198109425210 | 594570 | BE      | 102               | 357949.0               | 644.5                   | 23                   | Total War: WARHAMMER II | Action;Strategy       | CREATIVE ASSEMBLY; Feral Interactive (Mac); Feral Interactive (Linux)    | SEGA; Feral Interactive (Mac); Feral Interactive (Linux) | windows;mac;linux | 2017-09-28   | 1208.0     | 8854491.0                   | 1     | 0.0                |
| 76561198281198045 | 1588010|         | 68                | 254639.0               | 194.5                   | 13                   | PGA TOUR 2K23           | RPG;Simulation;Sports | HB Studios                                                              | 2K                                          | windows          | 2022-10-13   | 123.0      | 283888.0                    | 1     | 0.0                |

</details>
  
- `test_user_game_pairs.csv`

<details>
<summary>Show test_user_game_pairs.csv</summary>
    
| steamid           | appid  | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name                     | genres                  | developer                                                                 | publisher | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|--------|---------|-------------------|------------------------|-------------------------|----------------------|--------------------------|-------------------------|---------------------------------------------------------------------------|-----------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561198064675174 | 812140 | IT      | 168               | 498693.0               | 588.0                   | 15                   | Assassin's Creed® Odyssey | Action;Adventure;RPG    | Ubisoft Quebec; Ubisoft Montreal; Ubisoft Bucharest; Ubisoft Singapore; Ubisoft Montpellier; Ubisoft Kiev; Ubisoft Shanghai | Ubisoft   | windows          | 2018-10-05   | 2614.0     | 9709148.0                   | 1     | 0.0                |
| 76561198109425210 | 239140 | BE      | 102               | 357949.0               | 644.5                   | 23                   | Dying Light              | Action;RPG             | Techland                                                                  | Techland  | windows;mac;linux | 2015-01-26   | 7595.0     | 18529467.0                  | 1     | 0.0                |
| 76561198281198045 | 577670 |         | 68                | 254639.0               | 194.5                   | 13                   | Demolish & Build 2018    | Indie;Simulation       | Noble Muffins                                                            | Demolish Games S.A. | windows          | 2018-03-08   | 271.0      | 46561.0                     | 1     | 0.0                |

</details>
  
-----------------------------------     
  
For each (steamid, appid) pair:  
  
- if the pair appears in validation_user_game_pairs.csv → the row is written to `val_positive.csv` 
- if the pair appears in test_user_game_pairs.csv → the row is written to `test_positive.csv`
- otherwise → the row is written to `train_positive.csv`

*The script also checks whether validation and test pair sets overlap. If any overlap is found, it stops with an error to prevent split contamination.*
  
-----------------------------------   
  
Outputs:
- `train_positive.csv`  
- `val_positive.csv`  
- `test_positive.csv`
  
-----------------------------------     
  
</details>  
<details>
<summary>STEP 4: Adding negatives to positive splits</summary>
    
### CODE: `make_correct_splits.py`
  
It takes the already prepared positive interactions and adds negative samples, so each output file contains both:
  
games the user owns / interacted with (owned = 1)  
games the user did not own (owned = 0)  
  
 -----------------------------------   
   
Inputs:
- `train_positive.csv`
<details>
<summary>Show val_positive.csv</summary>  
    
| steamid           | appid | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name          | genres | developer | publisher | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|-------|---------|-------------------|------------------------|-------------------------|----------------------|---------------|--------|-----------|-----------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561198064675174 | 400   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Portal        | Action | Valve     | Valve     | windows;linux    | 2007-10-10   | 7807.0     | 2544088.0                   | 1     | 367.0              |
| 76561198064675174 | 500   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Left 4 Dead   | Action | Valve     | Valve     | windows          | 2008-11-17   | 6018.0     | 7031495.0                   | 1     | 117.0              |
| 76561198064675174 | 550   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Left 4 Dead 2 | Action | Valve     | Valve     | windows;linux    | 2009-11-16   | 16225.0    | 67545173.0                  | 1     | 0.0                |
  
</details>  
  
- `val_positive.csv`

<details>
<summary>Show val_positive.csv</summary>  
    
| steamid           | appid  | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name                    | genres                | developer                                                                 | publisher                                   | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|--------|---------|-------------------|------------------------|-------------------------|----------------------|-------------------------|-----------------------|---------------------------------------------------------------------------|---------------------------------------------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561198064675174 | 383870 | IT      | 168               | 498693.0               | 588.0                   | 15                   | Firewatch               | Adventure;Indie       | Campo Santo                                                             | Panic; Campo Santo                          | windows;mac;linux | 2016-02-09   | 1965.0     | 657036.0                    | 1     | 0.0                |
| 76561198109425210 | 594570 | BE      | 102               | 357949.0               | 644.5                   | 23                   | Total War: WARHAMMER II | Action;Strategy       | CREATIVE ASSEMBLY; Feral Interactive (Mac); Feral Interactive (Linux)    | SEGA; Feral Interactive (Mac); Feral Interactive (Linux) | windows;mac;linux | 2017-09-28   | 1208.0     | 8854491.0                   | 1     | 0.0                |
| 76561198281198045 | 1588010|         | 68                | 254639.0               | 194.5                   | 13                   | PGA TOUR 2K23           | RPG;Simulation;Sports | HB Studios                                                              | 2K                                          | windows          | 2022-10-13   | 123.0      | 283888.0                    | 1     | 0.0                |
  
</details>
  
- `test_positive.csv`
<details>
<summary>Show test_posotive.csv</summary> 
    
| steamid           | appid  | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name                     | genres               | developer                                                                 | publisher              | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|--------|---------|-------------------|------------------------|-------------------------|----------------------|--------------------------|----------------------|---------------------------------------------------------------------------|------------------------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561198064675174 | 812140 | IT      | 168               | 498693.0               | 588.0                   | 15                   | Assassin's Creed® Odyssey | Action;Adventure;RPG | Ubisoft Quebec; Ubisoft Montreal; Ubisoft Bucharest; Ubisoft Singapore; Ubisoft Montpellier; Ubisoft Kiev; Ubisoft Shanghai | Ubisoft                | windows          | 2018-10-05   | 2614.0     | 9709148.0                   | 1     | 0.0                |
| 76561198109425210 | 239140 | BE      | 102               | 357949.0               | 644.5                   | 23                   | Dying Light              | Action;RPG           | Techland                                                                  | Techland               | windows;mac;linux | 2015-01-26   | 7595.0     | 18529467.0                  | 1     | 0.0                |
| 76561198281198045 | 577670 |         | 68                | 254639.0               | 194.5                   | 13                   | Demolish & Build 2018    | Indie;Simulation     | Noble Muffins                                                            | Demolish Games S.A.    | windows          | 2018-03-08   | 271.0      | 46561.0                     | 1     | 0.0                |
  
</details>
  
- `games.csv` - game catalog
<details>
<summary>Show games.csv</summary>  
    
| appid  | name              | genres             | developer                          | publisher                 | platforms        | release_date   | user_count |
|--------|-------------------|--------------------|------------------------------------|---------------------------|------------------|----------------|------------|
| 730    | Counter-Strike 2  | Action;Free To Play| Valve                              | Valve                     | windows;linux    | 21 Aug, 2012   | 38752      |
| 550    | Left 4 Dead 2     | Action             | Valve                              | Valve                     | windows;linux    | 16 Nov, 2009   | 26253      |
| 218620 | PAYDAY 2          | Action;RPG         | OVERKILL - a Starbreeze Studio.    | Starbreeze Entertainment  | windows;linux    | 13 Aug, 2013   | 24022      |
</details>
  
-----------------------------------     
  
Negatives per positive:
- Train : 10 negatives / 1 positive
- Val : 100 negatives / 1 positive
- Test : 100 negatives / 1 positive

#### Negative sampling strategy (weighted sampling): 
Target:  
- **30 % popular games**  
- **70% random**  
If its not possible (user has not enough popular games to sample from for remaining negatives -> fill with random, if not enough random -> duplicates here are allowed inside a split)
  
It uses a **round robin** for processing order  
train → val → test → train → val → test ...  
  
**Why?** 
  
To make sure:  
  
- negatives are assigned fairly across splits  
- one split doesn’t “consume” all good candidates first  

Script is being very careful with data leaking:  
It builds a forbidden set:  
- all user’s positive games  
- games already used in other splits  

This prevents the same sampled negative game from appearing across train, validation, and test for the same user.  
  
-----------------------------------   
  
Outputs:
- `train.csv`
- `val.csv`
- `test.csv`
  
-----------------------------------   

</details>
<details>
<summary>STEP 5: enrich prepared splits with user genre-group playtime features</summary>
     
### CODE: `build_groups_playtime_correct_splits.py`

It enriches the correct_splits train, validation, and test  (step above) datasets with user genre-group playtime features.

The script replaces the single `user_game_playtime` feature with a set of aggregated user preference features based on broader genre groups such as *Action, Adventure, RPG, Simulation, and Strategy*.
  
-----------------------------------  
  
Inputs:  
- `train.csv`
<details>
<summary>Show train.csv</summary>

  | steamid           | appid  | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name             | genres  | developer | publisher | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|--------|---------|-------------------|------------------------|-------------------------|----------------------|------------------|---------|-----------|-----------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561197960266945 | 10     | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Counter-Strike   | Action  | Valve     | Valve     | windows;mac;linux | 2000-11-01   | 8366.0     | 107248640.0                 | 1     | 2218.0             |
| 76561197960266945 | 1517290| RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Battlefield™ 2042 | Action;Adventure;Casual | DICE | Electronic Arts | windows | 19 Nov, 2021 | 6312       |                             | 0     | 0                  |
| 76561197960266945 | 1361000| RU      | 1503              | 1091628.0              | 60.0                    | 27                   | In Silence       | Action  | Ravenhood Games | Ravenhood Games | windows;mac | 29 Oct, 2021 | 753        |                             | 0     | 0                  |
  
 </details>
   
- `val.csv`
<details>
<summary>Show val.csv</summary>

| steamid           | appid  | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name                 | genres                          | developer           | publisher         | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|--------|---------|-------------------|------------------------|-------------------------|----------------------|----------------------|---------------------------------|---------------------|-------------------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561197960266945 | 569860 | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Thimbleweed Park™    | Adventure;Indie                | Terrible Toybox     | Terrible Toybox   | windows;mac;linux | 2017-03-30   | 91.0       | 28608.0                     | 1     | 0.0                |
| 76561197960266945 | 960090 | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Bloons TD 6          | Strategy                       | Ninja Kiwi          | Ninja Kiwi        | windows;mac      | 17 Dec, 2018 | 6034       |                             | 0     | 0                  |
| 76561197960266945 | 1190340| RU      | 1503              | 1091628.0              | 60.0                    | 27                   | SUPER PEOPLE         | Action;Casual;Massively Multiplayer;Free To Play;Early Access | Wonder People | Wonder Games | windows | 8 Oct, 2022 | 1378 |                             | 0     | 0                  |
  
 </details>
   
- `test.csv`
<details>
<summary>Show test.csv</summary>
    
| steamid           | appid  | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name                    | genres                | developer          | publisher          | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|--------|---------|-------------------|------------------------|-------------------------|----------------------|-------------------------|-----------------------|--------------------|--------------------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561197960266945 | 287120 | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Ionball 2: Ionstorm     | Action;Casual         | Ironsun Studios    | KISS ltd           | windows          | 2014-06-06   | 790.0      | 133344.0                    | 1     | 0.0                |
| 76561197960266945 | 451020 | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Battle Chasers: Nightwar | Indie;RPG             | Airship Syndicate  | THQ Nordic         | windows;mac;linux | 3 Oct, 2017 | 763        |                             | 0     | 0                  |
| 76561197960266945 | 516480 | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Pinkman                 | Action;Adventure;Casual;Indie | Viridino Studios | Viridino Studios | windows | 16 Jan, 2017 | 151 |                             | 0     | 0                  |
  
  </details>
    
*These input files already contain both positive (owned = 1) and negative (owned = 0) user–game interactions.*
  
-----------------------------------

#### Genre-group mapping:
  
The script defines a manual mapping from raw game genre labels to broader genre groups.
<details>
<summary>Show genre group mapping</summary>

| Genre Group           | Mapped Genres                                                                 |
|----------------------|------------------------------------------------------------------------------|
| Action               | Action, Acción, Akcja, Aksiyon, Actie, Akční, Экшены, 動作                   |
| Adventure            | Adventure, Aventura, Avontuur, 冒险, Приключенческие gry, Приключенческие игры, Macera |
| RPG                  | RPG, RYO, Rol, Ролевые игры, 角色扮演                                        |
| Casual               | Casual, Occasionnel, Казуальные игры                                         |
| Indie                | Indie, Indépendant, 独立, Инди                                               |
| Racing               | Racing                                                                       |
| Simulation           | Simulation, Simuladores, Symulacje, Симуляторы                               |
| Strategy             | Strategy, Strategie, Стратегии                                                |
| Sports               | Sport, Sports                                                                |
| Violent              | Gore, Violent                                                                |
| Adult                | Nudity, Sexual Content                                                       |
| Non-gameplay_Tools   | Education, Documentary, Movie, Tutorial, Accounting, Audio Production, Video Production, Photo Editing, Design & Illustration, Web Publishing, Utilities, Software Training, Game Development, Animation & Modeling |
| Other                | Early Access, Episodic, Free To Play, Massively Multiplayer, Бесплатные       |

</details>
  
-----------------------------------
  
#### User profile construction:

The script builds a user-level genre-group playtime profile using only positive interactions from the **training** split.  
  
For each user:  
- only rows with owned = 1 are used  
- user_game_playtime is aggregated across mapped genre groups  
- if a game belongs to multiple genre groups, its playtime is divided equally across them  
  
This produces a historical user preference profile such as:  
- `user_playtime_group_Action`  
- `user_playtime_group_RPG`  
- `user_playtime_group_Simulation`
    
-----------------------------------
  
#### Feature transformation
  
For each dataset row, the script removes:  
- `user_game_playtime`

and replaces it with the full set of genre-group playtime features:
- `user_playtime_group_Action`
- `user_playtime_group_Adventure`
- `user_playtime_group_RPG`
  ...

*Each row is therefore represented by the user’s historical playtime distribution across genre groups rather than by a single interaction-level playtime value.*
  
-----------------------------------
  
#### Leakage prevention:
To avoid data leakage, the user genre-group profile is built only from the training split.  
  
In addition, for positive training rows:  
  
the current game’s own contribution is subtracted from the user profile before writing the row  
  
This prevents leakage-from-self, where the model could otherwise directly benefit from the target game’s own playtime contribution being present in its input features.  
  
Validation and test rows use the same user profile built from training data only.  
  
-----------------------------------
  
Outputs:
- `correct_splits/with_genre_groups/train.csv`
- `correct_splits/with_genre_groups/val.csv`
- `correct_splits/with_genre_groups/test.csv`
    
-----------------------------------    
  
</details>
<details>
<summary>STEP 6: Enrich baseline dataset with additional network features to create network datasets</summary>

### CODE: build_network_dataset_correct_splits.py

It enriches the datasets with additional network features.  
  
Input:
- `train.csv`
  
<details>
<summary>Show train.csv</summary>

| steamid           | appid   | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name              | genres                    | developer        | publisher        | platforms          | release_date | user_count | game_total_playtime_minutes | owned | user_playtime_group_Action | user_playtime_group_Adventure | user_playtime_group_RPG | user_playtime_group_Casual | user_playtime_group_Indie | user_playtime_group_Racing | user_playtime_group_Simulation | user_playtime_group_Strategy | user_playtime_group_Sports | user_playtime_group_Violent | user_playtime_group_Adult | user_playtime_group_Non-gameplay_Tools | user_playtime_group_Other |
|-------------------|---------|---------|-------------------|------------------------|-------------------------|----------------------|-------------------|---------------------------|------------------|------------------|--------------------|--------------|------------|-----------------------------|-------|----------------------------|-------------------------------|-------------------------|----------------------------|---------------------------|----------------------------|-------------------------------|-----------------------------|---------------------------|----------------------------|--------------------------|-----------------------------------------|---------------------------|
| 76561197960266945 | 10      | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Counter-Strike    | Action                    | Valve            | Valve            | windows;mac;linux  | 304.0        | 8366.0     | 107248640.0                 | 1     | 575679.447619              | 126260.064286                 | 62692.183333            | 25453.047619               | 55046.947619              | 1200.797619                | 17330.330952                  | 76800.397619                | 1220.666667                | 86.0                       | 86.0                     | 62053.0                                 | 84251.116667              |
| 76561197960266945 | 1517290 | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Battlefield™ 2042 | Action;Adventure;Casual   | DICE             | Electronic Arts  | windows            | 52.0         | 6312.0     | 12254570.0                  | 0     | 577897.447619              | 126260.064286                 | 62692.183333            | 25453.047619               | 55046.947619              | 1200.797619                | 17330.330952                  | 76800.397619                | 1220.666667                | 86.0                       | 86.0                     | 62053.0                                 | 84251.116667              |
| 76561197960266945 | 1361000 | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | In Silence        | Action                    | Ravenhood Games  | Ravenhood Games  | windows;mac        | 53.0         | 753.0      | 68233.0                     | 0     | 577897.447619              | 126260.064286                 | 62692.183333            | 25453.047619               | 55046.947619              | 1200.797619                | 17330.330952                  | 76800.397619                | 1220.666667                | 86.0                       | 86.0                     | 62053.0                                 | 84251.116667              |
  
</details>
  
- `val.csv`

<details>
<summary>Show val.csv</summary>

| steamid           | appid   | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name               | genres                                              | developer         | publisher         | platforms          | release_date | user_count | game_total_playtime_minutes | owned | user_playtime_group_Action | user_playtime_group_Adventure | user_playtime_group_RPG | user_playtime_group_Casual | user_playtime_group_Indie | user_playtime_group_Racing | user_playtime_group_Simulation | user_playtime_group_Strategy | user_playtime_group_Sports | user_playtime_group_Violent | user_playtime_group_Adult | user_playtime_group_Non-gameplay_Tools | user_playtime_group_Other |
|-------------------|---------|---------|-------------------|------------------------|-------------------------|----------------------|--------------------|-----------------------------------------------------|-------------------|-------------------|--------------------|--------------|------------|-----------------------------|-------|----------------------------|-------------------------------|-------------------------|----------------------------|---------------------------|----------------------------|-------------------------------|-----------------------------|---------------------------|----------------------------|--------------------------|-----------------------------------------|---------------------------|
| 76561197960266945 | 569860  | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Thimbleweed Park™  | Adventure;Indie                                    | Terrible Toybox   | Terrible Toybox   | windows;mac;linux  | 108.0        | 91.0       | 28608.0                     | 1     | 577897.447619              | 126260.064286                 | 62692.183333            | 25453.047619               | 55046.947619              | 1200.797619                | 17330.330952                  | 76800.397619                | 1220.666667                | 86.0                       | 86.0                     | 62053.0                                 | 84251.116667              |
| 76561197960266945 | 960090  | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Bloons TD 6        | Strategy                                           | Ninja Kiwi        | Ninja Kiwi        | windows;mac        | 87.0         | 6034.0     | 11950083.0                  | 0     | 577897.447619              | 126260.064286                 | 62692.183333            | 25453.047619               | 55046.947619              | 1200.797619                | 17330.330952                  | 76800.397619                | 1220.666667                | 86.0                       | 86.0                     | 62053.0                                 | 84251.116667              |
| 76561197960266945 | 1190340 | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | SUPER PEOPLE       | Action;Casual;Massively Multiplayer;Free To Play;Early Access | Wonder People     | Wonder Games      | windows            | 41.0         | 1378.0     | 484742.0                    | 0     | 577897.447619              | 126260.064286                 | 62692.183333            | 25453.047619               | 55046.947619              | 1200.797619                | 17330.330952                  | 76800.397619                | 1220.666667                | 86.0                       | 86.0                     | 62053.0                                 | 84251.116667              |
  
 </details> 
   
- `test.csv`
  
<details>
<summary>Show test.csv</summary>
    
  | steamid           | appid  | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name                    | genres                        | developer         | publisher         | platforms          | release_date | user_count | game_total_playtime_minutes | owned | user_playtime_group_Action | user_playtime_group_Adventure | user_playtime_group_RPG | user_playtime_group_Casual | user_playtime_group_Indie | user_playtime_group_Racing | user_playtime_group_Simulation | user_playtime_group_Strategy | user_playtime_group_Sports | user_playtime_group_Violent | user_playtime_group_Adult | user_playtime_group_Non-gameplay_Tools | user_playtime_group_Other |
|-------------------|--------|---------|-------------------|------------------------|-------------------------|----------------------|-------------------------|-------------------------------|-------------------|-------------------|--------------------|--------------|------------|-----------------------------|-------|----------------------------|-------------------------------|-------------------------|----------------------------|---------------------------|----------------------------|-------------------------------|-----------------------------|---------------------------|----------------------------|--------------------------|-----------------------------------------|---------------------------|
| 76561197960266945 | 287120 | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Ionball 2: Ionstorm     | Action;Casual                | Ironsun Studios   | KISS ltd          | windows            | 141.0        | 790.0      | 133344.0                    | 1     | 577897.447619              | 126260.064286                 | 62692.183333            | 25453.047619               | 55046.947619              | 1200.797619                | 17330.330952                  | 76800.397619                | 1220.666667                | 86.0                       | 86.0                     | 62053.0                                 | 84251.116667              |
| 76561197960266945 | 451020 | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Battle Chasers: Nightwar | Indie;RPG                   | Airship Syndicate | THQ Nordic        | windows;mac;linux  | 101.0        | 763.0      | 227626.0                    | 0     | 577897.447619              | 126260.064286                 | 62692.183333            | 25453.047619               | 55046.947619              | 1200.797619                | 17330.330952                  | 76800.397619                | 1220.666667                | 86.0                       | 86.0                     | 62053.0                                 | 84251.116667              |
| 76561197960266945 | 516480 | RU      | 1503              | 1091628.0              | 60.0                    | 27                   | Pinkman                 | Action;Adventure;Casual;Indie | Viridino Studios  | Viridino Studios  | windows            | 110.0        | 151.0      | 26798.0                     | 0     | 577897.447619              | 126260.064286                 | 62692.183333            | 25453.047619               | 55046.947619              | 1200.797619                | 17330.330952                  | 76800.397619                | 1220.666667                | 86.0                       | 86.0                     | 62053.0                                 | 84251.116667              |
  
</details>

- `users_friend_counts.csv`
  
<details>
<summary>Show users_friend_counts.csv</summary>

  | steamid           | friend_count |
|-------------------|-------------|
| 76561198064675174 | 28          |
| 76561198109425210 | 16          |
| 76561198281198045 | 22          |
  
</details>
   
- `game_pca_embeddings_k32_trainonly.csv`
<details>
<summary>Show game_pca_embeddings_k32_trainonly.csv</summary>

  | game_emb_0 | game_emb_1 | game_emb_2 | game_emb_3 | ... | game_emb_30 | game_emb_31 | game_index | appid |
|------------|------------|------------|------------|-----|-------------|-------------|------------|-------|
| 646.1727   | 249.22913  | 88.80311   | 43.777756  | ... | -1.5141871  | 0.69528323  | 0          | 10    |
| 547.0699   | 167.5004   | 39.855713  | 11.052478  | ... | 0.20238768  | -1.7163113  | 1          | 20    |
| 536.5776   | 162.22127  | 39.3537    | 12.142582  | ... | 1.0581001   | -3.8984723  | 2          | 30    |
  
</details>
  
-----------------------------------

#### Friend count feature:
  
The script loads user-level friend counts from `users_friend_counts.csv`.  

For each row:  
  
the steamid is used to look up the user’s number of friends   
the value is stored in a new column:  
    
- `friend_count`
    
 -----------------------------------  
   
#### Game embedding features

The script also loads PCA-based game embeddings from:  
  
- `game_pca_embeddings_k32_trainonly.csv`
  
For each row:  
  
the appid is used to look up the game embedding  
all embedding dimensions are appended as new columns.  
  
 -----------------------------------  
   
Outputs:
- train.csv  
- val.csv  
- test.csv
  
 -----------------------------------
   
</details>


<details>
<summary>STEP 7: Fill game_total_playtime features</summary>

### CODE: fill_game_total_playtime_from_baseline.py

#### FIX 
This script repairs missing `game_total_playtime_minutes` values in both `with_genre_groups` and `with_genre_groups_network` datasets by mapping each `appid` to the corresponding value from `baseline_features_playtime_capped_owned_semicolon.csv`.  
  
 -----------------------------------
   
Inputs:
- "with_genre_groups" / `train.csv`
- "with_genre_groups" / `val.csv`
- "with_genre_groups" / `test.csv`
-  "with_genre_groups_network" / `train.csv`
-  "with_genre_groups_network" / `val.csv`
- "with_genre_groups_network" / `test.csv`
  
*train, val and test sets for both datasets, with and without netwoek features* 
  
 -----------------------------------
 
The script reads:  
  
- `appid`
- `game_total_playtime_minutes`
  
from the baseline feature dataset and builds an `appid` → `game_total_playtime_minutes` mapping using the first non-null value available for each game.  
  
Then, for each target file:  
  
- rows with missing `game_total_playtime_minutes` are identified
- missing values are filled by matching on `appid`
  
-----------------------------------
  
#### Backup behavior
  
Before overwriting each repaired file, the script creates a backup copy with the extension:
`.bak`  

The script overwrites the original dataset files after filling missing values.  
As a result, the corrected versions remain in the same directories. 

*the "with_genre_groups_network" was then renamed manually for "with_genre_groups_network_fixed" as input to models in steps of training models in `models/`*
