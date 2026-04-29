<details>
<summary>Data preparation for Neural Network models</summary>

### Data preparation for Neural Network models

Neural Network models do not train directly on raw CSV files.  
Before training, the data is transformed into a cached graph-based representation and grouped tensors.

This preprocessing pipeline prepares all files needed later by:
- `train_GraphSAGE.py`
- `train_GraphSAGE_multiseed.py`

-------------------------------------
  
### Overview

The preprocessing consists of three scripts:  
  
/data_preparation_graph_models/
  
1. `01_build_graph_cache_baseline.py` / `01_build_graph_cache_network.py`
2. `02_add_cat_encodings.py`
3. `03_build_grouped_tensors.py`

Pipeline:

`train.csv`, `val.csv`, `test.csv`, `friends.csv`  
↓  
graph cache  
↓  
categorical index tensors  
↓  
grouped training tensors  
↓  
Neural Network training

-------------------------------------

## STEP 1: Graph cache construction

### SCRIPTS:
- `01_build_graph_cache_baseline.py`
- `01_build_graph_cache_network.py`

These scripts create the main cached graph representation used later by the neural models.

### Input:
- `train.csv`
- `val.csv`
- `test.csv`
- `friends.csv`

<details>
<summary>Show friends.csv example</summary>

| user_steamid      | friend_steamid    |
|------------------|--------------------|
| 76561198064675174 | 76561197972380369 |
| 76561198064675174 | 76561198109425210 |
| 76561198109425210 | 76561198064675174 |
| 76561198109425210 | 76561198281198045 |
| 76561198109425210 | 76561198362520139 |

</details>

### Target:
- `owned`

### What these scripts do:
- create mappings:
  - `user2idx`
  - `game2idx`
- build a heterogeneous graph (`torch_geometric.data.HeteroData`)
- save graph-based tensors and validation/test data used later during training and evaluation

### Graph structure:
- nodes:
  - users
  - games
- edges:
  - user → game
  - game → user
  - user → user

### Features included

User features:
- numeric user features
- categorical `country`

Game features:
- numeric game features
- categorical:
  - `genres`
  - `developer`
  - `publisher`
  - `platforms`

### Additional network version features:
- `friend_count`
- `game_emb_0 ... game_emb_31`

### Outputs:
- **`graph.pt`**
- **`user2idx.pt`**
- **`game2idx.pt`**
- `train_edge_label_index.pt`
- `train_edge_label.pt`
- `val_edge_label_index.pt`
- `val_edge_label.pt`
- `val_filtered_df.parquet`
- `test_df.parquet`
    
-------------------------------------

## STEP 2: Categorical encoding for game metadata

### SCRIPT:
- `02_add_cat_encodings.py`

This script extends the cache with categorical index tensors for game metadata.

### Input:
- `train.csv`
- **`graph.pt`**
- **`game2idx.pt`**

### What this script does:
- builds vocabularies for:
  - `genres`
  - `developer`
  - `publisher`
  - `platforms`
- converts these fields into integer index tensors
- pads multi-value fields
- attaches them to `graph.pt`

### Outputs:
- updated `graph.pt`
- `cat_vocabs.json`
- `meta.json`
- categorical index tensors for game features

-------------------------------------


## STEP 3: Grouped interaction tensors

### SCRIPT:
- `03_build_grouped_tensors.py`

This script prepares grouped training examples for ranking-based neural training.

### Input:
- `train.csv`
- `user2idx.pt`
- `game2idx.pt`

### What this script does:
- converts user/game ids into index-based tensors
- groups training examples into:
  - 1 positive interaction
  - 10 negative interactions

Example label group:

`[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]`

### Outputs:
- `grouped_train_edge_label_index.pt`
- `grouped_train_edge_label.pt`

These files are saved to both cache variants:
- baseline cache
- network cache

-------------------------------------

## Cache variants

Two dataset versions are created:

### Baseline (`no_net`)
This cache does not include additional network-derived features.

### Network (`with_net`)
This cache additionally includes:
- `friend_count`
- `game_emb_0 ... game_emb_31`

-------------------------------------

## What the training scripts actually use as input

The neural training scripts use the outputs of the preprocessing pipeline, not raw CSV files.

### `train_GraphSAGE.py` and `train_GraphSAGE_multiseed.py` use:
- `graph.pt`
- `user2idx.pt`
- `game2idx.pt`
- `grouped_train_edge_label_index.pt`
- `grouped_train_edge_label.pt`
- `val_filtered_df.parquet`
- `test_df.parquet`
- `cat_vocabs.json`
- `meta.json`

So in practice, the model input is:

- graph cache from `01_build_graph_cache_*.py`
- categorical encoding outputs from `02_add_cat_encodings.py`
- grouped training tensors from `03_build_grouped_tensors.py`

-------------------------------------

## Summary

Unlike classical ML models:

| Approach | Input |
|--------|------|
| Logistic Regression / RF / XGB | CSV files |
| Neural Networks | cached graph + grouped tensors |

The preprocessing pipeline is needed only once, and its outputs are then reused by the neural training scripts.

</details>

<details>
<summary>GraphSAGE model - single-seed training</summary>

### GraphSAGE model — single-seed training

`train_GraphSAGE.py no_net`  
`train_GraphSAGE.py with_net`

This script performs GraphSAGE training using one random seed.

Its role is to:
- train the model using cached graph data
- evaluate validation ROC-AUC during training
- save the best checkpoint
- report validation and test ranking metrics

-------------------------------------

## Input

This script does **not** use raw CSV files directly.

It uses the outputs created earlier by:
- `01_build_graph_cache_baseline.py` / `01_build_graph_cache_network.py`
- `02_add_cat_encodings.py`
- `03_build_grouped_tensors.py`

### Input files:
- `graph.pt`
- `user2idx.pt`
- `game2idx.pt`
- `grouped_train_edge_label_index.pt`
- `grouped_train_edge_label.pt`
- `val_edge_label_index.pt`
- `val_edge_label.pt`
- `val_filtered_df.parquet`
- `test_df.parquet`
- `cat_vocabs.json`
- `meta.json`

-------------------------------------

## What the script does

The script:
- loads the cached heterogeneous graph
- loads grouped BPR training tensors
- builds a GraphSAGE link prediction model
- trains the model for 20 epochs
- evaluates validation ROC-AUC during training
- saves the best model checkpoint
- evaluates validation and test ranking metrics

-------------------------------------

## Model structure

The model contains:
- user feature projection
- game feature encoder
- heterogeneous GraphSAGE encoder
- MLP link decoder

### User encoder
User numeric features are projected using:
- linear layer
- ReLU

### Game encoder
Game representation is built from:
- numeric game features
- categorical embeddings for:
  - `genres`
  - `developer`
  - `publisher`
  - `platforms`

Categorical fields can contain multiple values.  
The model embeds these values and applies mean pooling over non-padding tokens.

### Graph encoder
The model uses GraphSAGE layers converted to a heterogeneous graph model with:

- `to_hetero`
- aggregation: `sum`

The graph contains:
- user nodes
- game nodes
- user-game edges
- user-user friendship edges

### Link decoder
For each candidate user-game pair:
- user embedding and game embedding are concatenated
- an MLP produces one relevance score

-------------------------------------

## Training setup

- loss: Bayesian Personalized Ranking loss (`BPR`)
- optimizer: `Adam`
- weight decay: `1e-5`
- scheduler: `ReduceLROnPlateau`
- epochs: `20`
- sampled groups per epoch: `200000`
- negatives per positive: `10`
- seed: `42`

The BPR group structure is:

`[positive, negative, negative, ..., negative]`

The training loader uses `shuffle=False` to preserve this group structure.

-------------------------------------

## Outputs

### For `no_net`
- `gsage_bpr_v2_no_net.pt`
- `gsage_bpr_v2_no_net.json`
- `gsage_bpr_v2_no_net_roc.png`

### For `with_net`
- `gsage_bpr_v2_with_net.pt`
- `gsage_bpr_v2_with_net.json`
- `gsage_bpr_v2_with_net_roc.png`

-------------------------------------
## Single-seed plots

<img width="800" height="500" alt="gsage_no_net_roc" src="https://github.com/user-attachments/assets/1fa5b714-8fce-493a-86d8-31a485322af8" />
<img width="800" height="500" alt="gsage_with_net_roc" src="https://github.com/user-attachments/assets/4c3e5e38-26c0-452d-a020-a108b95c055b" />
  
The plots produced by train_GraphSAGE.py come from a single training run (seed = 42).

They are useful for:
- showing the training dynamics
- showing how the model improves over epochs
- illustrating the selected configuration
  
They do not show variance across seeds.  
  
------------------------------------- 
  
## Single-seed results
  
These runs were used mainly to:  
- perform hyperparameter search
- identify the best final configuration
  
These runs use:  
- `seed = 42`
  
<details>
<summary>Show results for GraphSAGE - baseline model</summary>

### GraphSAGE baseline model

- mode: `no_net`
- hidden_channels: `128`
- num_layers: `2`
- learning_rate: `0.0005`
- loss: `bpr`

<details>
<summary>Show validation results</summary>

#### Validation results

| Metric | Value |
|---|---:|
| HitRate@1 | 0.1925 |
| Recall@1 | 0.1925 |
| NDCG@1 | 0.1925 |
| HitRate@5 | 0.5233 |
| Recall@5 | 0.5233 |
| NDCG@5 | 0.3609 |
| HitRate@10 | 0.7166 |
| Recall@10 | 0.7166 |
| NDCG@10 | 0.4235 |
| HitRate@20 | 0.8925 |
| Recall@20 | 0.8925 |
| NDCG@20 | 0.4683 |
| MRR | 0.3497 |
| Evaluated users | 28211 |

</details>

<details>
<summary>Show test results</summary>

#### Test results

| Metric | Value |
|---|---:|
| HitRate@1 | 0.2029 |
| Recall@1 | 0.2029 |
| NDCG@1 | 0.2029 |
| HitRate@5 | 0.5338 |
| Recall@5 | 0.5338 |
| NDCG@5 | 0.3717 |
| HitRate@10 | 0.7291 |
| Recall@10 | 0.7291 |
| NDCG@10 | 0.4349 |
| HitRate@20 | 0.8962 |
| Recall@20 | 0.8962 |
| NDCG@20 | 0.4773 |
| MRR | 0.3599 |
| Evaluated users | 28211 |

</details>
</details>


<details>
<summary>Show results for GraphSAGE — network model</summary>

### GraphSAGE network model

- mode: `with_net`
- hidden_channels: `128`
- num_layers: `2`
- learning_rate: `0.0005`
- loss: `bpr`

<details>
<summary>Show validation results</summary>

#### Validation results

| Metric | Value |
|---|---:|
| HitRate@1 | 0.2026 |
| Recall@1 | 0.2026 |
| NDCG@1 | 0.2026 |
| HitRate@5 | 0.5380 |
| Recall@5 | 0.5380 |
| NDCG@5 | 0.3738 |
| HitRate@10 | 0.7308 |
| Recall@10 | 0.7308 |
| NDCG@10 | 0.4363 |
| HitRate@20 | 0.8990 |
| Recall@20 | 0.8990 |
| NDCG@20 | 0.4791 |
| MRR | 0.3611 |
| Evaluated users | 28211 |

</details>

<details>
<summary>Show test results</summary>

#### Test results

| Metric | Value |
|---|---:|
| HitRate@1 | 0.2073 |
| Recall@1 | 0.2073 |
| NDCG@1 | 0.2073 |
| HitRate@5 | 0.5461 |
| Recall@5 | 0.5461 |
| NDCG@5 | 0.3810 |
| HitRate@10 | 0.7366 |
| Recall@10 | 0.7366 |
| NDCG@10 | 0.4427 |
| HitRate@20 | 0.9004 |
| Recall@20 | 0.9004 |
| NDCG@20 | 0.4844 |
| MRR | 0.3672 |
| Evaluated users | 28211 |

</details>
</details>

Final robust evaluation is reported separately in the multi-seed section below.

</details>

<details>
<summary>GraphSAGE model - multi-seed final evaluation</summary>

### GraphSAGE model - multi-seed final evaluation

`train_GraphSAGE_multiseed.py no_net`  
`train_GraphSAGE_multiseed.py with_net`

This script performs the **final evaluation** of the GraphSAGE model using multiple random seeds.

It uses the same:
- architecture
- input cache
- training setup
- fixed hyperparameters

The model is trained multiple times to estimate:
- mean performance
- standard deviation

-------------------------------------

## Why this script was added

A single GraphSAGE run may depend on:
- random initialization
- random group sampling
- stochastic training dynamics

Because of this, one run can be slightly lucky or unlucky.

The multi-seed version was added to make the final results:
- more stable
- more reliable
- easier to compare fairly

-------------------------------------

## Relation to `train_GraphSAGE.py`

The workflow is:

1. `train_GraphSAGE.py`
   - single-seed training
   - validation monitoring
   - checkpoint selection

2. `train_GraphSAGE_multiseed.py`
   - final evaluation
   - same final configuration
   - multiple seeds
   - aggregated metrics

-------------------------------------

## Fixed hyperparameters used

For both dataset variants, the multi-seed script uses:

- `hidden_channels = 128`
- `num_layers = 2`
- `learning_rate = 0.0005`
- `loss = bpr`

-------------------------------------

## Multi-seed setup

The final model is trained with:

- `seeds = [42, 0, 1]`

For each seed, the script:
- trains the model independently
- saves the best checkpoint for that seed
- evaluates validation metrics
- evaluates test metrics

Then it aggregates the results across seeds using:
- mean
- standard deviation

-------------------------------------

## Outputs

### For `no_net` baseline model:
- `gsage_no_net_metrics.json`
- `gsage_no_net_learning_curve.png`
- per-seed model checkpoints

### For `with_net` network model:
- `gsage_with_net_metrics.json`
- `gsage_with_net_learning_curve.png`
- per-seed model checkpoints

The metrics JSON files contain:
- aggregated validation metrics
- aggregated test metrics
- per-seed validation results
- per-seed test results
- train/validation metric history across epochs

-------------------------------------

## Multi-seed plots

The multi-seed plots show:
- mean training / validation ROC-AUC
- mean validation NDCG@10
- mean validation Recall@10

The shaded area represents:
- standard deviation across seeds
  
</details>


<details>
<summary>Final multi-seed results</summary>

### Final multi-seed results

The tables below report the final GraphSAGE results from `train_GraphSAGE_multiseed.py`.

All values are reported as:

- **mean ± std**

across seeds:
- `42`
- `0`
- `1`

-------------------------------------

## GraphSAGE - no_net (baseline model)

### Validation results

| Metric | Mean ± Std |
|---|---:|
| HitRate@1 | 0.1971 ± 0.0021 |
| Recall@1 | 0.1971 ± 0.0021 |
| NDCG@1 | 0.1971 ± 0.0021 |
| HitRate@5 | 0.5366 ± 0.0017 |
| Recall@5 | 0.5366 ± 0.0017 |
| NDCG@5 | 0.3702 ± 0.0020 |
| HitRate@10 | 0.7329 ± 0.0009 |
| Recall@10 | 0.7329 ± 0.0009 |
| NDCG@10 | 0.4338 ± 0.0017 |
| HitRate@20 | 0.9026 ± 0.0013 |
| Recall@20 | 0.9026 ± 0.0013 |
| NDCG@20 | 0.4770 ± 0.0018 |
| MRR | 0.3573 ± 0.0020 |

### Test results

| Metric | Mean ± Std |
|---|---:|
| HitRate@1 | 0.2066 ± 0.0018 |
| Recall@1 | 0.2066 ± 0.0018 |
| NDCG@1 | 0.2066 ± 0.0018 |
| HitRate@5 | 0.5471 ± 0.0027 |
| Recall@5 | 0.5471 ± 0.0027 |
| NDCG@5 | 0.3802 ± 0.0022 |
| HitRate@10 | 0.7408 ± 0.0020 |
| Recall@10 | 0.7408 ± 0.0020 |
| NDCG@10 | 0.4430 ± 0.0019 |
| HitRate@20 | 0.9050 ± 0.0016 |
| Recall@20 | 0.9050 ± 0.0016 |
| NDCG@20 | 0.4847 ± 0.0018 |
| MRR | 0.3663 ± 0.0018 |

<details>
<summary>Show multi-seed plot — baseline model:</summary>

#### Multi-seed learning curve (`no_net`)
  
<img width="1200" height="1200" alt="gsage_no_net_learning_curve(1)" src="https://github.com/user-attachments/assets/8d437889-19a7-4afd-9cdb-bb769ba10663" />
  
</details>

-------------------------------------

## GraphSAGE — with_net (network model)

### Validation results

| Metric | Mean ± Std |
|---|---:|
| HitRate@1 | 0.2017 ± 0.0033 |
| Recall@1 | 0.2017 ± 0.0033 |
| NDCG@1 | 0.2017 ± 0.0033 |
| HitRate@5 | 0.5424 ± 0.0018 |
| Recall@5 | 0.5424 ± 0.0018 |
| NDCG@5 | 0.3754 ± 0.0027 |
| HitRate@10 | 0.7375 ± 0.0021 |
| Recall@10 | 0.7375 ± 0.0021 |
| NDCG@10 | 0.4385 ± 0.0026 |
| HitRate@20 | 0.9049 ± 0.0004 |
| Recall@20 | 0.9049 ± 0.0004 |
| NDCG@20 | 0.4811 ± 0.0023 |
| MRR | 0.3618 ± 0.0028 |

### Test results

| Metric | Mean ± Std |
|---|---:|
| HitRate@1 | 0.2101 ± 0.0028 |
| Recall@1 | 0.2101 ± 0.0028 |
| NDCG@1 | 0.2101 ± 0.0028 |
| HitRate@5 | 0.5536 ± 0.0029 |
| Recall@5 | 0.5536 ± 0.0029 |
| NDCG@5 | 0.3857 ± 0.0030 |
| HitRate@10 | 0.7444 ± 0.0022 |
| Recall@10 | 0.7444 ± 0.0022 |
| NDCG@10 | 0.4475 ± 0.0028 |
| HitRate@20 | 0.9060 ± 0.0007 |
| Recall@20 | 0.9060 ± 0.0007 |
| NDCG@20 | 0.4887 ± 0.0024 |
| MRR | 0.3708 ± 0.0029 |


<details>
<summary>Show multi-seed plot — network model:</summary>

#### Multi-seed learning curve (`with_net`)
  
<img width="1200" height="1200" alt="gsage_with_net_learning_curve(1)" src="https://github.com/user-attachments/assets/97c4ef3a-b121-4d5d-b10d-7b817848785f" />
  
</details>
  
</details>


<details>
<summary>Comparison of approach</summary>

### Comparison of approach

The GraphSAGE experiments are split into two stages:

### Stage 1: `train_GraphSAGE.py`
This stage is used for:
- single-seed training
- validation monitoring
- saving the best checkpoint

### Stage 2: `train_GraphSAGE_multiseed.py`
This stage is used for:
- final evaluation
- repeated training on multiple seeds
- reporting mean ± std

-------------------------------------

## Same elements in both variants

Both **baseline model** `no_net` and **network model** `with_net` use:
- the same GraphSAGE architecture
- the same training logic
- the same grouped interactions
- the same number of epochs
- the same hyperparameters

-------------------------------------

## Difference between baseline model `no_net` and network model `with_net`

The difference is in the input representation.

### Baseline model `no_net`
Uses the baseline cache without extra network-derived information.

### Network model `with_net`
Uses the enriched cache with additional network-based features.

The architecture is the same, but the feature space is richer in the `with_net` variant.

-------------------------------------

## Final evaluation protocol

The final reported GraphSAGE results come from the multi-seed script.

This means the final comparison is based on:
- the same final hyperparameters
- the same evaluation procedure
- multiple seeds
- averaged results with standard deviation

</details>


<details>
<summary>Comparison of final multi-seed results</summary>

### Comparison of final multi-seed results

The table below compares the final **test** results of the two GraphSAGE variants.

| Metric | GraphSAGE baseline model (`no_net`) | GraphSAGE network model (`with_net`) |
|---|---:|---:|
| HitRate@1 | 0.2066 ± 0.0018 | 0.2101 ± 0.0028 |
| Recall@1 | 0.2066 ± 0.0018 | 0.2101 ± 0.0028 |
| NDCG@1 | 0.2066 ± 0.0018 | 0.2101 ± 0.0028 |
| HitRate@5 | 0.5471 ± 0.0027 | 0.5536 ± 0.0029 |
| Recall@5 | 0.5471 ± 0.0027 | 0.5536 ± 0.0029 |
| NDCG@5 | 0.3802 ± 0.0022 | 0.3857 ± 0.0030 |
| HitRate@10 | 0.7408 ± 0.0020 | 0.7444 ± 0.0022 |
| Recall@10 | 0.7408 ± 0.0020 | 0.7444 ± 0.0022 |
| NDCG@10 | 0.4430 ± 0.0019 | 0.4475 ± 0.0028 |
| HitRate@20 | 0.9050 ± 0.0016 | 0.9060 ± 0.0007 |
| Recall@20 | 0.9050 ± 0.0016 | 0.9060 ± 0.0007 |
| NDCG@20 | 0.4847 ± 0.0018 | 0.4887 ± 0.0024 |
| MRR | 0.3663 ± 0.0018 | 0.3708 ± 0.0029 |

-------------------------------------

## Key observations

The multi-seed results show that the network version is consistently slightly better than the baseline version.

The largest improvements appear in:
- HitRate@5
- NDCG@5
- MRR

However, the improvements are still modest.

This suggests that adding network-derived features helps GraphSAGE, but the effect is limited.

The standard deviations are low in both variants, which suggests that the training procedure is stable across seeds.

</details>
