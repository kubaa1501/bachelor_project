#### train-test-split
import os
import numpy as np
import pandas as pd
from tqdm import tqdm

SEED = 42
np.random.seed(SEED)

DATA_FILE = "baseline/baseline_dataset.csv"
OUT_DIR = "outputs_baseline_full"
DATA_DIR = os.path.join(OUT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

TEST_FRAC_PER_USER = 0.2

TRAIN_OUT_PARQUET = os.path.join(DATA_DIR, "train_all.parquet")
TEST_OUT_PARQUET  = os.path.join(DATA_DIR, "test_all.parquet")
TRAIN_OUT_CSV = os.path.join(DATA_DIR, "train_all.csv")
TEST_OUT_CSV  = os.path.join(DATA_DIR, "test_all.csv")

def rebalance(df_):
    pos = df_[df_["owned"] == 1]
    neg = df_[df_["owned"] == 0]
    if len(pos) == 0 or len(neg) == 0:
        return df_
    if len(neg) >= len(pos):
        neg = neg.sample(n=len(pos), random_state=SEED)
    else:
        pos = pos.sample(n=len(neg), random_state=SEED)
    return pd.concat([pos, neg], ignore_index=True).sample(frac=1, random_state=SEED).reset_index(drop=True)

def attach_features(pairs_df, users_features, games_features):
    out = pairs_df.merge(users_features, on="steamid", how="left")
    out = out.merge(games_features, on="appid", how="left")
    return out

print(f"Loading: {DATA_FILE}")
df = pd.read_csv(DATA_FILE, sep=",", quotechar='"')
print("Original shape:", df.shape)
print("Unique users:", df["steamid"].nunique())
print("Unique games:", df["appid"].nunique())

# user/game features
users_features = df[['steamid', 'country', 'total_games_owned',
                     'total_playtime_minutes', 'median_playtime_minutes',
                     'unique_genres_played', 'user_count']].drop_duplicates('steamid')

games_features = df[['appid', 'name', 'genres', 'developer',
                     'publisher', 'platforms', 'release_date',
                     'game_total_playtime_minutes']].drop_duplicates('appid')

positives = df[['steamid', 'appid']].drop_duplicates()
positives["owned"] = 1

all_games = np.array(sorted(df["appid"].unique()))
user_owned = positives.groupby("steamid")["appid"].apply(lambda s: np.array(s.values)).to_dict()

train_pairs, test_pairs, neg_train_pairs, neg_test_pairs = [], [], [], []

print("Building per-user train/test with negative sampling...")
for user, owned_games in tqdm(user_owned.items(), desc="Users"):
    owned_games = np.unique(owned_games)

    # split positives for this user
    if len(owned_games) < 2:
        pos_train = owned_games
        pos_test = np.array([], dtype=owned_games.dtype)
    else:
        rng = np.random.default_rng(SEED + int(user) % 100000)
        shuffled = owned_games.copy()
        rng.shuffle(shuffled)
        n_test = max(1, int(np.ceil(TEST_FRAC_PER_USER * len(shuffled))))
        pos_test = shuffled[:n_test]
        pos_train = shuffled[n_test:]

    train_pairs.extend([(user, g, 1) for g in pos_train])
    test_pairs.extend([(user, g, 1) for g in pos_test])

    # negatives
    not_owned = all_games[~np.isin(all_games, owned_games)]
    if len(not_owned) == 0:
        continue

    n_neg_train = len(pos_train)
    n_neg_test = len(pos_test)

    # sample negative test first
    if n_neg_test > 0:
        replace_test = len(not_owned) < n_neg_test
        neg_test = np.random.choice(not_owned, size=n_neg_test, replace=replace_test)
        neg_test_set = set(map(int, neg_test))
    else:
        neg_test = np.array([], dtype=not_owned.dtype)
        neg_test_set = set()

    # sample negative train excluding test negatives
    train_pool = np.array([g for g in not_owned if int(g) not in neg_test_set])
    if len(train_pool) == 0:
        train_pool = not_owned

    if n_neg_train > 0:
        replace_train = len(train_pool) < n_neg_train
        neg_train = np.random.choice(train_pool, size=n_neg_train, replace=replace_train)
    else:
        neg_train = np.array([], dtype=not_owned.dtype)

    neg_train_pairs.extend([(user, g, 0) for g in neg_train])
    neg_test_pairs.extend([(user, g, 0) for g in neg_test])

train_df = pd.DataFrame(train_pairs + neg_train_pairs, columns=["steamid", "appid", "owned"])
test_df  = pd.DataFrame(test_pairs  + neg_test_pairs,  columns=["steamid", "appid", "owned"])

# dedup
train_before, test_before = len(train_df), len(test_df)
train_df = train_df.drop_duplicates(subset=["steamid","appid"], keep="last").reset_index(drop=True)
test_df  = test_df.drop_duplicates(subset=["steamid","appid"], keep="last").reset_index(drop=True)
print("Dedup removed train:", train_before - len(train_df), "test:", test_before - len(test_df))

# overlap sanity
overlap = pd.merge(
    train_df[["steamid","appid"]],
    test_df[["steamid","appid"]],
    on=["steamid","appid"],
    how="inner"
)
print("Overlap train/test unique pairs:", len(overlap))

# rebalance 1:1
train_df = rebalance(train_df)
test_df  = rebalance(test_df)
print("After rebalance:",
      "train pos", int(train_df["owned"].sum()), "train neg", int((train_df["owned"]==0).sum()),
      "| test pos", int(test_df["owned"].sum()), "test neg", int((test_df["owned"]==0).sum()))

# attach features
train_all = attach_features(train_df, users_features, games_features)
test_all  = attach_features(test_df,  users_features, games_features)

print("Saving split to:", DATA_DIR)
try:
    train_all.to_parquet(TRAIN_OUT_PARQUET, index=False)
    test_all.to_parquet(TEST_OUT_PARQUET, index=False)
    print("Saved parquet:", TRAIN_OUT_PARQUET, TEST_OUT_PARQUET)
except Exception as e:
    print("Parquet failed (likely missing pyarrow/fastparquet). Falling back to CSV.")
    print("Reason:", repr(e))
    train_all.to_csv(TRAIN_OUT_CSV, index=False)
    test_all.to_csv(TEST_OUT_CSV, index=False)
    print("Saved CSV:", TRAIN_OUT_CSV, TEST_OUT_CSV)

print("DONE.")

#### train LR ####
import os, json, joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.linear_model import LogisticRegression

SEED = 42
SCORING = "roc_auc"
N_ITER = int(os.getenv("N_ITER", "10"))
CV_SPLITS = int(os.getenv("CV_SPLITS", "3"))

OUT_DIR = "outputs_baseline_full"
DATA_DIR = os.path.join(OUT_DIR, "data")
MODELS_DIR = os.path.join(OUT_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

TRAIN_CSV = os.path.join(DATA_DIR, "train_all.csv")
TEST_CSV  = os.path.join(DATA_DIR, "test_all.csv")

numeric_features = [
    "total_games_owned","total_playtime_minutes","median_playtime_minutes",
    "unique_genres_played","user_count","game_total_playtime_minutes"
]
categorical_features = ["country","developer","publisher","platforms","genres"]
target = "owned"
usecols = ["steamid","appid",target] + numeric_features + categorical_features

dtypes = {
    "steamid": "int64",
    "appid": "int32",
    "owned": "int8",
    "total_games_owned": "float32",
    "total_playtime_minutes": "float32",
    "median_playtime_minutes": "float32",
    "unique_genres_played": "float32",
    "user_count": "float32",
    "game_total_playtime_minutes": "float32",
    "country": "object",
    "developer": "object",
    "publisher": "object",
    "platforms": "object",
    "genres": "object",
}

print("Loading CSV (train/test) with selected columns...")
train_all = pd.read_csv(TRAIN_CSV, usecols=usecols, dtype=dtypes)
test_all  = pd.read_csv(TEST_CSV,  usecols=usecols, dtype=dtypes)

X_train = train_all[numeric_features + categorical_features].copy()
y_train = train_all[target].astype(int).copy()
X_test  = test_all[numeric_features + categorical_features].copy()
y_test  = test_all[target].astype(int).copy()

# ---- FIX: sklearn prefers np.nan over pd.NA (pandas 'string' dtype uses pd.NA) ----
X_train = X_train.replace({pd.NA: np.nan})
X_test  = X_test.replace({pd.NA: np.nan})

print("y_train counts:", np.bincount(y_train))

numeric_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")),
                         ("scaler", StandardScaler())])
categorical_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                             ("onehot", OneHotEncoder(handle_unknown="ignore"))])

preprocessor = ColumnTransformer([
    ("num", numeric_pipe, numeric_features),
    ("cat", categorical_pipe, categorical_features),
])

cv = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=SEED)

pipe = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LogisticRegression(max_iter=2000, random_state=SEED))
])

params = {"model__C": np.logspace(-3, 2, 20)}

search = RandomizedSearchCV(
    pipe, params,
    n_iter=min(N_ITER, 20),
    scoring=SCORING, cv=cv,
    random_state=SEED,
    n_jobs=1, verbose=1, error_score=np.nan
)

search.fit(X_train, y_train)
best = search.best_estimator_

y_pred = best.predict(X_test)
y_proba = best.predict_proba(X_test)[:, 1]

metrics = {
    "accuracy": float(accuracy_score(y_test, y_pred)),
    "precision": float(precision_score(y_test, y_pred, zero_division=0)),
    "recall": float(recall_score(y_test, y_pred, zero_division=0)),
    "f1": float(f1_score(y_test, y_pred, zero_division=0)),
    "roc_auc": float(roc_auc_score(y_test, y_proba)),
    "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
}

model_path = os.path.join(MODELS_DIR, "LogisticRegression_best.joblib")
joblib.dump(best, model_path)

row = {
    "model": "LogisticRegression",
    "best_cv_score": float(search.best_score_),
    "best_params": json.dumps(search.best_params_),
    **metrics,
    "model_path": model_path
}

out_csv = os.path.join(OUT_DIR, "results_lr.csv")
pd.DataFrame([row]).to_csv(out_csv, index=False)

print("Saved:", out_csv)
print(row)

#### train RF############

import os, json, joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier

SEED = 42
SCORING = "roc_auc"
N_ITER = int(os.getenv("N_ITER", "8"))          # RF is heavy; 8 is ok baseline
CV_SPLITS = int(os.getenv("CV_SPLITS", "3"))
RF_NJOBS = int(os.getenv("RF_NJOBS", "16"))

OUT_DIR = "outputs_baseline_full"
DATA_DIR = os.path.join(OUT_DIR, "data")
MODELS_DIR = os.path.join(OUT_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

TRAIN_CSV = os.path.join(DATA_DIR, "train_all.csv")
TEST_CSV  = os.path.join(DATA_DIR, "test_all.csv")

numeric_features = [
    "total_games_owned","total_playtime_minutes","median_playtime_minutes",
    "unique_genres_played","user_count","game_total_playtime_minutes"
]
categorical_features = ["country","developer","publisher","platforms","genres"]
target = "owned"
usecols = ["steamid","appid",target] + numeric_features + categorical_features

dtypes = {
    "steamid": "int64",
    "appid": "int32",
    "owned": "int8",
    "total_games_owned": "float32",
    "total_playtime_minutes": "float32",
    "median_playtime_minutes": "float32",
    "unique_genres_played": "float32",
    "user_count": "float32",
    "game_total_playtime_minutes": "float32",
    "country": "object",
    "developer": "object",
    "publisher": "object",
    "platforms": "object",
    "genres": "object",
}

print("Loading CSV (train/test) with selected columns...")
train_all = pd.read_csv(TRAIN_CSV, usecols=usecols, dtype=dtypes)
test_all  = pd.read_csv(TEST_CSV,  usecols=usecols, dtype=dtypes)

X_train = train_all[numeric_features + categorical_features].copy()
y_train = train_all[target].astype(int).copy()
X_test  = test_all[numeric_features + categorical_features].copy()
y_test  = test_all[target].astype(int).copy()

# ---- FIX: sklearn prefers np.nan over pd.NA ----
X_train = X_train.replace({pd.NA: np.nan})
X_test  = X_test.replace({pd.NA: np.nan})

print("y_train counts:", np.bincount(y_train))

numeric_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")),
                         ("scaler", StandardScaler())])
categorical_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                             ("onehot", OneHotEncoder(handle_unknown="ignore"))])

preprocessor = ColumnTransformer([
    ("num", numeric_pipe, numeric_features),
    ("cat", categorical_pipe, categorical_features),
])

cv = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=SEED)

rf = RandomForestClassifier(
    n_estimators=400,
    random_state=SEED,
    n_jobs=RF_NJOBS
)

pipe = Pipeline([("preprocessor", preprocessor),
                 ("model", rf)])

params = {
    "model__max_depth": [None, 24],
    "model__min_samples_split": [2, 10],
    "model__min_samples_leaf": [1, 2],
    "model__max_features": ["sqrt", None],
}

search = RandomizedSearchCV(
    pipe, params,
    n_iter=min(N_ITER, 12),
    scoring=SCORING, cv=cv,
    random_state=SEED,
    n_jobs=1, verbose=1, error_score=np.nan
)

search.fit(X_train, y_train)
best = search.best_estimator_

y_pred = best.predict(X_test)
y_proba = best.predict_proba(X_test)[:, 1]

metrics = {
    "accuracy": float(accuracy_score(y_test, y_pred)),
    "precision": float(precision_score(y_test, y_pred, zero_division=0)),
    "recall": float(recall_score(y_test, y_pred, zero_division=0)),
    "f1": float(f1_score(y_test, y_pred, zero_division=0)),
    "roc_auc": float(roc_auc_score(y_test, y_proba)),
    "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
}

model_path = os.path.join(MODELS_DIR, "RandomForest_best.joblib")
joblib.dump(best, model_path)

row = {
    "model": "RandomForest",
    "best_cv_score": float(search.best_score_),
    "best_params": json.dumps(search.best_params_),
    **metrics,
    "model_path": model_path
}

out_csv = os.path.join(OUT_DIR, "results_rf.csv")
pd.DataFrame([row]).to_csv(out_csv, index=False)

print("Saved:", out_csv)
print(row)


#### train XGB #############

import os, json, joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from xgboost import XGBClassifier

SEED = 42
SCORING = "roc_auc"
N_ITER = int(os.getenv("N_ITER", "10"))
CV_SPLITS = int(os.getenv("CV_SPLITS", "3"))
USE_XGB_GPU = os.getenv("USE_XGB_GPU", "1") == "1"

OUT_DIR = "outputs_baseline_full"
DATA_DIR = os.path.join(OUT_DIR, "data")
MODELS_DIR = os.path.join(OUT_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

TRAIN_CSV = os.path.join(DATA_DIR, "train_all.csv")
TEST_CSV  = os.path.join(DATA_DIR, "test_all.csv")

numeric_features = [
    "total_games_owned","total_playtime_minutes","median_playtime_minutes",
    "unique_genres_played","user_count","game_total_playtime_minutes"
]
categorical_features = ["country","developer","publisher","platforms","genres"]
target = "owned"
usecols = ["steamid","appid",target] + numeric_features + categorical_features

dtypes = {
    "steamid": "int64",
    "appid": "int32",
    "owned": "int8",
    "total_games_owned": "float32",
    "total_playtime_minutes": "float32",
    "median_playtime_minutes": "float32",
    "unique_genres_played": "float32",
    "user_count": "float32",
    "game_total_playtime_minutes": "float32",
    "country": "object",
    "developer": "object",
    "publisher": "object",
    "platforms": "object",
    "genres": "object",
}

print("Loading CSV (train/test) with selected columns...")
train_all = pd.read_csv(TRAIN_CSV, usecols=usecols, dtype=dtypes)
test_all  = pd.read_csv(TEST_CSV,  usecols=usecols, dtype=dtypes)

X_train = train_all[numeric_features + categorical_features].copy()
y_train = train_all[target].astype(int).copy()
X_test  = test_all[numeric_features + categorical_features].copy()
y_test  = test_all[target].astype(int).copy()

# ---- FIX: sklearn prefers np.nan over pd.NA ----
X_train = X_train.replace({pd.NA: np.nan})
X_test  = X_test.replace({pd.NA: np.nan})

print("y_train counts:", np.bincount(y_train))

numeric_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")),
                         ("scaler", StandardScaler())])
categorical_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                             ("onehot", OneHotEncoder(handle_unknown="ignore"))])

preprocessor = ColumnTransformer([
    ("num", numeric_pipe, numeric_features),
    ("cat", categorical_pipe, categorical_features),
])

cv = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=SEED)

xgb = XGBClassifier(
    eval_metric="logloss",
    random_state=SEED,
    n_estimators=600,
    learning_rate=0.05,
    tree_method="hist",
    device="cpu",
)
pipe = Pipeline([("preprocessor", preprocessor),
                 ("model", xgb)])

params = {
    "model__max_depth": [4, 6, 8],
    "model__subsample": [0.6, 0.8],
    "model__colsample_bytree": [0.6, 0.8],
    "model__reg_lambda": [1.0, 2.0],
}

search = RandomizedSearchCV(
    pipe, params,
    n_iter=min(N_ITER, 12),
    scoring=SCORING, cv=cv,
    random_state=SEED,
    n_jobs=1, verbose=1, error_score=np.nan
)

search.fit(X_train, y_train)
best = search.best_estimator_

p = best.named_steps["model"].get_params()
print("XGB tree_method:", p.get("tree_method"), "| device:", p.get("device"))

y_pred = best.predict(X_test)
y_proba = best.predict_proba(X_test)[:, 1]

metrics = {
    "accuracy": float(accuracy_score(y_test, y_pred)),
    "precision": float(precision_score(y_test, y_pred, zero_division=0)),
    "recall": float(recall_score(y_test, y_pred, zero_division=0)),
    "f1": float(f1_score(y_test, y_pred, zero_division=0)),
    "roc_auc": float(roc_auc_score(y_test, y_proba)),
    "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
}

model_path = os.path.join(MODELS_DIR, "XGBoost_best.joblib")
joblib.dump(best, model_path)

row = {
    "model": "XGBoost",
    "best_cv_score": float(search.best_score_),
    "best_params": json.dumps(search.best_params_),
    **metrics,
    "model_path": model_path
}

out_csv = os.path.join(OUT_DIR, "results_xgb.csv")
pd.DataFrame([row]).to_csv(out_csv, index=False)

print("Saved:", out_csv)
print(row)


