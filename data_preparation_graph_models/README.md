### Data preparation for Neural Network models

Neural Network models do not operate directly on raw CSV files.  
Instead, they use a **precomputed graph cache**, built in several sequential steps.

This pipeline transforms raw interaction data (`train.csv`, `val.csv`, `test.csv` (baseline and network)) into a format optimized for:
- tensor-based training  
- GPU processing  
- ranking loss (BPR / sampled softmax)  

-------------------------------------

### Overview of the pipeline

The preprocessing consists of three steps:

1. `01_build_graph_cache_baseline.py` / `01_build_graph_cache_network.py`    
2. `02_add_cat_encodings.py`    
3. `03_build_grouped_tensors.py`    
  
Pipeline:
CSV files  
↓  
Graph cache (nodes + edges)  
↓  
Categorical embedding tensors  
↓  
Grouped interaction tensors  
↓  
Neural Network training  

-------------------------------------

### STEPS IN ORDER:
  
<details>
<summary>STEP 1: 01_build_graph_cache_baseline.py/01_build_graph_cache_network.py </summary>

## STEP 1: Graph cache construction

### SCRIPT: `01_build_graph_cache_baseline.py`

*(Baseline version — no network features)*

-------------------------------------

### SCRIPT: `01_build_graph_cache_network.py`

*(Network version — includes friend_count and embeddings)*

-------------------------------------

#### Input:

- `train.csv`
- `val.csv`
- `test.csv`
- `friends.csv`  (from data sraping)
  
<details>
<summary>Show friends.csv</summary>
    
| user_steamid      | friend_steamid    |
|------------------|--------------------|
| 76561198064675174 | 76561197972380369 |
| 76561198064675174 | 76561198109425210 |
| 76561198109425210 | 76561198064675174 |
| 76561198109425210 | 76561198281198045 |
| 76561198109425210 | 76561198362520139 |
  
</details>
  
-------------------------------------

#### Target:

- `owned`  
*Binary interaction label (1 = user owns game)*

-------------------------------------

#### What the script does:

- creates mappings:
  - `user2idx`
  - `game2idx`
- builds a **heterogeneous graph** (`torch_geometric.data.HeteroData`)

Graph structure:
- nodes:
  - users
  - games
- edges:
  - `user → game` (interactions)
  - `game → user` (reverse edges)
  - `user → user` (friend connections)

-------------------------------------

#### Features used

User features:
- numeric features (playtime, counts, etc.)
- categorical: `country`

Game features:
- numeric features  
- categorical:
  - `genres`
  - `developer`
  - `publisher`
  - `platforms`

**Network version adds:**
- `friend_count`
- `game_emb_0 ... game_emb_31`

-------------------------------------

#### Preprocessing

Numeric:
- median imputation  
- standard scaling  

Categorical:
- missing → `"MISSING"`
- `OneHotEncoder`

-------------------------------------

#### Outputs:

- `graph.pt` — full graph object
- `user2idx.pt`
- `game2idx.pt`
- `train_edge_label_index.pt`
- `train_edge_label.pt`
- `val_edge_label_index.pt`
- `val_edge_label.pt`
- `val_filtered_df.parquet`
- `test_df.parquet`

</details>

<details>
<summary>STEP 2: 02_add_cat_encodings.py</summary>

## STEP 2: Categorical embedding encoding

### SCRIPT: `02_add_cat_encodings.py`

-------------------------------------

#### Input:

- `train.csv`
- existing cache:
  - `graph.pt`
  - `game2idx.pt`

-------------------------------------

#### What the script does:

- builds vocabularies for categorical game features:
  - `genres`
  - `developer`
  - `publisher`
  - `platforms`

- encodes them into **integer index tensors**
- converts multi-value fields into padded sequences
- attaches them to graph:
data["game"].genres_idx  
data["game"].developer_idx  
...

-------------------------------------

#### Important:

- this step **does NOT rebuild the graph**
- it only **extends the existing cache**

-------------------------------------

#### Outputs:

- `game_genres_idx.pt`
- `game_developer_idx.pt`
- `game_publisher_idx.pt`
- `game_platforms_idx.pt`
- updated `graph.pt`
- `cat_vocabs.json`
- `meta.json`

</details>

<details>
<summary>STEP 2: 03_build_grouped_tensors.py</summary>
  
## STEP 3: Grouped interaction tensors

### SCRIPT: `03_build_grouped_tensors.py`

-------------------------------------

#### Input:

- `train.csv`
- `user2idx.pt`
- `game2idx.pt`

-------------------------------------

#### What the script does:

- converts interactions into indexed tensors
- builds grouped training samples for ranking loss

Each training example:  
1 positive + 10 negative samples  
Label structure:    
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]    
  
-------------------------------------
  
#### Why this is needed:
  
Neural models use **BPR loss**, which compares:
- positive interaction  
- vs sampled negative interactions  
  
-------------------------------------
  
#### Outputs:
  
- `grouped_train_edge_label_index.pt`
- `grouped_train_edge_label.pt`
  
*Saved to both:*
- baseline cache
- network cache

</details>
  
-------------------------------------
  
## Dataset variants

Two cache versions are created:
  
### Baseline (`no_net`)
- no `friend_count`
- no `game_emb_*`
- simpler feature space
  
### Network (`with_net`)  
- includes:  
  - `friend_count`
  - `game_emb_0 ... game_emb_31`
- richer representation
  
-------------------------------------
  
## Summary
  
Unlike classical ML models:  
  
| Approach | Input |
|--------|------|
| Logistic Regression / RF / XGB | CSV |
| Neural Networks | Graph cache |
  
Neural models require:
- indexed nodes    
- tensor features  
- graph structure  
- grouped ranking samples  
  
This pipeline builds all of that **once**, enabling efficient training later.  
  
</details>
