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
  "HitRate@10": 0.748537804402538,  
  "Recall@10": 0.748537804402538,  
  "NDCG@10": 0.42749191661367153,  
  "HitRate@20": 0.8400269398461593,  
  "Recall@20": 0.8400269398461593,  
  "NDCG@20": 0.45076122932644225,  
  "MRR": 0.3383544483777126,  
  "HitRate@1": 0.1609655808018149,  
  "Recall@1": 0.1609655808018149,  
  "NDCG@1": 0.1609655808018149,  
  "HitRate@5": 0.5760873418170217,  
  "Recall@5": 0.5760873418170217,  
  "NDCG@5": 0.37077277924236496  
    
## LOGISTIC REGRESSION NETWORK:
  
  "test_roc_auc": 0.9876183344254614,
  "HitRate@10": 0.9606890929070221,
  "Recall@10": 0.9606890929070221,
  "NDCG@10": 0.9150393074077323,
  "HitRate@20": 0.9785544645705576,
  "Recall@20": 0.9785544645705576,
  "NDCG@20": 0.9195517694895029,  
  "MRR": 0.902257312245997    
  "HitRate@1": 0.8684201198114211  
  "Recall@1": 0.8684201198114211  
  "NDCG@1": 0.8684201198114211  
  "HitRate@5": 0.941653964765517  
  "Recall@5": 0.941653964765517  
  "NDCG@5": 0.908881431345946  

  
## RANDOM FOREST BASELINE:
  
  "test_roc_auc": 0.9497294416366708,  
  "HitRate@10": 0.8368721420722414,  
  "Recall@10": 0.8368721420722414,  
  "NDCG@10": 0.7299644781294305,  
  "HitRate@20": 0.8997199673886073,  
  "Recall@20": 0.8997199673886073,  
  "NDCG@20": 0.7458518838681654,  
  "MRR": 0.7035482723067408,  
  "HitRate@1": 0.6297543511396264,  
  "Recall@1": 0.6297543511396264,  
  "NDCG@1": 0.6297543511396264,  
  "HitRate@5": 0.7824961894296552,    
  "Recall@5": 0.7824961894296552,  
  "NDCG@5": 0.7124230983603488  
    
## RANDOM FOREST NETWORK:
  
 "test_roc_auc": 0.9999666700517238,  
  "HitRate@10": 0.9998936585020027,  
  "Recall@10": 0.9998936585020027,  
  "NDCG@10": 0.9998936585020027,  
  "HitRate@20": 0.9998936585020027,  
  "Recall@20": 0.9998936585020027,  
  "NDCG@20": 0.9998936585020027,  
  "MRR": 0.9998969782819882,  
  "HitRate@1": 0.9998936585020027,  
  "Recall@1": 0.9998936585020027,  
  "NDCG@1": 0.9998936585020027,  
  "HitRate@5": 0.9998936585020027,  
  "Recall@5": 0.9998936585020027,  
  "NDCG@5": 0.9998936585020027  
    
## XGB BASELINE:
    
 "test_roc_auc": 0.9553326932270335,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.6866824997341463,  
  "Recall@1": 0.6866824997341463,  
  "NDCG@1": 0.6866824997341463,  
  "HitRate@5": 0.8125199390308745,  
  "Recall@5": 0.8125199390308745,  
  "NDCG@5": 0.7539586444201957,  
  "HitRate@10": 0.8605154017936266,  
  "Recall@10": 0.8605154017936266,  
  "NDCG@10": 0.769402995676433,  
  "HitRate@20": 0.913189890468257,  
  "Recall@20": 0.913189890468257,  
  "NDCG@20": 0.7827518035090931,  
  "MRR": 0.7469435346206998    
      
## XGB NETWORK:
    
  "test_roc_auc": 0.9991033188025167,  
  "n_users_evaluated": 28211,  
  "HitRate@1": 0.9942575591081493,  
  "Recall@1": 0.9942575591081493,  
  "NDCG@1": 0.9942575591081493,  
  "HitRate@5": 0.9963134947360959,  
  "Recall@5": 0.9963134947360959,  
  "NDCG@5": 0.9953548266791248,  
  "HitRate@10": 0.99730601538407,  
  "Recall@10": 0.99730601538407,  
  "NDCG@10": 0.9956734626043735,  
  "HitRate@20": 0.9983694303640424,  
  "Recall@20": 0.9983694303640424,  
  "NDCG@20": 0.9959396544720378,  
  "MRR": 0.9952806135904906    
  
  ## lightGCN
      
  "test_roc_auc": 0.745641667637136,  
  "test_HitRate@1": 0.10953174293715218,  
  "test_Recall@1": 0.10953174293715218,  
  "test_NDCG@1": 0.10953174293715218,  
  "test_HitRate@5": 0.32377441423558184,  
  "test_Recall@5": 0.32377441423558184,  
  "test_NDCG@5": 0.21826246219471468,  
  "test_HitRate@10": 0.47626812236361704,  
  "test_Recall@10": 0.47626812236361704,  
  "test_NDCG@10": 0.2672034446425509,  
  "test_HitRate@20": 0.6584665555988799,  
  "test_Recall@20": 0.6584665555988799,  
  "test_NDCG@20": 0.3131695800171958,  
  "test_MRR": 0.2242679398076897 

  ## NN_baseline (BPR)   
        
  "test_roc_auc": 0.9115379317137908,  
  "test_HitRate@1": 0.17599517918542412,  
  "test_Recall@1": 0.17599517918542412,  
  "test_NDCG@1": 0.17599517918542412,  
  "test_HitRate@5": 0.479422920137535,  
  "test_Recall@5": 0.479422920137535,  
  "test_NDCG@5": 0.3299697215176235,  
  "test_HitRate@10": 0.6729289993265039,  
  "test_Recall@10": 0.6729289993265039,  
  "test_NDCG@10": 0.3924237983859982,  
  "test_HitRate@20": 0.867959306653433,  
  "test_Recall@20": 0.867959306653433,  
  "test_NDCG@20": 0.4420244575384093,  
  "test_MRR": 0.32489356440774336  

  ## NN_network (BPR) 
  "test_roc_auc": 0.9114223090543274,  
  "test_HitRate@1": 0.16777143667363795,  
  "test_Recall@1": 0.16777143667363795,  
  "test_NDCG@1": 0.16777143667363795,  
  "test_HitRate@5": 0.4712346247917479,  
  "test_Recall@5": 0.4712346247917479,  
  "test_NDCG@5": 0.3207774007209469,  
  "test_HitRate@10": 0.6757293254404311,  
  "test_Recall@10": 0.6757293254404311,  
  "test_NDCG@10": 0.38684166284709987,  
  "test_HitRate@20": 0.8696253234553898,  
  "test_Recall@20": 0.8696253234553898,  
  "test_NDCG@20": 0.43615097499379407,  
  "test_MRR": 0.3168876048201971  

  ## 


| Model                        |    AUC | HitRate@1 | HitRate@5 | HitRate@10 |
| ---------------------------- | -----: | --------: | --------: | ---------: |
| Naive Random                 |      — |    0.0111 |    0.0526 |     0.1021 |
| Naive Popularity             |      — |    0.1506 |    0.4048 |     0.5879 |
| Logistic Regression Baseline | 0.9035 |    0.1610 |    0.5761 |     0.7485 |
| Logistic Regression Network  | 0.9876 |    0.8684 |    0.9417 |     0.9607 |
| Random Forest Baseline       | 0.9497 |    0.6298 |    0.7825 |     0.8369 |
| Random Forest Network        | 1.0000 |    0.9999 |    0.9999 |     0.9999 |
| XGBoost Baseline             | 0.9681 |    0.7763 |    0.8649 |     0.8994 |
| XGBoost Network              | 0.9999 |    0.9999 |    0.9999 |     0.9999 |
| LightGCN                     | 0.7456 |    0.1095 |    0.3238 |     0.4763 |
| NN Baseline (BPR)            | 0.9115 |    0.1760 |    0.4794 |     0.6729 |
| NN Network (BPR)             | 0.9114 |    0.1678 |    0.4712 |     0.6757 |

