import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# ======================================
# SETTINGS
# ======================================

FILE_PATH = r"D:\bachelor_project\micheles_algorithm\new_version\game_game_dists_sq_20988.mmap"

USE_LOG = True
VARIANCE_THRESHOLD = 0.90
MAX_COMPONENTS = 500  # Safety cap for PCA; adjust depending on RAM

OUTPUT_FILE = r"D:\bachelor_project\micheles_algorithm\new_version\game_pca_embeddings_full.csv"

# ======================================
# 1️⃣ LOAD FULL MATRIX
# ======================================

print("Loading full memory-mapped matrix...")
matrix = np.memmap(FILE_PATH, dtype=np.float32, mode='r', shape=(20988, 20988))
print("Matrix shape:", matrix.shape)

# ======================================
# 2️⃣ RECONSTRUCT SYMMETRIC MATRIX
# ======================================

print("\nReconstructing symmetric matrix...")
S = matrix + matrix.T
np.fill_diagonal(S, 0)
print("Symmetric matrix created. Shape:", S.shape)

# ======================================
# 3️⃣ SANITY CHECKS
# ======================================

print("\nSanity checks (before normalization):")
print("Any NaNs?", np.isnan(S).sum())
print("Min value:", np.min(S))
print("Max value:", np.max(S))
print("Matrix symmetric check:", np.allclose(S, S.T))

# ======================================
# 4️⃣ LOG NORMALIZATION
# ======================================

if USE_LOG:
    print("\nApplying log1p normalization...")
    S = np.log1p(S)
    print("Min value:", np.min(S))
    print("Max value:", np.max(S))

# ======================================
# 5️⃣ STANDARDIZE FEATURES
# ======================================

print("\nStandardizing features...")
scaler = StandardScaler()
S_scaled = scaler.fit_transform(S)
print("Mean (should ~0):", np.mean(S_scaled))
print("Std (should ~1):", np.std(S_scaled))

# ======================================
# 6️⃣ PCA
# ======================================

print("\nFitting PCA...")

pca = PCA(
    n_components=min(MAX_COMPONENTS, S_scaled.shape[1]),
    svd_solver='randomized',
    random_state=42
)

S_reduced_full = pca.fit_transform(S_scaled)

explained = pca.explained_variance_ratio_
cumulative = np.cumsum(explained)

# ======================================
# 7️⃣ AUTOMATIC COMPONENT SELECTION
# ======================================

optimal_components = np.argmax(cumulative >= VARIANCE_THRESHOLD) + 1

print(f"\nVariance threshold: {VARIANCE_THRESHOLD}")
print(f"Optimal number of components: {optimal_components}")
print(f"Achieved variance: {cumulative[optimal_components - 1]:.4f}")

game_embeddings = S_reduced_full[:, :optimal_components]
print("Final embedding shape:", game_embeddings.shape)

# ======================================
# 8️⃣ SANITY CHECKS AFTER PCA
# ======================================

print("\nSanity checks (after PCA):")
print("Any NaNs?", np.isnan(game_embeddings).sum())
print("Embedding mean (should ~0):", np.mean(game_embeddings))
print("Embedding std:", np.std(game_embeddings))

# ======================================
# 9️⃣ SCREE PLOT
# ======================================

plt.figure(figsize=(8,5))
plt.plot(cumulative)
plt.axhline(y=VARIANCE_THRESHOLD, linestyle='--')
plt.axvline(x=optimal_components, linestyle='--')
plt.xlabel("Number of Components")
plt.ylabel("Cumulative Explained Variance")
plt.title("PCA Explained Variance (Full Matrix)")
plt.show()

# ======================================
# 🔟 SAVE FULL EMBEDDINGS
# ======================================

embedding_df = pd.DataFrame(
    game_embeddings,
    columns=[f"game_emb_{i}" for i in range(optimal_components)]
)
embedding_df["game_index"] = embedding_df.index
embedding_df.to_csv(OUTPUT_FILE, index=False)

print(f"\nEmbeddings saved to {OUTPUT_FILE}")