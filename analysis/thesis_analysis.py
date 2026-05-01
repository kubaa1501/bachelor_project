import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
from collections import defaultdict
import torch

# ── paths ─────────────────────────────────────────────────────────────────
BASE        = "/home/jaga"
TEST_CSV    = f"{BASE}/data/sets/with_net_feat/test.csv"
BASE_SCORES = f"{BASE}/results/metrics/xgboost_test_scores.csv"
EMB_SCORES  = f"{BASE}/results/metrics/xgboost_test_scores_one_embedding.csv"
GRAPH_PT    = f"{BASE}/data/cache/graph.pt"
GAME2IDX_PT = f"{BASE}/data/cache/game2idx.pt"
GRAPH_STRUCT_CSV = f"{BASE}/results/graph_structure/per_game_with_structure.csv"
OUTDIR      = f"{BASE}/results/thesis_analysis/plots"
os.makedirs(OUTDIR, exist_ok=True)

# ── genre grouping ────────────────────────────────────────────────────────
genre_groups = {
    "Action":      ['Action','Acción','Akcja','Aksiyon','Actie','Akční','Экшены','動作'],
    "Adventure":   ['Adventure','Aventura','Avontuur','冒险','Приключенческие игры','Macera'],
    "RPG":         ['RPG','RYO','Ролевые игры','角色扮演'],
    "Casual":      ['Casual','Occasionnel','Казуальные игры'],
    "Indie":       ['Indie','Indépendant','独立','Инди'],
    "Racing":      ['Racing','Rol'],
    "Simulation":  ['Simulation','Simuladores','Symulacje','Симуляторы'],
    "Strategy":    ['Strategy','Strategie','Стратегии'],
    "Sports":      ['Sport','Sports'],
    "Violent":     ['Gore','Violent'],
    "Adult":       ['Nudity','Sexual Content'],
    "Non-gameplay/Tools": ['Education','Documentary','Movie','Tutorial','Accounting',
                           'Audio Production','Video Production','Photo Editing',
                           'Design & Illustration','Web Publishing','Utilities',
                           'Software Training','Game Development','Animation & Modeling'],
    "Other":       ['Early Access','Episodic','Free To Play',
                    'Massively Multiplayer','Бесплатные'],
}
raw_to_group = {m: g for g, members in genre_groups.items() for m in members}

FONT_SIZE_TICK  = 11
FONT_SIZE_LABEL = 12
FONT_SIZE_TITLE = 13
FONT_SIZE_ANNOT = 9

matplotlib.rcParams.update({
    'font.size':        FONT_SIZE_TICK,
    'axes.titlesize':   FONT_SIZE_TITLE,
    'axes.labelsize':   FONT_SIZE_LABEL,
    'xtick.labelsize':  FONT_SIZE_TICK,
    'ytick.labelsize':  FONT_SIZE_TICK,
    'axes.titleweight': 'normal',
})

def savefig(name):
    path = os.path.join(OUTDIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"  saved → {path}", flush=True)

# ════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ════════════════════════════════════════════════════════════════════════════
print("Loading data...", flush=True)
test        = pd.read_csv(TEST_CSV, sep=";")
base_scores = pd.read_csv(BASE_SCORES)
emb_scores  = pd.read_csv(EMB_SCORES)

base_m = test.merge(base_scores, on=["steamid","appid","owned"], how="inner")
emb_m  = test.merge(emb_scores,  on=["steamid","appid","owned"], how="inner")

merged = base_m[["steamid","appid","owned","score",
                  "game_emb_0","user_count",
                  "game_total_playtime_minutes","genres"]].rename(
    columns={"score":"score_base"}).copy()
merged["score_emb"] = emb_m["score"].values
merged["delta"]     = merged["score_emb"] - merged["score_base"]

owned_1 = merged[merged["owned"] == 1].copy()
owned_0 = merged[merged["owned"] == 0].copy()
print(f"owned=1: {len(owned_1):,}   owned=0: {len(owned_0):,}", flush=True)

# ── load graph for degree ─────────────────────────────────────────────────
print("Loading graph...", flush=True)
graph    = torch.load(GRAPH_PT, map_location="cpu")
game2idx = torch.load(GAME2IDX_PT, map_location="cpu")
idx2game = {int(v): int(k) for k, v in game2idx.items()}
plays_edge    = graph[("user","plays","game")].edge_index.numpy()
game_nodes    = plays_edge[1]
game_degree_arr = np.bincount(game_nodes, minlength=len(game2idx))
degree_map = {idx2game[i]: int(game_degree_arr[i])
              for i in range(len(game2idx))}
merged["graph_degree"] = merged["appid"].map(degree_map)
owned_1 = merged[merged["owned"] == 1].copy()
owned_0 = merged[merged["owned"] == 0].copy()

# ════════════════════════════════════════════════════════════════════════════
# METRICS
# ════════════════════════════════════════════════════════════════════════════
print("\nComputing metrics...", flush=True)

n_test_rows = len(merged)
n_games     = merged["appid"].nunique()
n_users     = merged["steamid"].nunique()

score_separation_baseline = (
    base_m.loc[base_m["owned"]==1,"score"].mean() -
    base_m.loc[base_m["owned"]==0,"score"].mean()
)
score_separation_emb0 = (
    emb_m.loc[emb_m["owned"]==1,"score"].mean() -
    emb_m.loc[emb_m["owned"]==0,"score"].mean()
)

# per-game delta for correlations
game_delta = merged.groupby("appid")["delta"].mean().reset_index(name="mean_delta")
emb0_per_game   = merged.groupby("appid")["game_emb_0"].mean().reset_index(name="game_emb_0")
degree_per_game = game_delta.merge(
    merged[["appid","graph_degree"]].drop_duplicates("appid"), on="appid", how="left")
emb0_deg = game_delta.merge(emb0_per_game, on="appid").merge(
    merged[["appid","graph_degree"]].drop_duplicates("appid"), on="appid")

spearman_delta_vs_emb0, _       = spearmanr(
    emb0_deg["mean_delta"], emb0_deg["game_emb_0"])
spearman_delta_vs_graph_degree, _ = spearmanr(
    emb0_deg["mean_delta"].dropna(), emb0_deg.loc[emb0_deg["mean_delta"].notna(),"graph_degree"])
spearman_emb0_vs_graph_degree, _  = spearmanr(
    emb0_deg["game_emb_0"], emb0_deg["graph_degree"])

# partial spearman: emb0 vs delta controlling for log(degree)
from scipy.stats import rankdata
_df = emb0_deg.dropna(subset=["mean_delta","game_emb_0","graph_degree"]).copy()
_df["log_degree"] = np.log1p(_df["graph_degree"])
def partial_spearman(x, y, z):
    """Partial Spearman correlation of x,y controlling for z."""
    rx = rankdata(x); ry = rankdata(y); rz = rankdata(z)
    rx_res = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ry_res = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    rho, _ = spearmanr(rx_res, ry_res)
    return rho

partial_spearman_emb0_controlling_deg = partial_spearman(
    _df["game_emb_0"], _df["mean_delta"], _df["log_degree"])

# Top 10 recommendation overlap
print("  Computing Top 10 overlap...", flush=True)
overlap_rows = []
for uid, g in base_m.groupby("steamid"):
    top_base = g.nlargest(10,"score")["appid"].tolist()
    top_emb  = emb_m[emb_m["steamid"]==uid].nlargest(10,"score")["appid"].tolist()
    overlap_rows.append(len(set(top_base) & set(top_emb)))
mean_top10_overlap = np.mean(overlap_rows)

# rank of owned game per user
print("  Computing rank of owned game...", flush=True)
rank_base_list = []
rank_emb_list  = []
promoted_list  = []
for uid, g_base in base_m.groupby("steamid"):
    pos_base = g_base[g_base["owned"]==1]
    if pos_base.empty:
        continue
    g_emb = emb_m[emb_m["steamid"]==uid]
    # rank: 1 = highest score
    g_base_sorted = g_base.sort_values("score",ascending=False).reset_index(drop=True)
    g_emb_sorted  = g_emb.sort_values("score",ascending=False).reset_index(drop=True)
    owned_appid   = pos_base["appid"].iloc[0]
    rank_b = g_base_sorted.index[g_base_sorted["appid"]==owned_appid].tolist()
    rank_e = g_emb_sorted.index[g_emb_sorted["appid"]==owned_appid].tolist()
    if rank_b and rank_e:
        rank_base_list.append(rank_b[0]+1)
        rank_emb_list.append(rank_e[0]+1)
        promoted_list.append(rank_e[0] < rank_b[0])

mean_rank_base           = np.mean(rank_base_list)
mean_rank_emb0           = np.mean(rank_emb_list)
percent_positives_promoted = np.mean(promoted_list)

metrics = {
    "n_test_rows":                         n_test_rows,
    "n_games":                             n_games,
    "n_users":                             n_users,
    "score_separation_baseline":           score_separation_baseline,
    "score_separation_emb0":               score_separation_emb0,
    "spearman_delta_vs_emb0":              spearman_delta_vs_emb0,
    "spearman_delta_vs_graph_degree":      spearman_delta_vs_graph_degree,
    "spearman_emb0_vs_graph_degree":       spearman_emb0_vs_graph_degree,
    "partial_spearman_emb0_controlling_deg": partial_spearman_emb0_controlling_deg,
    "mean_top10_overlap":                  mean_top10_overlap,
    "mean_rank_base":                      mean_rank_base,
    "mean_rank_emb0":                      mean_rank_emb0,
    "percent_positives_promoted":          percent_positives_promoted,
}

print("\nMETRICS:")
for k, v in metrics.items():
    print(f"  {k}: {v}")

metrics_df = pd.DataFrame([metrics])
metrics_df.to_csv(f"{BASE}/results/thesis_analysis/metrics_summary.csv", index=False)

# ════════════════════════════════════════════════════════════════════════════
# PLOT A — Extended correlations, separated owned=1 / owned=0
# ════════════════════════════════════════════════════════════════════════════
print("\nPlot A: extended correlations separated...", flush=True)

graph_struct = pd.read_csv(
    GRAPH_STRUCT_CSV,
    usecols=["appid","graph_degree","clustering_coeff",
             "second_order_size","friend_reach_2hop",
             "mean_owner_game_deg","mean_owner_friend_deg",
             "mainstream_overlap","game_emb_0","user_count"]
)

features_to_correlate = [
    ("graph_degree",         "Graph degree"),
    ("game_emb_0",           "Game embedding 0"),
    ("user_count",           "User count"),
    ("clustering_coeff",     "Clustering coefficient"),
    ("second_order_size",    "2nd-order neighborhood"),
    ("friend_reach_2hop",    "2-hop friend reach"),
    ("mean_owner_game_deg",  "Mean owner library size"),
    ("mean_owner_friend_deg","Mean owner friend count"),
    ("mainstream_overlap",   "Mainstream overlap"),
]

def compute_corrs(df_subset, struct_df, feat_list):
    game_delta_local = df_subset.groupby("appid")["delta"].mean().reset_index()
    game_delta_local = game_delta_local.merge(struct_df, on="appid", how="left")
    rows = []
    for col, label in feat_list:
        if col not in game_delta_local.columns:
            continue
        valid = game_delta_local[["delta", col]].dropna()
        if len(valid) < 10:
            continue
        rho, p = spearmanr(valid["delta"], valid[col])
        rows.append({"feature": label, "rho": rho, "p": p})
    return pd.DataFrame(rows)

corr_1_ext = compute_corrs(owned_1, graph_struct, features_to_correlate)
corr_0_ext = compute_corrs(owned_0, graph_struct, features_to_correlate)

order_ext = corr_0_ext.sort_values("rho")["feature"].tolist()

fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)
for ax, cdf, label in [
    (axes[0], corr_1_ext, "Owned games (owned=1)"),
    (axes[1], corr_0_ext, "Non-owned games (owned=0)"),
]:
    cdf = cdf.set_index("feature").reindex(order_ext).reset_index()
    colors = ["#1a9850" if r > 0 else "#d73027" for r in cdf["rho"]]
    bars = ax.barh(cdf["feature"], cdf["rho"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    for bar, rho in zip(bars, cdf["rho"]):
        if pd.isna(rho):
            continue
        ax.text(rho + (0.01 if rho >= 0 else -0.01),
                bar.get_y() + bar.get_height()/2,
                f"{rho:+.3f}", va="center",
                ha="left" if rho >= 0 else "right", fontsize=FONT_SIZE_ANNOT)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Spearman ρ with mean Δscore (network − baseline)")
    ax.set_title(label)

plt.suptitle("Graph structure correlations with score change\n"
             "Left: for the game the user actually owns  |  "
             "Right: for games the user does not own",
             y=1.02)
savefig("PA_extended_corr_separated.png")

# ════════════════════════════════════════════════════════════════════════════
# PLOT B — Δscore vs popularity, separated, colored by delta sign
# ════════════════════════════════════════════════════════════════════════════
print("\nPlot B: delta vs popularity separated (colored by delta sign)...", flush=True)

game_1 = owned_1.groupby("appid").agg(
    mean_delta=("delta","mean"),
    mean_uc   =("user_count","mean"),
    mean_deg  =("graph_degree","mean"),
).reset_index()
game_0 = owned_0.groupby("appid").agg(
    mean_delta=("delta","mean"),
    mean_uc   =("user_count","mean"),
    mean_deg  =("graph_degree","mean"),
).reset_index()

rho_1_uc, _ = spearmanr(game_1["mean_uc"].dropna(),
                         game_1.loc[game_1["mean_uc"].notna(),"mean_delta"])
rho_0_uc, _ = spearmanr(game_0["mean_uc"].dropna(),
                         game_0.loc[game_0["mean_uc"].notna(),"mean_delta"])

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, gdf, rho, label in [
    (axes[0], game_1, rho_1_uc, "Owned games (owned=1)"),
    (axes[1], game_0, rho_0_uc, "Non-owned games (owned=0)"),
]:
    sample = gdf.sample(n=min(5000, len(gdf)), random_state=42)
    point_colors = ["#1a9850" if d > 0 else "#d73027" for d in sample["mean_delta"]]
    ax.scatter(sample["mean_uc"], sample["mean_delta"],
               c=point_colors, alpha=0.4, s=10)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("User count (game popularity)")
    ax.set_ylabel("Mean Δscore (network − baseline)")
    ax.set_title(f"{label}\nSpearman ρ = {rho:+.3f}")

plt.suptitle("Score change vs game popularity\n"
             "Separated by whether the user owns the game",
             y=1.02)
savefig("PB_delta_vs_popularity_separated.png")

# ════════════════════════════════════════════════════════════════════════════
# PLOT C — Genre delta, separated (owned=1 / owned=0)
# ════════════════════════════════════════════════════════════════════════════
print("\nPlot C: genre delta separated...", flush=True)

def genre_agg(df):
    rows = []
    for _, row in df.iterrows():
        if pd.isna(row["genres"]):
            continue
        seen = set()
        for rg in str(row["genres"]).replace('"','').split(";"):
            rg = rg.strip()
            grp = raw_to_group.get(rg)
            if grp and grp not in seen:
                seen.add(grp)
                rows.append({"group": grp, "delta": row["delta"],
                             "appid": row["appid"]})
    gdf = pd.DataFrame(rows)
    game_level = gdf.groupby(["appid","group"])["delta"].mean().reset_index()
    agg = game_level.groupby("group").agg(
        n_games      =("delta","size"),
        mean_delta   =("delta","mean"),
        median_delta =("delta","median"),
    ).reset_index()
    return agg

print("  genre agg owned=1...", flush=True)
g1 = genre_agg(owned_1)
print("  genre agg owned=0...", flush=True)
g0 = genre_agg(owned_0)

order_genre = g0.sort_values("median_delta")["group"].tolist()

fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)
for ax, gdf, label, color in [
    (axes[0], g1, "Owned games (owned=1)",    "#1a9850"),
    (axes[1], g0, "Non-owned games (owned=0)","#d73027"),
]:
    gdf = gdf.set_index("group").reindex(order_genre).reset_index()
    bars = ax.barh(gdf["group"], gdf["median_delta"], color=color, alpha=0.85)
    ax.axvline(0, color="black", linewidth=0.8)
    for bar, val, n in zip(bars, gdf["median_delta"], gdf["n_games"]):
        if pd.isna(val):
            continue
        ax.text(val + (0.001 if val >= 0 else -0.001),
                bar.get_y() + bar.get_height()/2,
                f"{val:.4f} (n={int(n)})", va="center",
                ha="left" if val >= 0 else "right", fontsize=FONT_SIZE_ANNOT)
    ax.set_title(label)
    ax.set_xlabel("Median Δscore per game")

plt.suptitle("Median score change by genre group\n"
             "when adding network embedding to XGBoost",
             y=1.01)
savefig("PC_genre_delta_separated.png")

# ════════════════════════════════════════════════════════════════════════════
# PLOT D — Genre popularity profile
# ════════════════════════════════════════════════════════════════════════════
print("\nPlot D: genre popularity profiles...", flush=True)

genre_game_rows = []
for _, row in test[["appid","genres","user_count",
                      "game_total_playtime_minutes"]].drop_duplicates(
        "appid").iterrows():
    if pd.isna(row["genres"]):
        continue
    seen = set()
    for rg in str(row["genres"]).replace('"','').split(";"):
        rg = rg.strip()
        grp = raw_to_group.get(rg)
        if grp and grp not in seen:
            seen.add(grp)
            genre_game_rows.append({
                "group"      : grp,
                "appid"      : row["appid"],
                "user_count" : row["user_count"],
                "total_play" : row["game_total_playtime_minutes"],
            })

gg = pd.DataFrame(genre_game_rows).drop_duplicates(["appid","group"])
gg["graph_degree"] = gg["appid"].map(degree_map)

genre_pop = gg.groupby("group").agg(
    n_games       =("appid","nunique"),
    median_uc     =("user_count","median"),
    q25_uc        =("user_count", lambda x: x.quantile(0.25)),
    q75_uc        =("user_count", lambda x: x.quantile(0.75)),
    median_degree =("graph_degree","median"),
    q25_degree    =("graph_degree", lambda x: x.quantile(0.25)),
    q75_degree    =("graph_degree", lambda x: x.quantile(0.75)),
).reset_index()

genre_pop = genre_pop.merge(
    g0[["group","median_delta"]].rename(columns={"median_delta":"median_delta_notowned"}),
    on="group", how="left")
genre_pop = genre_pop.merge(
    g1[["group","median_delta"]].rename(columns={"median_delta":"median_delta_owned"}),
    on="group", how="left")

genre_pop = genre_pop.sort_values("median_uc", ascending=False)
genre_pop.to_csv(
    f"{BASE}/results/thesis_analysis/genre_popularity_profile.csv", index=False)

# scatter: median_uc / median_degree vs median_delta (non-owned)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, x_col, x_label in [
    (axes[0], "median_uc",     "Median user count per genre"),
    (axes[1], "median_degree", "Median graph degree per genre"),
]:
    ax.scatter(genre_pop[x_col], genre_pop["median_delta_notowned"],
               s=80, color="#d73027", alpha=0.8, zorder=3)
    for _, row in genre_pop.iterrows():
        ax.annotate(row["group"],
                    (row[x_col], row["median_delta_notowned"]),
                    fontsize=7, xytext=(4, 2), textcoords="offset points")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel(x_label)
    ax.set_ylabel("Median Δscore (non-owned games)")
    rho, _ = spearmanr(genre_pop[x_col].dropna(),
                       genre_pop.loc[genre_pop[x_col].notna(),"median_delta_notowned"])
    ax.set_title(f"ρ = {rho:+.3f}")

plt.suptitle("Why do genres differ in score change?\n"
             "More popular genres get larger score suppression for non-owned games",
             y=1.02)
savefig("PD_genre_popularity_vs_delta.png")

# horizontal bar: genre popularity profile
fig, axes = plt.subplots(1, 2, figsize=(14, 7), sharey=True)
order_genre_rev = list(reversed(order_genre))
gp = genre_pop.set_index("group").reindex(order_genre_rev).reset_index()

for ax, col, label, color in [
    (axes[0], "median_uc",     "Median user count",  "#636363"),
    (axes[1], "median_degree", "Median graph degree","#525252"),
]:
    ax.barh(gp["group"], gp[col], color=color, alpha=0.8)
    ax.set_xlabel(label)
    ax.set_title(label)

plt.suptitle("Game popularity by genre\n"
             "(same genre order as score change plot — bottom = most negative Δscore)",
             y=1.01)
savefig("PE_genre_popularity_profile.png")

# ════════════════════════════════════════════════════════════════════════════
# PLOT F — Overall genre delta (combined, all owned values)
# ════════════════════════════════════════════════════════════════════════════
print("\nPlot F: overall genre delta combined...", flush=True)

g_all = genre_agg(merged)
plot_df = g_all.sort_values("median_delta", ascending=True)

fig, ax = plt.subplots(figsize=(9, 6))
colors_g = ["#d73027" if x < 0 else "#1a9850" for x in plot_df["median_delta"]]
bars = ax.barh(plot_df["group"], plot_df["median_delta"], color=colors_g)
ax.axvline(0, color="black", linewidth=0.8)
for bar, val, n in zip(bars, plot_df["median_delta"], plot_df["n_games"]):
    ax.text(val + (0.00005 if val >= 0 else -0.00005),
            bar.get_y() + bar.get_height()/2,
            f"{val:.4f}  (n={int(n)})", va="center",
            ha="left" if val >= 0 else "right", fontsize=FONT_SIZE_ANNOT)
ax.set_xlabel("Median Δscore per game (network model − baseline)")
ax.set_title("Median score change by genre group\n"
             "when adding network embedding to XGBoost")
savefig("PF_genre_delta_combined.png")

# ════════════════════════════════════════════════════════════════════════════
# PLOT G — Correlation bars (basic features), separated
# ════════════════════════════════════════════════════════════════════════════
print("\nPlot G: basic correlation bars separated...", flush=True)

features_basic = [
    ("user_count",                 "User count (popularity)"),
    ("game_emb_0",                 "Game embedding 0"),
    ("game_total_playtime_minutes","Total playtime"),
]

def corr_per_game_basic(df, feat_list):
    game_agg = df.groupby("appid").agg(
        mean_delta          =("delta","mean"),
        mean_user_count     =("user_count","mean"),
        mean_game_emb_0     =("game_emb_0","mean"),
        mean_total_playtime =("game_total_playtime_minutes","mean"),
    ).reset_index()
    col_map = {
        "user_count":                   "mean_user_count",
        "game_emb_0":                   "mean_game_emb_0",
        "game_total_playtime_minutes":  "mean_total_playtime",
    }
    rows = []
    for feat, label in feat_list:
        col = col_map[feat]
        valid = game_agg[["mean_delta", col]].dropna()
        rho, p = spearmanr(valid["mean_delta"], valid[col])
        rows.append({"feature": label, "rho": rho, "p": p})
    return pd.DataFrame(rows)

corr_basic_1 = corr_per_game_basic(owned_1, features_basic)
corr_basic_0 = corr_per_game_basic(owned_0, features_basic)

fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
for ax, cdf, label in [
    (axes[0], corr_basic_1, "Owned games (owned=1)"),
    (axes[1], corr_basic_0, "Non-owned games (owned=0)"),
]:
    colors_c = ["#1a9850" if r > 0 else "#d73027" for r in cdf["rho"]]
    bars = ax.barh(cdf["feature"], cdf["rho"], color=colors_c)
    ax.axvline(0, color="black", linewidth=0.8)
    for bar, rho in zip(bars, cdf["rho"]):
        ax.text(rho + (0.01 if rho >= 0 else -0.01),
                bar.get_y() + bar.get_height()/2,
                f"{rho:+.3f}", va="center",
                ha="left" if rho >= 0 else "right", fontsize=FONT_SIZE_ANNOT+1)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Spearman ρ with mean Δscore")
    ax.set_title(label)

plt.suptitle("What predicts the score change?\n"
             "Spearman correlations separated by ownership",
             y=1.02)
savefig("PG_basic_correlations_by_owned.png")

# ════════════════════════════════════════════════════════════════════════════
# PLOT H — Score separation comparison (baseline vs emb0)
# ════════════════════════════════════════════════════════════════════════════
print("\nPlot H: score separation comparison...", flush=True)

sep_data = pd.DataFrame({
    "model":    ["Baseline", "Network (emb0)"],
    "mean_pos": [base_m.loc[base_m["owned"]==1,"score"].mean(),
                 emb_m.loc[emb_m["owned"]==1,"score"].mean()],
    "mean_neg": [base_m.loc[base_m["owned"]==0,"score"].mean(),
                 emb_m.loc[emb_m["owned"]==0,"score"].mean()],
    "std_pos":  [base_m.loc[base_m["owned"]==1,"score"].std(),
                 emb_m.loc[emb_m["owned"]==1,"score"].std()],
    "std_neg":  [base_m.loc[base_m["owned"]==0,"score"].std(),
                 emb_m.loc[emb_m["owned"]==0,"score"].std()],
})
sep_data["separation"] = sep_data["mean_pos"] - sep_data["mean_neg"]
sep_data.to_csv(f"{BASE}/results/thesis_analysis/score_separation_summary.csv", index=False)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# left: mean scores by model
x = np.arange(2)
width = 0.35
ax = axes[0]
ax.bar(x - width/2, sep_data["mean_pos"], width, label="Owned (owned=1)",    color="#1a9850", alpha=0.85)
ax.bar(x + width/2, sep_data["mean_neg"], width, label="Non-owned (owned=0)",color="#d73027", alpha=0.85)
ax.set_xticks(x)
ax.set_xticklabels(sep_data["model"])
ax.set_ylabel("Mean predicted score")
ax.set_title("Mean predicted scores by model and ownership")
ax.legend(fontsize=FONT_SIZE_TICK)

# right: score separation
ax2 = axes[1]
colors_sep = ["#636363","#1a9850"]
bars2 = ax2.bar(sep_data["model"], sep_data["separation"], color=colors_sep, alpha=0.85)
for bar, val in zip(bars2, sep_data["separation"]):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f"{val:.4f}", ha="center", va="bottom", fontsize=FONT_SIZE_ANNOT+1)
ax2.set_ylabel("Score separation (owned − non-owned)")
ax2.set_title("Score separation by model")

plt.suptitle("How well do models separate owned from non-owned games?", y=1.02)
savefig("PH_score_separation.png")

# ════════════════════════════════════════════════════════════════════════════
# PLOT I — Top 10 overlap & rank improvement
# ════════════════════════════════════════════════════════════════════════════
print("\nPlot I: Top 10 overlap and rank improvement...", flush=True)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# left: overlap histogram
ax = axes[0]
ax.hist(overlap_rows, bins=range(0,12), color="#636363", alpha=0.8, edgecolor="white")
ax.axvline(mean_top10_overlap, color="#d73027", linewidth=2, linestyle="--",
           label=f"Mean = {mean_top10_overlap:.2f}")
ax.set_xlabel("Number of games in common (out of Top 10)")
ax.set_ylabel("Number of users")
ax.set_title(f"Top 10 recommendation overlap\nbetween baseline and network model")
ax.legend(fontsize=FONT_SIZE_TICK)

# right: rank distribution
ax2 = axes[1]
ax2.hist(rank_base_list, bins=range(1,12), alpha=0.7, label=f"Baseline (mean={mean_rank_base:.2f})",
         color="#636363", edgecolor="white")
ax2.hist(rank_emb_list,  bins=range(1,12), alpha=0.7, label=f"Network emb0 (mean={mean_rank_emb0:.2f})",
         color="#1a9850", edgecolor="white")
ax2.set_xlabel("Rank of owned game (1 = highest score)")
ax2.set_ylabel("Number of users")
ax2.set_title(f"Rank of owned game per user\n{percent_positives_promoted*100:.1f}% of users had rank improved")
ax2.legend(fontsize=FONT_SIZE_TICK)

plt.suptitle("Recommendation quality: ranking of owned games", y=1.02)
savefig("PI_top10_overlap_and_rank.png")

print("\nAll done.", flush=True)
