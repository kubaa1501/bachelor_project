<details>
<summary>XGBoost model — hyperparameter search</summary>

### XGBoost model — hyperparameter search

`train_xgb_baseline.py`
`train_xgb_network.py`

These scripts perform the original XGBoost training procedure and hyperparameter search.

Their role is to:
- train the model on one seed
- compare hyperparameter configurations
- select the best final setup

-------------------------------------

## Input
- `train.csv`
- `val.csv`
- `test.csv`

*use baseline dataset for `train_xgb_baseline.py` and network dataset for `train_xgb_network.py`*

-------------------------------------

## What the scripts do

The scripts:
- load the full training, validation, and test splits
- build a full sklearn pipeline
- preprocess numeric and categorical features
- train an XGBoost classifier
- compare several hyperparameter combinations
- select the best configuration using validation ranking quality
- evaluate the best model on the test split
- create learning curve experiments for the selected configuration

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
The network version uses the same structure, but extends the numeric feature space with:
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

The scripts build a `sklearn` Pipeline with a `ColumnTransformer`.

### Numeric preprocessing
- missing values are filled using **median imputation**

### Categorical preprocessing
- missing values are replaced with **"MISSING"**
- categorical features are encoded using constrained `OneHotEncoder`

Configuration:
- `handle_unknown="infrequent_if_exist"`
- `max_categories=100`
- `min_frequency=50`

Unlike Logistic Regression, XGBoost does **not** require feature scaling, so no `StandardScaler` is used.

-------------------------------------

## Model

The classifier is: **XGBClassifier**

Configuration:
- `objective="binary:logistic"`
- `eval_metric="logloss"`
- `tree_method="hist"`
- `random_state=42`
- `n_jobs=8`

The hyperparameter search tests five configurations:

- `n_estimators=200`, `max_depth=4`, `learning_rate=0.05`, `min_child_weight=3`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=1.0`, `reg_alpha=0.0`
- `n_estimators=300`, `max_depth=4`, `learning_rate=0.05`, `min_child_weight=3`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=1.0`, `reg_alpha=0.0`
- `n_estimators=300`, `max_depth=6`, `learning_rate=0.05`, `min_child_weight=5`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=1.0`, `reg_alpha=0.1`
- `n_estimators=300`, `max_depth=6`, `learning_rate=0.10`, `min_child_weight=5`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=2.0`, `reg_alpha=0.1`
- `n_estimators=400`, `max_depth=6`, `learning_rate=0.05`, `min_child_weight=5`, `subsample=1.0`, `colsample_bytree=1.0`, `reg_lambda=2.0`, `reg_alpha=0.1`

The best model is selected using:
- **validation NDCG@10**

So even though the underlying model is a classifier, model selection is based on ranking quality.

-------------------------------------

## Learning curve analysis

After selecting the best validation configuration, the scripts train the model on increasing fractions of the training set:
- 5%
- 10%
- 20%
- 40%
- 70%
- 100%

For each fraction, they measure:
- training ROC-AUC
- validation ROC-AUC
- validation ranking metrics
- training time

To keep computation manageable, learning curves can be limited to:
- `learning_curve_max_rows = 1000000`

The scripts save:
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
- `test_scores.csv.gz`
- `test_per_user_metrics.csv`
- `best_model.joblib`
- `results.json`
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`

*you can see results.json for all in `results folder`*

-------------------------------------

<details>
<summary>Show single-seed plots</summary>

## Single-seed plots

### Baseline model

 <img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/685722e9-9465-4b4a-a1c4-4f613f3eb96f" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/7caa2cb5-b445-4082-ae98-8dfdee8ab851" />
  
### Network model

<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/dbe8d489-8bb5-4698-a905-cfdf652cfd01" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/e0816822-1e3a-4840-b29f-b92401db8038" />
  
These plots come from a **single training run** (`seed = 42`).

They are useful for:
- showing how the model behaves as training data grows
- illustrating the selected configuration
- documenting the original hyperparameter-search experiment

They do **not** show variance across seeds.

</details>

-------------------------------------

## Single-seed results

These runs were used mainly to:
- perform hyperparameter search
- identify the best final configuration

<details>
<summary>Show results for XGBoost - baseline model</summary>

### XGBoost - baseline model

- `"model_type": "xgb"`
- `"dataset_type": "baseline"`
- `"seed": 42`
- `"train_rows": 43494594`
- `"val_rows": 2849311`
- `"test_rows": 2849311`
- `"xgb_njobs": 8`
- `"ohe_max_categories": 100`
- `"ohe_min_frequency": 50`
- `"learning_curve_max_rows": 1000000`

**Best validation parameters:**
- `n_estimators = 300`
- `max_depth = 6`
- `learning_rate = 0.1`
- `min_child_weight = 5`
- `subsample = 0.8`
- `colsample_bytree = 0.8`
- `reg_lambda = 2.0`
- `reg_alpha = 0.1`

<details>
<summary>Show validation results</summary>

#### Validation results:

| Metric | Value |
|---|---:|
| Trial | 4 |
| n_estimators | 300 |
| max_depth | 6 |
| learning_rate | 0.1 |
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

</details>

<details>
<summary>Show results for XGBoost - network model</summary>

### XGBoost - network model

- `"model_type": "xgb"`
- `"dataset_type": "network"`
- `"seed": 42`
- `"train_rows": 43494594`
- `"val_rows": 2849311`
- `"test_rows": 2849311`
- `"xgb_njobs": 8`
- `"ohe_max_categories": 100`
- `"ohe_min_frequency": 50`
- `"learning_curve_max_rows": 1000000`

**Best validation parameters:**
- `n_estimators = 300`
- `max_depth = 6`
- `learning_rate = 0.1`
- `min_child_weight = 5`
- `subsample = 0.8`
- `colsample_bytree = 0.8`
- `reg_lambda = 2.0`
- `reg_alpha = 0.1`

<details>
<summary>Show validation results</summary>

#### Validation results:

| Metric | Value |
|---|---:|
| Trial | 4 |
| n_estimators | 300 |
| max_depth | 6 |
| learning_rate | 0.1 |
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

*Final evaluation is reported separately in the multi-seed section below.*

</details>

</details>


<details>
<summary>XGBoost model — multi-seed final evaluation</summary>

### XGBoost model — multi-seed final evaluation

`train_xgb_baseline_multiseed.py`
`train_xgb_network_multiseed.py`

These scripts perform the **final evaluation** of the XGBoost model using multiple random seeds.

They use the same:
- preprocessing pipeline
- feature definitions
- training data
- best hyperparameters selected earlier by the single-seed search scripts

The only difference is that the final model is now trained multiple times to estimate:
- mean performance
- standard deviation

-------------------------------------

## Why these scripts were added

A single XGBoost run may depend on:
- subsampling of training rows
- subsampling of columns
- randomness inside boosted tree construction
- the selected random seed

Because of this, one run can look slightly better or slightly worse than another.

The multi-seed version was added to make the final results:
- more stable
- more reliable
- easier to compare fairly

-------------------------------------

## Relation to `train_xgb_baseline.py` and `train_xgb_network.py`

The workflow is:

1. `train_xgb_baseline.py` / `train_xgb_network.py`
- hyperparameter search
- single-seed training
- selection of the best configuration

2. `train_xgb_baseline_multiseed.py` / `train_xgb_network_multiseed.py`
- final evaluation
- same best configuration
- multiple seeds
- aggregated metrics

So the multi-seed scripts do **not** repeat the hyperparameter search.

*They only evaluate the already selected final model more robustly.*

-------------------------------------

## Fixed hyperparameters used

For both dataset variants, the multi-seed scripts use:

- `n_estimators = 300`
- `max_depth = 6`
- `learning_rate = 0.1`
- `min_child_weight = 5`
- `subsample = 0.8`
- `colsample_bytree = 0.8`
- `reg_lambda = 2.0`
- `reg_alpha = 0.1`

-------------------------------------

## Multi-seed setup

The final model is trained with:

- `seeds = [42, 0, 1]`

For each seed, the scripts:
- train the model independently
- save the fitted sklearn pipeline for that seed
- evaluate validation metrics
- evaluate test metrics
- save test predictions and per-user ranking metrics

Then they aggregate the results across seeds using:
- mean
- standard deviation

-------------------------------------

## Multi-seed learning curves

The multi-seed scripts also build learning curves for the final configuration across seeds.

They use the same fractions as the single-seed version:
- 5%
- 10%
- 20%
- 40%
- 70%
- 100%

For each fraction and each seed, they measure:
- training ROC-AUC
- validation ROC-AUC
- validation NDCG@10
- validation Recall@10

They save:
- `learning_curve_per_seed.csv`
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`

The plotted curves show:
- mean value across seeds
- shaded area for standard deviation across seeds

-------------------------------------

## Outputs

### For Baseline model
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
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`
- `results.json`

### For Network model
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
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`
- `results.json`

*you can see results.json for all in `results folder`*

</details>


<details>
<summary>Final multi-seed results</summary>

### Final multi-seed results

The tables below report the final XGBoost results from the multi-seed scripts.

All values are reported as:

- **mean ± std**

across seeds:
- `42`
- `0`
- `1`

-------------------------------------

## XGBoost — baseline model

### Validation results

| Metric | Mean ± Std |
|---|---:|
| ROC-AUC | 0.9687 ± 0.0002 |
| HitRate@1 | 0.7744 ± 0.0008 |
| Recall@1 | 0.7744 ± 0.0008 |
| NDCG@1 | 0.7744 ± 0.0008 |
| HitRate@5 | 0.8625 ± 0.0023 |
| Recall@5 | 0.8625 ± 0.0023 |
| NDCG@5 | 0.8214 ± 0.0010 |
| HitRate@10 | 0.9002 ± 0.0022 |
| Recall@10 | 0.9002 ± 0.0022 |
| NDCG@10 | 0.8336 ± 0.0005 |
| HitRate@20 | 0.9399 ± 0.0015 |
| Recall@20 | 0.9399 ± 0.0015 |
| NDCG@20 | 0.8436 ± 0.0004 |
| MRR | 0.8172 ± 0.0005 |

### Test results

| Metric | Mean ± Std |
|---|---:|
| ROC-AUC | 0.9682 ± 0.0002 |
| HitRate@1 | 0.7768 ± 0.0004 |
| Recall@1 | 0.7768 ± 0.0004 |
| NDCG@1 | 0.7768 ± 0.0004 |
| HitRate@5 | 0.8630 ± 0.0021 |
| Recall@5 | 0.8630 ± 0.0021 |
| NDCG@5 | 0.8228 ± 0.0011 |
| HitRate@10 | 0.8992 ± 0.0016 |
| Recall@10 | 0.8992 ± 0.0016 |
| NDCG@10 | 0.8345 ± 0.0009 |
| HitRate@20 | 0.9382 ± 0.0013 |
| Recall@20 | 0.9382 ± 0.0013 |
| NDCG@20 | 0.8444 ± 0.0008 |
| MRR | 0.8187 ± 0.0006 |

<details>
<summary>Show multi-seed plot — baseline model</summary>

#### Multi-seed learning curves — baseline model

<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/b047dafc-be91-4658-9435-16bd3c908f98" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/ca962215-ac07-4da2-b13e-551b8f74022c" />
  
</details>

-------------------------------------

## XGBoost — network model

### Validation results

| Metric | Mean ± Std |
|---|---:|
| ROC-AUC | 0.9993 ± 0.0000 |
| HitRate@1 | 0.9949 ± 0.0001 |
| Recall@1 | 0.9949 ± 0.0001 |
| NDCG@1 | 0.9949 ± 0.0001 |
| HitRate@5 | 0.9970 ± 0.0001 |
| Recall@5 | 0.9970 ± 0.0001 |
| NDCG@5 | 0.9960 ± 0.0001 |
| HitRate@10 | 0.9977 ± 0.0001 |
| Recall@10 | 0.9977 ± 0.0001 |
| NDCG@10 | 0.9962 ± 0.0001 |
| HitRate@20 | 0.9984 ± 0.0001 |
| Recall@20 | 0.9984 ± 0.0001 |
| NDCG@20 | 0.9964 ± 0.0000 |
| MRR | 0.9959 ± 0.0001 |

### Test results

| Metric | Mean ± Std |
|---|---:|
| ROC-AUC | 0.9992 ± 0.0000 |
| HitRate@1 | 0.9942 ± 0.0002 |
| Recall@1 | 0.9942 ± 0.0002 |
| NDCG@1 | 0.9942 ± 0.0002 |
| HitRate@5 | 0.9965 ± 0.0001 |
| Recall@5 | 0.9965 ± 0.0001 |
| NDCG@5 | 0.9954 ± 0.0001 |
| HitRate@10 | 0.9976 ± 0.0001 |
| Recall@10 | 0.9976 ± 0.0001 |
| NDCG@10 | 0.9958 ± 0.0000 |
| HitRate@20 | 0.9984 ± 0.0001 |
| Recall@20 | 0.9984 ± 0.0001 |
| NDCG@20 | 0.9960 ± 0.0000 |
| MRR | 0.9953 ± 0.0001 |

<details>
<summary>Show multi-seed plot — network model</summary>

#### Multi-seed learning curves — network model

<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/8f4ec3ee-0938-4bbf-a56b-7f4d05c30ebc" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/b702b1f7-491d-45a6-9c26-df5a2a0019b0" />
  
</details>

</details>


<details>
<summary>Comparison of approach</summary>

### Comparison of approach

The XGBoost experiments are now split into two stages.

### Stage 1: `train_xgb_baseline.py` / `train_xgb_network.py`
This stage is used for:
- hyperparameter search
- single-seed training
- selecting the best final configuration

### Stage 2: `train_xgb_baseline_multiseed.py` / `train_xgb_network_multiseed.py`
This stage is used for:
- final evaluation
- repeated training on multiple seeds
- reporting mean ± std

-------------------------------------

## Same elements in both variants

Both Baseline and Network XGBoost models use:
- the same model family
- the same preprocessing logic
- the same evaluation procedure
- the same ranking metrics
- the same final selected hyperparameters

-------------------------------------

## Main difference between Baseline and Network

The difference is in the input representation.

### Baseline model
Uses the baseline tabular feature set.

### Network model
Uses the extended feature set with:
- `friend_count`
- `game_emb_0 ... game_emb_31`

So the training procedure is the same, but the Network model has access to richer information.

-------------------------------------

## Final evaluation protocol

The final reported XGBoost results come from the multi-seed scripts, not from the single-seed search scripts.

This means the final comparison is based on:
- the same final hyperparameters
- the same evaluation procedure
- multiple seeds
- averaged results with standard deviation

</details>


<details>
<summary>Comparison of final multi-seed results</summary>

### Comparison of final multi-seed results

The table below compares the final **test** results of the two XGBoost variants.

| Metric | XGB baseline model | XGB network model |
|---|---:|---:|
| ROC-AUC | 0.9682 ± 0.0002 | 0.9992 ± 0.0000 |
| HitRate@1 | 0.7768 ± 0.0004 | 0.9942 ± 0.0002 |
| Recall@1 | 0.7768 ± 0.0004 | 0.9942 ± 0.0002 |
| NDCG@1 | 0.7768 ± 0.0004 | 0.9942 ± 0.0002 |
| HitRate@5 | 0.8630 ± 0.0021 | 0.9965 ± 0.0001 |
| Recall@5 | 0.8630 ± 0.0021 | 0.9965 ± 0.0001 |
| NDCG@5 | 0.8228 ± 0.0011 | 0.9954 ± 0.0001 |
| HitRate@10 | 0.8992 ± 0.0016 | 0.9976 ± 0.0001 |
| Recall@10 | 0.8992 ± 0.0016 | 0.9976 ± 0.0001 |
| NDCG@10 | 0.8345 ± 0.0009 | 0.9958 ± 0.0000 |
| HitRate@20 | 0.9382 ± 0.0013 | 0.9984 ± 0.0001 |
| Recall@20 | 0.9382 ± 0.0013 | 0.9984 ± 0.0001 |
| NDCG@20 | 0.8444 ± 0.0008 | 0.9960 ± 0.0000 |
| MRR | 0.8187 ± 0.0006 | 0.9953 ± 0.0001 |

-------------------------------------

## Key observations

The final multi-seed results show a very large difference between the two XGBoost variants.

Compared with the baseline model, the network model is substantially stronger across all reported metrics.

The largest gains are visible near the top of the ranking:
- `HitRate@1` increases from `0.7768` to `0.9942`
- `NDCG@10` increases from `0.8345` to `0.9958`
- `MRR` increases from `0.8187` to `0.9953`

This suggests that the network-enriched feature set helps XGBoost place relevant games almost immediately at the top of the recommendation list.

The standard deviations are also very low in both variants, especially in the network model, which suggests that the XGBoost training procedure is stable across seeds.

Overall, the Network XGBoost model clearly outperforms the baseline version, indicating that social/network-derived features and embedding-based signals provide much stronger information for the recommendation task than the baseline metadata features alone.

</details>
