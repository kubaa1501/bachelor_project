### database:

  "random_seed": 42,  
  "n_users_requested": 2000,  
  "common_users_count": 28211,  
  "heldout_users_count": 2000,  
  "train_users_before": 31021,  
  "val_users_before": 28211,  
  "test_users_before": 28211,  
  "train_rows_before": 43494594,  
  "val_rows_before": 2849311,  
  "test_rows_before": 2849311,  
  "train_users_after": 29021,  
  "val_users_after": 2000,  
  "test_users_after": 2000,  
  "train_rows_after": 40443381,  
  "val_rows_after": 202000,  
  "test_rows_after": 202000,  
  "train_overlap_with_heldout": 0,  
  "val_equals_heldout": true,  
  "test_equals_heldout": true,  
  "val_equals_test": true  

-------------------------------------------------------------    
  
### xgb baseline SIM
  
  "test_roc_auc": 0.9667584362499999,  
  "n_users_evaluated": 2000,  
  "HitRate@1": 0.7745,  
  "Recall@1": 0.7745,  
  "NDCG@1": 0.7745,  
  "HitRate@5": 0.8575,  
  "Recall@5": 0.8575,  
  "NDCG@5": 0.8195664995750498,  
  "HitRate@10": 0.891,  
  "Recall@10": 0.891,  
  "NDCG@10": 0.8303920669838222,  
  "HitRate@20": 0.9325,  
  "Recall@20": 0.9325,  
  "NDCG@20": 0.8409538876976344,  
  "MRR": 0.8161863790621792  
    
### xgb network SIM  
  
 "test_roc_auc": 0.9991920975,  
  "n_users_evaluated": 2000,  
  "HitRate@1": 0.995,  
  "Recall@1": 0.995,  
  "NDCG@1": 0.995,  
  "HitRate@5": 0.996,  
  "Recall@5": 0.996,  
  "NDCG@5": 0.995508891280403,  
  "HitRate@10": 0.997,  
  "Recall@10": 0.997,  
  "NDCG@10": 0.9958536615406236,  
  "HitRate@20": 0.998,  
  "Recall@20": 0.998,  
  "NDCG@20": 0.9961282520906628,  
  "MRR": 0.9956616644366645  
  
## COMPARISON:
  
| Metric            | XGB Baseline | XGB Baseline SIM |         Δ |
| ----------------- | -----------: | ---------------: | --------: |
| test_roc_auc      |       0.9681 |           0.9668 | -0.001367 |
| HitRate@1         |       0.7763 |           0.7745 | -0.001793 |
| NDCG@1            |       0.7763 |           0.7745 | -0.001793 |
| HitRate@5         |       0.8649 |           0.8575 | -0.007446 |
| NDCG@5            |       0.8237 |           0.8196 | -0.004154 |
| HitRate@10        |       0.8994 |           0.8910 | -0.008365 |
| NDCG@10           |       0.8348 |           0.8304 | -0.004447 |
| HitRate@20        |       0.9381 |           0.9325 | -0.005574 |
| NDCG@20           |       0.8447 |           0.8410 | -0.003697 |
| MRR               |       0.8190 |           0.8162 | -0.002813 |
  
  
| Metric            | XGB Network | XGB Network SIM |         Δ |
| ----------------- | ----------: | --------------: | --------: |
| test_roc_auc      |      0.9992 |          0.9992 | -0.000041 |
| HitRate@1         |      0.9940 |          0.9950 | +0.000991 |
| NDCG@1            |      0.9940 |          0.9950 | +0.000991 |
| HitRate@5         |      0.9965 |          0.9960 | -0.000526 |
| NDCG@5            |      0.9953 |          0.9955 | +0.000179 |
| HitRate@10        |      0.9977 |          0.9970 | -0.000696 |
| NDCG@10           |      0.9957 |          0.9959 | +0.000147 |
| HitRate@20        |      0.9985 |          0.9980 | -0.000511 |
| NDCG@20           |      0.9959 |          0.9961 | +0.000213 |
| MRR               |      0.9952 |          0.9957 | +0.000474 |
  
</details> 
