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

# NEW APPROACH 
## Datasets:
**Saved to: /home/anci/new/correct_splits - train,test,val -.csv  
**    
Train positives: 3,954,054  
Train negatives: 39,540,540  
**Train total:     43,494,594  
**  
Val positives:   28,211  
Val negatives:   2,821,100  
**Val total:       2,849,311  
**  
Test positives:  28,211  
Test negatives:  2,821,100  
**Test total:      2,849,311  
**  
Expected target ratios:  
  train: 1:10  
  val:   1:100  
  test:  1:100  
  
#### notes: 
train size: 33700323      
val size:   2834092    
test size:  2834378    
(to sa unikatowe rekordy: ten sam user-game para mogla zostac uzyta pare razy w tym samym secie - jezeli brakowalo popular i random do dobrania)   
train ∩ val : 0  
train ∩ test: 0  
val ∩ test  : 0  

### GENRE BUCKETS:
-20813 records (+) with no genre "" from the training set ( ~0,5 % of all (+))  
  
| steamid           |   appid | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name              | genres                       | developer       | publisher               | platforms         | release_date | user_count | game_total_playtime_minutes | owned | user_playtime_group_Action | user_playtime_group_Adventure | user_playtime_group_RPG | user_playtime_group_Casual | user_playtime_group_Indie | user_playtime_group_Racing | user_playtime_group_Simulation | user_playtime_group_Strategy | user_playtime_group_Sports | user_playtime_group_Violent | user_playtime_group_Adult | user_playtime_group_Non-gameplay_Tools | user_playtime_group_Other |
| ----------------- | ------: | ------- | ----------------: | ---------------------: | ----------------------: | -------------------: | ----------------- | ---------------------------- | --------------- | ----------------------- | ----------------- | ------------ | ---------: | --------------------------: | ----: | -------------------------: | ----------------------------: | ----------------------: | -------------------------: | ------------------------: | -------------------------: | -----------------------------: | ---------------------------: | -------------------------: | --------------------------: | ------------------------: | -------------------------------------: | ------------------------: |
| 76561197960266945 |      10 | RU      |              1503 |              1091628.0 |                    60.0 |                   27 | Counter-Strike    | Action                       | Valve           | Valve                   | windows;mac;linux | 2000-11-01   |     8366.0 |                 107248640.0 |     1 |              575679.447619 |                 126260.064286 |            62692.183333 |               25453.047619 |              55046.947619 |                1200.797619 |                   17330.330952 |                 76800.397619 |                1220.666667 |                   86.000000 |                 86.000000 |                           62053.000000 |              84251.116667 |
| 76561197960266945 | 1517290 | RU      |              1503 |              1091628.0 |                    60.0 |                   27 | Battlefield™ 2042 | Action;Adventure;Casual      | DICE            | Electronic Arts         | windows           | 19 Nov, 2021 |       6312 |                             |     0 |              577897.447619 |                 126260.064286 |            62692.183333 |               25453.047619 |              55046.947619 |                1200.797619 |                   17330.330952 |                 76800.397619 |                1220.666667 |                   86.000000 |                 86.000000 |                           62053.000000 |              84251.116667 |
| 76561197960266945 | 1361000 | RU      |              1503 |              1091628.0 |                    60.0 |                   27 | In Silence        | Action                       | Ravenhood Games | Ravenhood Games         | windows;mac       | 29 Oct, 2021 |        753 |                             |     0 |              577897.447619 |                 126260.064286 |            62692.183333 |               25453.047619 |              55046.947619 |                1200.797619 |                   17330.330952 |                 76800.397619 |                1220.666667 |                   86.000000 |                 86.000000 |                           62053.000000 |              84251.116667 |
| 76561197960266945 |  575550 | RU      |              1503 |              1091628.0 |                    60.0 |                   27 | Hell Girls        | Adventure;Indie;RPG;Strategy | Athena Works    | Athena Works;SakuraGame | windows;mac       | 12 Jan, 2017 |       1009 |                             |     0 |              577897.447619 |                 126260.064286 |            62692.183333 |               25453.047619 |              55046.947619 |                1200.797619 |                   17330.330952 |                 76800.397619 |                1220.666667 |                   86.000000 |                 86.000000 |                           62053.000000 |              84251.116667 |
| 76561197960266945 |  793400 | RU      |              1503 |              1091628.0 |                    60.0 |                   27 | Fist of Brave     | Action;Adventure;Indie       | ALOOF PROJECT   | Beliebrave              | windows           | 19 Feb, 2018 |          6 |                             |     0 |              577897.447619 |                 126260.064286 |            62692.183333 |               25453.047619 |              55046.947619 |                1200.797619 |                   17330.330952 |                 76800.397619 |                1220.666667 |                   86.000000 |                 86.000000 |                           62053.000000 |              84251.116667 |


### NETWORK FEATURES:
steamid;appid;country;total_games_owned;total_playtime_minutes;median_playtime_minutes;unique_genres_played;name;genres;developer;publisher;platforms;release_date;user_count;game_total_playtime_minutes;owned;user_playtime_group_Action;user_playtime_group_Adventure;user_playtime_group_RPG;user_playtime_group_Casual;user_playtime_group_Indie;user_playtime_group_Racing;user_playtime_group_Simulation;user_playtime_group_Strategy;user_playtime_group_Sports;user_playtime_group_Violent;user_playtime_group_Adult;user_playtime_group_Non-gameplay_Tools;user_playtime_group_Other;friend_count;game_emb_0;game_emb_1;game_emb_2;game_emb_3;game_emb_4;game_emb_5;game_emb_6;game_emb_7;game_emb_8;game_emb_9;game_emb_10;game_emb_11;game_emb_12;game_emb_13;game_emb_14;game_emb_15;game_emb_16;game_emb_17;game_emb_18;game_emb_19;game_emb_20;game_emb_21;game_emb_22;game_emb_23;game_emb_24;game_emb_25;game_emb_26;game_emb_27;game_emb_28;game_emb_29;game_emb_30;game_emb_31

### embeddings: 
<img width="1600" height="1000" alt="pca_cumulative_plot_k32_trainonly" src="https://github.com/user-attachments/assets/fc2ccbf3-4dfa-4a1d-a7ac-71527fabb1d4" />
  
- K=32      
- explained var: 0,9868

# MODELS:

## NAIVE POPULARITY:
  
  "HitRate@10": 0.5878558009287157,  
  "Recall@10": 0.5878558009287157,  
  "NDCG@10": 0.3382964551955261,  
  "HitRate@20": 0.8112083938889085,  
  "Recall@20": 0.8112083938889085,  
  "NDCG@20": 0.39471513390492685,  
  "MRR": 0.28408198995817924,  
  "HitRate@1": 0.15057956116408494,  
  "Recall@1": 0.15057956116408494,  
  "NDCG@1": 0.15057956116408494,  
  "HitRate@5": 0.40484208287547413,  
  "Recall@5": 0.40484208287547413,  
  "NDCG@5": 0.2793162612233727  
    
## NAIVE RANDOM:
  
  "n_runs": 100,  
  "HitRate@10": 0.1021232852433448,  
  "Recall@10": 0.1021232852433448,  
  "NDCG@10": 0.04700499092443008,  
  "HitRate@20": 0.20105632554677252,  
  "Recall@20": 0.20105632554677252,  
  "NDCG@20": 0.07171802796295731,  
  "MRR": 0.05303363486054278,  
  "HitRate@1": 0.01113041012371061,  
  "Recall@1": 0.01113041012371061,  
  "NDCG@1": 0.01113041012371061,  
  "HitRate@5": 0.052639041508631385,  
  "Recall@5": 0.052639041508631385,  
  "NDCG@5": 0.031199634786967252    
      
## LOGISTIC REGRESSION BASELINE: 
  
  "test_roc_auc": 0.9035307763305926,  
  "HitRate@1": 0.1609655808018149,  
  "Recall@1": 0.1609655808018149,  
  "NDCG@1": 0.1609655808018149,  
  "HitRate@5": 0.5760873418170217,  
  "Recall@5": 0.5760873418170217,  
  "NDCG@5": 0.37077277924236496,  
  "HitRate@10": 0.748537804402538,  
  "Recall@10": 0.748537804402538,  
  "NDCG@10": 0.42749191661367153,  
  "HitRate@20": 0.8400269398461593,  
  "Recall@20": 0.8400269398461593,  
  "NDCG@20": 0.45076122932644225,  
  "MRR": 0.3383544483777126  
    
## LOGISTIC REGRESSION NETWORK: 
  
 "test_roc_auc": 0.9805927306953324,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.7772500088617915,  
  "Recall@1": 0.7772500088617915,  
  "NDCG@1": 0.7772500088617915,  
  "HitRate@5": 0.9182942823721244,  
  "Recall@5": 0.9182942823721244,  
  "NDCG@5": 0.8575702121735289,  
  "HitRate@10": 0.9447024210414378,  
  "Recall@10": 0.9447024210414378,  
  "NDCG@10": 0.8661613480999315,  
  "HitRate@20": 0.9682747864308249,  
  "Recall@20": 0.9682747864308249,  
  "NDCG@20": 0.8721455885062763,  
  "MRR": 0.8430285803213402    
    
## RANDOM FOREST BASELINE: 
   "test_roc_auc": 0.9491964679135025,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.6197228031618872,  
  "Recall@1": 0.6197228031618872,  
  "NDCG@1": 0.6197228031618872,  
  "HitRate@5": 0.7798730991457233,  
  "Recall@5": 0.7798730991457233,  
  "NDCG@5": 0.70644178503317,  
  "HitRate@10": 0.8367658005742441,  
  "Recall@10": 0.8367658005742441,  
  "NDCG@10": 0.7248064641263446,  
  "HitRate@20": 0.8991882598986211,  
  "Recall@20": 0.8991882598986211,  
  "NDCG@20": 0.7405922572858965,  
  "MRR": 0.6967694601919562  
    
## RANDOM FOREST NETWORK: 
  
  "test_roc_auc": 0.9933895985148382,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.9582786856190848,  
  "Recall@1": 0.9582786856190848,  
  "NDCG@1": 0.9582786856190848,  
  "HitRate@5": 0.9729892595087023,  
  "Recall@5": 0.9729892595087023,  
  "NDCG@5": 0.966191174803908,  
  "HitRate@10": 0.9786962532345539,  
  "Recall@10": 0.9786962532345539,  
  "NDCG@10": 0.9680310637945264,  
  "HitRate@20": 0.986423735422353,  
  "Recall@20": 0.986423735422353,  
  "NDCG@20": 0.9699606498427581,  
  "MRR": 0.9655960307906203  
      
## XGB BASELINE:
    
  "test_roc_auc": 0.9681250719433537,  
  "HitRate@1": 0.7762929353798164,  
  "Recall@1": 0.7762929353798164,  
  "NDCG@1": 0.7762929353798164,  
  "HitRate@5": 0.8649462975435114,  
  "Recall@5": 0.8649462975435114,  
  "NDCG@5": 0.8237206918322882,  
  "HitRate@10": 0.8993654957286165,  
  "Recall@10": 0.8993654957286165,  
  "NDCG@10": 0.8348392225148182,  
  "HitRate@20": 0.9380738009996101,  
  "Recall@20": 0.9380738009996101,  
  "NDCG@20": 0.8446513533056069,  
  "MRR": 0.8189992466505192  
        
## XGB NETWORK: 

 "test_roc_auc": 0.9992328183030956,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.9940094289461557,  
  "Recall@1": 0.9940094289461557,  
  "NDCG@1": 0.9940094289461557,  
  "HitRate@5": 0.9965261777320903,  
  "Recall@5": 0.9965261777320903,  
  "NDCG@5": 0.995330068733848,  
  "HitRate@10": 0.9976959342100599,  
  "Recall@10": 0.9976959342100599,  
  "NDCG@10": 0.9957064439365918,  
  "HitRate@20": 0.9985112190280387,  
  "Recall@20": 0.9985112190280387,  
  "NDCG@20": 0.995915275127317,  
  "MRR": 0.9951880134703508  
      
## lightGCN 
      
  "test_roc_auc": 0.9296967167315993,  
  "test_HitRate@1": 0.2797844812307256,  
  "test_Recall@1": 0.2797844812307256,  
  "test_NDCG@1": 0.2797844812307256,  
  "test_HitRate@5": 0.6278047570096771,  
  "test_Recall@5": 0.6278047570096771,  
  "test_NDCG@5": 0.4587482133121356,  
  "test_HitRate@10": 0.7994399347772145,  
  "test_Recall@10": 0.7994399347772145,  
  "test_NDCG@10": 0.5143682537824952,  
  "test_HitRate@20": 0.9305590018078055,  
  "test_Recall@20": 0.9305590018078055,  
  "test_NDCG@20": 0.5478593963439246,  
  "test_MRR": 0.4379026748253812  
    
## NN_baseline (BPR)  
  
  "n_users_evaluated": 28211,  
    "HitRate@1": 0.21115876785650986,  
    "Recall@1": 0.21115876785650986,  
    "NDCG@1": 0.21115876785650986,  
    "HitRate@5": 0.5297933430222254,  
    "Recall@5": 0.5297933430222254,  
    "NDCG@5": 0.37409319978341726,  
    "HitRate@10": 0.7206054375952643,  
    "Recall@10": 0.7206054375952643,  
    "NDCG@10": 0.43571650935395834,  
    "HitRate@20": 0.8909290702208359,  
    "Recall@20": 0.8909290702208359,  
    "NDCG@20": 0.47906482228723923,  
    "MRR": 0.36406691633984173  
      
## NN_network (BPR)  RUNNING 
  
  "n_users_evaluated": 28211,  
    "HitRate@1": 0.3338414093793201,  
    "Recall@1": 0.3338414093793201,  
    "NDCG@1": 0.3338414093793201,  
    "HitRate@5": 0.6895182730140725,  
    "Recall@5": 0.6895182730140725,  
    "NDCG@5": 0.5192855905767376,  
    "HitRate@10": 0.8433589734500727,  
    "Recall@10": 0.8433589734500727,  
    "NDCG@10": 0.5694762472416068,  
    "HitRate@20": 0.9496295771153096,  
    "Recall@20": 0.9496295771153096,  
    "NDCG@20": 0.5966241071996167,  
    "MRR": 0.4933085945607166  
      
## GraphSAGE baseline 

   "n_users_evaluated": 28211,  
    "HitRate@1": 0.21885080287830988,  
    "HitRate@5": 0.5589663606394669,  
    "HitRate@10": 0.7456311367906135,  
    "HitRate@20": 0.9064549289284322,  
    "Recall@1": 0.21885080287830988,  
    "Recall@5": 0.5589663606394669,  
    "Recall@10": 0.7456311367906135,  
    "Recall@20": 0.9064549289284322,  
    "NDCG@1": 0.21885080287830988,  
    "NDCG@5": 0.39268880519877153,  
    "NDCG@10": 0.45310978599422186,  
    "NDCG@20": 0.4940778856724079,  
    "MRR": 0.37765876291923967  

## GraphSAGE network

   "n_users_evaluated": 28211,  
    "HitRate@1": 0.2383112970118039,  
    "HitRate@5": 0.5864024671227536,  
    "HitRate@10": 0.7683527701960229,  
    "HitRate@20": 0.9173726560561483,  
    "Recall@1": 0.2383112970118039,  
    "Recall@5": 0.5864024671227536,  
    "Recall@10": 0.7683527701960229,  
    "Recall@20": 0.9173726560561483,  
    "NDCG@1": 0.2383112970118039,  
    "NDCG@5": 0.41673376281394714,  
    "NDCG@10": 0.47577682836312957,  
    "NDCG@20": 0.5137141266891314,  
    "MRR": 0.3988092625712067  
  
----------------------------------------------------------------------

## XGB embeddings only:
  
"test_roc_auc": 0.8652521319247597,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.10612881500124065,  
  "Recall@1": 0.10612881500124065,  
  "NDCG@1": 0.10612881500124065,  
  "HitRate@5": 0.3431285668710787,  
  "Recall@5": 0.3431285668710787,  
  "NDCG@5": 0.22622908929954413,  
  "HitRate@10": 0.5091630924107617,  
  "Recall@10": 0.5091630924107617,  
  "NDCG@10": 0.27951479942938,  
  "HitRate@20": 0.7474389422565666,  
  "Recall@20": 0.7474389422565666,  
  "NDCG@20": 0.3395649118854531,  
  "MRR": 0.23425836968159186  
    
## XGB 1 embedding only:
  
"test_roc_auc": 0.9978354337543525,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.9844386941264046,   
  "Recall@1": 0.9844386941264046,  
  "NDCG@1": 0.9844386941264046,  
  "HitRate@5": 0.990960972670235,  
  "Recall@5": 0.990960972670235,  
  "NDCG@5": 0.9879858600115983,  
  "HitRate@10": 0.9936904044521641,  
  "Recall@10": 0.9936904044521641,  
  "NDCG@10": 0.9888747285715469,  
  "HitRate@20": 0.9958881287441069,  
  "Recall@20": 0.9958881287441069,  
  "NDCG@20": 0.9894290867061667,  
  "MRR": 0.9876156515164041  
    
## XGB embeddings + unique_genres_played + total_minutes_played

 "test_roc_auc": 0.8984196370886451,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.15873240934387295,  
  "Recall@1": 0.15873240934387295,  
  "NDCG@1": 0.15873240934387295,  
  "HitRate@5": 0.42036794158307045,  
  "Recall@5": 0.42036794158307045,  
  "NDCG@5": 0.2911270281102486,  
  "HitRate@10": 0.6116762964800965,  
  "Recall@10": 0.6116762964800965,  
  "NDCG@10": 0.3528269063107399,  
  "HitRate@20": 0.829924497536422,  
  "Recall@20": 0.829924497536422,  
  "NDCG@20": 0.4080475869535707,  
  "MRR": 0.2949994593681889  
  
## XGB COMPARE:
| XGB model                   | HitRate@1 | HitRate@10 |      MRR |
| --------------------------- | --------: | ---------: | -------: |
| XGB Baseline                |  0.776293 |   0.899365 | 0.818999 |
| XGB Network                 |  0.994009 |   0.997696 | 0.995188 |
| XGB embeddings only         |  0.106129 |   0.509163 | 0.234258 |
| XGB embeddings + basic info |  0.158732 |   0.611676 | 0.294999 |
| XGB one embedding           |  0.984439 |   0.993690 | 0.987616 |


## MODELS COMPARE:
| Model                                                        | HitRate@1 | HitRate@10 |      MRR |
| ------------------------------------------------------------ | --------: | ---------: | -------: |
| Naive Popularity                                             |  0.150580 |   0.587856 | 0.284082 |
| Naive Random                                                 |  0.011130 |   0.102123 | 0.053034 |
| Logistic Regression Baseline                                 |  0.160966 |   0.748538 | 0.338354 |
| Logistic Regression Network                                  |  0.777250 |   0.944702 | 0.843029 |
| Random Forest Baseline                                       |  0.619723 |   0.836766 | 0.696769 |
| Random Forest Network                                        |  0.958279 |   0.978696 | 0.965596 |
| XGB Baseline                                                 |  0.776293 |   0.899365 | 0.818999 |
| XGB Network                                                  |  0.994009 |   0.997696 | 0.995188 |
| LightGCN                                                     |  0.279784 |   0.799440 | 0.437903 |
| NN Baseline (BPR)                                            |  0.211159 |   0.720605 | 0.364067 |
| NN Network (BPR)                                             |  0.333841 |   0.843359 | 0.493309 |
| GraphSAGE Baseline                                           |  0.218851 |   0.745631 | 0.377659 |
| GraphSAGE Network                                            |  0.238311 |   0.768353 | 0.398809 |
| XGB Embeddings Only                                          |  0.106129 |   0.509163 | 0.234258 |
| XGB 1 Embedding Only                                         |  0.984439 |   0.993690 | 0.987616 |
| XGB Embeddings + unique_genres_played + total_minutes_played |  0.158732 |   0.611676 | 0.294999 |


| Model                                                        |      MRR |
| ------------------------------------------------------------ | -------: |
| XGB Network                                                  | 0.995188 |
| XGB 1 Embedding Only                                         | 0.987616 |
| Random Forest Network                                        | 0.965596 |
| Logistic Regression Network                                  | 0.843029 |
| XGB Baseline                                                 | 0.818999 |
| Random Forest Baseline                                       | 0.696769 |
| NN Network (BPR)                                             | 0.493309 |
| LightGCN                                                     | 0.437903 |
| GraphSAGE Network                                            | 0.398809 |
| GraphSAGE Baseline                                           | 0.377659 |
| NN Baseline (BPR)                                            | 0.364067 |
| Logistic Regression Baseline                                 | 0.338354 |
| XGB Embeddings + unique_genres_played + total_minutes_played | 0.294999 |
| Naive Popularity                                             | 0.284082 |
| XGB Embeddings Only                                          | 0.234258 |
| Naive Random                                                 | 0.053034 |
  
# cold-start  recalculating...  
## xgb baseline SIM

## xgb baseline  SIM



# FEATURE IMPORTANCE: recalculating...
## xgb baseline:
| Feature                                  | Mean drop in NDCG@10 |        Std | Mean permuted NDCG@10 |
| ---------------------------------------- | -------------------: | ---------: | --------------------: |
| `game_total_playtime_minutes`            |       **0.58292324** | 0.00155112 |            0.25105577 |
| `user_count`                             |       **0.56902361** | 0.00164226 |            0.26495539 |
| `release_date`                           |       **0.16499448** | 0.00050787 |            0.66898453 |
| `genres`                                 |       **0.13768380** | 0.00051125 |            0.69629521 |
| `developer`                              |       **0.12377001** | 0.00068134 |            0.71020900 |
| `publisher`                              |       **0.10204180** | 0.00037157 |            0.73193721 |
| `platforms`                              |           0.03544365 | 0.00036427 |            0.79853536 |
| `total_games_owned`                      |           0.01032169 | 0.00031582 |            0.82365732 |
| `user_playtime_group_Violent`            |           0.00204458 | 0.00009196 |            0.83193443 |
| `median_playtime_minutes`                |           0.00137048 | 0.00010929 |            0.83260853 |
| `user_playtime_group_Non-gameplay_Tools` |           0.00067957 | 0.00015038 |            0.83329944 |
| `unique_genres_played`                   |           0.00054665 | 0.00010147 |            0.83343236 |
| `user_playtime_group_Other`              |           0.00032175 | 0.00011275 |            0.83365725 |
| `country`                                |           0.00022009 | 0.00014627 |            0.83375892 |
| `user_playtime_group_Casual`             |           0.00009159 | 0.00003826 |            0.83388742 |
| `user_playtime_group_Sports`             |           0.00007552 | 0.00000640 |            0.83390349 |
| `user_playtime_group_Indie`              |           0.00006984 | 0.00004772 |            0.83390917 |
| `user_playtime_group_Action`             |           0.00005110 | 0.00012138 |            0.83392790 |
| `total_playtime_minutes`                 |           0.00004807 | 0.00000985 |            0.83393094 |
| `user_playtime_group_Simulation`         |           0.00002744 | 0.00001835 |            0.83395157 |
| `user_playtime_group_Strategy`           |           0.00000271 | 0.00002659 |            0.83397629 |
| `user_playtime_group_RPG`                |          -0.00001566 | 0.00001532 |            0.83399467 |
| `user_playtime_group_Racing`             |          -0.00001622 | 0.00002376 |            0.83399523 |
| `user_playtime_group_Adult`              |          -0.00002528 | 0.00001999 |            0.83400429 |
| `user_playtime_group_Adventure`          |          -0.00005992 | 0.00006962 |            0.83403893 |

## xgb network:
| Feature                                  | Group       | Mean drop in NDCG@10 |        Std | Mean permuted NDCG@10 |
| ---------------------------------------- | ----------- | -------------------: | ---------: | --------------------: |
| `game_total_playtime_minutes`            | numeric     |       **0.45987492** | 0.00027930 |            0.54008963 |
| `game_emb_0`                             | embedding   |          -0.00001182 | 0.00001671 |            0.99997637 |
| `total_games_owned`                      | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `total_playtime_minutes`                 | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `median_playtime_minutes`                | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `unique_genres_played`                   | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_count`                             | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `release_date`                           | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `friend_count`                           | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_1`                             | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_2`                             | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_3`                             | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_4`                             | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_5`                             | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_6`                             | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_7`                             | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_8`                             | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_9`                             | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_10`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_11`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_12`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_13`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_14`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_15`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_16`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_17`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_18`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_19`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_20`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_21`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_22`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_23`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_24`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_25`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_26`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_27`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_28`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_29`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_30`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `game_emb_31`                            | embedding   |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Action`             | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Adventure`          | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Adult`              | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Casual`             | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Indie`              | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Racing`             | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_RPG`                | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Simulation`         | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Strategy`           | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Sports`             | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Violent`            | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Non-gameplay_Tools` | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Other`              | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `genres`                                 | categorical |           0.00000000 | 0.00000000 |            0.99996455 |
| `country`                                | categorical |           0.00000000 | 0.00000000 |            0.99996455 |
| `publisher`                              | categorical |           0.00000000 | 0.00000000 |            0.99996455 |
| `developer`                              | categorical |           0.00000000 | 0.00000000 |            0.99996455 |
| `platforms`                              | categorical |           0.00000000 | 0.00000000 |            0.99996455 |


## xgb one embedding:
| Feature                                  | Group       | Mean drop in NDCG@10 |        Std | Mean permuted NDCG@10 |
| ---------------------------------------- | ----------- | -------------------: | ---------: | --------------------: |
| `game_total_playtime_minutes`            | numeric     |       **0.54477562** | 0.00008476 |            0.45518894 |
| `game_emb_0`                             | embedding   |          -0.00001182 | 0.00001671 |            0.99997637 |
| `total_playtime_minutes`                 | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `total_games_owned`                      | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `median_playtime_minutes`                | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `unique_genres_played`                   | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_count`                             | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `release_date`                           | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `friend_count`                           | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Action`             | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Adventure`          | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_RPG`                | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Adult`              | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Casual`             | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Indie`              | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Racing`             | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Simulation`         | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Strategy`           | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Sports`             | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Violent`            | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `genres`                                 | categorical |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Non-gameplay_Tools` | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `user_playtime_group_Other`              | numeric     |           0.00000000 | 0.00000000 |            0.99996455 |
| `country`                                | categorical |           0.00000000 | 0.00000000 |            0.99996455 |
| `publisher`                              | categorical |           0.00000000 | 0.00000000 |            0.99996455 |
| `developer`                              | categorical |           0.00000000 | 0.00000000 |            0.99996455 |
| `platforms`                              | categorical |           0.00000000 | 0.00000000 |            0.99996455 |

## xgb only embeddings:
| Embedding dimension | Mean drop in NDCG@10 |        Std | Mean permuted NDCG@10 |
| ------------------- | -------------------: | ---------: | --------------------: |
| `game_emb_0`        |       **0.14224194** | 0.00171487 |            0.12830817 |
| `game_emb_1`        |       **0.06144283** | 0.00136823 |            0.20910728 |
| `game_emb_6`        |           0.00349115 | 0.00169083 |            0.26705897 |
| `game_emb_8`        |           0.00325253 | 0.00003011 |            0.26729758 |
| `game_emb_3`        |           0.00147313 | 0.00018580 |            0.26907698 |
| `game_emb_15`       |           0.00116910 | 0.00006209 |            0.26938101 |
| `game_emb_28`       |           0.00088728 | 0.00017180 |            0.26966283 |
| `game_emb_29`       |           0.00088703 | 0.00011552 |            0.26966308 |
| `game_emb_2`        |           0.00081123 | 0.00008229 |            0.26973888 |
| `game_emb_16`       |           0.00080329 | 0.00006958 |            0.26974682 |
| `game_emb_14`       |           0.00063307 | 0.00006620 |            0.26991704 |
| `game_emb_31`       |           0.00051383 | 0.00009130 |            0.27003628 |
| `game_emb_24`       |           0.00039220 | 0.00008960 |            0.27015791 |
| `game_emb_25`       |           0.00038720 | 0.00007029 |            0.27016291 |
| `game_emb_23`       |           0.00034507 | 0.00014277 |            0.27020504 |
| `game_emb_26`       |           0.00024270 | 0.00001970 |            0.27030741 |
| `game_emb_27`       |           0.00021993 | 0.00002063 |            0.27033019 |
| `game_emb_22`       |           0.00019195 | 0.00008518 |            0.27035816 |
| `game_emb_20`       |           0.00017971 | 0.00004726 |            0.27037040 |
| `game_emb_21`       |           0.00011915 | 0.00002033 |            0.27043096 |
| `game_emb_18`       |           0.00007733 | 0.00013792 |            0.27047279 |
| `game_emb_19`       |           0.00005886 | 0.00005151 |            0.27049125 |
| `game_emb_30`       |          -0.00018510 | 0.00001987 |            0.27073521 |
| `game_emb_12`       |          -0.00035705 | 0.00002569 |            0.27090716 |
| `game_emb_13`       |          -0.00060055 | 0.00012872 |            0.27115067 |
| `game_emb_7`        |          -0.00064567 | 0.00023109 |            0.27119578 |
| `game_emb_9`        |          -0.00067322 | 0.00010843 |            0.27122334 |
| `game_emb_17`       |          -0.00071608 | 0.00009099 |            0.27126619 |
| `game_emb_10`       |          -0.00177374 | 0.00020598 |            0.27232385 |
| `game_emb_11`       |          -0.00193819 | 0.00010962 |            0.27248831 |
| `game_emb_5`        |          -0.00266256 | 0.00011444 |            0.27321267 |
| `game_emb_4`        |          -0.00433035 | 0.00058855 |            0.27488046 |

## xgb embeddings +basic info:
| Feature                  | Group      | Mean drop in NDCG@10 |        Std | Mean permuted NDCG@10 |
| ------------------------ | ---------- | -------------------: | ---------: | --------------------: |
| `game_emb_0`             | embedding  |       **0.18233298** | 0.00173202 |            0.15736434 |
| `game_emb_1`             | embedding  |       **0.05392925** | 0.00074630 |            0.28576807 |
| `unique_genres_played`   | basic_info |       **0.03714114** | 0.00078417 |            0.30255619 |
| `total_playtime_minutes` | basic_info |       **0.01415943** | 0.00011515 |            0.32553789 |
| `game_emb_17`            | embedding  |           0.00715162 | 0.00013173 |            0.33254571 |
| `game_emb_7`             | embedding  |           0.00367668 | 0.00048933 |            0.33602065 |
| `game_emb_6`             | embedding  |           0.00330213 | 0.00017736 |            0.33639520 |
| `game_emb_3`             | embedding  |           0.00139456 | 0.00015272 |            0.33830277 |
| `game_emb_11`            | embedding  |           0.00133717 | 0.00012759 |            0.33836016 |
| `game_emb_13`            | embedding  |           0.00132002 | 0.00004839 |            0.33837731 |
| `game_emb_14`            | embedding  |           0.00112750 | 0.00031100 |            0.33856983 |
| `game_emb_30`            | embedding  |           0.00091958 | 0.00013383 |            0.33877775 |
| `game_emb_25`            | embedding  |           0.00087075 | 0.00006504 |            0.33882658 |
| `game_emb_8`             | embedding  |           0.00085805 | 0.00013961 |            0.33883928 |
| `game_emb_4`             | embedding  |           0.00076964 | 0.00016104 |            0.33892769 |
| `game_emb_15`            | embedding  |           0.00063313 | 0.00017703 |            0.33906419 |
| `game_emb_12`            | embedding  |           0.00044186 | 0.00016977 |            0.33925547 |
| `game_emb_28`            | embedding  |           0.00038310 | 0.00023094 |            0.33931422 |
| `game_emb_16`            | embedding  |           0.00033865 | 0.00002938 |            0.33935867 |
| `game_emb_18`            | embedding  |           0.00032969 | 0.00007096 |            0.33936763 |
| `game_emb_19`            | embedding  |           0.00029126 | 0.00016577 |            0.33940607 |
| `game_emb_20`            | embedding  |           0.00023488 | 0.00007678 |            0.33946244 |
| `game_emb_21`            | embedding  |           0.00020974 | 0.00006371 |            0.33948759 |
| `game_emb_29`            | embedding  |           0.00017286 | 0.00005543 |            0.33952447 |
| `game_emb_27`            | embedding  |           0.00002701 | 0.00008394 |            0.33967032 |
| `game_emb_26`            | embedding  |          -0.00002923 | 0.00011191 |            0.33972655 |
| `game_emb_24`            | embedding  |          -0.00008983 | 0.00030121 |            0.33978716 |
| `game_emb_22`            | embedding  |          -0.00014303 | 0.00003232 |            0.33984036 |
| `game_emb_10`            | embedding  |          -0.00016807 | 0.00004281 |            0.33986540 |
| `game_emb_23`            | embedding  |          -0.00020482 | 0.00009209 |            0.33990215 |
| `game_emb_5`             | embedding  |          -0.00026474 | 0.00020016 |            0.33996207 |
| `game_emb_31`            | embedding  |          -0.00042300 | 0.00020492 |            0.34012033 |
| `game_emb_2`             | embedding  |          -0.00050708 | 0.00034453 |            0.34020441 |
| `game_emb_9`             | embedding  |          -0.00148062 | 0.00009238 |            0.34117795 |


