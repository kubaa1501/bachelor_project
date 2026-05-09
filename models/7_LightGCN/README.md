<details>
<summary>LightGCN model - hyperparameter search</summary>

### LightGCN model — hyperparameter search

`train_lightGCN.py`

This script performs the original LightGCN training procedure and hyperparameter search.

Its role is to:
- train the model on one seed
- compare hyperparameter configurations
- select the best final setup

-------------------------------------

## Input
- `train.csv`
- `val.csv`
- `test.csv`

LightGCN does **not** use baseline or network feature variants.

It uses only:
- user identifiers
- game identifiers
- interaction labels

-------------------------------------

## What the script does

The script:
- loads the full training, validation, and test splits
- keeps only the columns needed for graph-based recommendation
- builds user and game index mappings
- constructs a bipartite user–game interaction graph
- trains a LightGCN model using BPR loss
- compares several hyperparameter combinations
- selects the best configuration using validation ranking quality
- evaluates the selected model on the test split
- creates learning curve experiments for the selected configuration

-------------------------------------

## Features used

LightGCN does **not** use tabular metadata features.
  
*Unlike all other models we trained, it does not use any numerical or categorical features.*
*The model uses only collaborative interaction information.*

#### Columns used:

- `steamid`
- `appid`
- `owned`

The identifier columns are used to build the graph:
- `steamid` becomes a user node
- `appid` becomes a game node

The target column:
- `owned`

is used to determine positive and negative interactions.

-------------------------------------

## Graph construction

The model builds a bipartite graph with:
- user nodes
- game nodes
- positive user–game edges

Only rows where:

- `owned = 1`

are used as graph edges.

Rows where:

- `owned = 0`

are not added to the graph.

They are used only for negative sampling during BPR training.

-------------------------------------

## Model

The model is: **LightGCN**

The model learns:
- user embeddings
- game embeddings

It then propagates these embeddings through the normalized user–game graph.

The final user and game representations are created by averaging embeddings from:
- the initial embedding layer
- the propagated graph layers

The score for a user–game pair is computed using:
- **dot product** between the user embedding and game embedding

-------------------------------------

## Training objective

The model is trained using:

- **Bayesian Personalized Ranking loss** also known as **BPR loss**

The goal is to make the model assign:
- higher scores to positive user–game pairs
- lower scores to sampled negative user–game pairs

For each positive interaction, the script samples negative games from that user's available negative examples.

-------------------------------------

## Negative sampling

The training setup uses:

- `NEG_PER_POS = 10`

This means that for each positive interaction, the model samples 10 negative games.

Negative samples are taken from:
- rows with `owned = 0`

Sampling is done:
- per mini-batch
- with replacement

-------------------------------------

## Hyperparameter search

The script tests 10 configurations:

| Trial | Hidden channels | Learning rate | Number of layers |
|---|---:|---:|---:|
| 1 | 64 | 0.0003 | 1 |
| 2 | 64 | 0.001 | 1 |
| 3 | 128 | 0.0003 | 1 |
| 4 | 128 | 0.001 | 1 |
| 5 | 256 | 0.0003 | 1 |
| 6 | 256 | 0.001 | 1 |
| 7 | 128 | 0.0003 | 2 |
| 8 | 128 | 0.001 | 2 |
| 9 | 256 | 0.0003 | 2 |
| 10 | 256 | 0.001 | 2 |

-------------------------------------

## Fixed training setup

- `NUM_EPOCHS = 30`
- `MIN_EPOCHS = 5`
- `EARLY_STOPPING_PATIENCE = 5`
- `WEIGHT_DECAY = 1e-6`
- `BPR_REG = 1e-6`
- `POS_BATCH_SIZE = 8192`
- `NEG_PER_POS = 10`


-------------------------------------

## Model selection

The best configuration is selected using:

- **validation NDCG@10**

-------------------------------------

## Learning curve analysis

After selecting the best validation configuration, the script trains LightGCN on increasing fractions of the positive training pairs:

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

To keep computation manageable, learning curves can be limited to:

- `LC_MAX_POS = 1000000`

The script saves:
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`

-------------------------------------

## Outputs

The script saves:

- `val_trials.csv`
- `val_trials_partial.csv`
- `val_scores.csv.gz`
- `test_scores.csv.gz`
- `val_per_user_metrics.csv`
- `test_per_user_metrics.csv`
- `best_model_state.pt`
- `results.json`
- `train_val_roc_curve.png`
- `learning_curve.csv`
- `learning_curve_roc_auc.png`
- `learning_curve_ranking.png`

-------------------------------------

<details>
<summary>Show single-seed plots</summary>

## Single-seed plots
  
### Training vs validation ROC-AUC

<img width="1600" height="1000" alt="train_val_roc_curve" src="https://github.com/user-attachments/assets/24f39261-54aa-4c76-8f5a-23ce1ae06a35" />

### Learning curve — ROC-AUC

<img width="1600" height="1000" alt="learning_curve_roc_auc" src="https://github.com/user-attachments/assets/9c5755a2-e74f-42d7-a160-f84e87a7c33f" />

### Learning curve — ranking

<img width="1600" height="1000" alt="learning_curve_ranking" src="https://github.com/user-attachments/assets/53853aa1-7f40-46fc-94ab-af5c072cde04" />

These plots come from a **single training run** (`seed = 42`).

They are useful for:
- showing how LightGCN behaves during training
- illustrating the selected configuration
- documenting the original hyperparameter-search experiment

They do **not** show variance across seeds.

</details>

-------------------------------------

## Single-seed results

This run was used mainly to:
- perform hyperparameter search
- identify the best final configuration

<details>
<summary>Show results for LightGCN</summary>

### LightGCN

- `"model_type": "lightgcn_bpr_small_grid"`
- `"dataset_type": "with_genre_groups"`
- `"seed": 42`
- `"num_users": 31021`
- `"num_games": 20918`
- `"num_train_positive_edges": 3954054`
- `"usable_positive_pairs_for_bpr": 3954054`
- `"usable_users_for_bpr": 31021`

**Best validation parameters:**
- `hidden_channels = 256`
- `lr = 0.001`
- `num_layers = 1`

<details>
<summary>Show validation results</summary>

#### Validation results

| Metric | Value |
|---|---:|
| ROC-AUC | 0.9278 |
| Evaluated users | 28211 |
| HitRate@1 | 0.2687 |
| Recall@1 | 0.2687 |
| NDCG@1 | 0.2687 |
| HitRate@5 | 0.6169 |
| Recall@5 | 0.6169 |
| NDCG@5 | 0.4481 |
| HitRate@10 | 0.7938 |
| Recall@10 | 0.7938 |
| NDCG@10 | 0.5055 |
| HitRate@20 | 0.9299 |
| Recall@20 | 0.9299 |
| NDCG@20 | 0.5402 |
| MRR | 0.4284 |

</details>

<details>
<summary>Show test results</summary>

#### Test results

| Metric | Value |
|---|---:|
| ROC-AUC | 0.9297 |
| Evaluated users | 28211 |
| HitRate@1 | 0.2798 |
| Recall@1 | 0.2798 |
| NDCG@1 | 0.2798 |
| HitRate@5 | 0.6278 |
| Recall@5 | 0.6278 |
| NDCG@5 | 0.4587 |
| HitRate@10 | 0.7994 |
| Recall@10 | 0.7994 |
| NDCG@10 | 0.5144 |
| HitRate@20 | 0.9306 |
| Recall@20 | 0.9306 |
| NDCG@20 | 0.5479 |
| MRR | 0.4379 |

</details>

</details>

</details>


<details>
<summary>LightGCN model - multi-seed final evaluation</summary>

### LightGCN model — multi-seed final evaluation

`train_lightGCN_multiseed.py`

This script performs the **final evaluation** of the LightGCN model using multiple random seeds.

It uses the same:
- data splits
- graph construction
- model architecture
- BPR training objective
- best hyperparameters selected earlier

The only difference is that the model is trained multiple times on diffrent seeds to estimate:
- mean performance
- standard deviation

-------------------------------------

## Why this script was added

A single LightGCN run may depend on:
- random initialization of embeddings
- mini-batch ordering
- negative sampling
- random seed

Because of this, one run can look slightly better or slightly worse than another.

The multi-seed version was added to make the final results:
- more stable
- more reliable
- easier to compare fairly

-------------------------------------

## Relation to `train_lightGCN.py`

The workflow is:

1. `train_lightGCN.py`
- hyperparameter search
- single-seed training
- selection of the best configuration

2. `train_lightGCN_multiseed.py`
- final evaluation
- same best configuration
- multiple seeds
- aggregated metrics

So the multi-seed script does **not** repeat the hyperparameter search.

*It only evaluates the already selected final LightGCN model more robustly.*

-------------------------------------

## Fixed hyperparameters used

The multi-seed script uses:

- `hidden_channels = 256`
- `lr = 0.001`
- `num_layers = 1`

-------------------------------------

## Multi-seed setup

The final model is trained with:

- `seeds = [0, 1, 42]`

For each seed, the script:
- trains the model independently
- saves the fitted model state
- evaluates validation metrics
- evaluates test metrics
- saves validation and test predictions
- saves per-user ranking metrics
- creates training and learning curve plots

Then the results are aggregated across seeds using:
- mean
- standard deviation

-------------------------------------

## Multi-seed learning curves

The multi-seed script also builds learning curves for the final configuration.

It uses the same fractions as the single-seed version:

- 5%
- 10%
- 20%
- 40%
- 70%
- 100%

For each fraction and each seed, it measures:
- training ROC-AUC
- validation ROC-AUC
- validation NDCG@10
- validation Recall@10

The script saves learning curve files inside each seed folder.

-------------------------------------

## Outputs

For each seed, the script saves:

- `seed_0/best_model_state.pt`
- `seed_1/best_model_state.pt`
- `seed_42/best_model_state.pt`

- `seed_0/val_scores.csv.gz`
- `seed_1/val_scores.csv.gz`
- `seed_42/val_scores.csv.gz`

- `seed_0/test_scores.csv.gz`
- `seed_1/test_scores.csv.gz`
- `seed_42/test_scores.csv.gz`

- `seed_0/val_per_user_metrics.csv`
- `seed_1/val_per_user_metrics.csv`
- `seed_42/val_per_user_metrics.csv`

- `seed_0/test_per_user_metrics.csv`
- `seed_1/test_per_user_metrics.csv`
- `seed_42/test_per_user_metrics.csv`

- `seed_0/training_history.csv`
- `seed_1/training_history.csv`
- `seed_42/training_history.csv`

- `seed_0/results.json`
- `seed_1/results.json`
- `seed_42/results.json`

The script also saves aggregated files:

- `summary_per_seed.csv`
- `summary_mean_std.json`
- `results_all_seeds.json`

</details>


<details>
<summary>Final multi-seed results</summary>

### Final multi-seed results

The tables below report the final LightGCN results from the multi-seed script.

All values are reported as:

- **mean ± std**

across seeds:

- `0`
- `1`
- `42`

-------------------------------------

## LightGCN model

### Validation results

| Metric | Mean ± Std |
|---|---:|
| ROC-AUC | 0.9278 ± 0.0001 |
| HitRate@1 | 0.2678 ± 0.0008 |
| Recall@1 | 0.2678 ± 0.0008 |
| NDCG@1 | 0.2678 ± 0.0008 |
| HitRate@5 | 0.6158 ± 0.0002 |
| Recall@5 | 0.6158 ± 0.0002 |
| NDCG@5 | 0.4474 ± 0.0005 |
| HitRate@10 | 0.7934 ± 0.0004 |
| Recall@10 | 0.7934 ± 0.0004 |
| NDCG@10 | 0.5051 ± 0.0006 |
| HitRate@20 | 0.9305 ± 0.0003 |
| Recall@20 | 0.9305 ± 0.0003 |
| NDCG@20 | 0.5400 ± 0.0005 |
| MRR | 0.4280 ± 0.0006 |

### Test results

| Metric | Mean ± Std |
|---|---:|
| ROC-AUC | 0.9296 ± 0.0001 |
| HitRate@1 | 0.2806 ± 0.0002 |
| Recall@1 | 0.2806 ± 0.0002 |
| NDCG@1 | 0.2806 ± 0.0002 |
| HitRate@5 | 0.6270 ± 0.0007 |
| Recall@5 | 0.6270 ± 0.0007 |
| NDCG@5 | 0.4588 ± 0.0004 |
| HitRate@10 | 0.7996 ± 0.0007 |
| Recall@10 | 0.7996 ± 0.0007 |
| NDCG@10 | 0.5148 ± 0.0004 |
| HitRate@20 | 0.9300 ± 0.0007 |
| Recall@20 | 0.9300 ± 0.0007 |
| NDCG@20 | 0.5481 ± 0.0002 |
| MRR | 0.4384 ± 0.0003 |

-------------------------------------

<details>
<summary>Show per-seed validation results</summary>

### Per-seed validation results

| Seed | ROC-AUC | HitRate@1 | HitRate@5 | HitRate@10 | HitRate@20 | NDCG@10 | MRR |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.9278 | 0.2685 | 0.6160 | 0.7938 | 0.9305 | 0.5057 | 0.4287 |
| 1 | 0.9277 | 0.2679 | 0.6157 | 0.7930 | 0.9302 | 0.5048 | 0.4279 |
| 42 | 0.9277 | 0.2670 | 0.6157 | 0.7934 | 0.9308 | 0.5047 | 0.4275 |

</details>

<details>
<summary>Show per-seed test results</summary>

### Per-seed test results

| Seed | ROC-AUC | HitRate@1 | HitRate@5 | HitRate@10 | HitRate@20 | NDCG@10 | MRR |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.9297 | 0.2804 | 0.6274 | 0.7998 | 0.9296 | 0.5152 | 0.4388 |
| 1 | 0.9295 | 0.2807 | 0.6274 | 0.8002 | 0.9297 | 0.5148 | 0.4382 |
| 42 | 0.9297 | 0.2807 | 0.6262 | 0.7988 | 0.9308 | 0.5144 | 0.4382 |

</details>

</details>


<details>
<summary>Comparison of approach</summary>

### Comparison of approach

The LightGCN experiments are split into two stages.

### Stage 1: `train_lightGCN.py`

This stage is used for:
- hyperparameter search
- single-seed training
- selecting the best final configuration

The script tests different values of:
- embedding size
- learning rate
- number of graph propagation layers

The best configuration is selected using:
- validation NDCG@10

### Stage 2: `train_lightGCN_multiseed.py`

This stage is used for:
- final evaluation
- repeated training on multiple seeds
- reporting mean ± standard deviation

The multi-seed script uses the best hyperparameters found in Stage 1.

It does **not** repeat hyperparameter search.

-------------------------------------

## Why there is no baseline/network split

For all other models, there were two dataset variants:
- baseline
- network

That distinction does not apply to LightGCN.

LightGCN does not take engineered features as input.

It does not use:
- baseline metadata features
- network features
- `friend_count`
- `game_emb_0 ... game_emb_31`

Instead, LightGCN learns directly from the user–game interaction graph.

So there is only one LightGCN model variant.

</details>


<details>
<summary>Comparison of final results</summary>

### Comparison of final results

The table below compares the single-seed search result with the final multi-seed test result.

The single-seed result is from:

- `train_lightGCN.py`
- `seed = 42`

The final result is from:

- `train_lightGCN_multiseed.py`
- `seeds = [0, 1, 42]`

-------------------------------------

## Test results comparison

| Metric | Single-seed LightGCN | Final multi-seed LightGCN |
|---|---:|---:|
| ROC-AUC | 0.9297 | 0.9296 ± 0.0001 |
| HitRate@1 | 0.2798 | 0.2806 ± 0.0002 |
| Recall@1 | 0.2798 | 0.2806 ± 0.0002 |
| NDCG@1 | 0.2798 | 0.2806 ± 0.0002 |
| HitRate@5 | 0.6278 | 0.6270 ± 0.0007 |
| Recall@5 | 0.6278 | 0.6270 ± 0.0007 |
| NDCG@5 | 0.4587 | 0.4588 ± 0.0004 |
| HitRate@10 | 0.7994 | 0.7996 ± 0.0007 |
| Recall@10 | 0.7994 | 0.7996 ± 0.0007 |
| NDCG@10 | 0.5144 | 0.5148 ± 0.0004 |
| HitRate@20 | 0.9306 | 0.9300 ± 0.0007 |
| Recall@20 | 0.9306 | 0.9300 ± 0.0007 |
| NDCG@20 | 0.5479 | 0.5481 ± 0.0002 |
| MRR | 0.4379 | 0.4384 ± 0.0003 |

-------------------------------------

## Key observations

The single-seed and multi-seed results are very close.

This suggests that the selected LightGCN configuration is stable across random seeds.

The standard deviations are very small across all reported metrics.

</details>
