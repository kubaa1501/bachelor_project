# XGBoost feature experiments

## Overview

This directory contains a series of controlled XGBoost experiments designed to analyze:

- the contribution of embedding features (`game_emb_*`)
- the role of `user_count` (popularity signal)
- interaction between embeddings and classical tabular features
- whether embeddings carry meaningful information or only reflect popularity

The experiments extend the original:

- `train_xgb_baseline.py`
- `train_xgb_network.py`

and systematically modify the feature space to isolate the impact of individual components.
## Reference models

### Baseline model

| Metric | Value |
|---|---:|
| HitRate@1 | 0.7763 |
| HitRate@10 | 0.8994 |
| MRR | 0.8190 |

### Network model

| Metric | Value |
|---|---:|
| HitRate@1 | 0.9940 |
| HitRate@10 | 0.9977 |
| MRR | 0.9952 |


# Experiments


<details>
<summary><b>1. Baseline + game_emb_0</b></summary>

`train_xgb_baseline+emb_0.py`
  
### Description

This experiment extends the baseline model by adding a single embedding dimension (`game_emb_0`).

The goal is to evaluate how much predictive power is contained in one embedding feature.

---

### Input features
  
**baseline features + emb_0**
  
<details>
<summary>Show feature list</summary>
  
**Numeric features:**
- `total_games_owned`
- `total_playtime_minutes`
- `median_playtime_minutes`
- `unique_genres_played`
- `user_count`
- `game_total_playtime_minutes`
- `release_date`
- `friend_count`
- `game_emb_0`
- `user_playtime_group_Action`
- `user_playtime_group_Adventure`
- `user_playtime_group_RPG`
- `user_playtime_group_Casual`
- `user_playtime_group_Indie`
- `user_playtime_group_Racing`
- `user_playtime_group_Simulation`
- `user_playtime_group_Strategy`
- `user_playtime_group_Sports`
- `user_playtime_group_Violent`
- `user_playtime_group_Adult`
- `user_playtime_group_Non-gameplay_Tools`
- `user_playtime_group_Other`

**Categorical features:**
- `country`
- `genres`
- `developer`
- `publisher`
- `platforms`

</details>

---

### Results

| Metric | Value |
|---|---:|
| HitRate@1 | 0.9844 |
| HitRate@10 | 0.9937 |
| MRR | 0.9876 |

---

### Comparison

| Model | HitRate@1 | HitRate@10 | MRR |
|---|---:|---:|---:|
| Baseline | 0.7763 | 0.8994 | 0.8190 |
| Baseline + game_emb_0 | 0.9844 | 0.9937 | 0.9876 |
| Network | 0.9940 | 0.9977 | 0.9952 |

---

### Summary

A single embedding dimension captures a large fraction of the signal responsible for the performance gap between baseline and network models.

</details>


<details>
<summary><b>2. Embeddings only</b></summary>

`train_xgb_embeddings_only.py`

### Description

This experiment evaluates the model trained exclusively on embedding features.

The goal is to determine whether embeddings alone contain enough information to perform accurate ranking, without any additional user or popularity signals.

---

### Input features

**only embeddings**

<details>
<summary>Show feature list</summary>

**Numeric features:**
- `game_emb_0`
- `game_emb_1`
- `game_emb_2`
- `game_emb_3`
- `game_emb_4`
- `game_emb_5`
- `game_emb_6`
- `game_emb_7`
- `game_emb_8`
- `game_emb_9`
- `game_emb_10`
- `game_emb_11`
- `game_emb_12`
- `game_emb_13`
- `game_emb_14`
- `game_emb_15`
- `game_emb_16`
- `game_emb_17`
- `game_emb_18`
- `game_emb_19`
- `game_emb_20`
- `game_emb_21`
- `game_emb_22`
- `game_emb_23`
- `game_emb_24`
- `game_emb_25`
- `game_emb_26`
- `game_emb_27`
- `game_emb_28`
- `game_emb_29`
- `game_emb_30`
- `game_emb_31`

No categorical features are used.

</details>

---

### Results

| Metric | Value |
|---|---:|
| HitRate@1 | 0.1061 |
| HitRate@10 | 0.5092 |
| MRR | 0.2343 |

---

### Comparison

| Model | HitRate@1 | HitRate@10 | MRR |
|---|---:|---:|---:|
| Baseline | 0.7763 | 0.8994 | 0.8190 |
| Embeddings only | 0.1061 | 0.5092 | 0.2343 |
| Network | 0.9940 | 0.9977 | 0.9952 |

---

### Summary

Embeddings alone are insufficient for effective recommendation.

Despite encoding meaningful structure, they lack critical contextual signals such as:
- user preferences
- popularity (`user_count`)
- recency and interaction statistics

As a result, performance drops significantly compared to the baseline model.

</details>


<details>
<summary><b>3. Embeddings + basic user information</b></summary>

`train_xgb_embeddings+unique_genres_played+total_playtime_minutes.py`

### Description

This experiment evaluates whether embeddings become more useful when combined with a small amount of user-level information.

The model uses all 32 game embedding dimensions together with:

- `unique_genres_played`
- `total_playtime_minutes`

The goal is to check whether embeddings need basic user context to become useful for ranking.

---

### Input features

**embeddings + basic user information**

<details>
<summary>Show feature list</summary>

**Numeric features:**
- `unique_genres_played`
- `total_playtime_minutes`
- `game_emb_0`
- `game_emb_1`
- `game_emb_2`
- `game_emb_3`
- `game_emb_4`
- `game_emb_5`
- `game_emb_6`
- `game_emb_7`
- `game_emb_8`
- `game_emb_9`
- `game_emb_10`
- `game_emb_11`
- `game_emb_12`
- `game_emb_13`
- `game_emb_14`
- `game_emb_15`
- `game_emb_16`
- `game_emb_17`
- `game_emb_18`
- `game_emb_19`
- `game_emb_20`
- `game_emb_21`
- `game_emb_22`
- `game_emb_23`
- `game_emb_24`
- `game_emb_25`
- `game_emb_26`
- `game_emb_27`
- `game_emb_28`
- `game_emb_29`
- `game_emb_30`
- `game_emb_31`

No categorical features are used.

</details>

---

### Results

| Metric | Value |
|---|---:|
| HitRate@1 | 0.1587 |
| HitRate@10 | 0.6117 |
| MRR | 0.2950 |
  
---

### Comparison

| Model | HitRate@1 | HitRate@10 | MRR |
|---|---:|---:|---:|
| Baseline | 0.7763 | 0.8994 | 0.8190 |
| Embeddings only | 0.1061 | 0.5092 | 0.2343 |
| Embeddings + basic user information | 0.1587 | 0.6117 | 0.2950 |
| Network | 0.9940 | 0.9977 | 0.9952 |

---

### Summary

Adding `unique_genres_played` and `total_playtime_minutes` improves performance over embeddings alone.

However, the model is still far below the baseline model. This suggests that embeddings contain some useful game-structure signal, but they are not enough without stronger tabular features such as popularity, game metadata, and richer user preference features.

In other words: embeddings help a bit, but they are not magic dust. Without context, they mostly just sit there looking mathematical.

</details>


<details>
<summary><b>Feature importance / SHAP analysis</b></summary>

### Goal

The SHAP analysis is used to understand the factors driving the XGBoost predictions, with a particular focus on:

- whether embedding features dominate the model
- whether `game_emb_0` acts as a proxy for popularity
- how embeddings interact with classical tabular features
- whether the performance gain of the network model is driven by meaningful structure or by a single dominant correlated feature

---

### Interaction structure

A key observation is that the interaction structure of the model changes after introducing embedding features.

#### Baseline model

- `num__user_count` interacts most strongly with `num__release_date`
- `num__game_total_playtime_minutes` interacts most strongly with `num__user_count`

This indicates that the baseline model relies primarily on a combination of popularity, recency, and playtime-related signals.

---

#### Embedding model (with `game_emb_0`)

- `num__user_count` interacts most strongly with `num__game_emb_0`
- `num__game_emb_0` interacts most strongly with `num__user_count`
- `num__release_date` also shows strong interaction with `num__game_emb_0`

This indicates that the embedding feature is not used independently, but rather in conjunction with:

- popularity (`user_count`)
- recency (`release_date`)

These patterns suggest that the embedding encodes a global structural signal aligned with popularity and centrality.

---

### Top features (SHAP)

#### Baseline model

| Rank | Feature | mean |SHAP| | Importance share |
|---|---|---:|---:|
| 1 | num__user_count | 12.1596 | 73.26% |
| 2 | num__game_total_playtime_minutes | 2.4655 | 14.85% |
| 3 | num__release_date | 0.6611 | 3.98% |
| 4 | num__user_playtime_group_Other | 0.1495 | 0.90% |
| 5 | num__total_games_owned | 0.1493 | 0.90% |
| 6 | num__median_playtime_minutes | 0.1449 | 0.87% |
| 7 | num__user_playtime_group_Indie | 0.1285 | 0.77% |
| 8 | num__user_playtime_group_Strategy | 0.1064 | 0.64% |
| 9 | num__user_playtime_group_RPG | 0.0942 | 0.57% |
| 10 | num__user_playtime_group_Sports | 0.0777 | 0.47% |

The model is strongly dominated by `user_count`, which accounts for over 70% of total importance.

---

#### Embedding model (Baseline + `game_emb_0`)

| Rank | Feature | mean |SHAP| | Importance share |
|---|---|---:|---:|
| 1 | num__user_count | 16.3508 | 61.12% |
| 2 | num__game_emb_0 | 8.1138 | 30.33% |
| 3 | num__release_date | 0.7825 | 2.92% |
| 4 | num__game_total_playtime_minutes | 0.5668 | 2.12% |
| 5 | num__median_playtime_minutes | 0.2307 | 0.86% |
| 6 | num__total_games_owned | 0.1022 | 0.38% |
| 7 | num__user_playtime_group_RPG | 0.0899 | 0.34% |
| 8 | num__friend_count | 0.0638 | 0.24% |
| 9 | num__user_playtime_group_Other | 0.0623 | 0.23% |
| 10 | num__user_playtime_group_Casual | 0.0606 | 0.23% |

The key change is the emergence of `game_emb_0` as the second most important feature, contributing over 30% of the total importance.

---

### Feature importance comparison

| Rank | Feature | Baseline share | Embedding share |
|---|---|---:|---:|
| 1 | num__user_count | 73.26% | 61.12% |
| 2 | num__game_emb_0 | – | 30.33% |
| 3 | num__game_total_playtime_minutes | 14.85% | 2.12% |
| 4 | num__release_date | 3.98% | 2.92% |

The introduction of the embedding redistributes importance from classical features to the embedding representation.

---

### Interpretation

The results indicate that `game_emb_0` functions as a compressed global signal.

It likely captures a combination of:

- game popularity (e.g., interaction frequency)
- graph centrality
- global co-play structure

Importantly, the embedding does not replace traditional features but reorganizes the feature space:

- in the baseline model, multiple features contribute independently
- in the embedding model, a dominant latent feature emerges and interacts with a smaller set of supporting signals

---

### Conclusion

The observed performance improvement is largely explained by:

- the introduction of a strong global signal captured by `game_emb_0`
- its interaction with `user_count` and other key features

This suggests that a significant portion of the predictive power comes from a compact representation of global game relationships rather than a large number of independent tabular features.

</details>
