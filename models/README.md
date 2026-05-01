 ### Models overall comparison

| Model | HitRate@1 | HitRate@10 | MRR |
|---|---:|---:|---:|
| Naive Popularity | 0.150580 | 0.587856 | 0.284082 |
| Naive Random | 0.011130 | 0.102123 | 0.053034 |
| Logistic Regression Baseline | 0.160966 | 0.748538 | 0.338354 |
| Logistic Regression Network | 0.777250 | 0.944702 | 0.843029 |
| Random Forest Baseline | 0.619723 | 0.836766 | 0.696769 |
| Random Forest Network | 0.958279 | 0.978696 | 0.965596 |
| XGB Baseline | 0.776293 | 0.899365 | 0.818999 |
| XGB Network | 0.994009 | 0.997696 | 0.995188 |
| LightGCN | 0.279784 | 0.799440 | 0.437903 |
| NN Baseline | 0.191308 | 0.690936 | 0.340198 |
| NN Network | 0.195172 | 0.697387 | 0.344302 |
| GraphSAGE Baseline | 0.202899 | 0.729112 |  0.359860 |
| GraphSAGE Network | 0.207295 | 0.736556 | 0.367246 |
| XGB Embeddings Only | 0.106129 | 0.509163 | 0.234258 |
| XGB 1 Embedding Only | 0.984439 | 0.993690 | 0.987616 |
| XGB Embeddings + unique_genres_played + total_minutes_played | 0.158732 | 0.611676 | 0.294999 |
