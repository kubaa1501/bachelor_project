<details> 
<summary>Neural Network BPR baseline model</summary>
  
### MODEL: Neural Network BPR baseline model  
    
`nn_bpr.py no_net`
      
It trains, validates, and evaluates a neural recommendation model using **Bayesian Personalized Ranking (BPR) loss** on the **no-network dataset**.  
  
The script builds a PyTorch-based recommendation pipeline that:
- loads cached user and game feature tensors
- encodes user features with a linear projection
- encodes game features using numeric inputs and categorical embeddings
- scores user-game pairs with an MLP
- trains the model using **pairwise BPR loss**
- performs hyperparameter search over hidden size, number of layers, and learning rate
- selects the best configuration using validation ROC-AUC
- evaluates the final model on validation and test sets as a ranking model  
*Additionally, it saves the ROC-AUC training curve for the best configuration.*

--------------------------------------

Input:   
  
- cached graph and tensor files from `cache_no_net`
- validation parquet file
- test parquet file  
**This input is created by codes in 5_Neural_network_prep**    
*This is the no-network / baseline dataset* 

-------------------------------------

The target column is:  
- `owned`  
*The model predicts a ranking score for a given (`steamid`, `appid`) pair and is trained to rank positive interactions above sampled negative interactions.*
  
-------------------------------------
    
#### Features used
    
The model uses:
- user numeric feature vectors
- game numeric feature vectors
- categorical game metadata represented as embedding indices

Categorical embedded columns:
- `genres`
- `developer`
- `publisher`
- `platforms`

Identifier columns:
- `steamid`
- `appid`

*These identifiers are mapped to internal user and game indices through cached dictionaries and are used for lookup, not as direct input features.*

-------------------------------------

#### Data representation
  
The training data is loaded from a precomputed cache containing:
- graph tensors
- user and game index mappings
- grouped training edges
- validation dataframe
- test dataframe
- categorical vocabularies
- feature metadata

Training examples are organized into groups of:
- **1 positive interaction**
- **10 negative interactions**

This means each training group has size:
- `N_NEG + 1 = 11`

*The model is therefore trained in a pairwise ranking setup rather than as a standard binary classifier.*

-------------------------------------

#### Model architecture
  
The model consists of three main parts.

##### 1. User encoder
User feature vectors are projected through:
- a linear layer
- ReLU activation

##### 2. Game encoder
Game features are encoded using:
- numeric game features projected with a linear layer
- categorical metadata embedded using trainable embedding layers
- masked average pooling over categorical token embeddings
- a final projection layer with ReLU

Embedding dimensions:
- `genres` → 16
- `developer` → 64
- `publisher` → 64
- `platforms` → 4

##### 3. MLP scorer
The user embedding and game embedding are concatenated and passed through a multilayer perceptron.

The hyperparameter search covers:
- hidden channels: `64`, `128`, `256`
- number of MLP layers: `2`, `3`, `4`
- learning rate: `1e-3`, `5e-4`

The final output is:
- a single relevance score for each user-game pair

-------------------------------------

#### Training objective
  
The training loss is: **BPR loss**
  
For each training group:
- the first item is treated as the positive example
- the remaining items are treated as negative examples
- the model is optimized so that the positive score is higher than the negative scores

This is implemented as:
- pairwise score differences
- sigmoid ranking objective
- mean negative log-likelihood over pairs

*This makes the model directly optimize relative ranking quality instead of pointwise classification loss.*

-------------------------------------

#### Training procedure
  
The model is trained using:
- optimizer: `Adam`
- weight decay: `1e-5`
- learning rate scheduler: `ReduceLROnPlateau`

Additional training setup:
- epochs: `20`
- sampled training groups per epoch: `200000`
- seed: `42`

At each epoch:
- a subset of grouped train examples is sampled
- the model is trained with mini-batches
- approximate train ROC-AUC is computed on a few training batches
- validation ROC-AUC is computed on the validation dataframe

The best configuration is selected using:
- **average validation ROC-AUC across epochs**

*This is an important difference from the sklearn ranking models, where model selection was based on validation NDCG@10.*

-------------------------------------

#### Ranking evaluation
  
After training, the best model is evaluated on the validation and test sets.

For each user (`steamid`):
- candidate games are sorted by predicted score
- ranking metrics are computed on the ordered owned labels

The script computes:
- HitRate@1
- Recall@1
- NDCG@1
- HitRate@5
- Recall@5
- NDCG@5
- HitRate@10
- Recall@10
- NDCG@10
- HitRate@20
- Recall@20
- NDCG@20
- MRR

Metrics are computed per user and then **averaged across all evaluated users**.  
*(Users with no positive items are skipped during ranking evaluation.)*

-------------------------------------

#### Additional classification metric
  
Besides ranking metrics, the script also tracks:
- ROC-AUC

ROC-AUC is used:
- during training
- during hyperparameter search
- for selecting the best model configuration

The script stores:
- best validation ROC-AUC
- train ROC-AUC history
- validation ROC-AUC history

-------------------------------------

Outputs:
- `nn_bpr_no_net_best.pt` — saved best model checkpoint
- `nn_bpr_no_net_metrics.json` — metrics and best configuration
- `nn_bpr_no_net_roc.png` — train/validation ROC-AUC curve for the best model

-------------------------------------

### Results:

<details> 
<summary>Show results for Neural Network BPR baseline model</summary> 

### Neural Network BPR baseline model:
  
- "mode": "no_net"
- "seed": 42
  
**Best configuration:**
- hidden_channels = 256
- num_layers = 4
- learning_rate = 0.0005
- loss = bpr
  
**Model selection metric:**
- best average validation ROC-AUC = 0.9100

<details> 
<summary>Show validation results</summary>
    
#### Validation results:
  
| Metric | Value |
|---|---:|
| Best validation ROC-AUC | 0.9100 |
| Evaluated users | 28211 |
| HitRate@1 | 0.1830 |
| Recall@1 | 0.1830 |
| NDCG@1 | 0.1830 |
| HitRate@5 | 0.4865 |
| Recall@5 | 0.4865 |
| NDCG@5 | 0.3365 |
| HitRate@10 | 0.6832 |
| Recall@10 | 0.6832 |
| NDCG@10 | 0.4000 |
| HitRate@20 | 0.8763 |
| Recall@20 | 0.8763 |
| NDCG@20 | 0.4491 |
| MRR | 0.3314 |

</details> 
  
<details> 
<summary>Show test results</summary>
    
#### Test results:
  
| Metric | Value |
|---|---:|
| Evaluated users | 28211 |
| HitRate@1 | 0.1913 |
| Recall@1 | 0.1913 |
| NDCG@1 | 0.1913 |
| HitRate@5 | 0.4952 |
| Recall@5 | 0.4952 |
| NDCG@5 | 0.3459 |
| HitRate@10 | 0.6909 |
| Recall@10 | 0.6909 |
| NDCG@10 | 0.4090 |
| HitRate@20 | 0.8785 |
| Recall@20 | 0.8785 |
| NDCG@20 | 0.4567 |
| MRR | 0.3402 |

</details>

<details> 
<summary>Show ROC-AUC plot</summary>
    
#### ROC-AUC plot:
  
<img width="800" height="500" alt="nn_no_net_roc" src="https://github.com/user-attachments/assets/91f353fc-5ff6-4e60-8074-3db226e54761" />

</details>
  
</details>

-------------------------------------
  
</details>

<details> 
<summary>Neural Network BPR model network model</summary>
  
### MODEL: Neural Network BPR model network model  
    
`nn_bpr.py with_net`
      
It trains, validates, and evaluates a neural recommendation model using **Bayesian Personalized Ranking (BPR) loss** on the **network-enriched dataset**.  
  
The script builds a PyTorch-based recommendation pipeline that:
- loads cached user and game feature tensors
- encodes user features with a linear projection
- encodes game features using numeric inputs and categorical embeddings
- scores user-game pairs with an MLP
- trains the model using **pairwise BPR loss**
- performs hyperparameter search over hidden size, number of layers, and learning rate
- selects the best configuration using validation ROC-AUC
- evaluates the final model on validation and test sets as a ranking model  
*Additionally, it saves the ROC-AUC training curve for the best configuration.*

--------------------------------------

Input:   
- cached graph and tensor files from `cache`
- validation parquet file
- test parquet file  
**This input is created by codes in 5_Neural_network_prep**      
*This is the network-enriched dataset* 

-------------------------------------

The target column is:  
- `owned`  
*The model predicts a ranking score for a given (`steamid`, `appid`) pair and is trained to rank positive interactions above sampled negative interactions.*

-------------------------------------
  
#### Features used
  
The model uses:
- user numeric feature vectors
- game numeric feature vectors
- categorical game metadata represented as embedding indices

Compared with the `no_net` version, the cached feature tensors additionally include network-enriched information.

Categorical embedded columns:
- `genres`
- `developer`
- `publisher`
- `platforms`

Identifier columns:
- `steamid`
- `appid`

*These identifiers are mapped to internal user and game indices through cached dictionaries and are used for lookup, not as direct input features.*

-------------------------------------

#### Data representation
  
The training data is loaded from a precomputed cache containing:
- graph tensors
- user and game index mappings
- grouped training edges
- validation dataframe
- test dataframe
- categorical vocabularies
- feature metadata

Training examples are organized into groups of:
- **1 positive interaction**
- **10 negative interactions**

This means each training group has size:
- `N_NEG + 1 = 11`

*The model is therefore trained in a pairwise ranking setup rather than as a standard binary classifier.*

-------------------------------------

#### Model architecture
  
The model consists of three main parts.

##### 1. User encoder
User feature vectors are projected through:
- a linear layer
- ReLU activation

##### 2. Game encoder
Game features are encoded using:
- numeric game features projected with a linear layer
- categorical metadata embedded using trainable embedding layers
- masked average pooling over categorical token embeddings
- a final projection layer with ReLU

Embedding dimensions:
- `genres` → 16
- `developer` → 64
- `publisher` → 64
- `platforms` → 4

##### 3. MLP scorer
The user embedding and game embedding are concatenated and passed through a multilayer perceptron.

The hyperparameter search covers:
- hidden channels: `64`, `128`, `256`
- number of MLP layers: `2`, `3`, `4`
- learning rate: `1e-3`, `5e-4`

The final output is:
- a single relevance score for each user-game pair

-------------------------------------

#### Training objective
  
The training loss is: **BPR loss**
  
For each training group:
- the first item is treated as the positive example
- the remaining items are treated as negative examples
- the model is optimized so that the positive score is higher than the negative scores

This is implemented as:
- pairwise score differences
- sigmoid ranking objective
- mean negative log-likelihood over pairs

-------------------------------------

#### Training procedure
  
The model is trained using:
- optimizer: `Adam`
- weight decay: `1e-5`
- learning rate scheduler: `ReduceLROnPlateau`

Additional training setup:
- epochs: `20`
- sampled training groups per epoch: `200000`
- seed: `42`

At each epoch:
- a subset of grouped train examples is sampled
- the model is trained with mini-batches
- approximate train ROC-AUC is computed on a few training batches
- validation ROC-AUC is computed on the validation dataframe

The best configuration is selected using:
- **average validation ROC-AUC across epochs**

-------------------------------------

#### Ranking evaluation
  
After training, the best model is evaluated on the validation and test sets.

For each user (`steamid`):
- candidate games are sorted by predicted score
- ranking metrics are computed on the ordered owned labels

The script computes:
- HitRate@1
- Recall@1
- NDCG@1
- HitRate@5
- Recall@5
- NDCG@5
- HitRate@10
- Recall@10
- NDCG@10
- HitRate@20
- Recall@20
- NDCG@20
- MRR

Metrics are computed per user and then **averaged across all evaluated users**.  
*(Users with no positive items are skipped during ranking evaluation.)*

-------------------------------------

#### Additional classification metric
  
Besides ranking metrics, the script also tracks:
- ROC-AUC

ROC-AUC is used:
- during training
- during hyperparameter search
- for selecting the best model configuration

-------------------------------------

Outputs:
- `nn_bpr_with_net_best.pt` — saved best model checkpoint
- `nn_bpr_with_net_metrics.json` — metrics and best configuration
- `nn_bpr_with_net_roc.png` — train/validation ROC-AUC curve for the best model

-------------------------------------

### Results:

<details> 
<summary>Show results for Neural Network BPR — with_net</summary> 

### Neural Network BPR — with_net:
  
- "mode": "with_net"
- "seed": 42
  
**Best configuration:**
- hidden_channels = 256
- num_layers = 4
- learning_rate = 0.0005
- loss = bpr
  
**Model selection metric:**
- best average validation ROC-AUC = 0.9128

<details> 
<summary>Show validation results</summary>
    
#### Validation results:
  
| Metric | Value |
|---|---:|
| Best validation ROC-AUC | 0.9128 |
| Evaluated users | 28211 |
| HitRate@1 | 0.1841 |
| Recall@1 | 0.1841 |
| NDCG@1 | 0.1841 |
| HitRate@5 | 0.4917 |
| Recall@5 | 0.4917 |
| NDCG@5 | 0.3405 |
| HitRate@10 | 0.6885 |
| Recall@10 | 0.6885 |
| NDCG@10 | 0.4040 |
| HitRate@20 | 0.8804 |
| Recall@20 | 0.8804 |
| NDCG@20 | 0.4528 |
| MRR | 0.3346 |

</details> 
  
<details> 
<summary>Show test results</summary>
    
#### Test results:
  
| Metric | Value |
|---|---:|
| Evaluated users | 28211 |
| HitRate@1 | 0.1952 |
| Recall@1 | 0.1952 |
| NDCG@1 | 0.1952 |
| HitRate@5 | 0.4990 |
| Recall@5 | 0.4990 |
| NDCG@5 | 0.3498 |
| HitRate@10 | 0.6974 |
| Recall@10 | 0.6974 |
| NDCG@10 | 0.4139 |
| HitRate@20 | 0.8821 |
| Recall@20 | 0.8821 |
| NDCG@20 | 0.4608 |
| MRR | 0.3443 |

</details>

<details> 
<summary>Show ROC-AUC plot</summary>
    
#### ROC-AUC plot:
  
<img width="800" height="500" alt="nn_with_net_roc" src="https://github.com/user-attachments/assets/ed9f16a5-9bd2-47b1-9abb-803b02ef84bf" />

</details>
  
</details>
  
-------------------------------------
  
</details>

<details>
<summary>Comparison of approach</summary>

### Comparison of approach

Both runs use the same **Neural Network BPR model** and the same general training pipeline.  
In both cases:

- the target column is `owned`
- training is based on grouped interactions: **1 positive + 10 negatives**
- the loss function is **BPR**
- user and game representations are learned through neural encoders
- final ranking scores are produced by an MLP
- model selection is based on **validation ROC-AUC**
- final evaluation includes ranking metrics

However, the two runs differ in the **underlying cached feature space**.

-------------------------------------

#### 1. Dataset and feature space

The **no_net** version uses cached features without additional network-derived information.

The **with_net** version uses network-enriched cached features, which include additional relational information in the user/game representation space.

*This means the neural architecture is the same, but the underlying input representation is richer in the `with_net` run.*

-------------------------------------

#### 2. Model architecture

Both versions use exactly the same model design:
- user linear encoder
- game numeric projection
- categorical embedding layers
- masked average pooling for multi-value categorical fields
- MLP scoring head

The searched hyperparameters are also identical:
- hidden channels: `64`, `128`, `256`
- layers: `2`, `3`, `4`
- learning rate: `1e-3`, `5e-4`

In both runs, the best configuration was:
- hidden_channels = 256
- num_layers = 4
- learning_rate = 0.0005

-------------------------------------

#### 3. Training objective

Both runs use:
- pairwise **Bayesian Personalized Ranking loss**
- grouped training examples with one positive item and multiple negatives
- mini-batch training with `Adam`
- validation monitoring with ROC-AUC

This differs from the sklearn models in the repository, which are mostly trained as pointwise classifiers and later evaluated as ranking models.

-------------------------------------

#### 4. Training setup

Both runs use the same training procedure:
- 20 epochs
- 200000 sampled groups per epoch
- ReduceLROnPlateau scheduler
- GPU training when available
- cached feature tensors loaded from disk

Unlike the large Logistic Regression network model, these neural runs do **not** use chunked CSV-based training.  
Instead, they rely on precomputed cached tensors and sampled grouped interactions.

-------------------------------------

#### 5. Model selection

A notable difference compared with LR / RF / XGB in the repository is that this model is selected using:

- **average validation ROC-AUC across epochs**

rather than:
- validation NDCG@10

So the neural BPR setup is optimized using a classification-oriented validation signal, while final reporting still includes ranking metrics.

-------------------------------------

#### Summary

The two neural BPR runs use the same architecture, same loss, and same hyperparameter search procedure.

- **`nn_bpr.py no_net`** uses the no-network cached feature representation
- **`nn_bpr.py with_net`** uses the network-enriched cached feature representation

The main difference is therefore the **input representation**, not the training algorithm itself.

</details>
  
<details>
<summary>Comparison of results</summary>  
  
### Comparison of results
  
The table below compares the final **test results** of the two Neural Network BPR runs.
  
| Metric | NN BPR baseline | NN BPR network |
|---|---:|---:|
| Best validation ROC-AUC | 0.9100 | 0.9128 |
| Evaluated users | 28211 | 28211 |
| HitRate@1 | 0.1913 | 0.1952 |
| Recall@1 | 0.1913 | 0.1952 |
| NDCG@1 | 0.1913 | 0.1952 |
| HitRate@5 | 0.4952 | 0.4990 |
| Recall@5 | 0.4952 | 0.4990 |
| NDCG@5 | 0.3459 | 0.3498 |
| HitRate@10 | 0.6909 | 0.6974 |
| Recall@10 | 0.6909 | 0.6974 |
| NDCG@10 | 0.4090 | 0.4139 |
| HitRate@20 | 0.8785 | 0.8821 |
| Recall@20 | 0.8785 | 0.8821 |
| NDCG@20 | 0.4567 | 0.4608 |
| MRR | 0.3402 | 0.3443 |

-------------------------------------
  
#### Key observations
  
Compared with the baseline run, the network version achieves slightly stronger results across all reported ranking metrics.

The improvements are consistent but relatively modest:
- **HitRate@1** increases from **0.1913** to **0.1952**
- **NDCG@10** increases from **0.4090** to **0.4139**
- **MRR** increases from **0.3402** to **0.3443**

This suggests that the network-enriched cached representation provides additional useful information, but the gain is much smaller than in the classical LR / RF / XGB comparisons.

Overall, the **network Neural Network BPR model outperforms the baseline version**, but the margin is limited.

</details>
