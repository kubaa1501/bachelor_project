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
<details>
<summary><b>MODELS</b></summary>
    
## MODELS:
  
### NAIVE POPULARITY:
  
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
    
### NAIVE RANDOM:
  
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
      
### LOGISTIC REGRESSION BASELINE: 
  
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
    
### LOGISTIC REGRESSION NETWORK: 
  
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
    
### RANDOM FOREST BASELINE: 
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
    
### RANDOM FOREST NETWORK: 
  
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
      
### XGB BASELINE:
    
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
        
### XGB NETWORK: 

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
      
### lightGCN 
      
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
    
### NN_baseline   
  
  "n_users_evaluated": 28211,  
    "HitRate@1": 0.191308354897026,  
    "HitRate@5": 0.4951614618411258,  
    "HitRate@10": 0.6909361596540357,  
    "HitRate@20": 0.8784516677891603,  
    "Recall@1": 0.191308354897026,  
    "Recall@5": 0.4951614618411258,  
    "Recall@10": 0.6909361596540357,  
    "Recall@20": 0.8784516677891603,  
    "NDCG@1": 0.191308354897026,  
    "NDCG@5": 0.3459096007433145,  
    "NDCG@10": 0.4090438561030869,  
    "NDCG@20": 0.45665369839857356,  
    "MRR": 0.3401984308816658  
      
### NN_network    
  
  "n_users_evaluated": 28211,  
    "HitRate@1": 0.19517209599092553,  
    "HitRate@5": 0.4989543086030272,  
    "HitRate@10": 0.6973875438658679,  
    "HitRate@20": 0.8821027258870653,  
    "Recall@1": 0.19517209599092553,  
    "Recall@5": 0.4989543086030272,  
    "Recall@10": 0.6973875438658679,  
    "Recall@20": 0.8821027258870653,  
    "NDCG@1": 0.19517209599092553,  
    "NDCG@5": 0.3498498561717657,  
    "NDCG@10": 0.4139153990045359,  
    "NDCG@20": 0.46082284790923866,  
    "MRR": 0.3443020487800702  
      
### GraphSAGE baseline 

   "n_users_evaluated": 28211,  
    "HitRate@1": 0.20289957817872462,    
    "HitRate@5": 0.5338343199461203,   
    "HitRate@10": 0.7291127574350431,    
    "HitRate@20": 0.8961752507886994,    
    "Recall@1": 0.20289957817872462,    
    "Recall@5": 0.5338343199461203,    
    "Recall@10": 0.7291127574350431,    
    "Recall@20": 0.8961752507886994,    
    "NDCG@1": 0.20289957817872462,    
    "NDCG@5": 0.3717026091676068,    
    "NDCG@10": 0.4348885044361438,    
    "NDCG@20": 0.4773046721774314,    
    "MRR": 0.359860154228877   

### GraphSAGE network

   "n_users_evaluated": 28211,  
    "HitRate@1": 0.20729502676261033,  
    "HitRate@5": 0.5461344865478005,  
    "HitRate@10": 0.7365566622948495,  
    "HitRate@20": 0.9004289107085889,  
    "Recall@1": 0.20729502676261033,  
    "Recall@5": 0.5461344865478005,  
    "Recall@10": 0.7365566622948495,  
    "Recall@20": 0.9004289107085889,  
    "NDCG@1": 0.20729502676261033,  
    "NDCG@5": 0.3810175742678832,  
    "NDCG@10": 0.4426932551793056,  
    "NDCG@20": 0.48441930026704577,  
    "MRR": 0.367246234841923  

</details>  
<details>
<summary><b>XGB variations</b></summary>
  
### XGB embeddings only:
  
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
    
## XGB emb0 + playtime
  
  "test_roc_auc": 0.8844167444259997,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.1355499627804757,  
  "Recall@1": 0.1355499627804757,  
  "NDCG@1": 0.1355499627804757,  
  "HitRate@5": 0.3804544326681082,  
  "Recall@5": 0.3804544326681082,  
  "NDCG@5": 0.2597729322938029,  
  "HitRate@10": 0.5697777462691858,  
  "Recall@10": 0.5697777462691858,  
  "NDCG@10": 0.3203092175224023,  
  "HitRate@20": 0.8063166849810358,  
  "Recall@20": 0.8063166849810358,  
  "NDCG@20": 0.3801327502536333,  
  "MRR": 0.2676715606500115  
    
## XGB baseline (log(user_count)):  **NEW**

  "test_roc_auc": 0.9670098515541268,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.7699833398319804,  
  "Recall@1": 0.7699833398319804,  
  "NDCG@1": 0.7699833398319804,  
  "HitRate@5": 0.8582113360036865,  
  "Recall@5": 0.8582113360036865,  
  "NDCG@5": 0.8172154819912589,  
  "HitRate@10": 0.8951118358087271,  
  "Recall@10": 0.8951118358087271,  
  "NDCG@10": 0.8291170470938715,  
  "HitRate@20": 0.9363014426996562,  
  "Recall@20": 0.9363014426996562,  
  "NDCG@20": 0.8395611181090973,  
  "MRR": 0.8131311751978452  

## XGB baseline +emb0 - user-count **NEW**
  
"test_roc_auc": 0.9077119983502737,  
  "n_users_evaluated": 28211, 
  "HitRate@1": 0.18811810995710893,  
  "Recall@1": 0.18811810995710893,  
  "NDCG@1": 0.18811810995710893,  
  "HitRate@5": 0.464499663251923,  
  "Recall@5": 0.464499663251923,  
  "NDCG@5": 0.32795707236574256,  
  "HitRate@10": 0.650809967743079,  
  "Recall@10": 0.650809967743079,  
  "NDCG@10": 0.38810799734545176,  
  "HitRate@20": 0.8473999503739676,  
  "Recall@20": 0.8473999503739676,  
  "NDCG@20": 0.4380110230719495, 
  "MRR": 0.3268621656777562  

  ## XGB baseline - user_count **NEW**
     
  "test_roc_auc": 0.898825278116792,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.17876005813335225,  
  "Recall@1": 0.17876005813335225,  
  "NDCG@1": 0.17876005813335225,  
  "HitRate@5": 0.4426642089964907,  
  "Recall@5": 0.4426642089964907,  
  "NDCG@5": 0.3123512229518346,  
  "HitRate@10": 0.625500691219737,  
  "Recall@10": 0.625500691219737,  
  "NDCG@10": 0.37125162655488037,  
  "HitRate@20": 0.8226578285066108,  
  "Recall@20": 0.8226578285066108,  
  "NDCG@20": 0.42125113163138717,  
  "MRR": 0.31345076987935355  

## XGB baseline - double user_count  **NEW**
  
"test_roc_auc": 0.9673081422580074,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.7716848037999362,  
  "Recall@1": 0.7716848037999362,  
  "NDCG@1": 0.7716848037999362,  
  "HitRate@5": 0.8565453192017298,  
  "Recall@5": 0.8565453192017298,  
  "NDCG@5": 0.8166319086230582,  
  "HitRate@10": 0.8958207791287086,  
  "Recall@10": 0.8958207791287086,  
  "NDCG@10": 0.8293071451314168,  
  "HitRate@20": 0.9387472971535926,  
  "Recall@20": 0.9387472971535926,  
  "NDCG@20": 0.8402310884684286,  
  "MRR": 0.8133206940685888  

## XGB emb0 + user_count

  "test_roc_auc": 0.9956989212309476,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.9528552692212258,  
  "Recall@1": 0.9528552692212258,  
  "NDCG@1": 0.9528552692212258,  
  "HitRate@5": 0.9792279607245401,  
  "Recall@5": 0.9792279607245401,  
  "NDCG@5": 0.9670199796936525,  
  "HitRate@10": 0.9878416220623161,  
  "Recall@10": 0.9878416220623161,  
  "NDCG@10": 0.9698228477061712,  
  "HitRate@20": 0.9936549572861649,  
  "Recall@20": 0.9936549572861649,  
  "NDCG@20": 0.9713046652004863,  
  "MRR": 0.9647126537762174  
    
    
## XGB COMPARE:
| XGB model                   | HitRate@1 | HitRate@10 |      MRR |
| --------------------------- | --------: | ---------: | -------: |
| XGB Network                 |  0.994009 |   0.997696 | 0.995188 |
| XGB one embedding           |  0.984439 |   0.993690 | 0.987616 |
| XGB emb0 + user_count       |  0.964712 |   0.952855 | 0.987841 |
| XGB Baseline                |  0.776293 |   0.899365 | 0.818999 |
| XGB Baseline double user_cou|  0.771684 |   0.771685 | 0.813321 |
| XGB Baseline (log)          |  0.769983 |   0.895112 | 0.813131 |
| XGB +emb0 - user_count      |  0.188118 |   0.65081  | 0.326862 |
| XGB baseline - user_count   |  0.178760 |   0.625501 | 0.313451 |
| XGB embeddings + basic info |  0.158732 |   0.611676 | 0.294999 |
| XGB emb0 + playtime         |  0.135549 |   0.569778 | 0.267672 |
| XGB embeddings only         |  0.106129 |   0.509163 | 0.234258 |

### Ranking by MRR

| Model | MRR |
|---|---:|
| XGB Network | 0.995188 |
| XGB 1 Embedding Only | 0.987616 |
| Random Forest Network | 0.965596 |
| Logistic Regression Network | 0.843029 |
| XGB Baseline | 0.818999 |
| Random Forest Baseline | 0.696769 |
| LightGCN | 0.437903 |
| GraphSAGE Network | 0.367246 |
| GraphSAGE Baseline | 0.359860 |
| NN Network | 0.344302 |  
| NN Baseline | 0.340198 |
| Logistic Regression Baseline | 0.338354 |
| XGB Embeddings + unique_genres_played + total_minutes_played | 0.294999 |
| Naive Popularity | 0.284082 |
| XGB emb0 + playtime | 0.267672 |
| XGB Embeddings Only | 0.234258 |
| Naive Random | 0.053034 |

</details>
<details>
  <summary><b>Cold-start split stats</b></summary>
  
  ### database:
    
  "random_seed": 42,  
  "n_users_requested": 2000,  
  "common_users_count": 28211,  
  "heldout_users_count": 2000,  
  "train_users_before": 31021,  
  "val_users_before": 28211,  
  "test_users_before": 28211,  
  "train_rows_before": 43494594,  
  "val_rows_before": 2849311,  
  "test_rows_before": 2849311,  
  "train_users_after": 29021,  
  "val_users_after": 2000,  
  "test_users_after": 2000,  
  "train_rows_after": 40443381,  
  "val_rows_after": 202000,  
  "test_rows_after": 202000,  
  "train_overlap_with_heldout": 0,  
  "val_equals_heldout": true,  
  "test_equals_heldout": true,  
  "val_equals_test": true  

-------------------------------------------------------------    
### xgb baseline SIM
  "test_roc_auc": 0.9667584362499999,  
  "n_users_evaluated": 2000,  
  "HitRate@1": 0.7745,  
  "Recall@1": 0.7745,  
  "NDCG@1": 0.7745,  
  "HitRate@5": 0.8575,  
  "Recall@5": 0.8575,  
  "NDCG@5": 0.8195664995750498,  
  "HitRate@10": 0.891,  
  "Recall@10": 0.891,  
  "NDCG@10": 0.8303920669838222,  
  "HitRate@20": 0.9325,  
  "Recall@20": 0.9325,  
  "NDCG@20": 0.8409538876976344,  
  "MRR": 0.8161863790621792  
    
### xgb network SIM  
 "test_roc_auc": 0.9991920975,  
  "n_users_evaluated": 2000,  
  "HitRate@1": 0.995,  
  "Recall@1": 0.995,  
  "NDCG@1": 0.995,  
  "HitRate@5": 0.996,  
  "Recall@5": 0.996,  
  "NDCG@5": 0.995508891280403,  
  "HitRate@10": 0.997,  
  "Recall@10": 0.997,  
  "NDCG@10": 0.9958536615406236,  
  "HitRate@20": 0.998,  
  "Recall@20": 0.998,  
  "NDCG@20": 0.9961282520906628,  
  "MRR": 0.9956616644366645  

## **COMPARISON:**
| Metric            | XGB Baseline | XGB Baseline SIM |         Δ |
| ----------------- | -----------: | ---------------: | --------: |
| test_roc_auc      |       0.9681 |           0.9668 | -0.001367 |
| HitRate@1         |       0.7763 |           0.7745 | -0.001793 |
| NDCG@1            |       0.7763 |           0.7745 | -0.001793 |
| HitRate@5         |       0.8649 |           0.8575 | -0.007446 |
| NDCG@5            |       0.8237 |           0.8196 | -0.004154 |
| HitRate@10        |       0.8994 |           0.8910 | -0.008365 |
| NDCG@10           |       0.8348 |           0.8304 | -0.004447 |
| HitRate@20        |       0.9381 |           0.9325 | -0.005574 |
| NDCG@20           |       0.8447 |           0.8410 | -0.003697 |
| MRR               |       0.8190 |           0.8162 | -0.002813 |
  
  
| Metric            | XGB Network | XGB Network SIM |         Δ |
| ----------------- | ----------: | --------------: | --------: |
| test_roc_auc      |      0.9992 |          0.9992 | -0.000041 |
| HitRate@1         |      0.9940 |          0.9950 | +0.000991 |
| NDCG@1            |      0.9940 |          0.9950 | +0.000991 |
| HitRate@5         |      0.9965 |          0.9960 | -0.000526 |
| NDCG@5            |      0.9953 |          0.9955 | +0.000179 |
| HitRate@10        |      0.9977 |          0.9970 | -0.000696 |
| NDCG@10           |      0.9957 |          0.9959 | +0.000147 |
| HitRate@20        |      0.9985 |          0.9980 | -0.000511 |
| NDCG@20           |      0.9959 |          0.9961 | +0.000213 |
| MRR               |      0.9952 |          0.9957 | +0.000474 |
  
</details> 

<details>
  <summary><b>feature importance</b></summary> 
    
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
| Rank | Feature                                | Feature group | Mean drop in NDCG@10 | Std drop |
| ---: | -------------------------------------- | ------------- | -------------------: | -------: |
|    1 | game_emb_0                             | embedding     |             0.987965 | 0.000272 |
|    2 | game_emb_1                             | embedding     |             0.916040 | 0.000843 |
|    3 | user_count                             | numeric       |             0.450489 | 0.000141 |
|    4 | game_emb_2                             | embedding     |             0.009604 | 0.000182 |
|    5 | game_total_playtime_minutes            | numeric       |             0.002632 | 0.000014 |
|    6 | game_emb_4                             | embedding     |             0.002138 | 0.000151 |
|    7 | game_emb_12                            | embedding     |             0.002096 | 0.000074 |
|    8 | game_emb_6                             | embedding     |             0.001822 | 0.000081 |
|    9 | game_emb_7                             | embedding     |             0.001739 | 0.000090 |
|   10 | game_emb_8                             | embedding     |             0.000758 | 0.000043 |
|   11 | game_emb_14                            | embedding     |             0.000637 | 0.000083 |
|   12 | total_games_owned                      | numeric       |             0.000410 | 0.000021 |
|   13 | game_emb_18                            | embedding     |             0.000406 | 0.000030 |
|   14 | game_emb_11                            | embedding     |             0.000280 | 0.000022 |
|   15 | release_date                           | numeric       |             0.000265 | 0.000025 |
|   16 | game_emb_30                            | embedding     |             0.000245 | 0.000031 |
|   17 | game_emb_29                            | embedding     |             0.000242 | 0.000023 |
|   18 | genres                                 | categorical   |             0.000216 | 0.000007 |
|   19 | game_emb_5                             | embedding     |             0.000215 | 0.000037 |
|   20 | game_emb_10                            | embedding     |             0.000204 | 0.000034 |
|   21 | game_emb_17                            | embedding     |             0.000192 | 0.000024 |
|   22 | game_emb_28                            | embedding     |             0.000177 | 0.000016 |
|   23 | game_emb_20                            | embedding     |             0.000166 | 0.000028 |
|   24 | publisher                              | categorical   |             0.000140 | 0.000009 |
|   25 | game_emb_3                             | embedding     |             0.000132 | 0.000010 |
|   26 | game_emb_26                            | embedding     |             0.000126 | 0.000028 |
|   27 | game_emb_22                            | embedding     |             0.000120 | 0.000001 |
|   28 | game_emb_24                            | embedding     |             0.000118 | 0.000021 |
|   29 | country                                | categorical   |             0.000115 | 0.000014 |
|   30 | game_emb_19                            | embedding     |             0.000109 | 0.000023 |
|   31 | game_emb_9                             | embedding     |             0.000109 | 0.000033 |
|   32 | game_emb_13                            | embedding     |             0.000108 | 0.000017 |
|   33 | game_emb_15                            | embedding     |             0.000107 | 0.000007 |
|   34 | user_playtime_group_Violent            | numeric       |             0.000095 | 0.000031 |
|   35 | developer                              | categorical   |             0.000094 | 0.000026 |
|   36 | game_emb_31                            | embedding     |             0.000093 | 0.000018 |
|   37 | game_emb_27                            | embedding     |             0.000090 | 0.000030 |
|   38 | median_playtime_minutes                | numeric       |             0.000090 | 0.000017 |
|   39 | friend_count                           | numeric       |             0.000081 | 0.000020 |
|   40 | user_playtime_group_Action             | numeric       |             0.000070 | 0.000011 |
|   41 | user_playtime_group_Non-gameplay_Tools | numeric       |             0.000060 | 0.000003 |
|   42 | game_emb_25                            | embedding     |             0.000058 | 0.000004 |
|   43 | game_emb_16                            | embedding     |             0.000056 | 0.000009 |
|   44 | user_playtime_group_Casual             | numeric       |             0.000053 | 0.000020 |
|   45 | user_playtime_group_Racing             | numeric       |             0.000043 | 0.000030 |
|   46 | game_emb_21                            | embedding     |             0.000036 | 0.000022 |
|   47 | unique_genres_played                   | numeric       |             0.000036 | 0.000001 |
|   48 | user_playtime_group_Other              | numeric       |             0.000035 | 0.000018 |
|   49 | user_playtime_group_RPG                | numeric       |             0.000035 | 0.000012 |
|   50 | user_playtime_group_Adult              | numeric       |             0.000034 | 0.000009 |
|   51 | game_emb_23                            | embedding     |             0.000026 | 0.000014 |
|   52 | user_playtime_group_Simulation         | numeric       |             0.000017 | 0.000006 |
|   53 | total_playtime_minutes                 | numeric       |             0.000010 | 0.000001 |
|   54 | user_playtime_group_Adventure          | numeric       |             0.000006 | 0.000019 |
|   55 | user_playtime_group_Strategy           | numeric       |             0.000003 | 0.000013 |
|   56 | user_playtime_group_Indie              | numeric       |             0.000000 | 0.000012 |
|   57 | platforms                              | categorical   |             0.000000 | 0.000000 |
|   58 | user_playtime_group_Sports             | numeric       |            -0.000005 | 0.000004 |


## xgb one embedding:
| Rank | Feature                                | Feature group | Mean drop in NDCG@10 | Std drop |
| ---: | -------------------------------------- | ------------- | -------------------: | -------: |
|    1 | game_emb_0                             | embedding     |             0.974195 | 0.000577 |
|    2 | user_count                             | numeric       |             0.475076 | 0.000497 |
|    3 | release_date                           | numeric       |             0.015984 | 0.000390 |
|    4 | game_total_playtime_minutes            | numeric       |             0.009521 | 0.000013 |
|    5 | genres                                 | categorical   |             0.002683 | 0.000014 |
|    6 | publisher                              | categorical   |             0.001548 | 0.000036 |
|    7 | total_games_owned                      | numeric       |             0.001159 | 0.000127 |
|    8 | platforms                              | categorical   |             0.000920 | 0.000024 |
|    9 | developer                              | categorical   |             0.000853 | 0.000078 |
|   10 | user_playtime_group_Violent            | numeric       |             0.000353 | 0.000050 |
|   11 | user_playtime_group_Action             | numeric       |             0.000108 | 0.000063 |
|   12 | user_playtime_group_Indie              | numeric       |             0.000093 | 0.000025 |
|   13 | median_playtime_minutes                | numeric       |             0.000091 | 0.000008 |
|   14 | country                                | categorical   |             0.000062 | 0.000012 |
|   15 | friend_count                           | numeric       |             0.000047 | 0.000002 |
|   16 | user_playtime_group_Racing             | numeric       |             0.000044 | 0.000017 |
|   17 | user_playtime_group_Strategy           | numeric       |             0.000044 | 0.000025 |
|   18 | user_playtime_group_Other              | numeric       |             0.000039 | 0.000036 |
|   19 | user_playtime_group_RPG                | numeric       |             0.000032 | 0.000019 |
|   20 | user_playtime_group_Non-gameplay_Tools | numeric       |             0.000030 | 0.000022 |
|   21 | user_playtime_group_Adult              | numeric       |             0.000012 | 0.000012 |
|   22 | user_playtime_group_Simulation         | numeric       |             0.000005 | 0.000011 |
|   23 | user_playtime_group_Adventure          | numeric       |             0.000001 | 0.000001 |
|   24 | user_playtime_group_Casual             | numeric       |            -0.000001 | 0.000019 |
|   25 | user_playtime_group_Sports             | numeric       |            -0.000001 | 0.000017 |
|   26 | unique_genres_played                   | numeric       |            -0.000002 | 0.000037 |
|   27 | total_playtime_minutes                 | numeric       |            -0.000005 | 0.000006 |


## xgb only embeddings:
| Rank | Feature     | Mean drop in NDCG@10 | Std drop |
| ---: | ----------- | -------------------: | -------: |
|    1 | game_emb_0  |             0.142242 | 0.001715 |
|    2 | game_emb_1  |             0.061443 | 0.001368 |
|    3 | game_emb_6  |             0.003491 | 0.001691 |
|    4 | game_emb_8  |             0.003253 | 0.000030 |
|    5 | game_emb_3  |             0.001473 | 0.000186 |
|    6 | game_emb_15 |             0.001169 | 0.000062 |
|    7 | game_emb_28 |             0.000887 | 0.000172 |
|    8 | game_emb_29 |             0.000887 | 0.000116 |
|    9 | game_emb_2  |             0.000811 | 0.000082 |
|   10 | game_emb_16 |             0.000803 | 0.000070 |
|   11 | game_emb_14 |             0.000633 | 0.000066 |
|   12 | game_emb_31 |             0.000514 | 0.000091 |
|   13 | game_emb_24 |             0.000392 | 0.000090 |
|   14 | game_emb_25 |             0.000387 | 0.000070 |
|   15 | game_emb_23 |             0.000345 | 0.000143 |
|   16 | game_emb_26 |             0.000243 | 0.000020 |
|   17 | game_emb_27 |             0.000220 | 0.000021 |
|   18 | game_emb_22 |             0.000192 | 0.000085 |
|   19 | game_emb_20 |             0.000180 | 0.000047 |
|   20 | game_emb_21 |             0.000119 | 0.000020 |
|   21 | game_emb_18 |             0.000077 | 0.000138 |
|   22 | game_emb_19 |             0.000059 | 0.000052 |
|   23 | game_emb_30 |            -0.000185 | 0.000020 |
|   24 | game_emb_12 |            -0.000357 | 0.000026 |
|   25 | game_emb_13 |            -0.000601 | 0.000129 |
|   26 | game_emb_7  |            -0.000646 | 0.000231 |
|   27 | game_emb_9  |            -0.000673 | 0.000108 |
|   28 | game_emb_17 |            -0.000716 | 0.000091 |
|   29 | game_emb_10 |            -0.001774 | 0.000206 |
|   30 | game_emb_11 |            -0.001938 | 0.000110 |
|   31 | game_emb_5  |            -0.002663 | 0.000114 |
|   32 | game_emb_4  |            -0.004330 | 0.000589 |
  


## xgb embeddings +basic info:
| Rank | Feature                | Feature group | Mean drop in NDCG@10 | Std drop |
| ---: | ---------------------- | ------------- | -------------------: | -------: |
|    1 | game_emb_0             | embedding     |             0.182333 | 0.001732 |
|    2 | game_emb_1             | embedding     |             0.053929 | 0.000746 |
|    3 | unique_genres_played   | basic_info    |             0.037141 | 0.000784 |
|    4 | total_playtime_minutes | basic_info    |             0.014159 | 0.000115 |
|    5 | game_emb_17            | embedding     |             0.007152 | 0.000132 |
|    6 | game_emb_7             | embedding     |             0.003677 | 0.000489 |
|    7 | game_emb_6             | embedding     |             0.003302 | 0.000177 |
|    8 | game_emb_3             | embedding     |             0.001395 | 0.000153 |
|    9 | game_emb_11            | embedding     |             0.001337 | 0.000128 |
|   10 | game_emb_13            | embedding     |             0.001320 | 0.000048 |
|   11 | game_emb_14            | embedding     |             0.001127 | 0.000311 |
|   12 | game_emb_30            | embedding     |             0.000920 | 0.000134 |
|   13 | game_emb_25            | embedding     |             0.000871 | 0.000065 |
|   14 | game_emb_8             | embedding     |             0.000858 | 0.000140 |
|   15 | game_emb_4             | embedding     |             0.000770 | 0.000161 |
|   16 | game_emb_15            | embedding     |             0.000633 | 0.000177 |
|   17 | game_emb_12            | embedding     |             0.000442 | 0.000170 |
|   18 | game_emb_28            | embedding     |             0.000383 | 0.000231 |
|   19 | game_emb_16            | embedding     |             0.000339 | 0.000029 |
|   20 | game_emb_18            | embedding     |             0.000330 | 0.000071 |
|   21 | game_emb_19            | embedding     |             0.000291 | 0.000166 |
|   22 | game_emb_20            | embedding     |             0.000235 | 0.000077 |
|   23 | game_emb_21            | embedding     |             0.000210 | 0.000064 |
|   24 | game_emb_29            | embedding     |             0.000173 | 0.000055 |
|   25 | game_emb_27            | embedding     |             0.000027 | 0.000084 |
|   26 | game_emb_26            | embedding     |            -0.000029 | 0.000112 |
|   27 | game_emb_24            | embedding     |            -0.000090 | 0.000301 |
|   28 | game_emb_22            | embedding     |            -0.000143 | 0.000032 |
|   29 | game_emb_10            | embedding     |            -0.000168 | 0.000043 |
|   30 | game_emb_23            | embedding     |            -0.000205 | 0.000092 |
|   31 | game_emb_5             | embedding     |            -0.000265 | 0.000200 |
|   32 | game_emb_31            | embedding     |            -0.000423 | 0.000205 |
|   33 | game_emb_2             | embedding     |            -0.000507 | 0.000345 |
|   34 | game_emb_9             | embedding     |            -0.001481 | 0.000092 |


</details> 

<details>
  <summary><b>plots</b></summary> 
  <img width="2200" height="1760" alt="01_scatter_emb0_emb1_color_usercount_size_playtime" src="https://github.com/user-attachments/assets/6ea5bd7e-9be7-4d49-98ef-d1f47ed00ce7" />
<img width="2200" height="1760" alt="emb0_emb1_hexbin_mean_log_playtime" src="https://github.com/user-attachments/assets/aedd45fb-4272-4cce-b93a-a625d8fae93b" />
<img width="2200" height="1760" alt="emb0_emb1_hexbin_mean_log_user_count" src="https://github.com/user-attachments/assets/cd0b3244-1322-4792-a770-695a94042884" />
  <img width="1980" height="1540" alt="02_hexbin_emb0_vs_log_user_count" src="https://github.com/user-attachments/assets/93d10fd9-77da-4a54-94f7-75662162c3e4" />
<img width="1980" height="1540" alt="03_hexbin_emb0_vs_log_game_total_playtime" src="https://github.com/user-attachments/assets/da779f39-2c55-4cfd-bd28-26600146993d" />
<img width="2200" height="1540" alt="04_hist_emb0_by_popularity_group" src="https://github.com/user-attachments/assets/d76bf7a0-76e4-4d37-9e40-a17af4a31ac0" />
<img width="1980" height="1320" alt="05_binned_emb0_vs_mean_log_user_count" src="https://github.com/user-attachments/assets/b68f66d3-39c8-47bb-a4fe-83b26b2edf55" />
<img width="1980" height="1320" alt="06_binned_emb0_vs_mean_log_playtime" src="https://github.com/user-attachments/assets/0cb9d3c7-4552-44bf-b7d0-25a9eeaf6131" />
<img width="1540" height="1320" alt="07_spearman_correlation_heatmap" src="https://github.com/user-attachments/assets/98ae00d4-f02e-4ade-9e30-56e3c6dd4969" />
<img width="3937" height="3773" alt="genre_one_vs_rest_panels_mapped" src="https://github.com/user-attachments/assets/c4922a68-89de-4816-bf66-0f094bc8f2d9" />
<img width="3080" height="1540" alt="genre_share_across_emb0_bins_heatmap_mapped" src="https://github.com/user-attachments/assets/70907484-79a0-4fba-a812-1b754a87b5c2" />

## NEW
<img width="2520" height="2040" alt="01_scatter_emb0_emb1_color_usercount_size_playtime_v2" src="https://github.com/user-attachments/assets/f8816dba-4d33-4ef3-867b-e644fd2c85b1" />

  <img width="3600" height="1488" alt="02_hexbin_emb0_vs_user_count_raw_and_log" src="https://github.com/user-attachments/assets/a187ebf7-cd37-495e-8746-f45ff45861b6" />
    
<img width="2520" height="1728" alt="04_hist_emb0_by_popularity_group_v2" src="https://github.com/user-attachments/assets/781c506b-7933-4484-8ca0-a4a80e2be2b4" />

  <img width="3600" height="1488" alt="05_binned_emb0_vs_user_count_raw_and_log" src="https://github.com/user-attachments/assets/9b70b617-b768-48c0-b65c-c7729a7774d1" />

  <img width="1800" height="1560" alt="07_spearman_correlation_heatmap_v2" src="https://github.com/user-attachments/assets/2558a8be-56eb-45ab-9155-19acb486c546" />
  
<img width="4293" height="4306" alt="genre_one_vs_rest_panels_mapped_v2" src="https://github.com/user-attachments/assets/ad5acd8c-5708-4c4c-98cf-5cbe6bafb491" />
  
<img width="3720" height="1800" alt="genre_share_across_emb0_bins_heatmap_mapped_v2_equal_width" src="https://github.com/user-attachments/assets/683d6112-d782-4b35-be90-4e5ce1bf9059" />
  
<img width="3720" height="1800" alt="genre_share_across_emb0_bins_heatmap_mapped_v2_quantile" src="https://github.com/user-attachments/assets/213404f9-eba1-4b54-8a27-819ea427a4c2" />

</details>
<details>
  <summary><b>SHAP</b></summary> 

### Interaction structure changes after adding the embedding
  
For the baseline model:  
- `num__user_count` interacts most strongly with `num__release_date`  
- `num__game_total_playtime_minutes` interacts most strongly with `num__user_count`  
  
For the embedding model:  
- `num__user_count` interacts most strongly with `num__game_emb_0`  
- `num__game_emb_0` interacts most strongly with `num__user_count`  
- `num__release_date` also interacts strongly with `num__game_emb_0`  

    
This suggests the embedding is used together with popularity and recency signals.  

  ## Top features from `xgb_baseline`
  
| rank | feature | mean_abs_shap | importance_share |
|---:|---|---:|---:|
| 1 | `num__user_count` | 12.1596 | 0.7326 |
| 2 | `num__game_total_playtime_minutes` | 2.4655 | 0.1485 |
| 3 | `num__release_date` | 0.6611 | 0.0398 |
| 4 | `num__user_playtime_group_Other` | 0.1495 | 0.0090 |
| 5 | `num__total_games_owned` | 0.1493 | 0.0090 |
| 6 | `num__median_playtime_minutes` | 0.1449 | 0.0087 |
| 7 | `num__user_playtime_group_Indie` | 0.1285 | 0.0077 |
| 8 | `num__user_playtime_group_Strategy` | 0.1064 | 0.0064 |
| 9 | `num__user_playtime_group_RPG` | 0.0942 | 0.0057 |
| 10 | `num__user_playtime_group_Sports` | 0.0777 | 0.0047 |

## Plots:
<img width="1588" height="1078" alt="scatter_num__game_total_playtime_minutes" src="https://github.com/user-attachments/assets/baeacf80-2809-40fa-8997-a6096a564988" />
popular game (user_count (popularity) playtime (game activity) -> models score goes up 
<img width="1593" height="1078" alt="scatter_num__median_playtime_minutes" src="https://github.com/user-attachments/assets/788c58c2-5169-4145-993b-87ca07ea8c85" />
no stabile sygnal  if SHAP score <0 -> prediction goes down
<img width="1588" height="1078" alt="scatter_num__release_date" src="https://github.com/user-attachments/assets/eaba991d-06fd-425a-a9a3-99ef4cdca300" />
old games -> SHAP lower  
new games -> SHAP up   
<img width="1588" height="1078" alt="scatter_num__total_games_owned" src="https://github.com/user-attachments/assets/d99ada5d-56eb-40f4-b196-31092a52f51d" />
more games owned = higher SHAP   
player with 2000 games is more likely to have that particular game
<img width="1571" height="1078" alt="scatter_num__user_count" src="https://github.com/user-attachments/assets/b29e9f40-09fc-497f-983f-d72e8eafaee8" />
biggr user_count -> lower SHAP -> model score lower (punishing)
baseline without user_count (0.32 MRR)  
baseline (0.82 MRR)  
popularity (0.60 MRR)   
<img width="1616" height="1078" alt="scatter_num__user_playtime_group_Indie" src="https://github.com/user-attachments/assets/c935377a-7cb9-4409-b80b-2610f5e3b371" />
indie -> lower score
<img width="1583" height="1078" alt="scatter_num__user_playtime_group_Other" src="https://github.com/user-attachments/assets/28862e96-4a84-4245-aa89-ea2f9cd7886e" />
weak signal
<img width="1620" height="1078" alt="scatter_num__user_playtime_group_Strategy" src="https://github.com/user-attachments/assets/25208743-7a74-45fc-ad27-c365f79e8b32" />
strategy -> lower score.
### Model prediction is here about popularity - not about what fits your preferences

<img width="1795" height="2509" alt="shap_bar" src="https://github.com/user-attachments/assets/2e69c181-7575-405f-b632-b8dade2868eb" />
core of model : user_count+playtime+release_date - rest is minor 
<img width="1789" height="2068" alt="shap_beeswarm" src="https://github.com/user-attachments/assets/b2ca6660-6431-4a65-9ab2-0004cd28a70c" />
(one dot = user-game pair)
-> right -> score goes up (more "owned")  
<- left <- lowering the score  
<img width="1789" height="2068" alt="shap_violin" src="https://github.com/user-attachments/assets/e7b174a7-9c72-46cf-a67c-9c2a443669db" />
<img width="1844" height="2494" alt="waterfall_highest_prediction" src="https://github.com/user-attachments/assets/0e07d31d-9239-4ddb-a77a-2091592b2ca4" />
HIGHEST PREDICTION
<img width="1854" height="2494" alt="waterfall_lowest_prediction" src="https://github.com/user-attachments/assets/2cc59862-1890-4164-96fe-ebd22a5d2c92" />
LOWEST PREDICTION
<img width="1784" height="2494" alt="waterfall_median_prediction" src="https://github.com/user-attachments/assets/c146c054-4239-4330-b98e-21dbbd2a7de0" />
MEDIAN PREDICTION 

## SO IT IS ABOUT:
- for high prediction - low popularity -> boost  
- for lowest prediction - big popularity -> decrease  
  so if the game is popular- decrease it, if the game is neeshe- boost. so user_count works like a correction.  
  
## Top features from `xgb_one_embedding`
    
| rank | feature | mean_abs_shap | importance_share |
|---:|---|---:|---:|
| 1 | `num__user_count` | 16.3508 | 0.6112 |
| 2 | `num__game_emb_0` | 8.1138 | 0.3033 |
| 3 | `num__release_date` | 0.7825 | 0.0292 |
| 4 | `num__game_total_playtime_minutes` | 0.5668 | 0.0212 |
| 5 | `num__median_playtime_minutes` | 0.2307 | 0.0086 |
| 6 | `num__total_games_owned` | 0.1022 | 0.0038 |
| 7 | `num__user_playtime_group_RPG` | 0.0899 | 0.0034 |
| 8 | `num__friend_count` | 0.0638 | 0.0024 |
| 9 | `num__user_playtime_group_Other` | 0.0623 | 0.0023 |
| 10 | `num__user_playtime_group_Casual` | 0.0606 | 0.0023 |

## Plots:
<img width="1604" height="1078" alt="scatter_num__friend_count" src="https://github.com/user-attachments/assets/e040682b-b99d-4361-9ef5-50be27cdb8db" />
friend_count ↑ → prediction ↑
- if a user has a lot of friends -> he is active? -> buys/has more games THEORY 
<img width="1592" height="1078" alt="scatter_num__game_emb_0" src="https://github.com/user-attachments/assets/9e4d597f-7e95-419b-a852-a0c3186bc063" />
emb0 = popularity + data structrure
<img width="1596" height="1078" alt="scatter_num__game_total_playtime_minutes" src="https://github.com/user-attachments/assets/04e7d5a3-8989-484e-a023-ba5a169222ca" />
<img width="1572" height="1078" alt="scatter_num__median_playtime_minutes" src="https://github.com/user-attachments/assets/5b7135ff-9220-40c8-bacb-ab9bbdabd966" />
<img width="1595" height="1078" alt="scatter_num__release_date" src="https://github.com/user-attachments/assets/b2c52f73-4f4a-41d8-bc5b-ef3fb7ea3f95" />
<img width="1596" height="1078" alt="scatter_num__total_games_owned" src="https://github.com/user-attachments/assets/40e68f64-7fdb-442d-a3f3-096c96b67cfd" />
<img width="1599" height="1078" alt="scatter_num__user_count" src="https://github.com/user-attachments/assets/57da74ad-2485-4e87-bb54-ec734bc31943" />
<img width="1601" height="1078" alt="scatter_num__user_playtime_group_RPG" src="https://github.com/user-attachments/assets/0128e440-31cc-4825-80e6-0dbf92081385" />
<img width="1795" height="2509" alt="shap_bar" src="https://github.com/user-attachments/assets/d46021e6-8573-49f9-a278-aa1425855f77" />
<img width="1789" height="2068" alt="shap_beeswarm" src="https://github.com/user-attachments/assets/62bc47ce-4cf9-4659-a8ad-1d865a69b3e4" />
<img width="1789" height="2068" alt="shap_violin" src="https://github.com/user-attachments/assets/e4df8edb-82c3-4b7d-8bb5-b6fc80584f24" />
<img width="1739" height="2494" alt="waterfall_highest_prediction" src="https://github.com/user-attachments/assets/678044a0-cc2e-4fef-92b0-5d4165914a19" />
<img width="1739" height="2494" alt="waterfall_lowest_prediction" src="https://github.com/user-attachments/assets/f71ae827-61cc-42b6-a28b-48207ffdb111" />
<img width="1787" height="2494" alt="waterfall_median_prediction" src="https://github.com/user-attachments/assets/5458fcd6-a0a2-47fe-9645-612d32a7e490" />


## Feature importance comparison (SHAP)

| Rank | Feature | Baseline mean\|SHAP\| | Baseline share | Baseline top interaction | Embedding mean\|SHAP\| | Embedding share | Embedding top interaction | Combined mean\|SHAP\| |
|---:|---|---:|---:|---|---:|---:|---|---:|
| 1 | `num__user_count` | 12.1596 | 73.26% | `num__release_date` | 16.3508 | 61.12% | `num__game_emb_0` | 28.5105 |
| 2 | `num__game_emb_0` | – | – | – | 8.1138 | 30.33% | `num__user_count` | 8.1138 |
| 3 | `num__game_total_playtime_minutes` | 2.4655 | 14.85% | `num__user_count` | 0.5668 | 2.12% | `num__game_emb_0` | 3.0323 |
| 4 | `num__release_date` | 0.6611 | 3.98% | `num__user_count` | 0.7825 | 2.92% | `num__game_emb_0` | 1.4436 |
| 5 | `num__median_playtime_minutes` | 0.1449 | 0.87% | `num__user_count` | 0.2307 | 0.86% | `num__release_date` | 0.3756 |
| 6 | `num__total_games_owned` | 0.1493 | 0.90% | `num__user_count` | 0.1022 | 0.38% | `num__game_emb_0` | 0.2516 |
| 7 | `num__user_playtime_group_Other` | 0.1495 | 0.90% | `num__unique_genres_played` | 0.0623 | 0.23% | – | 0.2117 |
| 8 | `num__user_playtime_group_RPG` | 0.0942 | 0.57% | – | 0.0899 | 0.34% | `num__game_emb_0` | 0.1841 |
| 9 | `num__user_playtime_group_Indie` | 0.1285 | 0.77% | `num__user_playtime_group_Casual` | 0.0069 | 0.03% | – | 0.1354 |
| 10 | `num__user_playtime_group_Strategy` | 0.1064 | 0.64% | `num__total_playtime_minutes` | 0.0288 | 0.11% | – | 0.1352 |
| 11 | `num__user_playtime_group_Non-gameplay_Tools` | 0.0705 | 0.42% | – | 0.0552 | 0.21% | – | 0.1258 |
| 12 | `num__user_playtime_group_Casual` | 0.0601 | 0.36% | – | 0.0606 | 0.23% | – | 0.1207 |
| 13 | `num__user_playtime_group_Racing` | 0.0755 | 0.45% | – | 0.0381 | 0.14% | – | 0.1136 |
| 14 | `num__user_playtime_group_Sports` | 0.0777 | 0.47% | – | 0.0275 | 0.10% | – | 0.1052 |
| 15 | `num__user_playtime_group_Adventure` | 0.0535 | 0.32% | – | 0.0487 | 0.18% | – | 0.1022 |
  
Jak to czytać:
  
*mean|SHAP| mówi, jak silnie dana cecha wpływa na predykcję średnio w całym zbiorze.
share mówi, jaki procent całkowitej ważności przypada na tę cechę.
top interaction pokazuje, z jaką inną cechą dana cecha najczęściej współdziała w modelu.*
  
SHAP analysis showed that in both XGBoost models the dominant predictor was `user_count`, indicating a strong popularity effect. In the baseline model the second most important feature was `game_total_playtime_minutes`, whereas after adding the embedding this feature lost much of its importance. At the same time, `game_emb_0` became the second most important feature overall in the embedding-based model, accounting for roughly 30% of total SHAP importance. This suggests that the embedding provides substantial additional information beyond simple popularity and activity statistics. The results also indicate that the model relies not only on game-level features but also on user preference signals, such as historical playtime across genre groups and the diversity of played genres.
  
  </details> 
