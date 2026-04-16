### CODE: `make_baseline_features_playtime_capped_owned_semicolon.py`
It creates the enriched baseline dataset `baseline_features_playtime_capped_owned_semicolon.csv` by recomputing user- and game-level features from training interactions only, capping playtime values, and adding owned and user_game_playtime.
  
The goal of this script is to prepare a cleaner feature-based baseline dataset while avoiding leakage from validation and test interactions.  
  
Inputs:  
- `user_games.csv`
-  `users.csv`
-  `baseline_dataset.csv`
  
-----------------------------------       
-  `validation_user_game_pairs.csv`
-  `test_user_game_pairs.csv`
  
 *These holdout pairs are excluded when computing features, so only training interactions contribute to user- and game-level aggregates.*
   
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

This means the resulting file represents only positive interactions, enriched with recalculated features.  
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
  
### CODE: `make_positive_splits_from_pairs.py`
  
This script creates positive-only train, validation, and test split files from the enriched baseline dataset.   
  
-----------------------------------  
  
Inputs:  
- `baseline_features_playtime_capped_owned_semicolon.csv`

| steamid           | appid | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name          | genres | developer | publisher | platforms     | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|-------|---------|-------------------|------------------------|-------------------------|----------------------|---------------|--------|-----------|-----------|---------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561198064675174 | 400   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Portal        | Action | Valve     | Valve     | windows;linux | 2007-10-10   | 7807.0     | 2544088.0                   | 1     | 367.0              |
| 76561198064675174 | 500   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Left 4 Dead   | Action | Valve     | Valve     | windows       | 2008-11-17   | 6018.0     | 7031495.0                   | 1     | 117.0              |
| 76561198064675174 | 550   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Left 4 Dead 2 | Action | Valve     | Valve     | windows;linux | 2009-11-16   | 16225.0    | 67545173.0                  | 1     | 0.0                |
- `validation_user_game_pairs.csv`
  
| steamid           | appid  | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name                    | genres                | developer                                                                 | publisher                                   | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|--------|---------|-------------------|------------------------|-------------------------|----------------------|-------------------------|-----------------------|---------------------------------------------------------------------------|---------------------------------------------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561198064675174 | 383870 | IT      | 168               | 498693.0               | 588.0                   | 15                   | Firewatch               | Adventure;Indie       | Campo Santo                                                             | Panic; Campo Santo                          | windows;mac;linux | 2016-02-09   | 1965.0     | 657036.0                    | 1     | 0.0                |
| 76561198109425210 | 594570 | BE      | 102               | 357949.0               | 644.5                   | 23                   | Total War: WARHAMMER II | Action;Strategy       | CREATIVE ASSEMBLY; Feral Interactive (Mac); Feral Interactive (Linux)    | SEGA; Feral Interactive (Mac); Feral Interactive (Linux) | windows;mac;linux | 2017-09-28   | 1208.0     | 8854491.0                   | 1     | 0.0                |
| 76561198281198045 | 1588010|         | 68                | 254639.0               | 194.5                   | 13                   | PGA TOUR 2K23           | RPG;Simulation;Sports | HB Studios                                                              | 2K                                          | windows          | 2022-10-13   | 123.0      | 283888.0                    | 1     | 0.0                |
  
- `test_user_game_pairs.csv`
  
| steamid           | appid  | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name                     | genres                  | developer                                                                 | publisher | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|--------|---------|-------------------|------------------------|-------------------------|----------------------|--------------------------|-------------------------|---------------------------------------------------------------------------|-----------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561198064675174 | 812140 | IT      | 168               | 498693.0               | 588.0                   | 15                   | Assassin's Creed® Odyssey | Action;Adventure;RPG    | Ubisoft Quebec; Ubisoft Montreal; Ubisoft Bucharest; Ubisoft Singapore; Ubisoft Montpellier; Ubisoft Kiev; Ubisoft Shanghai | Ubisoft   | windows          | 2018-10-05   | 2614.0     | 9709148.0                   | 1     | 0.0                |
| 76561198109425210 | 239140 | BE      | 102               | 357949.0               | 644.5                   | 23                   | Dying Light              | Action;RPG             | Techland                                                                  | Techland  | windows;mac;linux | 2015-01-26   | 7595.0     | 18529467.0                  | 1     | 0.0                |
| 76561198281198045 | 577670 |         | 68                | 254639.0               | 194.5                   | 13                   | Demolish & Build 2018    | Indie;Simulation       | Noble Muffins                                                            | Demolish Games S.A. | windows          | 2018-03-08   | 271.0      | 46561.0                     | 1     | 0.0                |
  
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
  
### CODE: `make_correct_splits.py`
  
It takes the already prepared positive interactions and adds negative samples, so each output file contains both:
  
games the user owns / interacted with (owned = 1)  
games the user did not own (owned = 0)  
  
 -----------------------------------   
   
Inputs:
- `train_positive.csv`

| steamid           | appid | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name          | genres | developer | publisher | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|-------|---------|-------------------|------------------------|-------------------------|----------------------|---------------|--------|-----------|-----------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561198064675174 | 400   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Portal        | Action | Valve     | Valve     | windows;linux    | 2007-10-10   | 7807.0     | 2544088.0                   | 1     | 367.0              |
| 76561198064675174 | 500   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Left 4 Dead   | Action | Valve     | Valve     | windows          | 2008-11-17   | 6018.0     | 7031495.0                   | 1     | 117.0              |
| 76561198064675174 | 550   | IT      | 168               | 498693.0               | 588.0                   | 15                   | Left 4 Dead 2 | Action | Valve     | Valve     | windows;linux    | 2009-11-16   | 16225.0    | 67545173.0                  | 1     | 0.0                |
  
- `val_positive.csv`
  
| steamid           | appid  | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name                    | genres                | developer                                                                 | publisher                                   | platforms        | release_date | user_count | game_total_playtime_minutes | owned | user_game_playtime |
|-------------------|--------|---------|-------------------|------------------------|-------------------------|----------------------|-------------------------|-----------------------|---------------------------------------------------------------------------|---------------------------------------------|------------------|--------------|------------|-----------------------------|-------|--------------------|
| 76561198064675174 | 383870 | IT      | 168               | 498693.0               | 588.0                   | 15                   | Firewatch               | Adventure;Indie       | Campo Santo                                                             | Panic; Campo Santo                          | windows;mac;linux | 2016-02-09   | 1965.0     | 657036.0                    | 1     | 0.0                |
| 76561198109425210 | 594570 | BE      | 102               | 357949.0               | 644.5                   | 23                   | Total War: WARHAMMER II | Action;Strategy       | CREATIVE ASSEMBLY; Feral Interactive (Mac); Feral Interactive (Linux)    | SEGA; Feral Interactive (Mac); Feral Interactive (Linux) | windows;mac;linux | 2017-09-28   | 1208.0     | 8854491.0                   | 1     | 0.0                |
| 76561198281198045 | 1588010|         | 68                | 254639.0               | 194.5                   | 13                   | PGA TOUR 2K23           | RPG;Simulation;Sports | HB Studios                                                              | 2K                                          | windows          | 2022-10-13   | 123.0      | 283888.0                    | 1     | 0.0                |
  
- `test_positive.csv` 
- `games.csv` - game catalog
  
| appid  | name              | genres             | developer                          | publisher                 | platforms        | release_date   | user_count |
|--------|-------------------|--------------------|------------------------------------|---------------------------|------------------|----------------|------------|
| 730    | Counter-Strike 2  | Action;Free To Play| Valve                              | Valve                     | windows;linux    | 21 Aug, 2012   | 38752      |
| 550    | Left 4 Dead 2     | Action             | Valve                              | Valve                     | windows;linux    | 16 Nov, 2009   | 26253      |
| 218620 | PAYDAY 2          | Action;RPG         | OVERKILL - a Starbreeze Studio.    | Starbreeze Entertainment  | windows;linux    | 13 Aug, 2013   | 24022      |
  
-----------------------------------     
  
Negatives per positive:
- Train : 10 negatives / 1 positive
- Val : 100 negatives / 1 positive
- Test : 100 negatives / 1 positive

Negative sampling strategy (weighted sampling): 
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
  

  
