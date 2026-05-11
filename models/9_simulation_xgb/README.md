### XGBoost leakage check — fresh users simulation
  
This experiment was added as an extra sanity check for possible data leakage.  
  
The goal was to test whether the very strong XGBoost results, especially for the Network model, were caused by users appearing in both training and evaluation data.  

**Reporting note:**  
All fresh-user simulation results are reported as **mean ± standard deviation** across 3 random seeds: `42`, `0`, and `1`.
The simulations were rerun using the best hyperparameters selected by the original training scripts.
  
        
The results stayed very close to the original XGBoost results, which suggests that the strong performance is not simply caused by the same users leaking from train into validation/test.  

-------------------------------------
  
## Motivation

The original split contains user-game rows in train, validation, and test.

Because recommendation data is user-based, we wanted to check whether the model was benefiting from seeing the same users during training.

To test this, we created a stricter evaluation setup:

- choose a fixed set of users
- remove these users from the training set
- keep only these users in validation and test

So validation and test contain “fresh” users from the model’s perspective.

-------------------------------------
  
<details>
<summary>STEP 1: Create fresh-user simulation split </summary>
    
CODE: `make_network_sim_from_existing_users.py`

-------------------------------------
  
Input dataset:
  
- `correct_splits/with_genre_groups_network_fixed/`
 *Our dataset for Network models*
  
-------------------------------------
  
### Script workflow:

- loads existing train.csv, val.csv, and test.csv
- finds the user column, usually steamid
- collects all users from train, validation, and test
- finds users present in all three splits:
  
```text
common_users = train_users & val_users & test_users
```
  
- randomly samples:
```text
N_USERS = 2000
```
  
- saves these users as:
 `heldout_steamids.txt`
  
-creates new split files:
  
| Split       | Rule                             |
| ----------- | -------------------------------- |
| `train.csv` | remove the 2000 heldout users    |
| `val.csv`   | keep only the 2000 heldout users |
| `test.csv`  | keep only the 2000 heldout users |

-------------------------------------
  
#### Sanity checks

After filtering, the script checks that:  

- no heldout user remains in train
- validation users are exactly the heldout users
- test users are exactly the heldout users
- validation and test contain the same user set
  
*If any of these checks fail, the script raises an error.*

So the final setup is:  

| Split      | User setup                          |
| ---------- | ----------------------------------- |
| Train      | original users except heldout users |
| Validation | only heldout users                  |
| Test       | only heldout users                  |

<details>
<summary>Show dataset info: </summary>
  
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

</details>
  
-------------------------------------
  
Output:
- `train.csv`
- `val.csv`
- `test.csv`
- `heldout_steamids.txt`
- `split_stats.json`
  
</details>

<details>
<summary>STEP 2: Train XGBoost models on the simulation split</summary>
  
#### CODE:  
  
- `train_xgb_baseline_sim.py`
- `train_xgb_network_sim.py`

-------------------------------------

#### Training 
  
These scripts follow the same logic as the normal XGBoost training scripts from:
  
`models/4_XGBoost_model/`
  
The only difference is the input directory.  

-------------------------------------
  
#### Results:   
  
**xgb baseline SIM**
    
| Metric     | Value |
| ---------- | ----: |
| ROC-AUC    | 0.9674 ± 0.0005 |
| HitRate@1  | 0.7785 ± 0.0033 |
| Recall@1   | 0.7785 ± 0.0033 |
| NDCG@1     | 0.7785 ± 0.0033 |
| HitRate@5  | 0.8610 ± 0.0027 |
| Recall@5   | 0.8610 ± 0.0027 |
| NDCG@5     | 0.8227 ± 0.0027 |
| HitRate@10 | 0.8952 ± 0.0037 |
| Recall@10  | 0.8952 ± 0.0037 |
| NDCG@10    | 0.8338 ± 0.0024 |
| HitRate@20 | 0.9352 ± 0.0022 |
| Recall@20  | 0.9352 ± 0.0022 |
| NDCG@20    | 0.8439 ± 0.0022 |
| MRR        | 0.8191 ± 0.0025 |

    
### xgb network SIM  
  
| Metric     | Value |
| ---------- | ----: |
| ROC-AUC    | 0.9992 ± 0.0000 |
| HitRate@1  | 0.9947 ± 0.0002 |
| Recall@1   | 0.9947 ± 0.0002 |
| NDCG@1     | 0.9947 ± 0.0002 |
| HitRate@5  | 0.9960 ± 0.0000 |
| Recall@5   | 0.9960 ± 0.0000 |
| NDCG@5     | 0.9953 ± 0.0001 |
| HitRate@10 | 0.9973 ± 0.0002 |
| Recall@10  | 0.9973 ± 0.0002 |
| NDCG@10    | 0.9958 ± 0.0001 |
| HitRate@20 | 0.9983 ± 0.0002 |
| Recall@20  | 0.9983 ± 0.0002 |
| NDCG@20    | 0.9960 ± 0.0001 |
| MRR        | 0.9954 ± 0.0002 |

*full results output you can find in folder `results/`*

-------------------------------------
  
#### Comparison: normal XGB vs fresh-user simulation
  
| Metric     | Normal XGB baseline | Fresh-user sim baseline | Δ |
| ---------- | ------------------: | ----------------------: | ----------: |
| HitRate@1  | 0.7768 ± 0.0004 | 0.7785 ± 0.0033 | **+0.0017** |
| HitRate@5  | 0.8630 ± 0.0021 | 0.8610 ± 0.0027 | **−0.0020** |
| HitRate@10 | 0.8992 ± 0.0016 | 0.8952 ± 0.0037 | **−0.0041** |
| MRR        | 0.8187 ± 0.0006 | 0.8191 ± 0.0025 | **+0.0004** |
  
    
    
| Metric     | Normal XGB network | Fresh-user sim network | Δ |
| ---------- | -----------------: | ---------------------: | ----------: |
| HitRate@1  | 0.9942 ± 0.0002 | 0.9947 ± 0.0002 | **+0.0004** |
| HitRate@5  | 0.9965 ± 0.0001 | 0.9960 ± 0.0000 | **−0.0005** |
| HitRate@10 | 0.9976 ± 0.0001 | 0.9973 ± 0.0002 | **−0.0002** |
| MRR        | 0.9953 ± 0.0001 | 0.9954 ± 0.0002 | **+0.0001** |

-------------------------------------
  
#### Interpretation
  
The fresh-user simulation gives almost the same results as the normal XGBoost setup.  
  
This suggests that the high performance of the Network XGBoost model is not simply caused by user leakage between train and test.  
  
The model still performs extremely well even when the users in validation and test are removed completely from training.   
  
</details> 
