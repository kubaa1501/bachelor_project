# SHAP report: xgb_baseline

- Model: `/home/anci/new/models_new/xgb_baseline/best_model.joblib`
- Data: `/home/anci/new/correct_splits/with_genre_groups/test.csv`
- Input rows: **2849311**
- Rows explained: **2849311**
- Features used after preprocessing: **425**

## Top 15 features by mean |SHAP|

| rank | feature | mean_abs_shap | share | top interaction |
|---:|---|---:|---:|---|
| 1 | num__user_count | 12.159643 | 73.26% | num__release_date |
| 2 | num__game_total_playtime_minutes | 2.465470 | 14.85% | num__user_count |
| 3 | num__release_date | 0.661086 | 3.98% | num__user_count |
| 4 | num__user_playtime_group_Other | 0.149454 | 0.90% | num__unique_genres_played |
| 5 | num__total_games_owned | 0.149335 | 0.90% | num__user_count |
| 6 | num__median_playtime_minutes | 0.144943 | 0.87% | num__user_count |
| 7 | num__user_playtime_group_Indie | 0.128519 | 0.77% | num__user_playtime_group_Casual |
| 8 | num__user_playtime_group_Strategy | 0.106396 | 0.64% | num__total_playtime_minutes |
| 9 | num__user_playtime_group_RPG | 0.094210 | 0.57% | - |
| 10 | num__user_playtime_group_Sports | 0.077703 | 0.47% | - |
| 11 | num__user_playtime_group_Racing | 0.075516 | 0.45% | - |
| 12 | num__user_playtime_group_Non-gameplay_Tools | 0.070517 | 0.42% | - |
| 13 | num__user_playtime_group_Casual | 0.060126 | 0.36% | - |
| 14 | num__user_playtime_group_Action | 0.059207 | 0.36% | - |
| 15 | num__unique_genres_played | 0.058121 | 0.35% | - |

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