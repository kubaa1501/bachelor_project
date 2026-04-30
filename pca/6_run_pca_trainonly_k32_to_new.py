import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

#input paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NPY_PATH = os.path.join(BASE_DIR, "game_game_dists_trainonly_cpu.npy")
MAP_CSV  = os.path.join(BASE_DIR, "game_index_to_gameid_20988.csv")

# output path 
OUT_DIR = "/home/anci/new/pca_k32_trainonly"
os.makedirs(OUT_DIR, exist_ok=True)

# PCA settings
K_FIXED = 32
DTYPE = np.float32
USE_LOG = True

OUT_EMB = os.path.join(OUT_DIR, f"game_pca_embeddings_k{K_FIXED}_trainonly.csv")
OUT_PNG = os.path.join(OUT_DIR, f"pca_cumulative_plot_k{K_FIXED}_trainonly.png")

# load game-game distance matrix
# rows/columns = games
print("Loading npy memmap:", NPY_PATH)
M = np.load(NPY_PATH, mmap_mode="r")
N = int(M.shape[0])
print("Matrix shape:", M.shape, "dtype:", M.dtype)

# materialize the memmap as a dense float32 matrix
# PCA needs the actual matrix in memory
print("Materializing dense matrix...")
S = np.array(M, dtype=DTYPE, copy=True)

# make sure the distance matrix is symmetric
# diagonal is set to 0 because distance(game, same game) should be 0
print("Symmetrizing + zero diagonal...")
S = (S + S.T).astype(DTYPE, copy=False)
np.fill_diagonal(S, 0)

# basic data checks before transformation
print("Sanity checks:")
print("NaNs:", int(np.isnan(S).sum()), "min:", float(np.min(S)), "max:", float(np.max(S)))

# optional log transform
# compresses very large distances so PCA is not dominated by extreme values
if USE_LOG:
    print("Applying log1p...")
    S = np.log1p(S).astype(DTYPE, copy=False)

# standardize each feature/column before PCA
# PCA is scale-sensitive, so this keeps columns comparable
print("Standardizing...")
scaler = StandardScaler(with_mean=True, with_std=True)
S_scaled = scaler.fit_transform(S).astype(DTYPE, copy=False)
del S

# fit PCA with fixed number of components (32)
K = int(min(K_FIXED, N))
print(f"Fitting PCA with K={K} ...")

pca = PCA(n_components=K, svd_solver="randomized", random_state=42)
Z = pca.fit_transform(S_scaled)

# explained variance for reporting
explained = pca.explained_variance_ratio_
cumulative = np.cumsum(explained)
achieved = float(cumulative[-1])

print(f"Explained variance @K={K}: {achieved:.6f} ({achieved*100:.2f}%)")

# plot cumulative explained variance
plt.figure(figsize=(8, 5))
plt.plot(np.arange(1, K + 1), cumulative * 100, marker="o")
plt.axvline(x=K, linestyle="--")
plt.axhline(y=achieved * 100, linestyle="--")
plt.xlabel("Number of Components (k)")
plt.ylabel("Cumulative Explained Variance (%)")
plt.title(f"PCA Cumulative Explained Variance (K={K})")
plt.tight_layout()
plt.savefig(OUT_PNG, dpi=200)
plt.close()
print("Saved plot:", OUT_PNG)

# build final game embedding dataframe
# each game gets K PCA dimensions
E = Z.astype(DTYPE, copy=False)

df = pd.DataFrame(E, columns=[f"game_emb_{i}" for i in range(K)])
df["game_index"] = np.arange(N, dtype=np.int64)

# add appid using game_index -> game_id mapping
m = pd.read_csv(MAP_CSV)

if "matrix_index" in m.columns and "game_id" in m.columns:
    m = m.rename(columns={"matrix_index": "game_index", "game_id": "appid"})
    df = df.merge(m[["game_index", "appid"]], on="game_index", how="left")
else:
    print("WARNING: mapping columns unexpected:", m.columns.tolist())

# save final PCA game embeddings
df.to_csv(OUT_EMB, index=False)

print("Saved embeddings:", OUT_EMB)