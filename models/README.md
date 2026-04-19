<details>
<summary> Random & Popularity model </summary>
    
### MODEL: train_naive.py
It trains and evaluates two naive ranking baselines:  
  
- a popularity-based baseline
- a random baseline
    
-----------------------------------------------
  
Input:
- `train.csv`
- `val.csv`
- `test.csv`

*Here you can ther use baseline, or network datasets. The model uses only columns: steamid, appid, owned, user_count*
  
-----------------------------------------------
#### Popularity baseline
  
The popularity baseline assigns a score to each game based on its global popularity.  
  
Popularity is derived from the `user_count` feature and computed using **train data only**:  
  
- for each `appid`, the script aggregates `user_count` across training rows  
- this value is then used as the ranking score  
  
This baseline assumes that globally popular games should be ranked higher for every user. 
  
-----------------------------------------------
#### Random baseline

The random baseline assigns a random score to each candidate game.  
To reduce variance, the script evaluates the random baseline multiple times:  
- default: 100 runs  
- configurable using N_RANDOM_RUNS  
  
For each run:  
  
- random scores are generated
- ranking metrics are computed
  
The script then:  
  
- averages the metrics across all runs
- stores per-run results
- keeps the best random run according to MRR
    
----------------------------------------------
  
#### Evaluation metrics
  
Both naive baselines are evaluated as ranking models using:  
- HitRate@10
- Recall@10
- NDCG@10
- HitRate@20
- Recall@20
- NDCG@20
- MRR
    
Metrics are computed per user and then averaged across all evaluated users.  
  
----------------------------------------------
  
### Results:
  
-  "model_type": "naive",
-  "dataset_type": "baseline",
-  "seed": 42,
-  "train_rows": 43494594,
-  "val_rows": 2849311,
-  "test_rows": 2849311,
-  "n_random_runs": 100,

<details>
<summary>Show results for Random baseline:</summary>

#### Random baseline:


| Metric           | Value      |
|-----------------|-----------|
| Runs            | 100       |
| HitRate@10      | 0.0989    |
| Recall@10       | 0.0989    |
| NDCG@10         | 0.0449    |
| HitRate@20      | 0.1980    |
| Recall@20       | 0.1980    |
| NDCG@20         | 0.0697    |
| MRR             | 0.0514    |
  
    
</details>
<details>
<summary>Show results for Popularity baseline: </summary>

#### Popularity baseline:


| Metric           | Value      |
|-----------------|-----------|
| HitRate@10      | 0.5879    |
| Recall@10       | 0.5879    |
| NDCG@10         | 0.3383    |
| HitRate@20      | 0.8112    |
| Recall@20       | 0.8112    |
| NDCG@20         | 0.3947    |
| MRR             | 0.2841    |
  
</details>
</details>
