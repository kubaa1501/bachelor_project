<details> 
<summary>Random Forest model — hyperparameter search</summary>

### Random Forest model — hyperparameter search

`train_rf_baseline.py`  
`train_rf_network.py`

These scripts perform the original Random Forest training procedure and hyperparameter search.

Their role is to:
- train the model on one seed
- compare hyperparameter configurations
- select the best final setup

-------------------------------------

## Input
- `train.csv`
- `val.csv`
- `test.csv`

*use baseline dataset for `train_rf_baseline.py` and network dataset for `train_rf_network.py`*
  
-------------------------------------

## What the scripts do

The scripts:
- load the full training, validation, and test splits
- build a full sklearn pipeline
- preprocess numeric and categorical features
- convert sparse transformed features to dense format
- train a Random Forest classifier
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

After preprocessing, the transformed matrix is converted from sparse to dense format using `FunctionTransformer`, because `RandomForestClassifier` in sklearn expects dense input.

Unlike Logistic Regression, Random Forest does **not** require feature scaling, so no `StandardScaler` is used. 
  
-------------------------------------

## Model

The classifier is: **RandomForestClassifier**

Configuration:
- `bootstrap=True`
- `class_weight="balanced_subsample"`
- `random_state=42`
- `n_jobs=8`

The hyperparameter search tests two configurations:

- `n_estimators=80`, `max_depth=20`, `min_samples_split=20`, `min_samples_leaf=10`, `max_features="sqrt"`
- `n_estimators=120`, `max_depth=30`, `min_samples_split=20`, `min_samples_leaf=10`, `max_features="sqrt"`

The best model is selected using:
- **validation NDCG@10**

So even though the underlying model is a classifier, model selection is based on ranking quality. 
  
-------------------------------------
  
## Learning curve analysis

After selecting the best validation configuration, the scripts train the model on increasing fractions of the training set:
- 10%
- 30%
- 60%
- 100%

For each fraction, they measure:
- training ROC-AUC
- validation ROC-AUC
- validation ranking metrics
- training time

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

## Single-seed plots

### Baseline model
  
<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/c4f35043-55cc-487b-916e-263321cad15f" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/c552c1a6-a3bf-4f33-9565-9f195991d6f4" />
  
### Network model
  
<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/0ed5866b-4d32-4905-aa18-2b2b9a92348c" />
<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/ed08b6fe-e9dd-4117-a5d5-64f7a8b5584b" />
  
These plots come from a **single training run** (`seed = 42`).
  
They are useful for:
- showing how the model behaves as training data grows
- illustrating the selected configuration
- documenting the original hyperparameter-search experiment
  
They do **not** show variance across seeds.
  
-------------------------------------

## Single-seed results

These runs were used mainly to:
- perform hyperparameter search
- identify the best final configuration

<details> 
<summary>Show results for Random Forest - baseline model</summary>

### Random Forest - baseline model

- `"model_type": "rf"`
- `"dataset_type": "baseline"`
- `"seed": 42`
- `"train_rows": 43494594`
- `"val_rows": 2849311`
- `"test_rows": 2849311`
- `"rf_njobs": 8`
- `"ohe_max_categories": 100`
- `"ohe_min_frequency": 50`
- `"learning_curve_max_rows": 300000`

**Best validation parameters:**
- `n_estimators = 120`
- `max_depth = 30`
- `min_samples_split = 20`
- `min_samples_leaf = 10`
- `max_features = sqrt`

<details> 
<summary>Show validation results</summary>

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

</details>

<details> 
<summary>Show results for Random Forest - network model</summary>

### Random Forest - network model

- `"model_type": "rf"`
- `"dataset_type": "network"`
- `"seed": 42`
- `"train_rows": 43494594`
- `"val_rows": 2849311`
- `"test_rows": 2849311`
- `"rf_njobs": 8`
- `"ohe_max_categories": 100`
- `"ohe_min_frequency": 50`
- `"learning_curve_max_rows": 300000`

**Best validation parameters:**
- `n_estimators = 120`
- `max_depth = 30`
- `min_samples_split = 20`
- `min_samples_leaf = 10`
- `max_features = sqrt`

<details> 
<summary>Show validation results</summary>

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

*Final evaluation is reported separately in the multi-seed section below.*

</details>

</details>


<details>
<summary>Random Forest model — multi-seed final evaluation</summary>

### Random Forest model — multi-seed final evaluation

`train_rf_baseline_multiseed.py`  
`train_rf_network_multiseed.py`

These scripts perform the **final evaluation** of the Random Forest model using multiple random seeds.

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

A single tree-based run may still depend on:
- bootstrap sampling
- randomness inside tree construction
- the selected random seed

Because of this, one run can look slightly better or slightly worse than another.

The multi-seed version was added to make the final results:
- more stable
- more reliable
- easier to compare fairly

-------------------------------------

## Relation to `train_rf_baseline.py` and `train_rf_network.py`

The workflow is:

1. `train_rf_baseline.py` / `train_rf_network.py`
   - hyperparameter search
   - single-seed training
   - selection of the best configuration

2. `train_rf_baseline_multiseed.py` / `train_rf_network_multiseed.py`
   - final evaluation
   - same best configuration
   - multiple seeds
   - aggregated metrics

So the multi-seed scripts do **not** repeat the hyperparameter search.

*They only evaluate the already selected final model more robustly.*

-------------------------------------

## Fixed hyperparameters used

For both dataset variants, the multi-seed scripts use:

- `n_estimators = 120`
- `max_depth = 30`
- `min_samples_split = 20`
- `min_samples_leaf = 10`
- `max_features = sqrt`

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
- 10%
- 30%
- 60%
- 100%

For each fraction and each seed, they measure:
- training ROC-AUC
- validation ROC-AUC
- validation NDCG@10
- validation Recall@10

They save:
- `learning_curve_per_seed.csv`
- `learning_curve_aggregated.csv`
- `learning_curve_roc_auc_multiseed.png`
- `learning_curve_ranking_multiseed.png`

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
- `learning_curve_aggregated.csv`
- `learning_curve_roc_auc_multiseed.png`
- `learning_curve_ranking_multiseed.png`
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
- `learning_curve_aggregated.csv`
- `learning_curve_roc_auc_multiseed.png`
- `learning_curve_ranking_multiseed.png`
- `results.json`

*you can see results.json for all in `results folder`*
  
</details>


<details>
<summary>Final multi-seed results</summary>

### Final multi-seed results

The tables below report the final Random Forest results from the multi-seed scripts.

All values are reported as:

- **mean ± std**

across seeds:
- `42`
- `0`
- `1`

-------------------------------------

## Random Forest — baseline model

### Validation results

| Metric | Mean ± Std |
|---|---:|
| ROC-AUC | 0.9492 ± 0.0002 |
| HitRate@1 | 0.6204 ± 0.0042 |
| Recall@1 | 0.6204 ± 0.0042 |
| NDCG@1 | 0.6204 ± 0.0042 |
| HitRate@5 | 0.7775 ± 0.0018 |
| Recall@5 | 0.7775 ± 0.0018 |
| NDCG@5 | 0.7056 ± 0.0016 |
| HitRate@10 | 0.8347 ± 0.0017 |
| Recall@10 | 0.8347 ± 0.0017 |
| NDCG@10 | 0.7240 ± 0.0015 |
| HitRate@20 | 0.8991 ± 0.0008 |
| Recall@20 | 0.8991 ± 0.0008 |
| NDCG@20 | 0.7403 ± 0.0015 |
| MRR | 0.6966 ± 0.0023 |

### Test results

| Metric | Mean ± Std |
|---|---:|
| ROC-AUC | 0.9490 ± 0.0001 |
| HitRate@1 | 0.6241 ± 0.0047 |
| Recall@1 | 0.6241 ± 0.0047 |
| NDCG@1 | 0.6241 ± 0.0047 |
| HitRate@5 | 0.7783 ± 0.0012 |
| Recall@5 | 0.7783 ± 0.0012 |
| NDCG@5 | 0.7076 ± 0.0019 |
| HitRate@10 | 0.8345 ± 0.0017 |
| Recall@10 | 0.8345 ± 0.0017 |
| NDCG@10 | 0.7258 ± 0.0019 |
| HitRate@20 | 0.8981 ± 0.0008 |
| Recall@20 | 0.8981 ± 0.0008 |
| NDCG@20 | 0.7418 ± 0.0018 |
| MRR | 0.6989 ± 0.0026 |

<details>
<summary>Show multi-seed plot — baseline model</summary>

#### Multi-seed learning curves — baseline model
  
<img width="1600" height="1000" alt="learning_curve_roc_auc_multiseed" src="https://github.com/user-attachments/assets/95d7e509-310d-4430-85c2-4cf7db8e6408" />
<img width="1600" height="1000" alt="learning_curve_ranking_multiseed" src="https://github.com/user-attachments/assets/8c90f2cd-2a10-49ca-9ac7-391ce4dac932" />
  
</details>

-------------------------------------

## Random Forest — network model

### Validation results

| Metric | Mean ± Std |
|---|---:|
| ROC-AUC | 0.9934 ± 0.0002 |
| HitRate@1 | 0.9587 ± 0.0010 |
| Recall@1 | 0.9587 ± 0.0010 |
| NDCG@1 | 0.9587 ± 0.0010 |
| HitRate@5 | 0.9723 ± 0.0007 |
| Recall@5 | 0.9723 ± 0.0007 |
| NDCG@5 | 0.9659 ± 0.0008 |
| HitRate@10 | 0.9788 ± 0.0006 |
| Recall@10 | 0.9788 ± 0.0006 |
| NDCG@10 | 0.9681 ± 0.0007 |
| HitRate@20 | 0.9869 ± 0.0003 |
| Recall@20 | 0.9869 ± 0.0003 |
| NDCG@20 | 0.9701 ± 0.0007 |
| MRR | 0.9656 ± 0.0008 |

### Test results

| Metric | Mean ± Std |
|---|---:|
| ROC-AUC | 0.9931 ± 0.0002 |
| HitRate@1 | 0.9577 ± 0.0008 |
| Recall@1 | 0.9577 ± 0.0008 |
| NDCG@1 | 0.9577 ± 0.0008 |
| HitRate@5 | 0.9719 ± 0.0008 |
| Recall@5 | 0.9719 ± 0.0008 |
| NDCG@5 | 0.9653 ± 0.0008 |
| HitRate@10 | 0.9781 ± 0.0006 |
| Recall@10 | 0.9781 ± 0.0006 |
| NDCG@10 | 0.9673 ± 0.0007 |
| HitRate@20 | 0.9857 ± 0.0006 |
| Recall@20 | 0.9857 ± 0.0006 |
| NDCG@20 | 0.9692 ± 0.0007 |
| MRR | 0.9649 ± 0.0007 |

<details>
<summary>Show multi-seed plot — network model</summary>

#### Multi-seed learning curves — network model
  
<img width="1600" height="1000" alt="learning_curve_roc_auc_multiseed" src="https://github.com/user-attachments/assets/b0c02a6f-7c94-4c2e-a908-ebd37f0b17f2" />
<img width="1600" height="1000" alt="learning_curve_ranking_multiseed" src="https://github.com/user-attachments/assets/a686d80e-693b-4675-802e-cfade1632d4c" />
  
</details>

</details>


<details>
<summary>Comparison of approach</summary>

### Comparison of approach

The Random Forest experiments are now split into two stages.

### Stage 1: `train_rf_baseline.py` / `train_rf_network.py`
This stage is used for:
- hyperparameter search
- single-seed training
- selecting the best final configuration

### Stage 2: `train_rf_baseline_multiseed.py` / `train_rf_network_multiseed.py`
This stage is used for:
- final evaluation
- repeated training on multiple seeds
- reporting mean ± std

-------------------------------------

## Same elements in both variants

Both Baseline and Network Random Forest models use:
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

The final reported Random Forest results come from the multi-seed scripts, not from the single-seed search scripts.

This means the final comparison is based on:
- the same final hyperparameters
- the same evaluation procedure
- multiple seeds
- averaged results with standard deviation

</details>


<details>
<summary>Comparison of final multi-seed results</summary>

### Comparison of final multi-seed results

The table below compares the final **test** results of the two Random Forest variants.

| Metric | RF baseline model | RF network model |
|---|---:|---:|
| ROC-AUC | 0.9490 ± 0.0001 | 0.9931 ± 0.0002 |
| HitRate@1 | 0.6241 ± 0.0047 | 0.9577 ± 0.0008 |
| Recall@1 | 0.6241 ± 0.0047 | 0.9577 ± 0.0008 |
| NDCG@1 | 0.6241 ± 0.0047 | 0.9577 ± 0.0008 |
| HitRate@5 | 0.7783 ± 0.0012 | 0.9719 ± 0.0008 |
| Recall@5 | 0.7783 ± 0.0012 | 0.9719 ± 0.0008 |
| NDCG@5 | 0.7076 ± 0.0019 | 0.9653 ± 0.0008 |
| HitRate@10 | 0.8345 ± 0.0017 | 0.9781 ± 0.0006 |
| Recall@10 | 0.8345 ± 0.0017 | 0.9781 ± 0.0006 |
| NDCG@10 | 0.7258 ± 0.0019 | 0.9673 ± 0.0007 |
| HitRate@20 | 0.8981 ± 0.0008 | 0.9857 ± 0.0006 |
| Recall@20 | 0.8981 ± 0.0008 | 0.9857 ± 0.0006 |
| NDCG@20 | 0.7418 ± 0.0018 | 0.9692 ± 0.0007 |
| MRR | 0.6989 ± 0.0026 | 0.9649 ± 0.0007 |

-------------------------------------

## Key observations

The final multi-seed results show a very large difference between the two Random Forest variants.

Compared with the baseline model, the network model is substantially stronger across all reported metrics.

The largest gains are visible near the top of the ranking:
- `HitRate@1` increases from `0.6241` to `0.9577`
- `NDCG@10` increases from `0.7258` to `0.9673`
- `MRR` increases from `0.6989` to `0.9649`

So unlike the neural experiments, where the difference between baseline and network was small, the Random Forest experiments show that the network-enriched feature set provides a **very strong improvement**.

The standard deviations are also low in both variants, which suggests that the Random Forest training procedure is stable across seeds.

</details>
