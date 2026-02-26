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
 Model | Best CV ROC-AUC | Best Params | Accuracy | Precision | Recall | F1 | Test ROC-AUC | Confusion Matrix (TN FP / FN TP) | Saved Model |
|---|---:|---|---:|---:|---:|---:|---:|---|---|
| LogisticRegression | 0.93298 | C=1.43845 | 0.85262 | 0.84530 | 0.86321 | 0.85416 | 0.91342 | [[20196, 3789], [3281, 20704]] | `outputs_baseline_small/models/LogisticRegression_best.joblib` |
| RandomForest | 0.94115 | max_depth=24, max_features=None, min_samples_leaf=2, min_samples_split=10 | 0.85864 | 0.84563 | 0.87747 | 0.86125 | 0.92028 | [[20143, 3842], [2939, 21046]] | `outputs_baseline_small/models/RandomForest_best.joblib` |
| XGBoost | 0.94491 | colsample_bytree=0.6, max_depth=8, reg_lambda=1.0, subsample=0.6 | 0.86250 | 0.84869 | 0.88230 | 0.86517 | 0.92342 | [[20212, 3773], [2823, 21162]] | `outputs_baseline_small/models/XGBoost_best.joblib` |


<img width="1152" height="908" alt="LogisticRegression_learning_curve" src="https://github.com/user-attachments/assets/6513294c-033d-4079-b2d8-759177144e90" />

<img width="1152" height="908" alt="RandomForest_learning_curve" src="https://github.com/user-attachments/assets/4e273056-7747-4be3-9965-31f094b1535f" />

<img width="1170" height="908" alt="XGBoost_learning_curve" src="https://github.com/user-attachments/assets/30fe8c3b-c5a5-4e51-ba1a-4339ba0e22c1" />


## Results (Baseline models)

### Logistic Regression (LR)
**Best CV ROC-AUC:** 0.9268  
**Best hyperparameter:** `C = 29.7635`

**Test metrics:**
- Accuracy: **0.8496**
- Precision: **0.8398**
- Recall: **0.8640**
- F1: **0.8517**
- ROC-AUC: **0.9248**
- Confusion matrix (TN FP / FN TP): **[[677022, 133617], [110236, 700403]]**

Saved model:
- `outputs_baseline_full/models/LogisticRegression_best.joblib`
Saved results:
- `outputs_baseline_full/results_lr.csv`

---

### XGBoost (XGB)
**Best CV ROC-AUC:** 0.9310  
**Best hyperparameters:**
- `max_depth = 8`
- `subsample = 0.6`
- `colsample_bytree = 0.6`
- `reg_lambda = 1.0`

**Test metrics:**
- Accuracy: **0.8523**
- Precision: **0.8425**
- Recall: **0.8667**
- F1: **0.8544**
- ROC-AUC: **0.9287**
- Confusion matrix (TN FP / FN TP): **[[679251, 131388], [108063, 702576]]**

Saved model:
- `outputs_baseline_full/models/XGBoost_best.joblib`
Saved results:
- `outputs_baseline_full/results_xgb.csv`

---

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

Missing-indicator flags (all ~0):
- `*_is_missing` → **0.000000** (no measurable impact)

Saved output:
- `outputs_baseline_full/feature_importance_blocks/block_permutation_importance.csv`


### my notes:
- game_index_to_gameid_sq_20988.mmap (map games id)    
- user_edge_graph_relabelled.pkl (31021 nodes/users, 40204 edges/connections)   
- old_to_new_node_id.csv (mapping users (2) 43613/filtered data -> 31021 (LCC)   
- game_game_dists_sq_20988.mmap -> upper triangle games relationships matrix   
