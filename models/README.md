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

### Results:

#### Random baseline:

#### Popularity baseline:
