# SHAP report: xgb_one_embedding

- Model: `/home/anci/new/models_new/xgb_one_embedding/best_model.joblib`
- Data: `/home/anci/new/correct_splits/with_genre_groups_network_fixed/test.csv`
- Input rows: **2849311**
- Rows explained: **2849311**
- Features used after preprocessing: **427**

## Top 15 features by mean |SHAP|

| rank | feature | mean_abs_shap | share | top interaction |
|---:|---|---:|---:|---|
| 1 | num__user_count | 16.350816 | 61.12% | num__game_emb_0 |
| 2 | num__game_emb_0 | 8.113760 | 30.33% | num__user_count |
| 3 | num__release_date | 0.782508 | 2.92% | num__game_emb_0 |
| 4 | num__game_total_playtime_minutes | 0.566819 | 2.12% | num__game_emb_0 |
| 5 | num__median_playtime_minutes | 0.230689 | 0.86% | num__release_date |
| 6 | num__total_games_owned | 0.102230 | 0.38% | num__game_emb_0 |
| 7 | num__user_playtime_group_RPG | 0.089870 | 0.34% | num__game_emb_0 |
| 8 | num__friend_count | 0.063761 | 0.24% | num__game_emb_0 |
| 9 | num__user_playtime_group_Other | 0.062290 | 0.23% | - |
| 10 | num__user_playtime_group_Casual | 0.060606 | 0.23% | - |
| 11 | num__user_playtime_group_Non-gameplay_Tools | 0.055249 | 0.21% | - |
| 12 | num__user_playtime_group_Adventure | 0.048699 | 0.18% | - |
| 13 | num__user_playtime_group_Racing | 0.038053 | 0.14% | - |
| 14 | num__user_playtime_group_Violent | 0.036503 | 0.14% | - |
| 15 | num__unique_genres_played | 0.032595 | 0.12% | - |

## Generated files

- `plots/shap_bar.png`
- `plots/shap_beeswarm.png`
- `plots/shap_violin.png`
- `plots/waterfall_lowest_prediction.png`
- `plots/waterfall_median_prediction.png`
- `plots/waterfall_highest_prediction.png`
- `plots/scatter_<top_8_features>.png`
- `tables/feature_summary.csv`
- `tables/sampled_predictions.csv`
- `tables/sampled_transformed_features.csv.gz`
- `run_summary.json`