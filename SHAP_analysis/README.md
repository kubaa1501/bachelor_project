### SHAP analysis
  
This section explains the XGBoost models using SHAP.
  
The main goal is to compare:  
- `xgb_baseline`
- `xgb_one_embedding`
  
The comparison checks what changes when only one embedding feature is added:
- `game_emb_0`
  
-----------------------------------
  
#### Motivation
  
what does game_emb_0 capture, and why does it improve the model so much?
The XGBoost model with embeddings performs much better than the baseline model.  
This SHAP analysis was added to understand why.  
  
-----------------------------------

#### CODE: `shap_models_analysis.py`
The script runs SHAP analysis for two trained XGBoost models:
- `baseline model` (From code : `models/4_XGBoost_model/train_xgb_baseline`)
- `baseline + emb_0 model` (From code: `models/8_xgb_variations/train_xgb_baseline+emb_0`)
  
It loads already trained models from:
- `best_model.joblib`
    
and compares their feature importance and interactions.
  
-----------------------------------
Input: 
- trained models `best_model.joblib`
- baseline and network datasets (that the models were trained on)

-----------------------------------
  
#### What the code does
  
1. loads both trained XGBoost pipelines  
2. separates each pipeline into:  
- preprocessor 
- XGBoost model  
3. loads the corresponding input data  
4. aligns the data columns with the model features  
5. applies the same preprocessing as during training  
6. computes SHAP values  
7. calculates feature importance using:    
`mean(|SHAP|)`  
8. finds approximate interaction partners for the top features  
9. saves SHAP plots  
10. saves summary tables  
11. creates a comparison between baseline and embedding model

-----------------------------------

#### Main finding
  
In the baseline model, the strongest signals are mostly popularity/activity features:
- `user_count`
- `game_total_playtime_minutes`
- `release_date`
  
After adding `game_emb_0`, the embedding becomes the second most important feature.  
  
That means the model is no longer relying only on simple popularity/activity statistics.  
  
Instead, `game_emb_0` gives the model an additional structural signal about the game.  

-----------------------------------
  
#### Key interpretation
  
**Baseline model**  
The baseline model is mostly driven by:  
*popularity + activity + release date*  
  
It mainly learns whether a game is generally common, active, or recent.  
  
**Embedding model**
  
The embedding model still uses popularity, but now also uses:    
  
- `game_emb_0`
  
This feature strongly interacts with:  
- `user_count`
- `release_date`
    
So `game_emb_0` seems to capture information related to:  
- game structure
- game similarity
- latent popularity patterns
- information not visible in the raw baseline features
    
-----------------------------------
  
Outputs
  
For each model, the script creates:  
  
`shap/<model_name>/`
Inside each model folder:  

```text
plots/
tables/
run_summary.json
REPORT.md
```

Plots    
```text
plots/shap_bar.png  
plots/shap_beeswarm.png  
plots/shap_violin.png  
plots/waterfall_lowest_prediction.png  
plots/waterfall_median_prediction.png  
plots/waterfall_highest_prediction.png  
plots/scatter_<top_feature>.png  
```
  
Tables  
```text
tables/feature_summary.csv  
tables/sampled_predictions.csv  
tables/sampled_transformed_features.csv.gz  
```
  
**Comparison output : **
The script also creates:  

`shap/comparison/`

with:
  
```text
feature_comparison.csv  
COMPARISON.md  
comparison_summary.json  
```

*all relevant results can be found in the folder results*
  
-----------------------------------
  
#### Important result summary

**Top features from baseline model**  
  
| rank | feature                            | mean_abs_shap | importance_share |
| ---: | ---------------------------------- | ------------: | ---------------: |
|    1 | `num__user_count`                  |       12.1596 |           0.7326 |
|    2 | `num__game_total_playtime_minutes` |        2.4655 |           0.1485 |
|    3 | `num__release_date`                |        0.6611 |           0.0398 |
  
**Top features from embedding model**

| rank | feature             | mean_abs_shap | importance_share |
| ---: | ------------------- | ------------: | ---------------: |
|    1 | `num__user_count`   |       16.3508 |           0.6112 |
|    2 | `num__game_emb_0`   |        8.1138 |           0.3033 |
|    3 | `num__release_date` |        0.7825 |           0.0292 |
  
**Feature importance comparison**
  
## Feature importance comparison

| Rank | Feature | Baseline mean\|SHAP\| | Baseline share | Baseline top interaction | Embedding mean\|SHAP\| | Embedding share | Embedding top interaction |
|---:|---|---:|---:|---|---:|---:|---|
| 1 | `num__user_count` | 12.1596 | 73.26% | `num__release_date` | 16.3508 | 61.12% | `num__game_emb_0` |
| 2 | `num__game_emb_0` | – | – | – | 8.1138 | 30.33% | `num__user_count` |
| 3 | `num__game_total_playtime_minutes` | 2.4655 | 14.85% | `num__user_count` | 0.5668 | 2.12% | `num__game_emb_0` |
| 4 | `num__release_date` | 0.6611 | 3.98% | `num__user_count` | 0.7825 | 2.92% | `num__game_emb_0` |
  
-----------------------------------
  
#### Conclusion
  
The SHAP analysis shows that adding `game_emb_0` changes the model.  
In the baseline model, XGBoost mostly relies on popularity and activity features.  
After adding `game_emb_0`, the model gets a new strong signal. The embedding becomes the **second most important feature** and **strongly interacts** with `user_count`.
  
This suggests that `game_emb_0` captures information that is not fully available in the baseline features.
  
