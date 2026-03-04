### EDA 
Number of nodes (users): 99,924   
Number of edges (from users to anyone): 8,039,785  
  
Degree statistics (computed for users only; degree counts friends too):  
Average degree: 80.81  
Median degree: 48  
Min degree: 1  
Max degree: 1999  
  
Network density (users-only subgraph): 0.00002668  
Number of connected components (users-only subgraph): 1  
Largest connected component size (users-only subgraph): 99,924  
Average clustering coefficient (users-only subgraph): 0.0431  
 
## After filtering: 
  
nodes: 43614  
edges: 44508  
## LCC
  
lcc_nodes: 31021  
lcc_edges: 40204  
directed: false    


## games: (enriched_games_filtered.scv)
20988 games (cols)  
<img width="838" height="221" alt="obraz" src="https://github.com/user-attachments/assets/956e0e60-fdfe-41b4-9ec3-630cebef532d" />



## users: (users_filtered.csv)
43675 users (rows)   WHY??????   
  
|             steamid  | public  | country |  account_created |   last_logoff |
|---------------------:|--------:|--------:|-----------------:|--------------:|
|  **76561198064675174** |  True   |   IT    |  1.338658e+09    |      NaN      |
|   76561198109425210  |  True   |   BE    |  1.380726e+09    |      NaN      |
|   76561198281198045  |  True   |  NaN    |  1.454511e+09    |      NaN      |


# on SSD (in correct_files) 

## matrix (user_game_01_steam_users_appid_games.pkl) 
31021 users (rows)  
20988 games (cols)   

|   steam_id\app_id |   10 |   20 |   30 |   40 |   50 |   60 |   70 |   80 |   100 |   130 |
|------------------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|------:|
|**76561198064675174**|    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198109425210 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198281198045 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561197994839969 |    1 |    0 |    1 |    1 |    0 |    1 |    1 |    1 |     1 |     0 |
| 76561197972380369 |    1 |    1 |    1 |    1 |    1 |    1 |    1 |    0 |     0 |     1 |
| 76561197992826872 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198362520139 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198859934865 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198011971157 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198004594504 |    0 |    1 |    0 |    0 |    1 |    0 |    1 |    0 |     0 |     1 |

## matrix ("game_game_dists_sq_20988.mmap)
! file itself does not have headers- use **game_index_to_gameid_20988.csv**


| game_id | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 100 | 130 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10  | 0.0 | 3044.402832 | 2602.100098 | 2589.406982 | 3096.431396 | 2608.204834 | 4139.877441 | 218.296112 | 223.433365 | 3089.372559 |
| 20  | 0.0 | 0.000000 | 868.383240 | 842.561584 | 203.534988 | 854.365906 | 1914.934814 | 3307.916016 | 3310.528809 | 185.563934 |
| 30  | 0.0 | 0.000000 | 0.000000 | 69.281372 | 983.639038 | 82.724724 | 2540.693604 | 2871.097656 | 2873.710938 | 958.206787 |
| 40  | 0.0 | 0.000000 | 0.000000 | 0.000000 | 952.704468 | 36.772652 | 2525.278320 | 2859.312012 | 2861.120605 | 930.687012 |
| 50  | 0.0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 969.919189 | 1842.784790 | 3362.189209 | 3365.393555 | 81.346985 |
| 60  | 0.0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 2532.195312 | 2876.781250 | 2878.662354 | 946.466309 |
| 70  | 0.0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 4365.642578 | 4364.226562 | 1837.330200 |
| 80  | 0.0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 10.618079 | 3357.562256 |
| 100 | 0.0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 3357.741211 |
| 130 | 0.0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |



## Graph (user_edge_graph_steamid_LCC31021.pkl)
**Type:** NetworkX undirected graph (`nx.Graph`)    
**Nodes:** Steam user IDs (`steam_id` as `string`)    
**Edges:** user–user connections (undirected)  

  
nodes: 31021  
edges: 40204  
```text
('76561198064675174', '76561197972380369')
('76561198064675174', '76561198109425210')
('76561198109425210', '76561198281198045')
('76561198109425210', '76561198362520139')
('76561198281198045', '76561197994839969')
('76561197994839969', '76561197977761889')
('76561197994839969', '76561198050217493')
('76561197994839969', '76561198113936877')
('76561197994839969', '76561198119199983')
('76561197972380369', '76561197966485747')
```


## models for small dataset:
| Model              | Best CV ROC-AUC | Best Params                                                                                                              | Accuracy | Precision |  Recall |      F1 | Test ROC-AUC | Confusion Matrix (TN FP / FN TP) | Saved Model                                                          |
| ------------------ | --------------: | ------------------------------------------------------------------------------------------------------------------------ | -------: | --------: | ------: | ------: | -----------: | -------------------------------- | -------------------------------------------------------------------- |
| LogisticRegression |         0.93290 | C=0.78476                                                                                                                |  0.85139 |   0.84864 | 0.85533 | 0.85197 |      0.91337 | [[20326, 3659], [3470, 20515]]   | `outputs_baseline_small/models/LogisticRegression_best_small.joblib` |
| RandomForest | 0.94392 | max_depth=20, max_features=0.5, min_samples_leaf=2, min_samples_split=50, bootstrap=True *(OHE max_cats=500; min_freq=5)* | 0.86023 | 0.84813 | 0.87759 | 0.86261 | 0.92349 | [[20216, 3769], [2936, 21049]] | `outputs_baseline_small/models/RandomForest_best_small.joblib` |
| XGBoost            |         0.94507 | colsample_bytree=0.8, max_depth=8, reg_lambda=1.0, subsample=0.8                                                         |  0.86333 |   0.85016 | 0.88213 | 0.86585 |      0.92354 | [[20256, 3729], [2827, 21158]]   | `outputs_baseline_small/models/XGBoost_best_small.joblib`            |


<img width="1600" height="1000" alt="learning_curve_lr_roc_auc_small" src="https://github.com/user-attachments/assets/767e995a-53dd-4f0c-b74b-0966994c53a7" />
<img width="1600" height="1000" alt="learning_curve_rf_roc_auc_small" src="https://github.com/user-attachments/assets/42fdaf4a-9711-4da1-a8bd-309e05dab73d" />
<img width="1600" height="1000" alt="learning_curve_xgb_roc_auc_small" src="https://github.com/user-attachments/assets/824cc432-4400-49bf-b080-2c94812496e6" />



## models for full dataset:

| Model              | Best CV ROC-AUC | Best Params                                                                                                                                     | Accuracy | Precision |  Recall |      F1 | Test ROC-AUC | Confusion Matrix (TN FP / FN TP)     | Saved Model                                                   |
| ------------------ | --------------: | ----------------------------------------------------------------------------------------------------------------------------------------------- | -------: | --------: | ------: | ------: | -----------: | ------------------------------------ | ------------------------------------------------------------- |
| LogisticRegression |         0.92679 | C=29.76351                                                                                                                                      |  0.84959 |   0.83979 | 0.86401 | 0.85173 |      0.92477 | [[677022, 133617], [110236, 700403]] | `outputs_baseline_full/models/LogisticRegression_best.joblib` |
| RandomForest | 0.91948 | max_depth=10, max_features=0.3, min_samples_leaf=10, min_samples_split=50, bootstrap=True *(train subsample=0.2; LC subsample=0.2; OHE max_cats=200; min_freq=20)* | 0.83880 | 0.83194 | 0.84913 | 0.84044 | 0.91804 | [[671584, 139055], [122302, 688337]] | `outputs_baseline_full/models/RandomForest_best.joblib` |     |
| XGBoost            |         0.93096 | colsample_bytree=0.6, max_depth=8, reg_lambda=1.0, subsample=0.6                                                                                |  0.85231 |   0.84245 | 0.86669 | 0.85440 |      0.92872 | [[679251, 131388], [108063, 702576]] | `outputs_baseline_full/models/XGBoost_best.joblib`            |


<img width="1600" height="1000" alt="learning_curve_lr_roc_auc" src="https://github.com/user-attachments/assets/a711eee6-1c6b-4815-8dd3-fdf7545be27a" />
<img width="1600" height="1000" alt="learning_curve_rf_roc_auc" src="https://github.com/user-attachments/assets/9e7fe82d-561f-4c0f-9ef4-4fa392069b77" />

<img width="1600" height="1000" alt="learning_curve_xgb_roc_auc" src="https://github.com/user-attachments/assets/1ef2e3a3-f4da-4288-a9f6-a50da206c518" />


## Feature Importance (Block Permutation Importance, ROC-AUC drop)
We compute **block permutation importance** on the **full test set**, measuring the **drop in ROC-AUC** when a feature block is permuted.
Interpretation: **higher AUC drop = more important feature block**.
**Repeats:** 5 (mean ± std)

| Feature block | ROC-AUC drop (mean ± std) |
|---|---:|
| **game_total_playtime_minutes** | **0.400609 ± 0.000281** |
| **total_games_owned** | **0.041662 ± 0.000072** |
| publisher | 0.004393 ± 0.000010 |
| developer | 0.003990 ± 0.000011 |
| genres | 0.003739 ± 0.000030 |
| platforms | 0.001401 ± 0.000016 |
| user_count | 0.000576 ± 0.000011 |
| total_playtime_minutes | 0.000383 ± 0.000002 |
| median_playtime_minutes | 0.000283 ± 0.000007 |
| country | 0.000092 ± 0.000005 |
| unique_genres_played | -0.000518 ± 0.000005 |

  
## baseline + freinds_count + PCA 

final shape: (4010476, 46)

|           steamid | appid | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name                         | genres           | developer     | publisher | platforms     | release_date | user_count | game_total_playtime_minutes | friend_count | game_index | game_emb_0 | game_emb_1 | game_emb_2 | game_emb_3 | game_emb_4 | game_emb_5 | game_emb_6 | game_emb_7 | game_emb_8 |  game_emb_9 | game_emb_10 | game_emb_11 | game_emb_12 | game_emb_13 | game_emb_14 | game_emb_15 | game_emb_16 | game_emb_17 | game_emb_18 | game_emb_19 | game_emb_20 | game_emb_21 | game_emb_22 | game_emb_23 | game_emb_24 | game_emb_25 | game_emb_26 | game_emb_27 | game_emb_28 |
| ----------------: | ----: | :-----: | ----------------: | ---------------------: | ----------------------: | -------------------: | ---------------------------- | ---------------- | ------------- | --------- | ------------- | ------------ | ---------: | --------------------------: | -----------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ---------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: |
| 76561198064675174 |   400 |    IT   |               170 |               505414.0 |                   588.0 |                   15 | Portal                       | Action           | Valve         | Valve     | windows;linux | 2007-10-10   |      12230 |                   2626344.0 |           28 |         16 |  630.75916 |  235.74579 |   72.54562 |  25.904493 |  -7.369573 |  7.6848702 |  7.2495575 |  4.7646413 |   14.26124 |  -21.685534 |  -31.503036 |  -7.8475413 |  0.96735793 |  -6.7931647 |  -10.103615 |   -11.61399 |   2.4698002 |   4.6987886 |   6.9499674 |   -4.071124 |   1.3690697 |  -1.1807152 |    -6.59566 |   6.8833833 |    3.741427 |  0.33851355 |   11.976154 |   -5.632161 |  -19.318426 |
| 76561198064675174 |   500 |    IT   |               170 |               505414.0 |                   588.0 |                   15 | Left 4 Dead                  | Action           | Valve         | Valve     | windows       | 2008-11-17   |       9389 |                   7100773.0 |           28 |         18 |   601.9306 |  215.86795 |   64.72638 |  22.973597 |  -4.199505 |   8.540773 |  2.4615386 |   3.255315 |  10.489542 |  -16.144653 |   -29.38277 |  -11.623671 | -0.63198966 |  0.02577714 |   3.1492097 | -0.06891072 |  -3.0322204 |   1.2568315 |   12.118297 |   -6.050477 |   4.4183187 |  -3.3006337 |   1.4158152 | -0.11214605 |    5.625076 |  -1.5341239 |   6.9283485 |   1.1788374 |   -6.297187 |
| 76561198064675174 |   550 |    IT   |               170 |               505414.0 |                   588.0 |                   15 | Left 4 Dead 2                | Action           | Valve         | Valve     | windows;linux | 2009-11-16   |      26253 |                  69129046.0 |           28 |         19 |   683.7639 |   285.9603 |  107.24204 |   47.04935 | -1.5980552 |  31.032335 |  1.9328676 |  12.893521 |  16.533867 |  -1.7018634 |  -3.4427319 |  -5.2860446 |    7.049412 |   -3.244441 |   -8.320024 |  -1.8394125 |   1.0495358 |   -1.846529 |   -2.949326 | 0.010995906 |    8.462385 |    -3.27282 |  -1.0441896 |   2.5599153 |   12.126819 |   -2.255205 |   23.305458 |    6.542681 |  -36.192795 |
| 76561198064675174 |   620 |    IT   |               170 |               505414.0 |                   588.0 |                   15 | Portal 2                     | Action;Adventure | Valve         | Valve     | windows;linux | 2011-04-18   |      17020 |                  12584145.0 |           28 |         21 |   667.1358 |  268.13412 |   93.35679 |  37.888783 | -4.4383454 |  20.302198 |   5.236955 |    8.47173 |  15.365093 |  -11.573789 |  -17.319775 |  -5.4135013 |   3.6591618 |   -8.029749 |  -11.136434 |  -10.106342 |   2.7152863 |    7.367307 |     4.26974 |  -3.1251187 |    4.212208 |  -1.2821062 |  -10.325581 |   12.463725 |     7.04293 |   1.7030023 |   22.602686 |   -8.296105 |  -37.514336 |
| 76561198064675174 |  3900 |    IT   |               170 |               505414.0 |                   588.0 |                   15 | Sid Meier's Civilization® IV | Strategy         | Firaxis Games | 2K        | windows;mac   | 2006-10-25   |       1262 |                    223960.0 |           28 |         84 |  301.28006 |   4.801401 | -24.707678 |  -8.812908 |  -6.113992 |  -4.800696 |   4.308728 |    6.08423 | -2.6863155 | -0.88333786 |   1.3589162 |  -2.3656147 |    6.239287 |  0.35651204 | -0.64102525 |  -0.4086798 |   3.1381812 |  -0.5871557 |  -1.5863887 |  -2.2396324 |   1.5458672 |  -0.8461953 | -0.17637874 |   1.6948044 |  -0.1395636 |   -1.039272 |  0.20626062 |  0.40612754 |    1.298332 |

 # NEW TRAIN-TEST SPLIT MODELS:
## Split (game-disjoint) — dataset summary

| Item | Value |
|---|---:|
| Split strategy | **Game-disjoint** (`appid` in train ∩ test = ∅) |
| Goal | Simulate “new game release” (test contains unseen games) |
| Seed | 42 |
| Test game fraction (`TEST_GAME_FRAC`) | 0.20 |
| Negative sampling ratio (`NEG_RATIO`) | 1.0 (1 negative per positive) |
| Users | 31,021 |
| Games total | 20,918 |
| Games in test | 4,184 |
| Games in train | 16,734 |
| Users with ≥1 positive in both train & test | 29,939 |
| Appid overlap between train & test | **0**  |
| Embedding dimensions | 29 (`game_emb_0 … game_emb_28`) |

### Notes
- Train/test **share users**, but **do not share games** (strictly enforced).
- Negatives are sampled **separately** within train and test game pools.
- `baseline_with_network` adds `friend_count` (per user) and `game_emb_*` (per game) features.

## New gamexgame matrix (games only in training preventing data leaking) :
**Train-only game–game similarity (cosine)**  

We compute a **game×game cosine similarity** matrix using **TRAIN positives only** (`owned=1`) and store it as an **upper-triangle float32 array** (excluding diagonal). This prevents test-leakage when later building embeddings.  

#### Stored matrix stats
| Metric | Value |
|---|---:|
| Train games (`n_games`) | 16,734 |
| Stored values (upper triangle) | 140,005,011 |
| Storage | Upper triangle (i < j), diagonal excluded |
| dtype | float32 |
| File size | 534.1 MB |
| Files | `train_game_sim_cosine_upper_f32.npy`, `train_game_sim_cosine_upper_meta.json`, `train_game_index.csv` |

**Indexing formula (upper triangle):**  
`k = i*(2n - i - 1)//2 + (j - i - 1)` for `0 ≤ i < j < n`

#### First 10 games (by train game_idx)
| game_idx | appid |
|---:|---:|
| 0 | 10 |
| 1 | 20 |
| 2 | 40 |
| 3 | 50 |
| 4 | 60 |
| 5 | 70 |
| 6 | 130 |
| 7 | 220 |
| 8 | 280 |
| 9 | 300 |

#### 10×10 similarity preview (rows/cols = appid)
| appid | 10 | 20 | 40 | 50 | 60 | 70 | 130 | 220 | 280 | 300 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 0.0000 | 0.6162 | 0.6640 | 0.6162 | 0.6622 | 0.5982 | 0.6157 | 0.5738 | 0.5799 | 0.5891 |
| 20 | 0.6162 | 0.0000 | 0.8310 | 0.9609 | 0.8295 | 0.7467 | 0.9645 | 0.6293 | 0.8995 | 0.7679 |
| 40 | 0.6640 | 0.8310 | 0.0000 | 0.8139 | 0.9918 | 0.6421 | 0.8169 | 0.5467 | 0.7796 | 0.8043 |
| 50 | 0.6162 | 0.9609 | 0.8139 | 0.0000 | 0.8113 | 0.7628 | 0.9850 | 0.6453 | 0.8946 | 0.7579 |
| 60 | 0.6622 | 0.8295 | 0.9918 | 0.8113 | 0.0000 | 0.6416 | 0.8147 | 0.5466 | 0.7780 | 0.8033 |
| 70 | 0.5982 | 0.7467 | 0.6421 | 0.7628 | 0.6416 | 0.0000 | 0.7612 | 0.7337 | 0.6989 | 0.6121 |
| 130 | 0.6157 | 0.9645 | 0.8169 | 0.9850 | 0.8147 | 0.7612 | 0.0000 | 0.6434 | 0.8993 | 0.7587 |
| 220 | 0.5738 | 0.6293 | 0.5467 | 0.6453 | 0.5466 | 0.7337 | 0.6434 | 0.0000 | 0.6298 | 0.5683 |
| 280 | 0.5799 | 0.8995 | 0.7796 | 0.8946 | 0.7780 | 0.6989 | 0.8993 | 0.6298 | 0.0000 | 0.7893 |
| 300 | 0.5891 | 0.7679 | 0.8043 | 0.7579 | 0.8033 | 0.6121 | 0.7587 | 0.5683 | 0.7893 | 0.0000 |


### PCA95 game embeddings
| appid | emb0 | emb1 | emb2 | emb3 | emb4 | emb5 | emb6 | emb7 | emb8 | emb9 | emb10 | emb11 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10  | -18.409132 | -4.319274 | -0.9189478 | 0.3999531 | 0.4293030 | 1.1332549 | -1.7259296 | -0.3306376 | -0.6646197 | 1.4975620 | 1.4892817 | 0.0436611 |
| 20  | -17.322119 | -1.678589 | 0.0964240 | 0.6387344 | 1.3623946 | 2.0647311 | -1.8057147 | -0.4516179 | -0.7089579 | 1.7256294 | 1.5963341 | 0.1672443 |
| 40  | -17.240707 | -2.327463 | -0.2841532 | 0.4887637 | 0.8431156 | 1.4215784 | -1.6851312 | -0.4551899 | -0.5191811 | 1.4549949 | 1.3946556 | 0.0885037 |
| 50  | -17.391333 | -1.734731 | 0.0915704 | 0.6396646 | 1.3897355 | 2.1104310 | -1.8281013 | -0.4546433 | -0.7365656 | 1.7704560 | 1.6408337 | 0.1742452 |
| 60  | -17.243963 | -2.350560 | -0.2899061 | 0.4858887 | 0.8527242 | 1.4432449 | -1.6825049 | -0.4388882 | -0.5487711 | 1.4666959 | 1.3669611 | 0.0970209 |
| 70  | -18.061094 | -2.536264 | -0.0848833 | 0.6058696 | 1.4819728 | 2.3099554 | -1.9732434 | -0.4666621 | -0.7035309 | 1.9587950 | 1.9017795 | 0.0828693 |
| 130 | -17.282185 | -1.518037 | 0.1082908 | 0.5630072 | 1.4247332 | 2.0908344 | -1.8575177 | -0.4903648 | -0.7169039 | 1.7961316 | 1.6293833 | 0.1697471 |
| 220 | -18.360088 | -2.842084 | -0.1417450 | 0.6011832 | 1.5561073 | 2.4555657 | -2.0543263 | -0.4497394 | -0.8084972 | 2.0706496 | 2.0046163 | 0.0989048 |
| 280 | -17.053340 | -1.240685 | 0.1694918 | 0.5531242 | 1.3946271 | 1.9881690 | -1.8606758 | -0.5276797 | -0.6358551 | 1.7524627 | 1.5859109 | 0.1774690 |
| 300 | -17.238493 | -2.188106 | -0.1962015 | 0.4979853 | 1.0333966 | 1.6512796 | -1.6938734 | -0.4759845 | -0.5959634 | 1.5575571 | 1.4815848 | 0.1373427 |

- **Method:** IncrementalPCA  
- **Target explained variance:** 0.95  
- **Selected components:** 12 (emb0..emb11)
- **Seed:** 42
- **Training scope:** similarity computed on **train positives only** (`owned=1`), so embeddings are **train-only** (cold-start safe)
  
### Datasets 

| Dataset variant | Train rows | Test rows | Train path | Test path |
|---|---:|---:|---|---|
| Baseline (no network) | 5,368,456 | 2,600,070 | `new_approach_dataset/baseline/data/train.csv` | `new_approach_dataset/baseline/data/test.csv` |
| Baseline + network | 5,368,456 | 2,600,070 | `new_approach_dataset/baseline_with_network/data/train.csv` | `new_approach_dataset/baseline_with_network/data/test.csv` |



###
### Logistic Regression
| Variant | CV ROC-AUC | Test ROC-AUC | Accuracy | Precision | Recall | F1 | Best params |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline | 0.507633 | 0.504176 | 0.502102 | 0.509589 | 0.222475 | 0.309729 | C=0.000259, penalty=l1, class_weight=balanced, solver=liblinear |
| + Network (friend_count + 29 embeddings) | 0.927460 | 0.949093 | 0.876257 | 0.840302 | 0.930365 | 0.883043 | C=0.048939, penalty=l2, class_weight=balanced, solver=liblinear |
<img width="1600" height="1000" alt="learning_curve_lr_roc_auc" src="https://github.com/user-attachments/assets/a483895c-4965-4b66-9948-5d3e6e3b8de4" />
<img width="1600" height="1000" alt="learning_curve_lr_roc_auc" src="https://github.com/user-attachments/assets/0fe076f0-8768-4bda-9b81-f210d9a1b5fa" />

### XGBoost 
| Variant | CV ROC-AUC | Test ROC-AUC | Accuracy | Precision | Recall | F1 | Best params |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline | 0.505019 | 0.504176 | 0.502102 | 0.507851 | 0.270787 | 0.353230 | max_depth=3, subsample=1.0, colsample=0.6, min_child_weight=1, gamma=1.0, reg_alpha=0.5, reg_lambda=2.0 |
| + Network (friend_count + 29 embeddings) | 0.957359 | 0.966717 | 0.905709 | 0.871810 | 0.952221 | 0.910243 | max_depth=8, subsample=0.6, colsample=0.8, min_child_weight=10, gamma=1.0, reg_alpha=0.5, reg_lambda=0.5 |

<img width="1600" height="1000" alt="learning_curve_xgb_roc_auc" src="https://github.com/user-attachments/assets/cb880482-342f-4502-9f68-7737b1ff2f34" />
<img width="1600" height="1000" alt="learning_curve_xgb_roc_auc" src="https://github.com/user-attachments/assets/e27fc72d-d645-4ab9-b6de-1146230705ba" />

