<details> 
<summary>Logistic Regression Baseline model</summary>
  
### MODEL: Logistic Regression Baseline model   
    
`lr_baseline.py`
      
It trains, validates, and evaluates a Logistic Regression baseline for the game recommendation task.  
  
The script builds a full sklearn pipeline that:  
- preprocesses numeric features  
- preprocesses categorical features  
- trains a Logistic Regression classifier  
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
- features are scaled using `StandardScaler`
  
Categorical preprocessing:  
- missing values are replaced with **"MISSING"**
- features are encoded using `OneHotEncoder(handle_unknown="ignore")`

*This allows the model to work with mixed numeric and categorical data in one pipeline.*

-------------------------------------

#### Model
  
The classifier is: **LogisticRegression**
  
Configuration:  
  
- solver: saga  
- penalty: l2  
- random seed: 42  
  
A small hyperparameter grid is tested:  
- C = 0.1, class_weight = None  
- C = 1.0, class_weight = "balanced"  
  
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
- 50%
- 100%
  
For each fraction, it measures:  
- training ROC-AUC
- validation ROC-AUC
- validation ranking metrics
- training time
  
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
<summary>Show results for Random baseline:</summary> 

### Logistic Regression Baseline:  
  
- "model_type": "lr"
- "dataset_type": "baseline"
- "seed": 42
- "train_rows": 43494594
- "val_rows": 2849311
- "test_rows": 2849311
  
**Best validation parameters:**
- C = 1.0
- class_weight = balanced
  
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
  
| Metric          |    Value |
| --------------- | -------: |
| Trial           |        2 |
| C               |      1.0 |
| class_weight    | balanced |
| Fit time (s)    | 10079.65 |
| ROC-AUC         |   0.9036 |
| Evaluated users |    28211 |
| HitRate@1       |   0.1616 |
| Recall@1        |   0.1616 |
| NDCG@1          |   0.1616 |
| HitRate@5       |   0.5689 |
| Recall@5        |   0.5689 |
| NDCG@5          |   0.3669 |
| HitRate@10      |   0.7480 |
| Recall@10       |   0.7480 |
| NDCG@10         |   0.4257 |
| HitRate@20      |   0.8435 |
| Recall@20       |   0.8435 |
| NDCG@20         |   0.4500 |
| MRR             |   0.3366 |

</details> 
  
<details> 
<summary>Show test results</summary>
    
#### Test results:
  
| Metric          |  Value |
| --------------- | -----: |
| ROC-AUC         | 0.9035 |
| Evaluated users |  28211 |
| HitRate@1       | 0.1610 |
| Recall@1        | 0.1610 |
| NDCG@1          | 0.1610 |
| HitRate@5       | 0.5761 |
| Recall@5        | 0.5761 |
| NDCG@5          | 0.3708 |
| HitRate@10      | 0.7485 |
| Recall@10       | 0.7485 |
| NDCG@10         | 0.4275 |
| HitRate@20      | 0.8400 |
| Recall@20       | 0.8400 |
| NDCG@20         | 0.4508 |
| MRR             | 0.3384 |
  
</details>

<details> 
<summary>Show learning curves:</summary>
    
#### Learning curves:
  
<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/21207457-62a1-4fef-9d7c-0057f056097a" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/429b68de-f167-4d41-9b38-5ddfd5368f24" />
  
</details>
  
</details>

-------------------------------------
  
</details>

<details> 
<summary>Logistic Regression Network model</summary>
  
### MODEL: Logistic Regression Network model   
    
`lr_network.py`
      
It trains, validates, and evaluates a Logistic Regression model for the game recommendation task using the **network-enriched dataset**.  
  
The script builds a memory-aware sklearn-based pipeline that:  
- preprocesses numeric features  
- preprocesses categorical features  
- trains a Logistic Regression classifier  
- uses chunked training with warm start to handle the large dataset  
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
  
The script builds a `ColumnTransformer`-based preprocessing pipeline.
  
Numeric preprocessing:  
- missing values are filled using **median imputation**
- features are scaled using `StandardScaler`
  
Categorical preprocessing:  
- missing values are replaced with **"MISSING"**
- features are encoded using `OneHotEncoder`

In the network version, one-hot encoding is additionally constrained to control feature explosion:  
- `handle_unknown="infrequent_if_exist"`
- `max_categories=100`
- `min_frequency=50`

*This is important because the network dataset is much larger and would otherwise blow up the sparse feature space like popcorn in a microwave.*

-------------------------------------

#### Model
  
The classifier is: **LogisticRegression**
  
Configuration:  
  
- solver: saga  
- random seed: 42  
- training mode: `full_chunked_warm_start`
  
A small hyperparameter grid is tested:  
- C = 0.1, class_weight = None  
- C = 1.0, class_weight = "balanced"  
  
Each configuration is trained on the training split and evaluated on the validation split.  
  
The best model is selected using: **Validation NDCG@10**

-------------------------------------

#### Chunked training
  
Unlike the baseline version, the network dataset is too large for a standard full in-memory fit.  
Because of that, the script uses a chunked training strategy.
  
Workflow:
- the preprocessor is fit on a large sample of training rows
- `train.csv` is read in chunks
- each chunk is transformed separately
- Logistic Regression is trained with `warm_start=True`
- the model is updated repeatedly across chunks and epochs
  
Key settings:
- `chunksize = 200000`
- `epochs = 3`
- `preprocessor_sample_rows = 5000000`
  
This allows the script to process the full network dataset without loading everything into memory at once.

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
  
After selecting the best validation configuration, the script builds learning curves on a reduced subset of the training data.  
  
The model is trained on increasing fractions of that subset:  
- 10%
- 50%
- 100%
  
For each fraction, it measures:  
- training ROC-AUC
- validation ROC-AUC
- validation ranking metrics
- training time
  
It then saves:  
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`

*In this version, learning curves are computed on a smaller subset instead of the full training split to keep runtime reasonable.*

-------------------------------------

Outputs:  
- `val_trials.csv` — validation results for all tested hyperparameter settings
- `fit_log_trial_*.csv` — chunk-level training logs for each trial
- `best_fit_log.csv` — training log for the selected model
- `test_scores.csv.gz` — predicted scores for test user-game pairs
- `test_per_user_metrics.csv` — ranking metrics per user on test data
- `preprocessor.joblib` — fitted preprocessor
- `best_model.joblib` — fitted Logistic Regression model
- `results.json` — final summary of the experiment
- `learning_curve.csv` — learning curve metrics
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`
  
-------------------------------------

### Results:

<details> 
<summary>Show results for Logistic Regression Network model</summary> 

### Logistic Regression Network:  
  
- "model_type": "lr"
- "dataset_type": "network"
- "training_mode": "full_chunked_warm_start"
- "seed": 42
- "train_rows": 43494594
- "val_rows": 2849311
- "test_rows": 2849311
- "n_features_out": 458
- "chunksize": 200000
- "epochs": 3
- "preprocessor_sample_rows": 5000000
  
**Best validation parameters:**
- C = 1.0
- class_weight = balanced
  
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
  
| Metric          |    Value |
| --------------- | -------: |
| Trial           |        2 |
| C               |      1.0 |
| class_weight    | balanced |
| Fit time (s)    |  1984.51 |
| ROC-AUC         |   0.9806 |
| Evaluated users |    28211 |
| HitRate@1       |   0.7743 |
| Recall@1        |   0.7743 |
| NDCG@1          |   0.7743 |
| HitRate@5       |   0.9169 |
| Recall@5        |   0.9169 |
| NDCG@5          |   0.8551 |
| HitRate@10      |   0.9455 |
| Recall@10       |   0.9455 |
| NDCG@10         |   0.8644 |
| HitRate@20      |   0.9683 |
| Recall@20       |   0.9683 |
| NDCG@20         |   0.8702 |
| MRR             |   0.8405 |

</details> 
  
<details> 
<summary>Show test results</summary>
    
#### Test results:
  
| Metric          |  Value |
| --------------- | -----: |
| ROC-AUC         | 0.9806 |
| Evaluated users |  28211 |
| HitRate@1       | 0.7773 |
| Recall@1        | 0.7773 |
| NDCG@1          | 0.7773 |
| HitRate@5       | 0.9183 |
| Recall@5        | 0.9183 |
| NDCG@5          | 0.8576 |
| HitRate@10      | 0.9447 |
| Recall@10       | 0.9447 |
| NDCG@10         | 0.8662 |
| HitRate@20      | 0.9683 |
| Recall@20       | 0.9683 |
| NDCG@20         | 0.8721 |
| MRR             | 0.8430 |
  
</details>

<details> 
<summary>Show Learning Curves</summary>
    
#### Learning Curves:
  
<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/b95de323-6406-47a6-b48c-673ec4c13dfc" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/6f08ced5-d214-4eeb-bf32-78748b25b3f6" />
  
</details>
  
</details>
  
-------------------------------------
  
</details>

<details>
<summary>Comparison of approach</summary>

### Comparison of approach

Both scripts implement a **Logistic Regression model** for the same recommendation task and use the same general evaluation framework.  
In both cases:

- the target column is `owned`
- ranking is based on predicted probabilities
- model selection is done using **validation NDCG@10**
- final evaluation includes ranking metrics and ROC-AUC

However, the two implementations differ in their **feature space**, **preprocessing setup**, and especially in their **training strategy**.

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

*This makes the network version much richer in representation, but also significantly heavier computationally.*

-------------------------------------

#### 2. Training strategy

The main difference between the two scripts is **how training is performed**.

##### Baseline version
`lr_baseline.py` uses a standard sklearn pipeline:
- the whole training split is loaded into memory
- preprocessing and model fitting are done in one standard pipeline
- Logistic Regression is trained directly using `fit()`

*This approach is simpler and easier to read, but it assumes the full transformed dataset can be handled in memory.*

##### Network version
  
`lr_network.py` uses a **chunked training approach** because the network dataset is too large for a standard full-data fit.

Instead of training in one pass:
- the preprocessor is fit on a sample of training data
- `train.csv` is read in chunks
- each chunk is transformed separately
- the model is updated repeatedly across chunks
- training is repeated over multiple epochs
- `warm_start=True` is used so model parameters are reused between chunk updates
  
*This makes the implementation more complex, but necessary for scaling to the larger feature space.*

-------------------------------------

#### 3. Preprocessing differences

Both versions use:
- median imputation + standard scaling for numeric features
- missing-value filling + one-hot encoding for categorical features

But the **network version** adds extra safeguards to control the size of the sparse matrix:
- `handle_unknown="infrequent_if_exist"`
- `max_categories=100`
- `min_frequency=50`

*This reduces feature explosion caused by rare categories in the larger dataset.*

The baseline version uses simpler categorical encoding:
- `OneHotEncoder(handle_unknown="ignore")`

-------------------------------------

#### 4. Sparse matrix handling

The baseline model relies on normal sklearn sparse processing inside the pipeline.

The network model adds explicit sparse-matrix handling:
- conversion to CSR format
- index type checks
- conversion of sparse matrix indices to `int32`

*This is a technical safeguard needed for very large sparse matrices.*  
  
-------------------------------------
  
#### 5. Learning curve setup
  
Both scripts generate learning curves for:
- 10%
- 50%
- 100%
  
But they differ in how this is done:  
- **baseline model**: learning curves are built directly from the full training split  
- **network model**: learning curves are computed on a smaller subset of training data  
  
*This is again a practical choice to keep runtime and memory usage under control for the larger network dataset.*

-------------------------------------

#### 6. Saved artifacts
  
Both scripts save:  
- validation trial summaries
- test predictions
- per-user metrics
- trained model outputs
- `results.json`
- learning curve files
  
The **network version** additionally saves:  
- chunk-level fit logs for each trial  
- best training log  
- fitted preprocessor separately 
  
*These extra outputs are useful because chunked training is more complex and benefits from better traceability.*
  
-------------------------------------
  
#### Summary
  
The two scripts follow the same modeling idea, but they are designed for different levels of scale.

- **`lr_baseline.py`** is a straightforward in-memory Logistic Regression pipeline on the baseline feature set
- **`lr_network.py`** is a memory-aware Logistic Regression pipeline adapted to a much larger network-enriched dataset using chunked training and stricter preprocessing controls  
    
</details>
  
<details>
<summary>Comparison of results</summary>  
  
### Comparison of results
  
The table below compares the final **test results** of the two Logistic Regression models.
  
| Metric | Baseline LR | Network LR |
|---|---:|---:|
| ROC-AUC | 0.9035 | 0.9806 |
| Evaluated users | 28211 | 28211 |
| HitRate@1 | 0.1610 | 0.7773 |
| Recall@1 | 0.1610 | 0.7773 |
| NDCG@1 | 0.1610 | 0.7773 |
| HitRate@5 | 0.5761 | 0.9183 |
| Recall@5 | 0.5761 | 0.9183 |
| NDCG@5 | 0.3708 | 0.8576 |
| HitRate@10 | 0.7485 | 0.9447 |
| Recall@10 | 0.7485 | 0.9447 |
| NDCG@10 | 0.4275 | 0.8662 |
| HitRate@20 | 0.8400 | 0.9683 |
| Recall@20 | 0.8400 | 0.9683 |
| NDCG@20 | 0.4508 | 0.8721 |
| MRR | 0.3384 | 0.8430 |
  
-------------------------------------
  
#### Key observations
  
Compared with the Baseline Logistic Regression model, the Network version achieves substantially stronger results across all ranking metrics.

The largest improvements are visible at the top of the ranking:
- **HitRate@1** increases from **0.1610** to **0.7773**
- **NDCG@10** increases from **0.4275** to **0.8662**
- **MRR** increases from **0.3384** to **0.8430**
  
This suggests that the network-enriched feature set helps the model place relevant games much closer to the top of the recommendation list.  
  
Overall, the **Network Logistic Regression model clearly outperforms the baseline version**, indicating that social/network-derived features and embedding-based signals provide much stronger information for the recommendation task than the baseline metadata features alone.  

</details>
