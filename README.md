# Steam Game Recommendation System  
### Bachelor Thesis Project

This project builds a **large-scale game recommendation system** using Steam data, combining:

- classical ML models (Logistic Regression, Random Forest, XGBoost)
- deep learning models (Neural Networks)
- graph-based models (GraphSAGE)
- network-aware feature engineering (PCA embeddings from social graph)

The pipeline covers the full lifecycle:
**data collection → feature engineering → model training → evaluation → interpretability**

---

## Project structure  

`data_scraping/`
`preparing_datasets/`
`pca/`
`data_preparation_graph_models/`
`models/`
`eda/`
`analysis/`
`shap_analysis/`

---

## Full Pipeline (Execution Order)

This is the **order you should run things**:

### 1. Data Collection
 `data_scraping/`

- Crawl Steam users, friendships, and owned games  
- Enrich games with metadata from Steam Store API  
- Clean data and filter to Largest Connected Component (LCC)  
- Build initial baseline dataset  

**Outputs:**  
- cleaned interaction data
- enriched game metadata
- `baseline_dataset.csv` 
  
---
  
### 2. Dataset Preparation
 `preparing_datasets/`  
  
This is where the **ML-ready dataset is built (with leakage prevention)**.
  
Steps include:
  
- leave-two-out split (1 val + 1 test interaction per user)
- recomputation of features using **training-only data**
- negative sampling:
  - train: 1:10  
  - val/test: 1:100
- creation of final train / val / test splits
- feature engineering:
  - user statistics
  - game statistics
  - genre-group playtime profiles
- network feature enrichment 
  
> **No validation/test leakage into features — everything is recomputed from training data only**

---

### IMPORTANT: PCA STEP (REQUIRED BEFORE NETWORK DATASETS)

After finishing **STEP 5 in `preparing_datasets/`**, you must run:

`pca/`

This step creates **network-based game embeddings**.

---

### 3. PCA-Based Network Features
 `pca/`

Pipeline:

1. Build user-user graph (LCC)
2. Create user–game matrix
3. Remove val/test interactions (train-only matrix)
4. Compute **game–game distances using graph-aware metric**
5. Apply PCA → 32-dimensional embeddings

**Output:**
- `game_pca_embeddings_k32_trainonly.csv`

These embeddings represent:
> game similarity derived from the **social network structure**

---

### 4. (Optional) Graph Model Preparation
`data_preparation_graph_models/`

Only needed for:
- Neural Network models
- GraphSAGE models
  
Contains graph-specific preprocessing pipelines.  
  
---

### 5. Model Training
`models/`

Models included (from simplest → most advanced):

1. Random & Popularity baseline  
2. Logistic Regression  
3. Random Forest  
4. XGBoost  
5. Neural Network  
6. GraphSAGE  
7. LightGCN 

Also includes:
- multiple XGBoost experiments
- simulation 

Metrics evaluating models:
- HitRate@1 / @5 / @10  
- MRR (Mean Reciprocal Rank)

---

### 6. Exploratory Data Analysis
`eda/`

- dataset statistics
- distributions
- sanity checks
- plots saved to `eda_plots/`

Helps understand:
- sparsity
- popularity bias
- user behavior 

---

### 7. Result Analysis
`analysis/`

- deeper evaluation of model outputs
- comparison between models
- interpretation of ranking performance

---

### 8. Model Explainability (SHAP)
`shap_analysis/`

Focus:
- explain **why embeddings improve performance**

Key finding:

> After adding `game_emb_0`, the model stops relying only on popularity  
> and starts using **structural similarity between games** 

