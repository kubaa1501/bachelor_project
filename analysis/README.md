# Analysis

This folder contains the final analysis scripts used to understand **why the network / embedding model improves XGBoost recommendations**.

The analysis is split into two steps:

1. `graph_structure_analysis.py`  
   graph-structure features per game

2. `thesis_analysis.py`  
   compares baseline XGBoost vs XGBoost with `game_emb_0`

The outputs are saved in:

```text
analysis_metrics/
analysis_plots/
```
  
--------------------------------

<details>
<summary>1. Graph structure analysis </summary>

#### CODE: `graph_structure_analysis.py`

#### Goal

This script computes extra graph-structure metrics for each game.
It uses the user-game graph and user-user friendship graph to describe each game not only by popularity, but also by its position in the graph.
  
--------------------------------

Inputs:
- /cache/graph.pt (from code `01_build_graph_cache_network.py`/`01_build_graph_cache_baseline.py` from STEP 1: Graph cache construction in `/data_preparation_graph_models/`)
- /cache/game2idx.pt (from code `01_build_graph_cache_network.py`/`01_build_graph_cache_baseline.py` from STEP 1: Graph cache construction in `/data_preparation_graph_models/`)
- /cache/user2idx.pt (from code `01_build_graph_cache_network.py`/`01_build_graph_cache_baseline.py` from STEP 1: Graph cache construction in `/data_preparation_graph_models/`)
- per_game_full.csv (from code `thesis_analysis.py` ( 2nd code in this folder) 

`graph.pt`  
Heterogeneous graph containing:  
`(user) --plays--> (game)`
`(user) --friend--> (user)`
  
Used to extract:
- users who own/play each game
- friendships between users

  
`game2idx.pt`  
Mapping from Steam appid to internal graph game index.  

  
`user2idx.pt`  
Mapping from Steam user id to internal graph user index.  
  
`per_game_full.csv`  
Base per-game table created earlier.
  
--------------------------------
    
#### What the code does
  
The script:
  
1. loads the graph and index mappings
2. extracts:
- user-game edges
- user-user friendship edges
3. builds adjacency structures:
- game_owners
- user_games
- friend_adj
4. loops over every game
5. computes graph metrics per game
6. merges the new metrics with per_game_full.csv
7. saves the extended table

-------------------------------- 
  
#### Metrics computed

| Metric              | Meaning                                                              |
| ------------------- | -------------------------------------------------------------------- |
| `clustering_coeff`  | how connected the neighboring games are through shared owners        |
| `second_order_size` | how many other games appear in libraries of users who own this game  |
| `friend_reach_2hop` | how many users can be reached through friends of owners up to 2 hops |

--------------------------------

Output:
- `analysis_metrics/per_game_full.csv`(This output is later used by `thesis_analysis.py.`)

</details>

<details>
<summary>2. Thesis analysis </summary>

#### CODE: `thesis_analysis.py`

#### Goal

This script analyzes what changes when the model gets the network embedding feature:
- `game_emb_0`
  
It compares:  
  
`XGBoost baseline  vs  XGBoost baseline + game_emb_0`

The key idea is to look at:    
  
`delta = score_emb - score_base`

So for every user-game pair, the script checks:  
*how much did the predicted score change after adding the embedding?*  

--------------------------------

Input:   
- /with_net_feat/test.csv (from code `make_positive_splits_from_pairs.py` from STEP 4: Adding negatives to positive splits in `/preparing_datasets/`)
- /metrics/xgboost_test_scores.csv  ( from code `train_xgb_baseline.py` from XGBoost model — hyperparameter search in `/models/4_XGBoost_model/`)
- /metrics/xgboost_test_scores_one_embedding.csv (from code `train_xgb_baseline+emb_0.py` from 1. Baseline + game_emb_0 in `/models/8_xgb_variations/`)
- /cache/graph.pt (from code `01_build_graph_cache_network.py`/`01_build_graph_cache_baseline.py` from STEP 1: Graph cache construction in `/data_preparation_graph_models/`)
- /cache/game2idx.pt (from code `01_build_graph_cache_network.py`/`01_build_graph_cache_baseline.py` from STEP 1: Graph cache construction in `/data_preparation_graph_models/`)
- per_game_full.csv ( from previous code) 

- `test.csv`  
Test set with user-game pairs and features  
  
- `xgboost_test_scores.csv`  
Predictions from the baseline XGBoost model  
  
- `xgboost_test_scores_one_embedding.csv`  
Predictions from the XGBoost model with game_emb_0  
  
- `graph.pt` and `game2idx.pt`  
Used to compute graph degree for each game  
  
- `per_game_with_structure.csv`  
Per-game graph structure table created by graph_structure_analysis.py  
    
--------------------------------

#### What the code does

- loads the test set
- loads baseline model scores
- loads embedding model scores
- merges both score files with the test set
- computes:
`delta = score_emb - score_base`
- separates rows into:  
`owned = 1`, `owned = 0`  
- computes graph degree per game
- calculates correlations between score change and graph/game features
- checks whether `game_emb_0` still matters after controlling for graph degree
- measures top-10 recommendation overlap between models
- checks whether the owned game rank improves
- creates plots
- saves summary CSV files

-------------------------------- 

#### Metrics computed
  
The script saves a metrics summary with:  

| Metric                                  | Meaning                                                                           |
| --------------------------------------- | --------------------------------------------------------------------------------- |
| `n_test_rows`                           | number of test rows used                                                          |
| `n_games`                               | number of unique games                                                            |
| `n_users`                               | number of unique users                                                            |
| `score_separation_baseline`             | mean score for owned games minus mean score for non-owned games in baseline       |
| `score_separation_emb0`                 | same separation for model with `game_emb_0`                                       |
| `spearman_delta_vs_emb0`                | correlation between score change and `game_emb_0`                                 |
| `spearman_delta_vs_graph_degree`        | correlation between score change and game graph degree                            |
| `spearman_emb0_vs_graph_degree`         | correlation between embedding value and graph degree                              |
| `partial_spearman_emb0_controlling_deg` | relation between `game_emb_0` and score change after controlling for graph degree |
| `mean_top10_overlap`                    | average overlap between baseline top-10 and embedding top-10 recommendations      |
| `mean_rank_base`                        | average rank of owned game in baseline model                                      |
| `mean_rank_emb0`                        | average rank of owned game in embedding model                                     |
| `percent_positives_promoted`            | fraction of users where the owned game moved higher in ranking                    |

--------------------------------

Output:
The script saves outputs in: 
  
- `analysis_metrics/`
- `analysis_plots/`

#### CSV outputs

- `analysis_metrics/metrics_summary.csv`
- `analysis_metrics/genre_popularity_profile.csv`
- `analysis_metrics/score_separation_summary.csv`
- `analysis_metrics/per_game_full.csv`

#### Plot outputs

- `analysis_plots/PA_extended_corr_separated.png`
- `analysis_plots/PB_delta_vs_popularity_separated.png`
- `analysis_plots/PC_genre_delta_by_owned.png`
- `analysis_plots/PD_genre_popularity_vs_delta.png`
- `analysis_plots/PE_genre_popularity_profile.png`
- `analysis_plots/PF_score_distributions.png`
- `analysis_plots/PG_top10_overlap.png`
- `analysis_plots/PH_score_separation.png`
- `analysis_plots/PI_emb0_vs_degree.png`

*you can find all outputs in corresponding folders*

--------------------------------
  
This analysis is used to explain the effect of adding:  
- `game_emb_0`  
  
The important question is:  
  
does the embedding only copy popularity, or does it add new graph information?  
  
The analysis checks this by comparing score changes against:  
  
- popularity (user_count)
- graph degree
- genre
- graph structure metrics
- ownership status
- ranking changes
      
The goal is to explain why the embedding model changes recommendations.  

</details>
