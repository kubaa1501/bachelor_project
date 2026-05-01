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

However, the model is still far below the baseline model. This suggests that embeddings contain some useful game-structure signal, but it works only with some other meaningful features.


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
  
| Rank | Feature | mean_abs_shap | Importance share |
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
  
| Rank | Feature | mean_abs_shap | Importance share |
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
- in the embedding model, a dominant latent feature emerges and interacts with a smaller set of supporting signals.

---

### Conclusion

The observed performance improvement is largely explained by:

- the introduction of a strong global signal captured by `game_emb_0`
- its interaction with `user_count` and other key features

</details>

<details>
<summary><b>3. Baseline without `user_count` </b></summary>

### Description

This experiment removes the `user_count` feature from the baseline model.  

The goal is to evaluate how much of the model performance is driven purely by the popularity signal, and how well the remaining features perform without it.  
  
This serves as a diagnostic test for:  
  
- reliance on global popularity
- robustness of behavioral and content-based features
- comparison baseline for embedding-based models
  
---
  
### Input features
  
**baseline features (excluding `user_count`)**

<details> 
<summary>Show feature list</summary>

**Numeric features:**
- `total_games_owned`
- `total_playtime_minutes`
- `median_playtime_minutes`
- `unique_genres_played`
- `game_total_playtime_minutes`
- `release_date`
- `friend_count`
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
  
### Results:

| Metric     |  Value |
| ---------- | -----: |
| HitRate@1  | 0.1788 |
| HitRate@10 | 0.6255 |
| MRR        | 0.3135 |

### Comparison:
  
| Model                    | HitRate@1 | HitRate@10 |    MRR |
| ------------------------ | --------: | ---------: | -----: |
| Baseline                 |    0.7763 |     0.8994 | 0.8190 |
| Baseline (no user_count) |    0.1788 |     0.6255 | 0.3135 |
| Network                  |    0.9940 |     0.9977 | 0.9952 |

---
  
### Summary:

Removing `user_count` leads to a dramatic performance drop across all ranking metrics.  
  
Key observations:

HitRate@1 decreases from 0.776 → 0.179  
MRR decreases from 0.819 → 0.313  
overall ranking quality collapses  
  
This confirms that:  
- `user_count` is the dominant signal in the baseline model  
- most predictive power comes from popularity rather than personalization
- remaining features (playtime, genres, metadata) are insufficient to recover performance
  
Interestingly, the model without `user_count` still outperforms the Random and Popularity (model that uses only `user_count`) model which means that tabular behavioral features carry some signal. 

--- 
  
### Interpretation
  
This experiment establishes a critical reference point:  
- the baseline model is largely driven by popularity
- any improvement from embeddings should be interpreted relative to this effect
  
In particular:  
- if embeddings recover performance lost after removing user_count, they likely encode popularity-like information
- if they improve beyond this baseline, they may capture meaningful relational structure
  
</details>

<details>
<summary><b>4. Baseline + game_emb_0 without `user_count`</b></summary>

`train_xgb_baseline+emb_0-user_count.py`

### Description

This experiment adds `game_emb_0` to the baseline feature set while still removing `user_count`.
  
The goal is to test whether the first embedding dimension can recover the performance lost after removing the main popularity feature.  
  
This directly checks whether `game_emb_0` behaves as a replacement for `user_count` or whether it contributes additional information.
  
---
  
### Input features
  
**baseline features + `game_emb_0`, excluding `user_count`**

<details>
<summary>Show feature list</summary>

**Numeric features:**
- `total_games_owned`
- `total_playtime_minutes`
- `median_playtime_minutes`
- `unique_genres_played`
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
| HitRate@1 | 0.1881 |
| HitRate@10 | 0.6508 |
| MRR | 0.3269 |

---

### Comparison

| Model | HitRate@1 | HitRate@10 | MRR |
|---|---:|---:|---:|
| Baseline | 0.7763 | 0.8994 | 0.8190 |
| Baseline without `user_count` | 0.1788 | 0.6255 | 0.3135 |
| Baseline + `game_emb_0` without `user_count` | 0.1881 | 0.6508 | 0.3269 |
| Network | 0.9940 | 0.9977 | 0.9952 |

---

### Summary

Adding `game_emb_0` without `user_count` improves performance only slightly compared to the baseline without `user_count`.  
  
This suggests that `game_emb_0` does not fully replace `user_count`.  
  
Its strongest effect appears when it is used together with `user_count`, which supports the SHAP finding that these two features interact strongly.  

---

### Interpretation
  
The result indicates that `game_emb_0` contains useful signal, but its predictive power depends heavily on interaction with popularity.
  
On its own, without `user_count`, it provides only a modest improvement.  
  
Therefore, the large gain observed in the full embedding model is likely caused by the combination of:  
  
- explicit popularity signal from `user_count`
- latent structural signal from `game_emb_0`
- interaction between both features
  
</details>

<details>
<summary><b>5. Only `user_count` + `game_emb_0`</b></summary>

`train_xgb_emb0+user_count.py`

### Description

This experiment trains XGBoost using only two features:

- `user_count`
- `game_emb_0`

The goal is to test whether the strong performance of the network model can be largely explained by the interaction between explicit popularity and the first embedding dimension.

This is a minimal-feature diagnostic experiment.

---

### Input features

**only `user_count` and `game_emb_0`**

<details>
<summary>Show feature list</summary>

**Numeric features:**
- `user_count`
- `game_emb_0`

No categorical features are used.

</details>

---

### Results

| Metric | Value |
|---|---:|
| HitRate@1 | 0.9529 |
| HitRate@10 | 0.9878 |
| MRR | 0.9647 |
  
---
  
### Comparison

| Model | HitRate@1 | HitRate@10 | MRR |
|---|---:|---:|---:|
| Baseline | 0.7763 | 0.8994 | 0.8190 |
| Only `user_count` + `game_emb_0` | 0.9529 | 0.9878 | 0.9647 |
| Network | 0.9940 | 0.9977 | 0.9952 |

---

### Summary

Using only `user_count` and `game_emb_0` is sufficient to recover most of the performance of the full network model.

This is a strong result:

- HitRate@1 reaches **0.9529**
- HitRate@10 reaches **0.9878**
- MRR reaches **0.9647**

Despite using only two features, the model performs far above the full baseline model.

---

### Interpretation

This suggests that the network model achieves slightly higher performance due to additional weak but informative features.

However, the majority of the predictive power is already captured by the interaction between `user_count` and `game_emb_0`.  
   
In particular:
  
- `user_count` provides a strong explicit popularity signal  
- `game_emb_0` captures a global latent structure of games  
- their combination forms a highly effective joint signal  
  
The remaining embedding dimensions and network-derived features contribute only marginal gains on top of this core interaction.  
  
As a result, the superior performance of the network model is not primarily driven by a rich high-dimensional representation, but rather by a small number of dominant features that complement each other extremely well.  
  
</details>
  
<details>
<summary><b>Additional validation: embedding vs. popularity signal</b></summary>

### Motivation

The strong interaction between `user_count` and `game_emb_0` raises an important question:

- Is the embedding providing genuinely new information, or is it simply a transformed version of popularity?

Two additional experiments were conducted to investigate this:

1. Replace the real embedding with a synthetic feature highly correlated with `user_count`
2. Replace `user_count` with a logarithmic transformation to match the observed embedding shape

---

### 1. Fake embedding (corr ≈ 0.97 with `user_count`)

A synthetic feature was constructed to mimic the correlation structure of `game_emb_0`.

The feature:
- is derived directly from `user_count`
- has Pearson correlation ≈ 0.97
- contains no additional structural information
  
---
  
#### Input features

- the same as baseline model - with addition of the synthetic emb_0 feature

---
  
#### Results

| Metric | Value |
|---|---:|
| HitRate@1 | 0.7755 |
| HitRate@10 | 0.9021 |
| MRR | 0.8180 |
  
---
  
### Comparison

| Model | HitRate@1 | HitRate@10 | MRR |
|---|---:|---:|---:|
| Baseline | 0.7763 | 0.8994 | 0.8190 |
| Baseline + fake emb_0 | 0.7755 | 0.9020 | 0.8180 |
| Baseline + game_emb_0 | 0.9844 | 0.9937 | 0.9876 |
| Network | 0.9940 | 0.9977 | 0.9952 |  

---
  
### Interpretation

The synthetic embedding (`fake_emb_0`) does **not reproduce the effect of the real embedding**, despite having a very high correlation (≈ 0.97) with `user_count`.  
  
Specifically:
  
- performance of *Baseline + fake emb_0* remains essentially identical to the baseline  
- no meaningful improvement is observed from adding the synthetic feature  
- in contrast, *Baseline + game_emb_0* leads to a dramatic performance increase  
  
This demonstrates that:  
  
- the improvement is **not caused by correlation with `user_count` alone**
- a randomly constructed feature, even with extremely high correlation, **does not carry the required signal**
- the real embedding contains **structured information that is not captured by simple statistical dependence**
  
In other words:  correlation ≠ information
  
Even though `game_emb_0` is strongly correlated with `user_count`, it encodes additional structure that the model is able to exploit.  
  
---
  
### Conclusion
  
The experiment confirms that `game_emb_0` is **not trivially replaceable** by a synthetic feature derived from `user_count`.  
  
The performance gain comes from:  
- meaningful structure encoded in the embedding  
- not merely from its correlation with popularity  
  
---

### 2. Log-transformed `user_count`

It was observed that `game_emb_0` follows an approximately logarithmic relationship with `user_count`.

To test this, `user_count` was replaced with `log1p(user_count)` in the Baseline model pipeline.

---
  
#### Input features

- the same as baseline model, but feature `user_count` has been transformed to `log1p(user_count)`

---
  
#### Results

| Metric | Value |
|---|---:|
| HitRate@1 | 0.7700 |
| HitRate@10 | 0.8951 |
| MRR | 0.8131 |
  
---
    
### Comparison
  
| Model | HitRate@1 | HitRate@10 | MRR |
|---|---:|---:|---:|
| Baseline | 0.7763 | 0.8994 | 0.8190 |
| Baseline (`log(user_cout)`) | 0.7700 | 0.8951 | 0.8131 |
| Baseline + game_emb_0 | 0.9844 | 0.9937 | 0.9876 |
| Network | 0.9940 | 0.9977 | 0.9952 |  
  
---

### Interpretation

Replacing `user_count` with its logarithmic transformation does **not improve the model**.
  
In fact:  
  
- performance slightly **decreases** compared to the baseline  
- the model does not benefit from this simple non-linear transformation  
- the gap to the embedding-based model remains extremely large  
  
This indicates that:  
  
- `game_emb_0` is **not equivalent to a simple log-transformation of popularity**  
- even if visually correlated, the embedding captures a **different functional structure**  
- the model cannot reproduce the embedding effect using a hand-crafted transformation  
  
---
  
### Conclusion
  
The experiment shows that:  
- a basic non-linear transformation of `user_count` is insufficient to explain the performance gain  
- `game_emb_0` encodes a more complex signal than monotonic scaling of popularity
  
</details>
  
---  
  
*Full results of all experiments can be seen in folder `results`*
  
<details>
<summary><b>XGB variations models comparison</b></summary>
  
| Rank | Model | HitRate@1 | HitRate@5 | HitRate@10 | MRR |
|---:|---|---:|---:|---:|---:|
| 1 | **XGB Network** | 0.9942 ± 0.0002 | 0.9965 ± 0.0001 | 0.9976 ± 0.0001 | 0.9953 ± 0.0001 |
| 2 | XGB Baseline + `game_emb_0` | 0.9844 | 0.9910 | 0.9937 | 0.9876 |
| 3 | XGB `user_count` + `game_emb_0` only | 0.9529 | 0.9792 | 0.9878 | 0.9647 |
| 4 | **XGB Baseline** | 0.7768 ± 0.0004 | 0.8630 ± 0.0021 | 0.8992 ± 0.0016 | 0.8187 ± 0.0006 |
| 5 | XGB Baseline + `fake emb_0` | 0.7755 | 0.8640 | 0.9021 | 0.8180 |
| 6 | XGB Baseline + `log(user_count)` | 0.7700 | 0.8582 | 0.8951 | 0.8131 |
| 7 | XGB Baseline + `game_emb_0` without `user_count` | 0.1881 | 0.4645 | 0.6508 | 0.3269 |
| 8 | XGB Baseline without `user_count` | 0.1788 | 0.4427 | 0.6255 | 0.3135 |
| 9 | XGB embeddings + basic user info | 0.1587 | 0.4204 | 0.6117 | 0.2950 |
| 10 | XGB embeddings only | 0.1061 | 0.3431 | 0.5092 | 0.2343 |
   
</details>
