<details>
<summary>Data preparation for Neural Network models</summary>

### Data preparation for Neural Network models

Neural Network models do not train directly on raw CSV files.  
Before training, the data is transformed into a cached graph-based representation and grouped tensors.

This preprocessing pipeline prepares all files needed later by:
- `train_NN.py`
- `train_NN_multiseed.py`

-------------------------------------
  
### Overview

The preprocessing consists of three scripts:

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

### `train_NN.py` and `train_NN_multiseed.py` use:
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
<summary>Neural Network model — hyperparameter search</summary>

### Neural Network model — hyperparameter search

`train_NN.py no_net`  
`train_NN.py with_net`

This script performs the original Neural Network training procedure and hyperparameter search.

Its role is to:
- train the model on one seed
- compare hyperparameter configurations
- select the best final setup

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
- `val_filtered_df.parquet`
- `test_df.parquet`
- `cat_vocabs.json`
- `meta.json`

-------------------------------------

## What the script does

The script:
- loads cached user and game feature tensors
- builds a neural recommendation model
- trains the model for 20 epochs
- evaluates validation ROC-AUC during training
- compares several hyperparameter combinations
- selects the best configuration
- saves the best model and its results

-------------------------------------

## Model structure

The model contains:
- user encoder
- game encoder
- MLP scoring head

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

### Final scorer
The user and game representations are concatenated and passed through an MLP to produce one final score.

-------------------------------------

## Hyperparameter search space

The script searches over:
- hidden channels: `64`, `128`, `256`
- number of layers: `2`, `3`, `4`
- learning rate: `1e-3`, `5e-4`

### Best configuration selected

For both dataset variants, the best final configuration was:

- `hidden_channels = 256`
- `num_layers = 4`
- `learning_rate = 0.0005`

-------------------------------------

## Training setup

- loss: ranking-based neural loss
- optimizer: `Adam`
- weight decay: `1e-5`
- scheduler: `ReduceLROnPlateau`
- epochs: `20`
- sampled groups per epoch: `200000`
- seed: `42`

The best configuration is selected using:
- **average validation ROC-AUC across epochs**

-------------------------------------

## Outputs

### For `no_net`
- `nn_bpr_no_net_best.pt`
- `nn_bpr_no_net_metrics.json`
- `nn_bpr_no_net_roc.png`

### For `with_net`
- `nn_bpr_with_net_best.pt`
- `nn_bpr_with_net_metrics.json`
- `nn_bpr_with_net_roc.png`

-------------------------------------

## Single-seed plots

<img width="800" height="500" alt="nn_no_net_roc" src="https://github.com/user-attachments/assets/91f353fc-5ff6-4e60-8074-3db226e54761" />
<img width="800" height="500" alt="nn_with_net_roc" src="https://github.com/user-attachments/assets/ed9f16a5-9bd2-47b1-9abb-803b02ef84bf" />

The plots produced by `train_NN.py` come from a **single training run** (`seed = 42`).

They are useful for:
- showing the training dynamics
- showing how the model improves over epochs
- illustrating the selected configuration

They do **not** show variance across seeds.

-------------------------------------

## Single-seed results

These runs were used mainly to:
- perform hyperparameter search
- identify the best final configuration

<details> 
<summary>Show results for Neural Network - baseline model</summary> 

### Neural Network baseline model:
  
- "mode": "no_net"
- "seed": 42
  
**Best configuration:**
- hidden_channels = 256
- num_layers = 4
- learning_rate = 0.0005
- loss = bpr
  
**Model selection metric:**
- best average validation ROC-AUC = 0.9100

<details> 
<summary>Show validation results</summary>
    
#### Validation results:
  
| Metric | Value |
|---|---:|
| Best validation ROC-AUC | 0.9100 |
| Evaluated users | 28211 |
| HitRate@1 | 0.1830 |
| Recall@1 | 0.1830 |
| NDCG@1 | 0.1830 |
| HitRate@5 | 0.4865 |
| Recall@5 | 0.4865 |
| NDCG@5 | 0.3365 |
| HitRate@10 | 0.6832 |
| Recall@10 | 0.6832 |
| NDCG@10 | 0.4000 |
| HitRate@20 | 0.8763 |
| Recall@20 | 0.8763 |
| NDCG@20 | 0.4491 |
| MRR | 0.3314 |

</details> 
  
<details> 
<summary>Show test results</summary>
    
#### Test results:
  
| Metric | Value |
|---|---:|
| Evaluated users | 28211 |
| HitRate@1 | 0.1913 |
| Recall@1 | 0.1913 |
| NDCG@1 | 0.1913 |
| HitRate@5 | 0.4952 |
| Recall@5 | 0.4952 |
| NDCG@5 | 0.3459 |
| HitRate@10 | 0.6909 |
| Recall@10 | 0.6909 |
| NDCG@10 | 0.4090 |
| HitRate@20 | 0.8785 |
| Recall@20 | 0.8785 |
| NDCG@20 | 0.4567 |
| MRR | 0.3402 |
  
</details>
</details>

<details> 
<summary>Show results for Neural Network - network model</summary> 

### Neural Network  — network model:
  
- "mode": "with_net"
- "seed": 42
  
**Best configuration:**
- hidden_channels = 256
- num_layers = 4
- learning_rate = 0.0005
- loss = bpr
  
**Model selection metric:**
- best average validation ROC-AUC = 0.9128

<details> 
<summary>Show validation results</summary>
    
#### Validation results:
  
| Metric | Value |
|---|---:|
| Best validation ROC-AUC | 0.9128 |
| Evaluated users | 28211 |
| HitRate@1 | 0.1841 |
| Recall@1 | 0.1841 |
| NDCG@1 | 0.1841 |
| HitRate@5 | 0.4917 |
| Recall@5 | 0.4917 |
| NDCG@5 | 0.3405 |
| HitRate@10 | 0.6885 |
| Recall@10 | 0.6885 |
| NDCG@10 | 0.4040 |
| HitRate@20 | 0.8804 |
| Recall@20 | 0.8804 |
| NDCG@20 | 0.4528 |
| MRR | 0.3346 |

</details> 
  
<details> 
<summary>Show test results</summary>
    
#### Test results:
  
| Metric | Value |
|---|---:|
| Evaluated users | 28211 |
| HitRate@1 | 0.1952 |
| Recall@1 | 0.1952 |
| NDCG@1 | 0.1952 |
| HitRate@5 | 0.4990 |
| Recall@5 | 0.4990 |
| NDCG@5 | 0.3498 |
| HitRate@10 | 0.6974 |
| Recall@10 | 0.6974 |
| NDCG@10 | 0.4139 |
| HitRate@20 | 0.8821 |
| Recall@20 | 0.8821 |
| NDCG@20 | 0.4608 |
| MRR | 0.3443 |

</details>

Final robust evaluation is reported separately in the multi-seed section below.

</details>
</details>

<details>
<summary>Neural Network model — multi-seed final evaluation</summary>

### Neural Network model — multi-seed final evaluation

`train_NN_multiseed.py no_net`  
`train_NN_multiseed.py with_net`

This script performs the **final evaluation** of the Neural Network model using multiple random seeds.

It uses the same:
- architecture
- input cache
- training setup
- best hyperparameters selected earlier by `train_NN.py`

The only difference is that the model is now trained multiple times to estimate:
- mean performance
- standard deviation

-------------------------------------

## Why this script was added

A single neural run may depend on:
- random initialization
- random negative sampling
- stochastic batch order

Because of this, one run can be slightly lucky or unlucky.

The multi-seed version was added to make the final results:
- more stable
- more reliable
- easier to compare fairly

-------------------------------------

## Relation to `train_NN.py`

The workflow is:

1. `train_NN.py`
   - hyperparameter search
   - single-seed training
   - selection of the best configuration

2. `train_NN_multiseed.py`
   - final evaluation
   - same best configuration
   - multiple seeds
   - aggregated metrics

So the multi-seed script does **not** repeat the hyperparameter search.

It only evaluates the already selected final model more robustly.

-------------------------------------

## Fixed hyperparameters used

For both dataset variants, the multi-seed script uses:

- `hidden_channels = 256`
- `num_layers = 4`
- `learning_rate = 0.0005`

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
- `nn_no_net_metrics.json`
- `nn_no_net_learning_curve.png`
- per-seed model checkpoints

### For `with_net` network model:
- `nn_with_net_metrics.json`
- `nn_with_net_learning_curve.png`
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
- **standard deviation across seeds**

So these plots are more informative than the single-seed curves from `train_NN.py`.

</details>


<details>
<summary>Final multi-seed results</summary>

### Final multi-seed results

The tables below report the final neural results from `train_NN_multiseed.py`.

All values are reported as:

- **mean ± std**

across seeds:
- `42`
- `0`
- `1`

-------------------------------------

## Neural Network — no_net

### Validation results

| Metric | Mean ± Std |
|---|---:|
| HitRate@1 | 0.1848 ± 0.0005 |
| Recall@1 | 0.1848 ± 0.0005 |
| NDCG@1 | 0.1848 ± 0.0005 |
| HitRate@5 | 0.4871 ± 0.0017 |
| Recall@5 | 0.4871 ± 0.0017 |
| NDCG@5 | 0.3382 ± 0.0005 |
| HitRate@10 | 0.6859 ± 0.0036 |
| Recall@10 | 0.6859 ± 0.0036 |
| NDCG@10 | 0.4023 ± 0.0011 |
| HitRate@20 | 0.8767 ± 0.0010 |
| Recall@20 | 0.8767 ± 0.0010 |
| NDCG@20 | 0.4508 ± 0.0005 |
| MRR | 0.3334 ± 0.0003 |

### Test results

| Metric | Mean ± Std |
|---|---:|
| HitRate@1 | 0.1935 ± 0.0013 |
| Recall@1 | 0.1935 ± 0.0013 |
| NDCG@1 | 0.1935 ± 0.0013 |
| HitRate@5 | 0.4991 ± 0.0013 |
| Recall@5 | 0.4991 ± 0.0013 |
| NDCG@5 | 0.3488 ± 0.0013 |
| HitRate@10 | 0.6948 ± 0.0022 |
| Recall@10 | 0.6948 ± 0.0022 |
| NDCG@10 | 0.4119 ± 0.0016 |
| HitRate@20 | 0.8790 ± 0.0023 |
| Recall@20 | 0.8790 ± 0.0023 |
| NDCG@20 | 0.4587 ± 0.0016 |
| MRR | 0.3425 ± 0.0013 |

<details>
<summary>Show multi-seed plot — baseline model:</summary>

#### Multi-seed learning curve (`no_net`)

<img width="1200" height="1200" alt="nn_no_net_learning_curve" src="https://github.com/user-attachments/assets/d2ab8bc4-272e-4304-b109-34713293f3f6" />


</details>

-------------------------------------

## Neural Network — with_net

### Validation results

| Metric | Mean ± Std |
|---|---:|
| HitRate@1 | 0.1826 ± 0.0020 |
| Recall@1 | 0.1826 ± 0.0020 |
| NDCG@1 | 0.1826 ± 0.0020 |
| HitRate@5 | 0.4904 ± 0.0051 |
| Recall@5 | 0.4904 ± 0.0051 |
| NDCG@5 | 0.3385 ± 0.0033 |
| HitRate@10 | 0.6886 ± 0.0034 |
| Recall@10 | 0.6886 ± 0.0034 |
| NDCG@10 | 0.4026 ± 0.0026 |
| HitRate@20 | 0.8801 ± 0.0018 |
| Recall@20 | 0.8801 ± 0.0018 |
| NDCG@20 | 0.4512 ± 0.0023 |
| MRR | 0.3327 ± 0.0024 |

### Test results

| Metric | Mean ± Std |
|---|---:|
| HitRate@1 | 0.1917 ± 0.0020 |
| Recall@1 | 0.1917 ± 0.0020 |
| NDCG@1 | 0.1917 ± 0.0020 |
| HitRate@5 | 0.4999 ± 0.0033 |
| Recall@5 | 0.4999 ± 0.0033 |
| NDCG@5 | 0.3483 ± 0.0018 |
| HitRate@10 | 0.6976 ± 0.0042 |
| Recall@10 | 0.6976 ± 0.0042 |
| NDCG@10 | 0.4122 ± 0.0021 |
| HitRate@20 | 0.8811 ± 0.0014 |
| Recall@20 | 0.8811 ± 0.0014 |
| NDCG@20 | 0.4588 ± 0.0015 |
| MRR | 0.3419 ± 0.0017 |

<details>
<summary>Show multi-seed plot — network model</summary>

#### Multi-seed learning curve (`with_net`)

<img width="1200" height="1200" alt="nn_with_net_learning_curve" src="https://github.com/user-attachments/assets/5d07b598-b193-44d7-b837-1a5ba99ed179" />

</details>

</details>


<details>
<summary>Comparison of approach</summary>

### Comparison of approach

The neural experiments are now split into two stages:

### Stage 1: `train_NN.py`
This stage is used for:
- hyperparameter search
- single-seed training
- selecting the best final configuration

### Stage 2: `train_NN_multiseed.py`
This stage is used for:
- final evaluation
- repeated training on multiple seeds
- reporting mean ± std

-------------------------------------

## Same elements in both variants

Both **Baseline model** `no_net` and **Network model** `with_net` use:
- the same model structure
- the same training logic
- the same grouped interactions
- the same number of epochs
- the same selected hyperparameters

-------------------------------------

## Difference between **Baseline model** `no_net` and **Network model** `with_net`

The difference is in the input representation.

### **Baseline model** `no_net`
Uses the baseline cache without extra network-derived information.

### **Network model** `with_net`
Uses the enriched cache with additional network-based features.

So the architecture is the same, but the feature space is richer in the `with_net` variant.

-------------------------------------

## Final evaluation protocol

The final reported neural results come from the multi-seed script, not from the single-seed search script.

This means the final comparison is based on:
- the same final hyperparameters
- the same evaluation procedure
- multiple seeds
- averaged results with standard deviation

</details>


<details>
<summary>Comparison of final multi-seed results</summary>

### Comparison of final multi-seed results

The table below compares the final **test** results of the two neural variants.

| Metric | NN baseline model (`no_net`) | NN network model (`with_net`) |
|---|---:|---:|
| HitRate@1 | 0.1935 ± 0.0013 | 0.1917 ± 0.0020 |
| Recall@1 | 0.1935 ± 0.0013 | 0.1917 ± 0.0020 |
| NDCG@1 | 0.1935 ± 0.0013 | 0.1917 ± 0.0020 |
| HitRate@5 | 0.4991 ± 0.0013 | 0.4999 ± 0.0033 |
| Recall@5 | 0.4991 ± 0.0013 | 0.4999 ± 0.0033 |
| NDCG@5 | 0.3488 ± 0.0013 | 0.3483 ± 0.0018 |
| HitRate@10 | 0.6948 ± 0.0022 | 0.6976 ± 0.0042 |
| Recall@10 | 0.6948 ± 0.0022 | 0.6976 ± 0.0042 |
| NDCG@10 | 0.4119 ± 0.0016 | 0.4122 ± 0.0021 |
| HitRate@20 | 0.8790 ± 0.0023 | 0.8811 ± 0.0014 |
| Recall@20 | 0.8790 ± 0.0023 | 0.8811 ± 0.0014 |
| NDCG@20 | 0.4587 ± 0.0016 | 0.4588 ± 0.0015 |
| MRR | 0.3425 ± 0.0013 | 0.3419 ± 0.0017 |

-------------------------------------

## Key observations

The multi-seed results show that both neural variants achieve very similar performance.

Compared with the baseline version, the network variant is only slightly better on some ranking metrics:
- `HitRate@10`
- `Recall@10`
- `NDCG@10`
- `HitRate@20`
- `Recall@20`
- `NDCG@20`

However, the improvements are very small.

At the same time:
- the baseline version is slightly better at `HitRate@1`, `Recall@1`, `NDCG@1`
- the baseline version is also slightly better in `MRR`

So unlike the earlier single-seed comparison, the final multi-seed comparison shows that the difference between `no_net` and `with_net` is very limited.

The standard deviations are also low in both variants, which suggests that the neural training procedure is relatively stable across seeds.

</details>


</details>
