<details> 
<summary>Random Forest Baseline model</summary>
  
### MODEL: Random Forest Baseline model   
    
`rf_baseline.py`
      
It trains, validates, and evaluates a Random Forest baseline for the game recommendation task.  
  
The script builds a full sklearn pipeline that:  
- preprocesses numeric features  
- preprocesses categorical features  
- converts sparse features to dense format  
- trains a Random Forest classifier  
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

After preprocessing, the transformed matrix is converted from sparse to dense format using `FunctionTransformer`, because `RandomForestClassifier` in sklearn expects dense input.

*Unlike Logistic Regression, Random Forest does not require feature scaling, so no `StandardScaler` is used for numeric columns.*

-------------------------------------

#### Model
  
The classifier is: **RandomForestClassifier**
  
Configuration:
- `bootstrap=True`
- `class_weight="balanced_subsample"`
- `random_state=42`
- `n_jobs=8`
  
A small hyperparameter grid is tested:
- `n_estimators=80`, `max_depth=20`, `min_samples_split=20`, `min_samples_leaf=10`, `max_features="sqrt"`
- `n_estimators=120`, `max_depth=30`, `min_samples_split=20`, `min_samples_leaf=10`, `max_features="sqrt"`
  
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
- 10%
- 30%
- 60%
- 100%
  
For each fraction, it measures:
- training ROC-AUC
- validation ROC-AUC
- validation ranking metrics
- training time
  
To keep computation manageable, learning curves can be limited to a subset of training rows:
- `learning_curve_max_rows = 300000`
  
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
<summary>Show results for Random Forest Baseline model</summary> 

### Random Forest Baseline:  
  
- "model_type": "rf"
- "dataset_type": "baseline"
- "seed": 42
- "train_rows": 43494594
- "val_rows": 2849311
- "test_rows": 2849311
- "rf_njobs": 8
- "ohe_max_categories": 100
- "ohe_min_frequency": 50
- "learning_curve_max_rows": 300000
  
**Best validation parameters:**
- n_estimators = 120
- max_depth = 30
- min_samples_split = 20
- min_samples_leaf = 10
- max_features = sqrt
  
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
| Trial | 2 |
| n_estimators | 120 |
| max_depth | 30 |
| min_samples_split | 20 |
| min_samples_leaf | 10 |
| max_features | sqrt |
| Fit time (s) | 4646.31 |
| ROC-AUC | 0.9495 |
| Evaluated users | 28211 |
| HitRate@1 | 0.6161 |
| Recall@1 | 0.6161 |
| NDCG@1 | 0.6161 |
| HitRate@5 | 0.7799 |
| Recall@5 | 0.7799 |
| NDCG@5 | 0.7048 |
| HitRate@10 | 0.8370 |
| Recall@10 | 0.8370 |
| NDCG@10 | 0.7232 |
| HitRate@20 | 0.8999 |
| Recall@20 | 0.8999 |
| NDCG@20 | 0.7391 |
| MRR | 0.6946 |

</details> 
  
<details> 
<summary>Show test results</summary>
    
#### Test results:
  
| Metric | Value |
|---|---:|
| ROC-AUC | 0.9492 |
| Evaluated users | 28211 |
| HitRate@1 | 0.6197 |
| Recall@1 | 0.6197 |
| NDCG@1 | 0.6197 |
| HitRate@5 | 0.7799 |
| Recall@5 | 0.7799 |
| NDCG@5 | 0.7064 |
| HitRate@10 | 0.8368 |
| Recall@10 | 0.8368 |
| NDCG@10 | 0.7248 |
| HitRate@20 | 0.8992 |
| Recall@20 | 0.8992 |
| NDCG@20 | 0.7406 |
| MRR | 0.6968 |
  
</details>

<details> 
<summary>Show learning curves</summary>
    
#### Learning curves:
  
<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/c4f35043-55cc-487b-916e-263321cad15f" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/c552c1a6-a3bf-4f33-9565-9f195991d6f4" />

  
</details>
  
</details>

-------------------------------------
  
</details>

<details> 
<summary>Random Forest Network model</summary>
  
### MODEL: Random Forest Network model   
    
`rf_network.py`
      
It trains, validates, and evaluates a Random Forest model for the game recommendation task using the **network-enriched dataset**.  
  
The script builds a full sklearn pipeline that:  
- preprocesses numeric features  
- preprocesses categorical features  
- converts sparse features to dense format  
- trains a Random Forest classifier  
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

After preprocessing, the transformed matrix is converted from sparse to dense format using `FunctionTransformer`, because `RandomForestClassifier` in sklearn expects dense input.

*Unlike Logistic Regression, Random Forest does not require feature scaling, so no `StandardScaler` is used for numeric columns.*

-------------------------------------

#### Model
  
The classifier is: **RandomForestClassifier**
  
Configuration:
- `bootstrap=True`
- `class_weight="balanced_subsample"`
- `random_state=42`
- `n_jobs=8`
  
A hyperparameter grid is tested:
- `n_estimators=80`, `max_depth=20`, `min_samples_split=20`, `min_samples_leaf=10`, `max_features="sqrt"`
- `n_estimators=120`, `max_depth=30`, `min_samples_split=20`, `min_samples_leaf=10`, `max_features="sqrt"`
  
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
- 10%
- 30%
- 60%
- 100%
  
For each fraction, it measures:
- training ROC-AUC
- validation ROC-AUC
- validation ranking metrics
- training time
  
To keep computation manageable, learning curves can be limited to a subset of training rows:
- `learning_curve_max_rows = 300000`
  
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
<summary>Show results for Random Forest Network model</summary> 

### Random Forest Network:  
  
- "model_type": "rf"
- "dataset_type": "network"
- "seed": 42
- "train_rows": 43494594
- "val_rows": 2849311
- "test_rows": 2849311
- "rf_njobs": 8
- "ohe_max_categories": 100
- "ohe_min_frequency": 50
- "learning_curve_max_rows": 300000
  
**Best validation parameters:**
- n_estimators = 120
- max_depth = 30
- min_samples_split = 20
- min_samples_leaf = 10
- max_features = sqrt
  
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
| Trial | 2 |
| n_estimators | 120 |
| max_depth | 30 |
| min_samples_split | 20 |
| min_samples_leaf | 10 |
| max_features | sqrt |
| Fit time (s) | 5309.52 |
| ROC-AUC | 0.9936 |
| Evaluated users | 28211 |
| HitRate@1 | 0.9594 |
| Recall@1 | 0.9594 |
| NDCG@1 | 0.9594 |
| HitRate@5 | 0.9730 |
| Recall@5 | 0.9730 |
| NDCG@5 | 0.9667 |
| HitRate@10 | 0.9791 |
| Recall@10 | 0.9791 |
| NDCG@10 | 0.9686 |
| HitRate@20 | 0.9871 |
| Recall@20 | 0.9871 |
| NDCG@20 | 0.9706 |
| MRR | 0.9663 |

</details> 
  
<details> 
<summary>Show test results</summary>
    
#### Test results:
  
| Metric | Value |
|---|---:|
| ROC-AUC | 0.9934 |
| Evaluated users | 28211 |
| HitRate@1 | 0.9583 |
| Recall@1 | 0.9583 |
| NDCG@1 | 0.9583 |
| HitRate@5 | 0.9730 |
| Recall@5 | 0.9730 |
| NDCG@5 | 0.9662 |
| HitRate@10 | 0.9787 |
| Recall@10 | 0.9787 |
| NDCG@10 | 0.9680 |
| HitRate@20 | 0.9864 |
| Recall@20 | 0.9864 |
| NDCG@20 | 0.9700 |
| MRR | 0.9656 |
  
</details>

<details> 
<summary>Show learning curves</summary>
    
#### Learning curves:
    
<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/0ed5866b-4d32-4905-aa18-2b2b9a92348c" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/ed08b6fe-e9dd-4117-a5d5-64f7a8b5584b" />
  
  
</details>
  
</details>
  
-------------------------------------
  
</details>

<details>
<summary>Comparison of approach</summary>

### Comparison of approach

Both scripts implement a **Random Forest model** for the same recommendation task and use the same general evaluation framework.  
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

Unlike the Logistic Regression network model, the Random Forest baseline and network versions use the **same overall training strategy**.  
  
In both scripts:  
- the full training split is loaded into memory  
- preprocessing and model fitting are done in one sklearn pipeline  
- the model is trained directly using `fit()`  

So, unlike `lr_network.py`, these Random Forest implementations do **not** use chunked training, warm start, or a separate preprocessing stage fitted on a sample.  

-------------------------------------

#### 3. Preprocessing differences

Both versions use:
- median imputation for numeric features
- missing-value filling + constrained one-hot encoding for categorical features
- sparse-to-dense conversion before model fitting

Categorical encoding is configured identically in both scripts:
- `handle_unknown="infrequent_if_exist"`
- `max_categories=100`
- `min_frequency=50`

This helps control feature explosion caused by rare categories.

Also, neither version uses `StandardScaler`, because Random Forest is a tree-based model and does not require feature scaling.

-------------------------------------

#### 4. Dense conversion step

Both models apply a dense-conversion step after preprocessing:
- sparse matrices produced by one-hot encoding are converted to dense arrays

This is necessary because `RandomForestClassifier` in sklearn expects dense input.

-------------------------------------

#### 5. Learning curve setup

Both scripts generate learning curves for:
- 10%
- 30%
- 60%
- 100%

Both versions also optionally limit the number of rows used for learning curve analysis:
- `learning_curve_max_rows = 300000`

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

The saved outputs are structurally the same for both baseline and network Random Forest experiments.

-------------------------------------

#### Summary

The two Random Forest scripts follow the same training and evaluation design.

- **`rf_baseline.py`** is a Random Forest model trained on the baseline feature set
- **`rf_network.py`** is a Random Forest model trained on the network-enriched feature set
  
</details>
  
<details>
<summary>Comparison of results</summary>  
  
### Comparison of results
  
The table below compares the final **test results** of the two Random Forest models.
  
| Metric | Baseline RF | Network RF |
|---|---:|---:|
| ROC-AUC | 0.9492 | 0.9934 |
| Evaluated users | 28211 | 28211 |
| HitRate@1 | 0.6197 | 0.9583 |
| Recall@1 | 0.6197 | 0.9583 |
| NDCG@1 | 0.6197 | 0.9583 |
| HitRate@5 | 0.7799 | 0.9730 |
| Recall@5 | 0.7799 | 0.9730 |
| NDCG@5 | 0.7064 | 0.9662 |
| HitRate@10 | 0.8368 | 0.9787 |
| Recall@10 | 0.8368 | 0.9787 |
| NDCG@10 | 0.7248 | 0.9680 |
| HitRate@20 | 0.8992 | 0.9864 |
| Recall@20 | 0.8992 | 0.9864 |
| NDCG@20 | 0.7406 | 0.9700 |
| MRR | 0.6968 | 0.9656 |
  
-------------------------------------
  
#### Key observations
  
Compared with the Baseline Random Forest model, the Network version achieves substantially stronger results across all ranking metrics.

The largest improvements are visible at the top of the ranking:
- **HitRate@1** increases from **0.6197** to **0.9583**
- **NDCG@10** increases from **0.7248** to **0.9680**
- **MRR** increases from **0.6968** to **0.9656**
  
This suggests that the network-enriched feature set helps the model place relevant games much closer to the top of the recommendation list.    
  
Overall, the **Network Random Forest model clearly outperforms the baseline version**, indicating that social/network-derived features and embedding-based signals provide much stronger information for the recommendation task than the baseline metadata features alone.

</details>
