<details> 
<summary>Logistic Regression model — hyperparameter search</summary>

### Logistic Regression model — hyperparameter search

`train_lr_baseline.py`  
`train_lr_network.py`

These scripts perform the original Logistic Regression training procedure and hyperparameter search.

Their role is to:
- train the model on one seed
- compare hyperparameter configurations
- select the best final setup

-------------------------------------

## Input
- `train.csv`
- `val.csv`
- `test.csv`

*use baseline dataset for `train_lr_baseline.py` and network dataset for `train_lr_network.py`*
  
-------------------------------------

## What the scripts do

The scripts:
- load the training, validation, and test splits
- build a sklearn-based preprocessing and modeling pipeline
- preprocess numeric and categorical features
- train a Logistic Regression classifier
- compare several hyperparameter combinations
- select the best configuration using validation ranking quality
- evaluate the best model on the test split
- create learning curve experiments for the selected configuration

The baseline and network versions follow the same general goal, but the network version uses a more memory-aware training procedure.

-------------------------------------

## Features used

Both scripts use:
- numeric features
- categorical features
- identifier columns:
  - `steamid`
  - `appid`

The identifier columns are loaded for evaluation and saving predictions, but they are **not** used as model features.

### Baseline model
The baseline version uses:
- standard user-level and game-level numeric features
- grouped user playtime features
- 5 categorical metadata columns

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

Grouped user playtime features:
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

#### Identifier columns (not used as features):

- `steamid`
- `appid`

</details>

### Network model
The network version uses the same general structure, but extends the numeric feature space with:
- `friend_count`
- `game_emb_0 ... game_emb_31`

So the Network model uses a richer input representation than the Baseline model.

<details>
<summary>Show full feature list for network model</summary>

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

#### Identifier columns (not used as features):

- `steamid`
- `appid`

</details>

-------------------------------------

## Preprocessing

Both scripts build a preprocessing pipeline based on `ColumnTransformer`.

### Numeric preprocessing
- missing values are filled using **median imputation**
- features are scaled using `StandardScaler`

### Categorical preprocessing
- missing values are replaced with **"MISSING"**
- categorical features are encoded using `OneHotEncoder`

### Baseline model
The baseline version uses:
- `OneHotEncoder(handle_unknown="ignore")`

### Network model
The network version uses stricter one-hot encoding settings to control feature explosion:
- `handle_unknown="infrequent_if_exist"`
- `max_categories=100`
- `min_frequency=50`

This is important because the network dataset is much larger and produces a much larger sparse feature space.

-------------------------------------

## Model

The classifier is: **LogisticRegression**

Shared core setup:
- solver: `saga`
- penalty: `l2`

The scripts test two hyperparameter configurations:
- `C = 0.1`, `class_weight = None`
- `C = 1.0`, `class_weight = "balanced"`

The best model is selected using:
- **validation NDCG@10**

So even though the underlying model is a classifier, model selection is based on ranking quality.

-------------------------------------

## Training strategy

### Baseline model
The baseline script uses a standard in-memory sklearn pipeline:
- the full training split is loaded into memory
- preprocessing and model fitting are done in one pipeline
- the model is trained directly using `fit()`

### Network model
The network script uses a memory-aware chunked training procedure because the dataset is too large for a standard full-data fit.

Workflow:
- the preprocessor is fit on a sample of training rows
- `train.csv` is read in chunks
- each chunk is transformed separately
- Logistic Regression is trained with `warm_start=True`
- the model is updated repeatedly across chunks and epochs

Key settings:
- `preprocessor_sample_rows = 5000000`
- `chunksize = 200000`
- `epochs = 3`

This means the Network version uses:
- `training_mode = "full_chunked_warm_start"`

-------------------------------------

## Ranking evaluation

Predicted probabilities are used as ranking scores.  
For each user (`steamid`):

candidate games are sorted by predicted score in descending order  
ranking metrics are computed on the ordered owned labels

The scripts compute:
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

## Additional classification metric

Besides ranking metrics, the scripts also compute:
- ROC-AUC

ROC-AUC is calculated on:
- validation data during model selection
- test data for the final selected model

-------------------------------------

## Learning curve analysis

After selecting the best validation configuration, the scripts build learning curves for the selected model.

### Baseline model
The baseline script trains on increasing fractions of the training set:
- 10%
- 50%
- 100%

It saves:
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`

### Network model
The network script also uses:
- 10%
- 50%
- 100%

But the learning curve is computed on a reduced subset of the training split:
- `lc_train_rows = 2000000`

This keeps runtime manageable for the much larger network setting.

It saves:
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`

-------------------------------------

## Outputs

### For Baseline model
- `val_trials.csv`
- `test_scores.csv.gz`
- `test_per_user_metrics.csv`
- `best_model.joblib`
- `results.json`
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`

### For Network model
- `val_trials.csv`
- `fit_log_trial_*.csv`
- `best_fit_log.csv`
- `test_scores.csv.gz`
- `test_per_user_metrics.csv`
- `preprocessor.joblib`
- `best_model.joblib`
- `results.json`
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`

*you can see results.json for all in `results folder`*

-------------------------------------
<details>
<summary>Show single-seed plots </summary>
    
## Single-seed plots

### Baseline model

<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/21207457-62a1-4fef-9d7c-0057f056097a" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/429b68de-f167-4d41-9b38-5ddfd5368f24" />

### Network model

<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/b95de323-6406-47a6-b48c-673ec4c13dfc" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/6f08ced5-d214-4eeb-bf32-78748b25b3f6" />

These plots come from a single training run (seed = 42).  

They are useful for:

- showing how the model behaves as training data grows
- illustrating the selected configuration
- documenting the original hyperparameter-search experiment
  
They do not show variance across seeds.  

</details>
  
-------------------------------------

## Single-seed results

These runs were used mainly to:  
- perform hyperparameter search  
- identify the best final configuration

<details> 
<summary>Show results for Logistic Regression - baseline model</summary>

### Logistic Regression - baseline model

- `"model_type": "lr"`
- `"dataset_type": "baseline"`
- `"seed": 42`
- `"train_rows": 43494594`
- `"val_rows": 2849311`
- `"test_rows": 2849311`
  
Best validation parameters:
- `C = 1.0`
-  `class_weight = balanced`

<details> 
<summary>Show validation results</summary>

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
</details>
<details> 
<summary>Show results for Logistic Regression - network model</summary>

### Logistic Regression - network model

- `"model_type": "lr"`
- `"dataset_type": "network"`
- `"training_mode": "full_chunked_warm_start"`
- `"seed": 42`
- `"train_rows": 43494594`
- `"val_rows": 2849311`
- `"test_rows": 2849311`
- `"n_features_out": 458`
- `"chunksize": 200000`
- `"epochs": 3`
- `"preprocessor_sample_rows": 5000000`
  
Best validation parameters:  
- `C = 1.0`
- `class_weight = balanced`

<details> 
<summary>Show validation results</summary>

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

*Final evaluation is reported separately in the multi-seed section below.*
  
</details>
</details>

<details>
<summary>Logistic Regression model — multi-seed final evaluation</summary>

### Logistic Regression model — multi-seed final evaluation

`train_lr_baseline_multiseed.py`  
`train_lr_network_multiseed.py`  

These scripts perform the final evaluation of the Logistic Regression model using multiple random seeds.  
  
They use the same:  
- preprocessing logic  
- feature definitions  
- training data  
- best hyperparameters selected earlier by the single-seed search scripts  
    
The only difference is that the final model is now trained multiple times to estimate:    
- mean performance  
- standard deviation

-------------------------------------
  
### Why these scripts were added

A single run may still depend on:  
- optimization randomness
- random seed
- details of numerical optimization
  
Because of this, one run can look slightly better or slightly worse than another.  
  
The multi-seed version was added to make the final results:  
- more stable   
- more reliable  
- easier to compare fairly

-------------------------------------
  
### Relation to `train_lr_baseline.py` and `train_lr_network.py`

The workflow is:  
  
1. `train_lr_baseline.py` / `train_lr_network.py`  
    - hyperparameter search
    - single-seed training
    - selection of the best configuration
      
2. `train_lr_baseline_multiseed.py` / `train_lr_network_multiseed.py`  
    - final evaluation
    - same best configuration
    - multiple seeds
    - aggregated metrics
  
So the multi-seed scripts do not repeat the hyperparameter search.  
  
*They only evaluate the already selected final model more robustly.*

-------------------------------------

### Fixed hyperparameters used

For both dataset variants, the multi-seed scripts use:  
- `C = 1.0`
- `class_weight = balanced`

-------------------------------------
  
### Multi-seed setup

The final model is trained with:  
  
`seeds = [42, 0, 1]`

For each seed, the scripts:  
- train the model independently   
- save the fitted sklearn pipeline for that seed  
- evaluate validation metrics  
- evaluate test metrics  
- save test predictions and per-user ranking metrics  
  
In the network version, the script also:  
- reuses one shared fitted preprocessor  
- trains the Logistic Regression model with chunked warm-start training  
  
Then the results are aggregated across seeds using:  
- mean
- standard deviation

-------------------------------------

### Multi-seed learning curves

The multi-seed scripts also build learning curves for the final configuration across seeds.  
They use the same fractions as the single-seed version:    
- 10%
- 50%
- 100%
  
For each fraction and each seed, they measure:  
- `training ROC-AUC`
- `validation ROC-AUC`
- `validation NDCG@10`
- `validation Recall@10`
  
They save:  
- `learning_curve_per_seed.csv`
- `learning_curve_aggregated.csv`
- `learning_curve_roc_auc_multiseed.png`
- `learning_curve_ranking_multiseed.png`
  
The plotted curves show:    
- mean value across seeds  
- shaded area for standard deviation across seeds

-------------------------------------

### Outputs:

#### For Baseline model:  
- `best_model_seed42.joblib`
- `best_model_seed0.joblib`
- `best_model_seed1.joblib`
- `test_scores_seed42.csv.gz`
- `test_scores_seed0.csv.gz`
- `test_scores_seed1.csv.gz`
- `test_per_user_metrics_seed42.csv`
- `test_per_user_metrics_seed0.csv`
- `test_per_user_metrics_seed1.csv`
- `learning_curve_per_seed.csv`
- `learning_curve_aggregated.csv`
- `learning_curve_roc_auc_multiseed.png`
- `learning_curve_ranking_multiseed.png`
- `results.json`
  
#### For Network model:  
- `best_model_seed42.joblib`
- `best_model_seed0.joblib`
- `best_model_seed1.joblib`
- `fit_log_seed_42.csv`
- `fit_log_seed_0.csv`
- `fit_log_seed_1.csv`
- `test_scores_seed42.csv.gz`
- `test_scores_seed0.csv.gz`
- `test_scores_seed1.csv.gz`
- `test_per_user_metrics_seed42.csv`
- `test_per_user_metrics_seed0.csv`
- `test_per_user_metrics_seed1.csv`
- `preprocessor.joblib`
- `learning_curve_per_seed.csv`
- `learning_curve_aggregated.csv`
- `learning_curve_roc_auc_multiseed.png`
- `learning_curve_ranking_multiseed.png`
- `results.json`

*you can see `results.json` for all in results folder*  

</details>
  
<details>
<summary>Final multi-seed results</summary>
    
### Final multi-seed results

The tables below report the final Logistic Regression results from the multi-seed scripts.  
  
All values are reported as:  
- **mean ± std**
  
across seeds:  
- 42
- 0
- 1

--------------------------------------------

### Logistic Regression — baseline model

#### Validation Results:
  
| Metric     |      Mean ± Std |
| ---------- | --------------: |
| ROC-AUC    | 0.9036 ± 0.0000 |
| HitRate@1  | 0.1616 ± 0.0000 |
| Recall@1   | 0.1616 ± 0.0000 |
| NDCG@1     | 0.1616 ± 0.0000 |
| HitRate@5  | 0.5689 ± 0.0000 |
| Recall@5   | 0.5689 ± 0.0000 |
| NDCG@5     | 0.3669 ± 0.0000 |
| HitRate@10 | 0.7480 ± 0.0000 |
| Recall@10  | 0.7480 ± 0.0000 |
| NDCG@10    | 0.4257 ± 0.0000 |
| HitRate@20 | 0.8434 ± 0.0000 |
| Recall@20  | 0.8434 ± 0.0000 |
| NDCG@20    | 0.4499 ± 0.0000 |
| MRR        | 0.3366 ± 0.0000 |

#### Test Results:

| Metric     |      Mean ± Std |
| ---------- | --------------: |
| ROC-AUC    | 0.9035 ± 0.0000 |
| HitRate@1  | 0.1610 ± 0.0000 |
| Recall@1   | 0.1610 ± 0.0000 |
| NDCG@1     | 0.1610 ± 0.0000 |
| HitRate@5  | 0.5761 ± 0.0000 |
| Recall@5   | 0.5761 ± 0.0000 |
| NDCG@5     | 0.3708 ± 0.0000 |
| HitRate@10 | 0.7485 ± 0.0000 |
| Recall@10  | 0.7485 ± 0.0000 |
| NDCG@10    | 0.4275 ± 0.0000 |
| HitRate@20 | 0.8400 ± 0.0000 |
| Recall@20  | 0.8400 ± 0.0000 |
| NDCG@20    | 0.4508 ± 0.0000 |
| MRR        | 0.3384 ± 0.0000 |

--------------------------------------------
<details>
<summary>Show multi-seed plot — baseline model</summary>

### Multi-seed learning curves — baseline model

<img width="1600" height="1000" alt="learning_curve_roc_auc_multiseed" src="https://github.com/user-attachments/assets/a97ec180-2cd0-4fa9-a021-1664af52f00c" />
<img width="1600" height="1000" alt="learning_curve_ranking_multiseed" src="https://github.com/user-attachments/assets/f9b858e1-416f-458f-9e66-695a41241f23" />
  
</details>
  
------------------------------------------
  
### Logistic Regression — network model
  
##### Validation Results:

| Metric     |      Mean ± Std |
| ---------- | --------------: |
| ROC-AUC    | 0.9805 ± 0.0001 |
| HitRate@1  | 0.7749 ± 0.0008 |
| Recall@1   | 0.7749 ± 0.0008 |
| NDCG@1     | 0.7749 ± 0.0008 |
| HitRate@5  | 0.9168 ± 0.0006 |
| Recall@5   | 0.9168 ± 0.0006 |
| NDCG@5     | 0.8554 ± 0.0002 |
| HitRate@10 | 0.9452 ± 0.0009 |
| Recall@10  | 0.9452 ± 0.0009 |
| NDCG@10    | 0.8647 ± 0.0002 |
| HitRate@20 | 0.9679 ± 0.0004 |
| Recall@20  | 0.9679 ± 0.0004 |
| NDCG@20    | 0.8704 ± 0.0002 |
| MRR        | 0.8409 ± 0.0004 |

#### Test Results:

| Metric     |      Mean ± Std |
| ---------- | --------------: |
| ROC-AUC    | 0.9805 ± 0.0001 |
| HitRate@1  | 0.7784 ± 0.0013 |
| Recall@1   | 0.7784 ± 0.0013 |
| NDCG@1     | 0.7784 ± 0.0013 |
| HitRate@5  | 0.9184 ± 0.0004 |
| Recall@5   | 0.9184 ± 0.0004 |
| NDCG@5     | 0.8581 ± 0.0005 |
| HitRate@10 | 0.9445 ± 0.0008 |
| Recall@10  | 0.9445 ± 0.0008 |
| NDCG@10    | 0.8666 ± 0.0003 |
| HitRate@20 | 0.9681 ± 0.0006 |
| Recall@20  | 0.9681 ± 0.0006 |
| NDCG@20    | 0.8726 ± 0.0003 |
| MRR        | 0.8437 ± 0.0006 |

<details>
<summary>Show multi-seed plot — network model</summary>

### Multi-seed learning curves — network model  

<img width="1600" height="1000" alt="learning_curve_roc_auc_multiseed" src="https://github.com/user-attachments/assets/d6e75819-1a97-41db-938f-5763ef56cdd8" />
<img width="1600" height="1000" alt="learning_curve_ranking_multiseed" src="https://github.com/user-attachments/assets/eb7e2f76-466b-413a-8b9c-d9c66eef706f" />
  
</details>
</details>
<details>
<summary>Comparison of approach</summary>

### Comparison of approach

The Logistic Regression experiments are now split into two stages.  
  
**Stage 1**: `train_lr_baseline.py` / `train_lr_network.py`  
 
This stage is used for:
- hyperparameter search
- single-seed training
- selecting the best final configuration
  
Stage 2: `train_lr_baseline_multiseed.py` / `train_lr_network_multiseed.py`
  
This stage is used for:  
- final evaluation
- repeated training on multiple seeds
- reporting mean ± std

---------------------------------------

### Same elements in both variants
Both Baseline and Network Logistic Regression models use:  
- the same model family
- the same ranking metrics
- the same general evaluation procedure
- the same final selected hyperparameters

---------------------------------------

### Main difference between Baseline and Network

The difference is in:  
- input feature space
- preprocessing details
- training strategy
- Baseline model
  
Uses the baseline tabular feature set and standard in-memory sklearn training.  
  
#### Network model:
Uses the extended feature set with:  
- friend_count
- game_emb_0 ... game_emb_31
  
It also uses:  
- stricter categorical encoding controls
- sample-based preprocessor fitting
- chunked warm-start training across the full split
  
So the Network model is not only richer in features, but also much heavier computationally.  

---------------------------------------

### Final evaluation protocol

The final reported Logistic Regression results come from the multi-seed scripts, not from the single-seed search scripts.    
This means the final comparison is based on:  
- the same final hyperparameters
- the same evaluation procedure
- multiple seeds
- averaged results with standard deviation
  
</details>
<details>
<summary>Comparison of final multi-seed results</summary>

### Comparison of final multi-seed results
The table below compares the final test results of the two Logistic Regression variants.  

| Metric     | LR baseline model | LR network model |
| ---------- | ----------------: | ---------------: |
| ROC-AUC    |   0.9035 ± 0.0000 |  0.9805 ± 0.0001 |
| HitRate@1  |   0.1610 ± 0.0000 |  0.7784 ± 0.0013 |
| Recall@1   |   0.1610 ± 0.0000 |  0.7784 ± 0.0013 |
| NDCG@1     |   0.1610 ± 0.0000 |  0.7784 ± 0.0013 |
| HitRate@5  |   0.5761 ± 0.0000 |  0.9184 ± 0.0004 |
| Recall@5   |   0.5761 ± 0.0000 |  0.9184 ± 0.0004 |
| NDCG@5     |   0.3708 ± 0.0000 |  0.8581 ± 0.0005 |
| HitRate@10 |   0.7485 ± 0.0000 |  0.9445 ± 0.0008 |
| Recall@10  |   0.7485 ± 0.0000 |  0.9445 ± 0.0008 |
| NDCG@10    |   0.4275 ± 0.0000 |  0.8666 ± 0.0003 |
| HitRate@20 |   0.8400 ± 0.0000 |  0.9681 ± 0.0006 |
| Recall@20  |   0.8400 ± 0.0000 |  0.9681 ± 0.0006 |
| NDCG@20    |   0.4508 ± 0.0000 |  0.8726 ± 0.0003 |
| MRR        |   0.3384 ± 0.0000 |  0.8437 ± 0.0006 |

---------------------------------------------

### Key observations

The final multi-seed results show a very large difference between the two Logistic Regression variants.  
Compared with the baseline model, the network model is substantially stronger across all reported metrics.  
The largest gains are visible near the top of the ranking:  
- HitRate@1 increases from 0.1610 to 0.7784
- NDCG@10 increases from 0.4275 to 0.8666
- MRR increases from 0.3384 to 0.8437
  
This suggests that the network-enriched feature set helps the model place relevant games much closer to the top of the recommendation list.  
  
Overall, the Network Logistic Regression model clearly outperforms the baseline version, indicating that social/network-derived features and embedding-based signals provide much stronger information for the recommendation task than the baseline metadata features alone.  

*Additionally :  
Unlike tree-based or neural models, Logistic Regression is effectively deterministic once the data and preprocessing are fixed.       
Because it optimizes a convex objective, different random seeds converge to nearly the same solution, which explains the near-zero variance across seeds.*    
  
</details>
