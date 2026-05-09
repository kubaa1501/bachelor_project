# Models
## Folder structure & experiments

Each model is stored in a separate folder and contains:  
- training code
- configuration
- results (metrics, plots, logs)
- short description of the experiment
  
## Additional experiment folders:

- **`8_xgb_variations/`**  
  Contains multiple XGBoost experiments exploring different feature sets   
  Each sub-experiment includes its own description and results  

- **`9_simulation_xgb/`**  
  Contains a dedicated simulation experiment on XGBoost 
  Includes full description, setup, and results

#### expaination
- "Baseline" = model trained without network features  
- "Network" = model trained with additional graph/network-based features
  
**The models are ordered from the simplest to more complex models:**
  
1. Random & Popularity baseline
2. Logistic Regression
3. Random Forest
4. XGBoost
5. Neural Network
6. GraphSAGE
7. LightGCN
  
8. XGBoost variations 
9. XGBoost simulation 
  
The table below summarizes the final test results.
  
*For models trained with multiple seeds, results are reported as:*
*`mean ± std`*

#### DEFINITIONS OF METRICS: 
- HitRate@K ( @1, @5, @10)  
      Fraction of users for whom the relevant item (positive game) appears in the top-K recommendations  
- MRR (Mean Reciprocal Rank)    
      Average of the reciprocal rank of the first relevant item (how fast the positive appear in the ranking of recommendations)
    
| Model                         | Hit@1  | Hit@5  | Hit@10 | MRR    |
| ----------------------------- | ------ | ------ | ------ | ------ |
| Random                        | ~0.0111 | ~0.0526 | 0.0989 | 0.0514 |
| Popularity                    | ~0.1506 | ~0.4048 | 0.5879 | 0.2841 |
| Logistic Regression Baseline  | 0.1610 ± 0.0000 | 0.5761 ± 0.0000 | 0.7485 ± 0.0000 | 0.3384 ± 0.0000 |
| Logistic Regression Network   | 0.7784 ± 0.0013 | 0.9184 ± 0.0004 | 0.9445 ± 0.0008 | 0.8437 ± 0.0006 |
| Random Forest Baseline        | 0.6241 ± 0.0047 | 0.7783 ± 0.0012 | 0.8345 ± 0.0017 | 0.6989 ± 0.0026 |
| Random Forest Network         | 0.9577 ± 0.0008 | 0.9719 ± 0.0008 | 0.9781 ± 0.0006 | 0.9649 ± 0.0007 |
| XGBoost Baseline              | 0.7768 ± 0.0004 | 0.8630 ± 0.0021 | 0.8992 ± 0.0016 | 0.8187 ± 0.0006 |
| XGBoost Network               | 0.9942 ± 0.0002 | 0.9965 ± 0.0001 | 0.9976 ± 0.0001 | 0.9953 ± 0.0001 |
| Neural Network Baseline       | 0.1935 ± 0.0013 | 0.4991 ± 0.0013 | 0.6948 ± 0.0022 | 0.3425 ± 0.0013 |
| Neural Network Network        | 0.1917 ± 0.0020 | 0.4999 ± 0.0033 | 0.6976 ± 0.0042 | 0.3419 ± 0.0017 |
| GraphSAGE  Baseline           | 0.2066 ± 0.0018 | 0.5471 ± 0.0027 | 0.7408 ± 0.0020 | 0.3663 ± 0.0018 |
| GraphSAGE Network             | 0.2101 ± 0.0028 | 0.5536 ± 0.0029 | 0.7444 ± 0.0022 | 0.3708 ± 0.0029 |
| LightGCN                      | 0.2806 ± 0.0002 | 0.6270 ± 0.0007 | 0.7996 ± 0.0007 | 0.4384 ± 0.0003 |

### Ranking by MRR: 
  
| Rank | Model                         | MRR                                            |
| ---- | ----------------------------- | ---------------------------------------------- |
| 1    | XGBoost + Network             |  0.9953 ± 0.0001                               |
| 2    | Random Forest + Network       |  0.9649 ± 0.0007                               |
| 3    | Logistic Regression + Network |  0.8437 ± 0.0006                               |
| 4    | XGBoost Baseline              |  0.8187 ± 0.0006                               |
| 5    | Random Forest Baseline        |  0.6989 ± 0.0026                               |
| 6    | LightGCN                      | 0.4384 ± 0.0003                                |
| 7    | GraphSAGE + Network           |  0.3708 ± 0.0029                               |
| 8    | GraphSAGE Baseline            |  0.3663 ± 0.0018                               |
| 9    | Neural Network Baseline       |  0.3425 ± 0.0013                               |
| 10   | Neural Network Network        |  0.3419 ± 0.0017                               |
| 11   | Logistic Regression Baseline  |  0.3384 ± 0.0000                               |
| 12   | Popularity                    | 0.2841                                         |
| 13   | Random                        | 0.0514                                         |

-------------------------------------

## Statistical significance testing

The repository also contains:

- **`stat_significance.ipynb`**

This notebook is used to test whether differences between selected model variants are statistically significant.

It compares multi-seed results using paired statistical tests across seeds.

-------------------------------------
