<details>
<summary>STEP 1: Build raw LCC inputs for PCA pipeline </summary>

### CODE: `1_build_raw_lcc_inputs.py`

This script creates the raw graph and user-game matrix inputs used later by the distance algorithm.

The goal of this step is to:

- build a user-user friendship graph from Steam friendship data
- select the Largest Connected Component (LCC)
- keep only users from the LCC
- create a binary user × game matrix for those users

This prepares the raw network-based input files before relabelling.

-----------------------------------

Inputs:

- `friends.csv` ( from STEP 1: Crawl Steam users, friends and owned games, in folder `data_scraping/`)
- `user_games.csv` ( from STEP 1: Crawl Steam users, friends and owned games, in folder `data_scraping/`)

<details>
<summary>Show friends.csv</summary>
  
| user_steamid      | friend_steamid    |
|-------------------|-------------------|
| 76561198064675174 | 76561197972380369 |
| 76561198064675174 | 76561198109425210 |
| 76561198109425210 | 76561198064675174 |
| 76561198109425210 | 76561198281198045 |
  
</details>

<details>
<summary>Show user_games.csv</summary>
  
| steamid           | appid | playtime_minutes |
|-------------------|-------|------------------|
| 76561198064675174 | 400   | 367              |
| 76561198064675174 | 500   | 117              |
| 76561198064675174 | 550   | 0                |
| 76561198064675174 | 620   | 710              |
  
</details>

-----------------------------------

#### Friendship graph construction

The script reads `friends.csv`, using:

- `user_steamid`
- `friend_steamid`

Each row represents one friendship edge.

A NetworkX graph is created where:

- nodes = Steam users
- edges = friendships between users

-----------------------------------

#### Largest Connected Component filtering

The script extracts the Largest Connected Component from the friendship graph.

Only users belonging to this LCC are kept for the rest of the PCA/network embedding pipeline.

This ensures that the graph used by the distance algorithm is connected and that all user nodes belong to the same component.

-----------------------------------

#### User-game matrix construction

The script reads `user_games.csv`, using:

- `steamid`
- `appid`

Only rows where the user belongs to the LCC are kept.

Then it creates a binary user × game matrix:

- rows = Steam users from the LCC
- columns = game appids
- value = `1` if the user has the game
- value = `0` otherwise

-----------------------------------

Outputs:

- `user_edge_graph_steamid_LCC31021.pkl`
- `user_game_01_steam_users_appid_games.pkl`
- `old_to_new_node_id.csv`
- `lcc_steamids_31021.csv`

<details>
<summary>Show user_edge_graph_steamid_LCC31021.pkl</summary>

NetworkX user-user friendship graph after filtering to the Largest Connected Component.  
  
- type: networkx.Graph
- nodes: 31021
- edges: 40204
- node labels: steam_id

example nodes:  
  
| node              |
| ----------------- |
| 76561198064675174 |
| 76561198109425210 |
| 76561198281198045 |
| 76561197994839969 |
| 76561197972380369 |

example edges:

| user_steamid      | friend_steamid    |
| ----------------- | ----------------- |
| 76561198064675174 | 76561197972380369 |
| 76561198064675174 | 76561198109425210 |
| 76561198109425210 | 76561198281198045 |
| 76561198109425210 | 76561198362520139 |
| 76561198281198045 | 76561197994839969 |
  
</details>

<details>
<summary>Show user_game_01_steam_users_appid_games.pkl</summary>
    
MATRIX:  
- 31021 users (rows)  
- 20988 games (cols)   

|   steam_id\app_id |   10 |   20 |   30 |   40 |   50 |   60 |   70 |   80 |   100 |   130 |
|------------------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|------:|
| 76561198064675174 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198109425210 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198281198045 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561197994839969 |    1 |    0 |    1 |    1 |    0 |    1 |    1 |    1 |     1 |     0 |
| 76561197972380369 |    1 |    1 |    1 |    1 |    1 |    1 |    1 |    0 |     0 |     1 |
| 76561197992826872 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198362520139 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198859934865 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198011971157 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198004594504 |    0 |    1 |    0 |    0 |    1 |    0 |    1 |    0 |     0 |     1 |

</details>
  
<details>
<summary>Show INFO </summary>
    
**Before filtering:**
  
- Number of nodes (users): 99,924   
- Number of edges (from users to anyone): 8,039,785

**After LCC filtering:**

- Number of nodes (users): 31021  
- Number of edges (from users to anyone): 40204  
- directed: false

</details>
</details>
  
<details> 
<summary>STEP 2: Relabel raw LCC inputs</summary>
    
### CODE: `2_relabell_inputs.py`
  
This script relabels the raw SteamID-based graph and user-game matrix into the format expected by the distance algorithm.
The goal is to make sure that the same user has the same numeric ID in both:  

- the user-user graph
- the user-game matrix

-----------------------------------
  
Inputs:

- `user_edge_graph_steamid_LCC31021.pkl` (from previous code) 
- `user_game_01_steam_users_appid_games.pkl` (from previous code) 
- `old_to_new_node_id.csv` (from preavious code) 

<details>
<summary>Show user_edge_graph_steamid_LCC31021.pkl</summary>
  
example nodes:  
    
| node              |
| ----------------- |
| 76561198064675174 |
| 76561198109425210 |
| 76561198281198045 |
| 76561197994839969 |
| 76561197972380369 |
  
example edges:
  
| user_steamid      | friend_steamid    |
| ----------------- | ----------------- |
| 76561198064675174 | 76561197972380369 |
| 76561198064675174 | 76561198109425210 |
| 76561198109425210 | 76561198281198045 |
| 76561198109425210 | 76561198362520139 |
| 76561198281198045 | 76561197994839969 |
  
</details>
  
<details> 
<summary>Show user_game_01_steam_users_appid_games.pkl</summary>

|   steam_id\app_id |   10 |   20 |   30 |   40 |   50 |   60 |   70 |   80 |   100 |   130 |
|------------------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|------:|
| 76561198064675174 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198109425210 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198281198045 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561197994839969 |    1 |    0 |    1 |    1 |    0 |    1 |    1 |    1 |     1 |     0 |
| 76561197972380369 |    1 |    1 |    1 |    1 |    1 |    1 |    1 |    0 |     0 |     1 |
| 76561197992826872 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198362520139 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198859934865 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198011971157 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198004594504 |    0 |    1 |    0 |    0 |    1 |    0 |    1 |    0 |     0 |     1 |

</details>
  
<details>
<summary>Show old_to_new_node_id.csv</summary>

| old_node_id | new_node_id |
| ----------- | ----------- |
| 0           | 0           |
| 1           | 1           |
| 2           | 2           |
| 3           | 3           |
| ...         | ...         |
| 43605       | 31016       |
| 43606       | 31017       |
| 43608       | 31018       |
| 43612       | 31019       |
| 43613       | 31020       |
  
</details>
  
-----------------------------------
      
#### User relabelling
  
The script takes the user order from the user-game matrix and creates:
- `steam_id → new_node_id`
  
where `new_node_id` is a numeric ID from 0 to N-1.    
*The graph nodes are relabelled from SteamIDs to these numeric IDs.*  

-----------------------------------
  
#### Matrix relabelling

The user-game matrix rows are also relabelled from SteamIDs to numeric IDs.  
The game columns stay as appids at this stage.  
  
-----------------------------------
  
#### Game index mapping
  
The script also creates a game mapping:
- `matrix_index → game_id`
  
This is later used to connect PCA embeddings back to real Steam appids.  

----------------------------------- 
  
Outputs:

- `user_edge_graph_relabelled.pkl`
- `user_game_01_relabelled.pkl`
- `steamid_to_newnodeid_LCC31021.csv`
- `game_index_to_gameid_20988.csv`
  
<details>
<summary>Show user_edge_graph_relabelled.pkl</summary>
  
NetworkX user-user friendship graph after relabelling Steam IDs to numeric node IDs.  
    
- type: `networkx.Graph`
- nodes: `31021`
- edges: `40204`
- node labels: `new_node_id`
    
Example nodes:  
  
| node |
|------|
| 0    |
| 1    |
| 2    |
| 3    |
    
Example edges:  
  
| user_node_id | friend_node_id |
|--------------|----------------|
| 0            | 4              |
| 0            | 1              |
| 1            | 2              |
| 1            | 6              |
| 2            | 3              |
| 3            | 14             |
  
</details>
  
<details>
<summary>Show user_game_01_relabelled.pkl</summary>
  
- shape: `(31021, 20988)`
- rows: `new_node_id`
- columns: `appid`
- values: `0/1`
  
Example 10 × 10 slice:
  
| new_node_id | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 100 | 130 |
|-------------|----|----|----|----|----|----|----|----|-----|-----|
| 0           | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 1           | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 2           | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 3           | 1  | 0  | 1  | 1  | 0  | 1  | 1  | 1  | 1   | 0   |
| 4           | 1  | 1  | 1  | 1  | 1  | 1  | 1  | 0  | 0   | 1   |
| 5           | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 6           | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 7           | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 8           | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 9           | 0  | 1  | 0  | 0  | 1  | 0  | 1  | 0  | 0   | 1   |
  
</details>
  
<details> 
<summary>Show steamid_to_newnodeid_LCC31021.csv</summary>
  
Mapping from Steam user IDs to relabelled numeric node IDs.  
  
| steam_id          | old_node_id | new_node_id |
|-------------------|-------------|-------------|
| 76561198064675174 | 0           | 0           |
| 76561198109425210 | 1           | 1           |
| 76561198281198045 | 2           | 2           |
| 76561197994839969 | 3           | 3           |
|        ...        |    ...      |     ...     |
| 76561198176677994 | 43605       | 31016       |
| 76561199050442561 | 43606       | 31017       |
| 76561198066001235 | 43608       | 31018       |
| 76561198401936102 | 43612       | 31019       |
| 76561199186273436 | 43613       | 31020       |
  
</details>

<details>
<summary>Show game_index_to_gameid_20988.csv</summary>
  
Mapping from matrix column index to Steam game appid.
  
| matrix_index | game_id |
|--------------|---------|
| 0            | 10      |
| 1            | 20      |
| 2            | 30      |
| 3            | 40      |
  
</details>
</details>

<details> <summary>STEP 3: Create train-only relabelled user-game matrix</summary>

### CODE: `3_make_relabelled_trainonly.job`
  
This job creates a train-only version of the relabelled user-game matrix.  
The goal is to **remove validation and test positive interactions from the matrix before computing game-game distances**

*This prevents data leakage, because PCA embeddings should not be built using validation or test interactions.*
  
-----------------------------------

Inputs:  
- `user_game_01_relabelled.pkl` (from previous code)
- `validation_user_game_pairs.csv` (from STEP 1. Selecting positives for validation & training splits, in folder `preparing_datasets/`)
- `test_user_game_pairs.csv` (from STEP 1. Selecting positives for validation & training splits, in folder `preparing_datasets/`)
- `steamid_to_newnodeid_LCC31021.csv` (from previous code)
- `game_index_to_gameid_20988.csv` (from previous code)
  
<details>
<summary>Show validation_user_game_pairs.csv</summary>

Positive validation interactions (one per user).  
  
| steamid           | appid  |
|-------------------|--------|
| 76561197960266945 | 569860 |
| 76561197960269228 | 240    |
| 76561197960270968 | 50     |
| 76561197960274625 | 20900  |
  
</details>
  
<details>
<summary>Show test_user_game_pairs.csv</summary>

Positive test interactions (one per user).
  
| steamid           | appid  |
|-------------------|--------|
| 76561197960266945 | 569860 |
| 76561197960269228 | 240    |
| 76561197960270968 | 50     |
| 76561197960274625 | 20900  |
  
</details>

-----------------------------------

#### Mapping validation/test pairs
  
Validation and test files contain pairs as:  
- `steamid`
- `appid`
  
The relabelled matrix uses:  
- row index = `new_node_id`
- column index = `matrix_index`
  
Therefore, the script maps:  
- `steamid → new_node_id`
- `appid → matrix_index`
  
-----------------------------------

#### Masking holdout interactions
  
For every **validation/test pair** found in the relabelled matrix, the script sets:  
  
```python  
user_game_matrix[row, col] = 0
```
  
This **removes the interaction from the training matrix**.  

-----------------------------------

Output:  

- `user_game_01_relabelled_TRAINONLY.pkl`
  
<details>
<summary>Show user_game_01_relabelled_TRAINONLY.pkl</summary>
  
Matrix shape:  
  
- users (rows): 31021  
- games (columns): 20988  
  
Binary user–game interaction matrix:  
- `1` → user owns the game    
- `0` → user does not own the game    
  
| user_id \ appid | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 100 | 130 |
|-----------------|----|----|----|----|----|----|----|----|-----|-----|
| 0               | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 1               | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 2               | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 3               | 1  | 0  | 1  | 1  | 0  | 1  | 1  | 1  | 1   | 0   |
| 4               | 1  | 1  | 1  | 1  | 1  | 1  | 1  | 0  | 0   | 1   |
| 5               | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 6               | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 7               | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 8               | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0   | 0   |
| 9               | 0  | 1  | 0  | 0  | 1  | 0  | 1  | 0  | 0   | 1   |
  
</details>
</details>
<details>
<summary>STEP 4: Compute game-game distances using Michele algorithm</summary>
    
### CODE: `4_run_game_game_gpu_trainonly.job`
  
This job computes a game-game distance matrix using the relabelled user-user graph and the train-only user-game matrix.  
The goal is to calculate distances between games based on:  
   
- the friendship network structure between users
- the games owned by users

*In other words:    
two games are considered similar if they are owned by users who are close in the social graph.*
  
-----------------------------------
  
Inputs:  
- `user_edge_graph_relabelled.pkl` (from previous code)
- `user_game_01_relabelled_TRAINONLY.pkl` (from previous code)
- `node_vector_distance/` **(code with algorithm provided by supervisor)**

-----------------------------------

#### Attributed graph construction
  
The script builds an `AttrGraph` object (attribute graph):  
  
```python
T = nvd.AttrGraph(G, df)
```
Where:  
- `G` = user-user friendship graph (nodes = users, edges = friendships)
- `df` = user × game matrix (game ownership) 

Each game is treated as a vector over users:
```python
game = [0, 1, 0, 0, 1, ...]
```
  
Meaning:  
`1` → user owns the game  
`0` → user does not own the game   
  
*So each game vector has one value per user node.*
  
-----------------------------------

#### Distance computation
  
The script computes distances between all pairs of games:

```text
D = nvd.pairwise_generalized_euclidean(T)
```
    
This uses the generalized Euclidean distance:
    
```text
Δ(v₁, v₂ | G) = sqrt( (v₁ - v₂)ᵀ · L† · (v₁ - v₂) )
```
  
where:

- `v₁`, `v₂` = game vectors over users
- `G` = user-user friendship graph
- `L†` = Moore-Penrose pseudoinverse of the graph Laplacian
- `Δ(v₁, v₂ | G)` = distance between two games, taking the graph structure into account

In this project:

```text
v₁ = ownership vector for game 1 across users
v₂ = ownership vector for game 2 across users
G  = user-user friendship graph
```

Key idea:

- normal Euclidean distance compares game vectors directly
- generalized Euclidean distance compares them through the user friendship graph
- differences between socially close users matter less than differences between distant users

-----------------------------------
  
#### Output distance matrix

The output is a square game × game distance matrix:

```text
D[i, j] = distance between game i and game j
```
  
**Structure:**  
- rows = games
- columns = games
- diagonal = 0
- matrix is symmetric
- values = generalized Euclidean distances

-----------------------------------

Output:

- `game_game_dists_trainonly.pkl`

<details>
<summary>Show game_game_dists_trainonly.pkl</summary>
  
- shape: `(20988, 20988)`    
- type: `float32`    
- rows/columns: game indices    
  
Properties:  
- symmetric matrix    
- diagonal = `0` (distance to itself)    
- larger value = less similar games    
  
| game_i \ game_j | 0.00 | 54.78 | 51.14 | 51.06 | 55.10 |
|-----------------|------|-------|-------|-------|-------|
| **0**           | 0.00 | 54.78 | 51.14 | 51.06 | 55.10 |
| **1**           | 54.78 | 0.00 | 30.55 | 30.27 | 17.03 |
| **2**           | 51.14 | 30.55 | 0.00 | 14.00 | 32.05 |
| **3**           | 51.06 | 30.27 | 14.00 | 0.00 | 31.70 |
| **4**           | 55.10 | 17.03 | 32.05 | 31.70 | 0.00 |
  
</details>    
  
-----------------------------------
  
#### Leakage prevention
  
This step uses:  
  
- `user_game_01_relabelled_TRAINONLY.pkl`
not the full user-game matrix.  
    
*That means validation and test positive interactions were already removed before calculating game-game distances.*  
*This prevents the PCA embeddings from seeing validation/test interactions.*  
  
</details>
<details>
<summary>STEP 5: Convert game-game distances to CPU NumPy array</summary>
    
### CODE: `5_convert_gg_to_cpu_npy_gpu.job`

This job converts the game-game distance matrix into a CPU-based NumPy array.   
The goal is to make the distance matrix easier to load for PCA.    

-----------------------------------
  
Input:  
- `game_game_dists_trainonly.pkl` (from previous code) 
  
<details>
<summary>Show game_game_dists_trainonly.pkl</summary>
  
| game_i \ game_j | 0.00 | 54.78 | 51.14 | 51.06 | 55.10 |
|-----------------|------|-------|-------|-------|-------|
| **0**           | 0.00 | 54.78 | 51.14 | 51.06 | 55.10 |
| **1**           | 54.78 | 0.00 | 30.55 | 30.27 | 17.03 |
| **2**           | 51.14 | 30.55 | 0.00 | 14.00 | 32.05 |
| **3**           | 51.06 | 30.27 | 14.00 | 0.00 | 31.70 |
| **4**           | 55.10 | 17.03 | 32.05 | 31.70 | 0.00 |
  
</details>

-----------------------------------

#### Conversion strategy
  
The script loads the distance matrix with:
  
```text
torch.load(..., map_location="cpu")
```
  
*This is important because the matrix may have been saved as a CUDA tensor.*
Then it converts the object to a NumPy array and saves it as float32.  
  
-----------------------------------

Output:  
- `game_game_dists_trainonly_cpu.npy`
  
<details>
<summary>Show game_game_dists_trainonly_cpu.npy</summary>
  
| game_i \ game_j | 0     | 1     | 2     | 3     | 4     |
| --------------- | ----- | ----- | ----- | ----- | ----- |
| **0**           | 0.00  | 54.78 | 51.14 | 51.06 | 55.10 |
| **1**           | 54.78 | 0.00  | 30.55 | 30.27 | 17.03 |
| **2**           | 51.14 | 30.55 | 0.00  | 14.00 | 32.05 |
| **3**           | 51.06 | 30.27 | 14.00 | 0.00  | 31.70 |
| **4**           | 55.10 | 17.03 | 32.05 | 31.70 | 0.00  |
    
</details>
</details>
<details>
<summary>STEP 6: Run PCA on train-only game-game distance matrix</summary>
  
### CODE: `6_run_pca_trainonly_k32_to_new.py`
  
This script creates **32-dimensional PCA game embeddings** from the **train-only** game-game distance matrix.  
The goal is to compress the full game-game distance matrix into **lower-dimensional game embeddings** that can later be used as network features.

-----------------------------------

Inputs:  
- `game_game_dists_trainonly_cpu.npy` (from previous code) 
- `game_index_to_gameid_20988.csv` ( from previous code, STEP 2: Relabel raw LCC inputs)
<details>
<summary>Show game_game_dists_trainonly_cpu.npy</summary>
  
| game_i \ game_j | 0     | 1     | 2     | 3     | 4     |
| --------------- | ----- | ----- | ----- | ----- | ----- |
| **0**           | 0.00  | 54.78 | 51.14 | 51.06 | 55.10 |
| **1**           | 54.78 | 0.00  | 30.55 | 30.27 | 17.03 |
| **2**           | 51.14 | 30.55 | 0.00  | 14.00 | 32.05 |
| **3**           | 51.06 | 30.27 | 14.00 | 0.00  | 31.70 |
| **4**           | 55.10 | 17.03 | 32.05 | 31.70 | 0.00  |
  
</details>
<details>
<summary>Show game_index_to_gameid_20988.csv</summary>

| matrix_index | game_id |
| ------------ | ------: |
| 0            |      10 |
| 1            |      20 |
| 2            |      30 |
| 3            |      40 |
|     ...      |   ...   |
| 20983        | 4215730 |
| 20984        | 4217610 |
| 20985        | 4225940 |
| 20986        | 4301100 |
| 20987        | 4351050 |
  
</details>
  
-----------------------------------

#### Matrix preprocessing
  
The script loads the game-game distance matrix and performs several preprocessing steps:

- materializes the matrix as dense `float32`
- symmetrizes the matrix
- sets the diagonal to `0`
- checks for `NaN` values
- applies `log1p`
- **standardizes** the matrix using `StandardScaler`
  
*The log transform compresses very large distance values, while standardization makes PCA less dominated by columns with larger scale.*

-----------------------------------

#### PCA
  
The script runs PCA with:
- `K = 32`

This produces **32 embedding dimensions per game**:
- `game_emb_0`
- `game_emb_1`  
- ...  
- `game_emb_31`

It also computes cumulative explained variance and saves a plot.

-----------------------------------
  
#### AppID mapping
  
After PCA, each row has a `game_index`.  
  
The script uses `game_index_to_gameid_20988.csv` to add the real `Steam appid` to each embedding row.  

-----------------------------------

Outputs:  
- `game_pca_embeddings_k32_trainonly.csv` 
- `pca_cumulative_plot_k32_trainonly.png`
<details>
<summary>Show game_pca_embeddings_k32_trainonly.csv</summary>
  
| appid | idx | emb_0 | emb_1 | emb_2 | emb_3 | emb_4 | emb_5 | emb_6 | emb_7 | emb_8 | emb_9 | ... | emb_30 | emb_31 |
|------:|----:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|-----|-------:|-------:|
| 10    | 0   | 646.17 | 249.23 | 88.80 | 43.78 | -6.68 | 17.21 | 4.29 | 16.19 | 10.98 | 16.97 | ... | -1.51 | 0.70 |
| 20    | 1   | 547.07 | 167.50 | 39.86 | 11.05 | -5.75 | -3.78 | 1.24 | -3.49 | -0.73 | 10.96 | ... | 0.20 | -1.72 |
| 30    | 2   | 536.58 | 162.22 | 39.35 | 12.14 | -4.39 | -1.22 | -0.64 | -1.04 | 0.93 | 8.65 | ... | 1.06 | -3.90 |
| 40    | 3   | 532.99 | 159.84 | 38.29 | 11.57 | -4.20 | -1.44 | -1.01 | -1.27 | 0.95 | 8.41 | ... | 1.18 | -3.86 |
  
</details>
<details>
<summary>Show pca_cumulative_plot_k32_trainonly.png</summary>
    
<img width="1600" height="1000" alt="pca_cumulative_plot_k32_trainonly" src="https://github.com/user-attachments/assets/0d579761-1b0f-4890-899a-8dd2e390e828" />
  
</details>
  
-----------------------------------

### Final note: use of PCA embeddings as network features

The output file:

- `game_pca_embeddings_k32_trainonly.csv`

contains the final PCA-based game embeddings.  
  
These embeddings are later joined to the datasets by `appid`.  

Each game receives 32 network-based features:    
- `game_emb_0`
- `game_emb_1`
- ...
- `game_emb_31`
  
These features represent each game based on the game-game distance structure computed from:  
- the Steam friendship network
- train-only user-game ownership data
  
They are later used as additional **game-level network features** in the network-enriched datasets to train Network models.   
  
*Joining of those features are made in `preparing_datasets/` STEP 6: Enrich baseline dataset with additional network features to create network datasets*

</details>
