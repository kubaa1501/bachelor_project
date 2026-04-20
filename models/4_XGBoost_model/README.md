<details> 
<summary>XGBoost Baseline model</summary>
  
### MODEL: XGBoost Baseline model   
    
`xgb_baseline.py`
      
It trains, validates, and evaluates an XGBoost baseline for the game recommendation task.  
  
The script builds a full sklearn pipeline that:  
- preprocesses numeric features  
- preprocesses categorical features  
- trains an XGBoost classifier  
- selects the best hyperparameter setting on validation data  
- evaluates the best model on the test set as a ranking model  
*Additionally, it creates learning curve experiments for the best configuration.*

--------------------------------------

Input:   
- `train.csv`
- `val.csv`
- `test.csv`  
    
*This is the baseline dataset* 

-------------------------------------

The target column is:  
- `owned`  
*The model predicts the probability that a given (`steamid`, `appid`) pair corresponds to a **positive interaction**.*

-------------------------------------
  
#### Features used
  
The script uses two groups of input features.  

<details> 
<summary>Show feature list</summary>
  
#### Numeric features:
  
- `total_games_owned`
- `total_playtime_minutes`
- `median_playtime_minutes`
- `unique_genres_played`
- `user_count`
- `game_total_playtime_minutes`
- `release_date`
- `user_playtime_group_Action`
- `user_playtime_group_Adventure`
- `user_playtime_group_RPG`
- `user_playtime_group_Casual`
- `user_playtime_group_Indie`
- `user_playtime_group_Racing`
- `user_playtime_group_Simulation`
- `user_playtime_group_Strategy`
- `user_playtime_group_Sports`
- `user_playtime_group_Violent`
- `user_playtime_group_Adult`
- `user_playtime_group_Non-gameplay_Tools`
- `user_playtime_group_Other`
  
#### Categorical features:
  
- `country`
- `genres`
- `developer`
- `publisher`
- `platforms`
    
Identifier columns:    
- `steamid`
- `appid`

*These **identifier columns** are loaded for evaluation and saving predictions, but they are not used as model features.* 
  
</details>
  
-------------------------------------

#### Preprocessing
  
The script builds a `sklearn` Pipeline with a `ColumnTransformer`.
  
Numeric preprocessing:  
- missing values are filled using **median imputation**
  
Categorical preprocessing:  
- missing values are replaced with **"MISSING"**
- features are encoded using constrained `OneHotEncoder`

Configuration:
- `handle_unknown="infrequent_if_exist"`
- `max_categories=100`
- `min_frequency=50`

*Unlike Logistic Regression, XGBoost does not require feature scaling, so no `StandardScaler` is used for numeric columns.*

-------------------------------------

#### Model
  
The classifier is: **XGBClassifier**
  
Configuration:
- `objective="binary:logistic"`
- `eval_metric="logloss"`
- `tree_method="hist"`
- `random_state=42`
- `n_jobs=8`
  
This hyperparameter grid is tested:
- `n_estimators=200`, `max_depth=4`, `learning_rate=0.05`, `min_child_weight=3`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=1.0`, `reg_alpha=0.0`
- `n_estimators=300`, `max_depth=4`, `learning_rate=0.05`, `min_child_weight=3`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=1.0`, `reg_alpha=0.0`
- `n_estimators=300`, `max_depth=6`, `learning_rate=0.05`, `min_child_weight=5`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=1.0`, `reg_alpha=0.1`
- `n_estimators=300`, `max_depth=6`, `learning_rate=0.10`, `min_child_weight=5`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=2.0`, `reg_alpha=0.1`
- `n_estimators=400`, `max_depth=6`, `learning_rate=0.05`, `min_child_weight=5`, `subsample=1.0`, `colsample_bytree=1.0`, `reg_lambda=2.0`, `reg_alpha=0.1`
  
Each configuration is trained on the training split and evaluated on the validation split.  
  
The best model is selected using: **Validation NDCG@10**

*So even though the underlying model is a classifier, model selection is based on ranking quality, not only classification quality.*

-------------------------------------
  
#### Ranking evaluation
  
Predicted probabilities are used as ranking scores.  
For each user (`steamid`):  

candidate games are sorted by predicted score in descending order  
ranking metrics are computed on the ordered owned labels

The script computes:  
- HitRate@1
- Recall@1
- NDCG@1
- HitRate@5
- Recall@5
- NDCG@5
- HitRate@10
- Recall@10
- NDCG@10
- HitRate@20
- Recall@20
- NDCG@20
- MRR
    
Metrics are computed per user and then **averaged across all evaluated users**.    
*(Users with no positive items are skipped during ranking evaluation.)*  

-------------------------------------

#### Additional classification metric
  
Besides ranking metrics, the script also computes:  
- ROC-AUC
  
ROC-AUC is calculated on:  
- validation data during model selection
- test data for the final selected model
  
*This gives an additional view of binary classification quality.*

-------------------------------------

#### Learning curve analysis
  
After selecting the best validation configuration, the script trains the model on increasing fractions of the training set:
- 5%
- 10%
- 20%
- 40%
- 70%
- 100%
  
For each fraction, it measures:
- training ROC-AUC
- validation ROC-AUC
- validation ranking metrics
- training time
  
To keep computation manageable, learning curves can be limited to a subset of training rows:
- `learning_curve_max_rows = 1000000`
  
It then saves:
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`

*This helps analyze whether the model benefits from more training data and whether it shows signs of underfitting or overfitting.*

-------------------------------------

Outputs:  
- `val_trials.csv` — validation results for all tested hyperparameter settings
- `test_scores.csv.gz` — predicted scores for test user-game pairs
- `test_per_user_metrics.csv` — ranking metrics per user on test data
- `best_model.joblib` — the fitted sklearn pipeline
- `results.json` — final summary of the experiment
- `learning_curve.csv` — learning curve metrics
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`
  
-------------------------------------

### Results:

<details> 
<summary>Show results for XGBoost Baseline model</summary> 

### XGBoost Baseline:  
  
- "model_type": "xgb"
- "dataset_type": "baseline"
- "seed": 42
- "train_rows": 43494594
- "val_rows": 2849311
- "test_rows": 2849311
- "xgb_njobs": 8
- "ohe_max_categories": 100
- "ohe_min_frequency": 50
- "learning_curve_max_rows": 1000000
  
**Best validation parameters:**
- n_estimators = 300
- max_depth = 6
- learning_rate = 0.1
- min_child_weight = 5
- subsample = 0.8
- colsample_bytree = 0.8
- reg_lambda = 2.0
- reg_alpha = 0.1
  
**Features used:**
- 20 numeric features  
- 5 categorical features
    
<details> 
<summary>Show feature list</summary>
  
#### Numeric features:
  
- `total_games_owned`
- `total_playtime_minutes`
- `median_playtime_minutes`
- `unique_genres_played`
- `user_count`
- `game_total_playtime_minutes`
- `release_date`
- `user_playtime_group_Action`
- `user_playtime_group_Adventure`
- `user_playtime_group_RPG`
- `user_playtime_group_Casual`
- `user_playtime_group_Indie`
- `user_playtime_group_Racing`
- `user_playtime_group_Simulation`
- `user_playtime_group_Strategy`
- `user_playtime_group_Sports`
- `user_playtime_group_Violent`
- `user_playtime_group_Adult`
- `user_playtime_group_Non-gameplay_Tools`
- `user_playtime_group_Other`
  
#### Categorical features:
  
- `country`
- `genres`
- `developer`
- `publisher`
- `platforms`
       
</details> 
  
<details> 
<summary>Show validation results for best model</summary>
    
#### Validation results:
  
| Metric | Value |
|---|---:|
| Trial | 4 |
| n_estimators | 300 |
| max_depth | 6 |
| learning_rate | 0.10 |
| min_child_weight | 5 |
| subsample | 0.8 |
| colsample_bytree | 0.8 |
| reg_lambda | 2.0 |
| reg_alpha | 0.1 |
| Fit time (s) | 796.21 |
| ROC-AUC | 0.9686 |
| Evaluated users | 28211 |
| HitRate@1 | 0.7747 |
| Recall@1 | 0.7747 |
| NDCG@1 | 0.7747 |
| HitRate@5 | 0.8650 |
| Recall@5 | 0.8650 |
| NDCG@5 | 0.8227 |
| HitRate@10 | 0.9000 |
| Recall@10 | 0.9000 |
| NDCG@10 | 0.8340 |
| HitRate@20 | 0.9396 |
| Recall@20 | 0.9396 |
| NDCG@20 | 0.8440 |
| MRR | 0.8177 |

</details> 
  
<details> 
<summary>Show test results</summary>
    
#### Test results:
  
| Metric | Value |
|---|---:|
| ROC-AUC | 0.9681 |
| Evaluated users | 28211 |
| HitRate@1 | 0.7763 |
| Recall@1 | 0.7763 |
| NDCG@1 | 0.7763 |
| HitRate@5 | 0.8649 |
| Recall@5 | 0.8649 |
| NDCG@5 | 0.8237 |
| HitRate@10 | 0.8994 |
| Recall@10 | 0.8994 |
| NDCG@10 | 0.8348 |
| HitRate@20 | 0.9381 |
| Recall@20 | 0.9381 |
| NDCG@20 | 0.8447 |
| MRR | 0.8190 |
  
</details>

<details> 
<summary>Show learning curves</summary>
    
#### Learning curves:

 <img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/685722e9-9465-4b4a-a1c4-4f613f3eb96f" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/7caa2cb5-b445-4082-ae98-8dfdee8ab851" />

  
</details>
  
</details>

-------------------------------------
  
</details>

<details> 
<summary>XGBoost Network model</summary>
  
### MODEL: XGBoost Network model   
    
`xgb_network.py`
      
It trains, validates, and evaluates an XGBoost model for the game recommendation task using the **network-enriched dataset**.  
  
The script builds a full sklearn pipeline that:  
- preprocesses numeric features  
- preprocesses categorical features  
- trains an XGBoost classifier  
- selects the best hyperparameter setting on validation data  
- evaluates the best model on the test set as a ranking model  
*Additionally, it creates learning curve experiments for the best configuration.*

--------------------------------------

Input:   
- `train.csv`
- `val.csv`
- `test.csv`  
    
*This is the network dataset* 

-------------------------------------

The target column is:  
- `owned`  
*The model predicts the probability that a given (`steamid`, `appid`) pair corresponds to a **positive interaction**.*

-------------------------------------
  
#### Features used
  
The script uses two groups of input features.  

<details> 
<summary>Show feature list</summary>
  
#### Numeric features:
  
- `total_games_owned`
- `total_playtime_minutes`
- `median_playtime_minutes`
- `unique_genres_played`
- `user_count`
- `game_total_playtime_minutes`
- `release_date`
- `friend_count`
- `game_emb_0`
- `game_emb_1`
- `game_emb_2`
- `game_emb_3`
- `game_emb_4`
- `game_emb_5`
- `game_emb_6`
- `game_emb_7`
- `game_emb_8`
- `game_emb_9`
- `game_emb_10`
- `game_emb_11`
- `game_emb_12`
- `game_emb_13`
- `game_emb_14`
- `game_emb_15`
- `game_emb_16`
- `game_emb_17`
- `game_emb_18`
- `game_emb_19`
- `game_emb_20`
- `game_emb_21`
- `game_emb_22`
- `game_emb_23`
- `game_emb_24`
- `game_emb_25`
- `game_emb_26`
- `game_emb_27`
- `game_emb_28`
- `game_emb_29`
- `game_emb_30`
- `game_emb_31`
- `user_playtime_group_Action`
- `user_playtime_group_Adventure`
- `user_playtime_group_RPG`
- `user_playtime_group_Casual`
- `user_playtime_group_Indie`
- `user_playtime_group_Racing`
- `user_playtime_group_Simulation`
- `user_playtime_group_Strategy`
- `user_playtime_group_Sports`
- `user_playtime_group_Violent`
- `user_playtime_group_Adult`
- `user_playtime_group_Non-gameplay_Tools`
- `user_playtime_group_Other`
  
#### Categorical features:
  
- `country`
- `genres`
- `developer`
- `publisher`
- `platforms`
    
Identifier columns:    
- `steamid`
- `appid`

*These **identifier columns** are loaded for evaluation and saving predictions, but they are not used as model features.* 
  
</details>
  
-------------------------------------

#### Preprocessing
  
The script builds a `sklearn` Pipeline with a `ColumnTransformer`.
  
Numeric preprocessing:  
- missing values are filled using **median imputation**
  
Categorical preprocessing:  
- missing values are replaced with **"MISSING"**
- features are encoded using constrained `OneHotEncoder`

Configuration:
- `handle_unknown="infrequent_if_exist"`
- `max_categories=100`
- `min_frequency=50`

*Unlike Logistic Regression, XGBoost does not require feature scaling, so no `StandardScaler` is used for numeric columns.*

-------------------------------------

#### Model
  
The classifier is: **XGBClassifier**
  
Configuration:
- `objective="binary:logistic"`
- `eval_metric="logloss"`
- `tree_method="hist"`
- `random_state=42`
- `n_jobs=8`
  
A hyperparameter grid is tested:
- `n_estimators=200`, `max_depth=4`, `learning_rate=0.05`, `min_child_weight=3`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=1.0`, `reg_alpha=0.0`
- `n_estimators=300`, `max_depth=4`, `learning_rate=0.05`, `min_child_weight=3`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=1.0`, `reg_alpha=0.0`
- `n_estimators=300`, `max_depth=6`, `learning_rate=0.05`, `min_child_weight=5`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=1.0`, `reg_alpha=0.1`
- `n_estimators=300`, `max_depth=6`, `learning_rate=0.10`, `min_child_weight=5`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=2.0`, `reg_alpha=0.1`
- `n_estimators=400`, `max_depth=6`, `learning_rate=0.05`, `min_child_weight=5`, `subsample=1.0`, `colsample_bytree=1.0`, `reg_lambda=2.0`, `reg_alpha=0.1`
  
Each configuration is trained on the training split and evaluated on the validation split.  
  
The best model is selected using: **Validation NDCG@10**

-------------------------------------
  
#### Ranking evaluation
  
Predicted probabilities are used as ranking scores.  
For each user (`steamid`):  

candidate games are sorted by predicted score in descending order  
ranking metrics are computed on the ordered owned labels

The script computes:  
- HitRate@1
- Recall@1
- NDCG@1
- HitRate@5
- Recall@5
- NDCG@5
- HitRate@10
- Recall@10
- NDCG@10
- HitRate@20
- Recall@20
- NDCG@20
- MRR
    
Metrics are computed per user and then **averaged across all evaluated users**.    
*(Users with no positive items are skipped during ranking evaluation.)*  

-------------------------------------

#### Additional classification metric
  
Besides ranking metrics, the script also computes:  
- ROC-AUC
  
ROC-AUC is calculated on:  
- validation data during model selection
- test data for the final selected model

-------------------------------------

#### Learning curve analysis
  
After selecting the best validation configuration, the script trains the model on increasing fractions of the training set:
- 5%
- 10%
- 20%
- 40%
- 70%
- 100%
  
For each fraction, it measures:
- training ROC-AUC
- validation ROC-AUC
- validation ranking metrics
- training time
  
To keep computation manageable, learning curves can be limited to a subset of training rows:
- `learning_curve_max_rows = 1000000`
  
It then saves:
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`

*This helps analyze whether the model benefits from more training data and whether it shows signs of underfitting or overfitting.*

-------------------------------------

Outputs:  
- `val_trials.csv` — validation results for all tested hyperparameter settings
- `test_scores.csv.gz` — predicted scores for test user-game pairs
- `test_per_user_metrics.csv` — ranking metrics per user on test data
- `best_model.joblib` — the fitted sklearn pipeline
- `results.json` — final summary of the experiment
- `learning_curve.csv` — learning curve metrics
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`
  
-------------------------------------

### Results:

<details> 
<summary>Show results for XGBoost Network model</summary> 

### XGBoost Network:  
  
- "model_type": "xgb"
- "dataset_type": "network"
- "seed": 42
- "train_rows": 43494594
- "val_rows": 2849311
- "test_rows": 2849311
- "xgb_njobs": 8
- "ohe_max_categories": 100
- "ohe_min_frequency": 50
- "learning_curve_max_rows": 1000000
  
**Best validation parameters:**
- n_estimators = 300
- max_depth = 6
- learning_rate = 0.1
- min_child_weight = 5
- subsample = 0.8
- colsample_bytree = 0.8
- reg_lambda = 2.0
- reg_alpha = 0.1
  
**Features used:**
- 53 numeric features  
- 5 categorical features
    
<details> 
<summary>Show feature list</summary>
  
#### Numeric features:
  
- `total_games_owned`
- `total_playtime_minutes`
- `median_playtime_minutes`
- `unique_genres_played`
- `user_count`
- `game_total_playtime_minutes`
- `release_date`
- `friend_count`
- `game_emb_0`
- `game_emb_1`
- `game_emb_2`
- `game_emb_3`
- `game_emb_4`
- `game_emb_5`
- `game_emb_6`
- `game_emb_7`
- `game_emb_8`
- `game_emb_9`
- `game_emb_10`
- `game_emb_11`
- `game_emb_12`
- `game_emb_13`
- `game_emb_14`
- `game_emb_15`
- `game_emb_16`
- `game_emb_17`
- `game_emb_18`
- `game_emb_19`
- `game_emb_20`
- `game_emb_21`
- `game_emb_22`
- `game_emb_23`
- `game_emb_24`
- `game_emb_25`
- `game_emb_26`
- `game_emb_27`
- `game_emb_28`
- `game_emb_29`
- `game_emb_30`
- `game_emb_31`
- `user_playtime_group_Action`
- `user_playtime_group_Adventure`
- `user_playtime_group_RPG`
- `user_playtime_group_Casual`
- `user_playtime_group_Indie`
- `user_playtime_group_Racing`
- `user_playtime_group_Simulation`
- `user_playtime_group_Strategy`
- `user_playtime_group_Sports`
- `user_playtime_group_Violent`
- `user_playtime_group_Adult`
- `user_playtime_group_Non-gameplay_Tools`
- `user_playtime_group_Other`
  
#### Categorical features:
  
- `country`
- `genres`
- `developer`
- `publisher`
- `platforms`
       
</details> 
  
<details> 
<summary>Show validation results for best model</summary>
    
#### Validation results:
  
| Metric | Value |
|---|---:|
| Trial | 4 |
| n_estimators | 300 |
| max_depth | 6 |
| learning_rate | 0.10 |
| min_child_weight | 5 |
| subsample | 0.8 |
| colsample_bytree | 0.8 |
| reg_lambda | 2.0 |
| reg_alpha | 0.1 |
| Fit time (s) | 1259.23 |
| ROC-AUC | 0.9993 |
| Evaluated users | 28211 |
| HitRate@1 | 0.9951 |
| Recall@1 | 0.9951 |
| NDCG@1 | 0.9951 |
| HitRate@5 | 0.9970 |
| Recall@5 | 0.9970 |
| NDCG@5 | 0.9961 |
| HitRate@10 | 0.9977 |
| Recall@10 | 0.9977 |
| NDCG@10 | 0.9963 |
| HitRate@20 | 0.9983 |
| Recall@20 | 0.9983 |
| NDCG@20 | 0.9965 |
| MRR | 0.9960 |

</details> 
  
<details> 
<summary>Show test results</summary>
    
#### Test results:
  
| Metric | Value |
|---|---:|
| ROC-AUC | 0.9992 |
| Evaluated users | 28211 |
| HitRate@1 | 0.9940 |
| Recall@1 | 0.9940 |
| NDCG@1 | 0.9940 |
| HitRate@5 | 0.9965 |
| Recall@5 | 0.9965 |
| NDCG@5 | 0.9953 |
| HitRate@10 | 0.9977 |
| Recall@10 | 0.9977 |
| NDCG@10 | 0.9957 |
| HitRate@20 | 0.9985 |
| Recall@20 | 0.9985 |
| NDCG@20 | 0.9959 |
| MRR | 0.9952 |
  
</details>

<details> 
<summary>Show learning curves</summary>
    
#### Learning curves:

<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/dbe8d489-8bb5-4698-a905-cfdf652cfd01" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/e0816822-1e3a-4840-b29f-b92401db8038" />

  
</details>
  
</details>
  
-------------------------------------
  
</details>

<details>
<summary>Comparison of approach</summary>

### Comparison of approach

Both scripts implement an **XGBoost model** for the same recommendation task and use the same general evaluation framework.  
In both cases:

- the target column is `owned`
- ranking is based on predicted probabilities
- model selection is done using **validation NDCG@10**
- final evaluation includes ranking metrics and ROC-AUC

However, the two implementations differ in their **feature space**, while the general training procedure remains the same.

-------------------------------------

#### 1. Dataset and feature space

The **baseline model** uses a smaller and simpler feature set:
- standard user-level features
- game-level popularity and metadata features
- grouped user playtime features
- 5 categorical metadata columns

The **network model** extends this setup with additional network-related information:
- `friend_count`
- `game_emb_0` to `game_emb_31`

*This makes the network version much richer in representation and gives the model access to additional relational information.*

-------------------------------------

#### 2. Training strategy

Unlike the Logistic Regression network model, the XGBoost baseline and network versions use the **same overall training strategy**.

In both scripts:
- the full training split is loaded into memory
- preprocessing and model fitting are done in one sklearn pipeline
- the model is trained directly using `fit()`

So, unlike `lr_network.py`, these XGBoost implementations do **not** use chunked training, warm start, or a separate preprocessing stage fitted on a sample.

-------------------------------------

#### 3. Preprocessing differences

Both versions use:
- median imputation for numeric features
- missing-value filling + constrained one-hot encoding for categorical features

Categorical encoding is configured identically in both scripts:
- `handle_unknown="infrequent_if_exist"`
- `max_categories=100`
- `min_frequency=50`

This helps control feature explosion caused by rare categories.

Also, neither version uses `StandardScaler`, because XGBoost is a tree-based boosting model and does not require feature scaling.

-------------------------------------

#### 4. Model configuration

Both models use the same XGBoost training setup:
- `objective="binary:logistic"`
- `eval_metric="logloss"`
- `tree_method="hist"`
- `n_jobs=8`

The same hyperparameter grid is evaluated in both baseline and network experiments.

-------------------------------------

#### 5. Learning curve setup

Both scripts generate learning curves for:
- 5%
- 10%
- 20%
- 40%
- 70%
- 100%

Both versions also optionally limit the number of rows used for learning curve analysis:
- `learning_curve_max_rows = 1000000`

This keeps runtime manageable while still showing how performance scales with training set size.

-------------------------------------

#### 6. Saved artifacts

Both scripts save:
- validation trial summaries
- test predictions
- per-user metrics
- trained model pipeline
- `results.json`
- learning curve files

The saved outputs are structurally the same for both baseline and network XGBoost experiments.

-------------------------------------

#### Summary

The two XGBoost scripts follow the same training and evaluation design.

- **`xgb_baseline.py`** is an XGBoost model trained on the baseline feature set
- **`xgb_network.py`** is an XGBoost model trained on the network-enriched feature set
  
</details>
  
<details>
<summary>Comparison of results</summary>  
  
### Comparison of results
  
The table below compares the final **test results** of the two XGBoost models.
  
| Metric | Baseline XGB | Network XGB |
|---|---:|---:|
| ROC-AUC | 0.9681 | 0.9992 |
| Evaluated users | 28211 | 28211 |
| HitRate@1 | 0.7763 | 0.9940 |
| Recall@1 | 0.7763 | 0.9940 |
| NDCG@1 | 0.7763 | 0.9940 |
| HitRate@5 | 0.8649 | 0.9965 |
| Recall@5 | 0.8649 | 0.9965 |
| NDCG@5 | 0.8237 | 0.9953 |
| HitRate@10 | 0.8994 | 0.9977 |
| Recall@10 | 0.8994 | 0.9977 |
| NDCG@10 | 0.8348 | 0.9957 |
| HitRate@20 | 0.9381 | 0.9985 |
| Recall@20 | 0.9381 | 0.9985 |
| NDCG@20 | 0.8447 | 0.9959 |
| MRR | 0.8190 | 0.9952 |
  
-------------------------------------
  
#### Key observations
  
Compared with the Baseline XGBoost model, the Network version achieves substantially stronger results across all ranking metrics.

The largest improvements are visible at the top of the ranking:
- **HitRate@1** increases from **0.7763** to **0.9940**
- **NDCG@10** increases from **0.8348** to **0.9957**
- **MRR** increases from **0.8190** to **0.9952**
  
This suggests that the network-enriched feature set helps the model place relevant games much closer to the top of the recommendation list.    
  
Overall, the **Network XGBoost model clearly outperforms the baseline version**, indicating that social/network-derived features and embedding-based signals provide much stronger information for the recommendation task than the baseline metadata features alone.

</details> 
