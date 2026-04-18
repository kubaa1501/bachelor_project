"""
Steam Recommendation System — Full EDA
========================================
Sections
  1. Raw Data Overview
     1a. File row counts table
     1b. Missing values per raw file (bar chart)
     1c. Public vs Private users (bar chart)
     1d. Missing values for public users only
     1e. Users with no games (raw users vs user_games_raw)

  2. Final Data — Users
     2a. Country distribution (top 15)
     2b. Account creation over time

  3. Final Data — Games & Playtime
     3a. Top 20 games by user count  (computed from user_games.csv)
     3b. Games per user distribution
     3c. Playtime distribution (log scale)
     3d. Genre breakdown (grouped, weighted by ownership from user_games.csv)

  4. Final Data — Social
     4a. Friend count distribution

  5. Graph / Network Analysis
     5a. Summary statistics table
     5b. Degree distribution (log-log + power-law reference)
     5c. Degree CDF + CCDF
     5d. Hub analysis (top-20 highest-degree users)
     5e. Clustering coefficient vs degree
     5f. User-game bipartite summary table
     5g. Bipartite distributions (games per user, owners per game)
     5h. Total playtime vs social degree

All figures saved to /home/jaga/results/eda/

Runtime note for clustering coefficient:
  Samples SAMPLE_N=50,000 users by default (representative and fast).
  Set SAMPLE_N = None to run on full graph (~10-30 min).
  If you have a pre-built NetworkX pickle set GRAPH_PICKLE to its path.
"""

import os
import warnings
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
RAW_PATH     = "/home/jaga/data/data_raw"
FINAL_PATH   = "/home/jaga/data/data_final"
OUT_DIR      = "/home/jaga/results/eda"
GRAPH_PICKLE = None       # path to NetworkX pickle, or None
SAMPLE_N     = 50_000     # users sampled for clustering; None = all

os.makedirs(OUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# STYLE
# ─────────────────────────────────────────────
PALETTE  = ["#4C72B0", "#DD8452", "#55A868", "#C44E52",
            "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
            "#CCB974", "#64B5CD"]
ACCENT   = "#4C72B0"
WARN_COL = "#C44E52"

def style_ax(ax, title="", xlabel="", ylabel="", grid_axis="y"):
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.tick_params(labelsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    if grid_axis:
        ax.grid(axis=grid_axis, color="#e5e5e5", linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)

def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"  Saved → {path}")
    plt.close(fig)

def make_table(ax, rows, col_labels, title):
    """Render a styled table on an axes object with axis off."""
    ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=col_labels,
                   loc="center", cellLoc="left")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.55)
    for j in range(len(col_labels)):
        tbl[0, j].set_facecolor("#4C72B0")
        tbl[0, j].set_text_props(color="white", fontweight="bold")
    for i in range(1, len(rows) + 1):
        for j in range(len(col_labels)):
            if all(c == "" for c in rows[i - 1]):
                tbl[i, j].set_facecolor("#f7f7f7")
                tbl[i, j].set_height(0.015)
            else:
                tbl[i, j].set_facecolor("#f0f4fa" if i % 2 == 0 else "white")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)

# ─────────────────────────────────────────────
# GENRE MAP
# ─────────────────────────────────────────────
GENRE_GROUPS = {
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

def map_genre(raw_genres_str):
    if pd.isna(raw_genres_str):
        return "Unknown"
    tags = [g.strip() for g in str(raw_genres_str).split(",")]
    for group, members in GENRE_GROUPS.items():
        if any(t in members for t in tags):
            return group
    return "Other"


# ═══════════════════════════════════════════════════════════════════
# SECTION 1 — RAW DATA OVERVIEW
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("SECTION 1 — Raw data overview")
print("=" * 60)

raw_files = {
    "users_raw":          ("users_raw.csv",          ","),
    "friends_raw":        ("friends_raw.csv",         ","),
    "user_games_raw":     ("user_games_raw.csv",      ","),
    "games_raw":          ("games_raw.csv",           ","),
    "enriched_games_raw": ("enriched_games_raw.csv",  ";"),
}

raw_dfs = {}
for key, (fname, sep) in raw_files.items():
    fpath = os.path.join(RAW_PATH, fname)
    if os.path.exists(fpath):
        raw_dfs[key] = pd.read_csv(fpath, sep=sep, on_bad_lines="skip")
        print(f"  Loaded {fname}: {len(raw_dfs[key]):,} rows, "
              f"{raw_dfs[key].shape[1]} cols")
    else:
        print(f"  MISSING: {fpath}")

# ── 1a. File row counts ───────────────────────────────────────────
print("[1a] File row counts …")
fig, ax = plt.subplots(figsize=(7, 3.5))
rows_1a = [[k, f"{len(v):,}", str(v.shape[1])] for k, v in raw_dfs.items()]
make_table(ax, rows_1a, ["File", "Rows", "Columns"], "Raw File Overview")
save(fig, "1a_raw_file_counts.png")

# ── 1b. Missing values per raw file ──────────────────────────────
print("[1b] Missing values per raw file …")
missing_summary = {}
for key, df in raw_dfs.items():
    pct = (df.isna().sum() / len(df) * 100).round(1)
    for col, val in pct.items():
        if val > 0:
            missing_summary[f"{key}\n({col})"] = val

if missing_summary:
    labels = list(missing_summary.keys())
    vals   = list(missing_summary.values())
    colors = [WARN_COL if v > 20 else "#DD8452" if v > 5 else ACCENT for v in vals]
    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 0.9), 5))
    bars = ax.bar(labels, vals, color=colors, width=0.6, zorder=3)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                f"{v:.1f}%", ha="center", va="bottom", fontsize=8)
    style_ax(ax, title="Missing Values in Raw Files (% per column)",
             ylabel="Missing (%)")
    ax.set_ylim(0, max(vals) * 1.18)
    plt.xticks(rotation=25, ha="right", fontsize=8)
    save(fig, "1b_raw_missing_values.png")

# ── 1c. Public vs Private ─────────────────────────────────────────
print("[1c] Public vs private …")
if "users_raw" in raw_dfs:
    users_raw = raw_dfs["users_raw"]
    if "public" in users_raw.columns:
        vc        = users_raw["public"].value_counts(dropna=False)
        public_n  = int(vc.get(True,  0))
        private_n = int(vc.get(False, 0)) + int(vc.get(np.nan, 0))
        total_n   = public_n + private_n
        fig, ax   = plt.subplots(figsize=(5.5, 4))
        ax.bar(["Public", "Private"], [public_n, private_n],
               color=[ACCENT, WARN_COL], width=0.45, zorder=3)
        for x_pos, n in zip(["Public", "Private"], [public_n, private_n]):
            ax.text(["Public", "Private"].index(x_pos),
                    n + total_n * 0.01,
                    f"{n:,}\n({n / total_n:.1%})",
                    ha="center", va="bottom", fontsize=10)
        style_ax(ax, title="Account Visibility in Crawled Users",
                 ylabel="Number of Users")
        ax.set_ylim(0, max(public_n, private_n) * 1.2)
        save(fig, "1c_public_vs_private.png")

# ── 1d. Missing values — public users only ───────────────────────
print("[1d] Missing values for public users …")
if "users_raw" in raw_dfs:
    users_raw = raw_dfs["users_raw"]
    if "public" in users_raw.columns:
        pub_df      = users_raw[users_raw["public"] == True]
        total_pub   = len(pub_df)
        missing_pub = (pub_df.isna().sum() / total_pub * 100).round(1)
        missing_pub = missing_pub[missing_pub > 0]
        if not missing_pub.empty:
            colors = [WARN_COL if v > 20 else "#DD8452" if v > 5 else ACCENT
                      for v in missing_pub.values]
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(missing_pub.index, missing_pub.values,
                   color=colors, width=0.45, zorder=3)
            for i, v in enumerate(missing_pub.values):
                ax.text(i, v + 0.5, f"{v:.1f}%",
                        ha="center", va="bottom", fontsize=9)
            style_ax(ax,
                     title=f"Missing Values for Public Users Only (n={total_pub:,})",
                     ylabel="Missing (%)")
            ax.set_ylim(0, missing_pub.max() * 1.2)
            save(fig, "1d_public_users_missing.png")

# ── 1e. Users with no games ───────────────────────────────────────
print("[1e] Users with no games …")
if "users_raw" in raw_dfs and "user_games_raw" in raw_dfs:
    ug_raw           = raw_dfs["user_games_raw"]
    users_raw        = raw_dfs["users_raw"].copy()
    users_with_games = set(ug_raw["steamid"].unique())
    users_raw["has_games"] = users_raw["steamid"].isin(users_with_games)
    users_raw["status"]    = (users_raw["public"]
                              .map({True: "Public", False: "Private"})
                              .fillna("Private"))

    total      = len(users_raw)
    no_games   = (~users_raw["has_games"]).sum()
    with_games = users_raw["has_games"].sum()
    print(f"  Total crawled:     {total:,}")
    print(f"  With games:        {with_games:,} ({with_games/total:.1%})")
    print(f"  Without any games: {no_games:,} ({no_games/total:.1%})")

    breakdown = (users_raw.groupby(["status", "has_games"])
                 .size().unstack(fill_value=0))
    breakdown.columns = ["No games", "Has games"]
    breakdown["Total"]      = breakdown.sum(axis=1)
    breakdown["No games %"] = (breakdown["No games"] / breakdown["Total"] * 100).round(1)

    groups   = breakdown.index.tolist()
    has_vals = breakdown["Has games"].values
    no_vals  = breakdown["No games"].values

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.bar(range(len(groups)), has_vals, label="Has games",
           color=ACCENT, zorder=3)
    ax.bar(range(len(groups)), no_vals, bottom=has_vals,
           label="No games", color=WARN_COL, zorder=3, alpha=0.85)
    for i, (h, n, tot) in enumerate(
            zip(has_vals, no_vals, breakdown["Total"].values)):
        ax.text(i, h / 2, f"{h:,}\n({h/tot:.0%})",
                ha="center", va="center", fontsize=9,
                color="white", fontweight="bold")
        ax.text(i, h + n / 2, f"{n:,}\n({n/tot:.0%})",
                ha="center", va="center", fontsize=9,
                color="white", fontweight="bold")
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups, fontsize=10)
    style_ax(ax, title="Users With / Without Games by Account Type",
             ylabel="Number of Users")
    ax.legend(fontsize=9)
    save(fig, "1e_users_no_games.png")

    table_rows_1e = [
        ["All users crawled",        f"{total:,}",      "100%"],
        ["  with at least one game", f"{with_games:,}", f"{with_games/total:.1%}"],
        ["  with no games at all",   f"{no_games:,}",   f"{no_games/total:.1%}"],
        ["", "", ""],
    ]
    for status in breakdown.index:
        row = breakdown.loc[status]
        table_rows_1e += [
            [f"{status} — total", f"{int(row['Total']):,}", ""],
            [f"  has games",      f"{int(row['Has games']):,}",
             f"{row['Has games']/row['Total']:.1%}"],
            [f"  no games",       f"{int(row['No games']):,}",
             f"{row['No games %']:.1f}%"],
            ["", "", ""],
        ]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    make_table(ax, table_rows_1e, ["Group", "Count", "Share"],
               "Users Without Any Games — Summary")
    save(fig, "1e_users_no_games_table.png")


# ═══════════════════════════════════════════════════════════════════
# SECTION 2 — FINAL DATA: USERS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("SECTION 2 — Final users")
print("=" * 60)

users = pd.read_csv(os.path.join(FINAL_PATH, "users.csv"))
if users["account_created"].dtype in [np.float64, np.int64]:
    users["account_created"] = pd.to_datetime(
        users["account_created"], unit="s", errors="coerce")
else:
    users["account_created"] = pd.to_datetime(
        users["account_created"], errors="coerce")
print(f"  users.csv: {len(users):,} rows")

# ── 2a. Country distribution ─────────────────────────────────────
print("[2a] Country distribution …")
ISO_NAMES = {
    "US": "United States", "CN": "China",           "BR": "Brazil",
    "RU": "Russia",        "DE": "Germany",          "PL": "Poland",
    "GB": "United Kingdom","TR": "Turkey",            "FR": "France",
    "PT": "Portugal",      "CA": "Canada",            "JP": "Japan",
    "SE": "Sweden",        "IN": "India",             "RO": "Romania",
    "DK": "Denmark",       "NL": "Netherlands",       "AU": "Australia",
    "CZ": "Czech Republic","AR": "Argentina",         "IT": "Italy",
    "NO": "Norway",        "UA": "Ukraine",           "ES": "Spain",
    "BE": "Belgium",       "FI": "Finland",
}
top_n          = 15
country_counts = users["country"].dropna().value_counts().head(top_n)
c_labels       = [ISO_NAMES.get(c, c) for c in country_counts.index]

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(c_labels[::-1], country_counts.values[::-1], color=ACCENT, zorder=3)
for i, v in enumerate(country_counts.values[::-1]):
    ax.text(v + 30, i, f"{v:,}", va="center", fontsize=8)
style_ax(ax, title=f"Top {top_n} Countries (Final Users)",
         xlabel="Number of Users", grid_axis="x")
ax.set_xlim(0, country_counts.max() * 1.15)
save(fig, "2a_country_distribution.png")

# ── 2b. Account creation over time ───────────────────────────────
print("[2b] Account creation over time …")
created_year = (users["account_created"].dropna()
                .dt.year.value_counts().sort_index())
created_year = created_year[(created_year.index >= 2003) &
                             (created_year.index <= 2025)]
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.fill_between(created_year.index, created_year.values,
                alpha=0.25, color=ACCENT)
ax.plot(created_year.index, created_year.values,
        color=ACCENT, linewidth=2, marker="o", markersize=5)
style_ax(ax, title="Steam Account Creation Year (Final Users)",
         xlabel="Year", ylabel="Number of Accounts")
ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
save(fig, "2b_account_creation_over_time.png")


# ═══════════════════════════════════════════════════════════════════
# SECTION 3 — GAMES & PLAYTIME
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("SECTION 3 — Games & playtime")
print("=" * 60)

games      = pd.read_csv(os.path.join(FINAL_PATH, "games.csv"))
user_games = pd.read_csv(os.path.join(FINAL_PATH, "user_games.csv"),
                         on_bad_lines="skip")
print(f"  games.csv:      {len(games):,} rows")
print(f"  user_games.csv: {len(user_games):,} rows")

# ownership counts from user_games.csv (single source of truth)
owners_per_game = user_games.groupby("appid")["steamid"].count().rename("owner_count")

# ── 3a. Top 20 games ─────────────────────────────────────────────
print("[3a] Top games (from user_games.csv) …")
top_games = (owners_per_game.reset_index()
             .merge(games[["appid", "name"]], on="appid", how="left")
             .nlargest(20, "owner_count"))
top_games["name"] = top_games["name"].fillna("Unknown").str[:35]

fig, ax = plt.subplots(figsize=(8, 7))
y_pos = range(len(top_games))
ax.barh(list(y_pos), top_games["owner_count"].values[::-1],
        color=ACCENT, zorder=3)
ax.set_yticks(list(y_pos))
ax.set_yticklabels(top_games["name"].values[::-1], fontsize=9)
for i, v in enumerate(top_games["owner_count"].values[::-1]):
    ax.text(v + top_games["owner_count"].max() * 0.01, i,
            f"{v:,}", va="center", fontsize=8)
style_ax(ax, title="Top 20 Games by Number of Owners (Final Data)",
         xlabel="Number of Users", grid_axis="x")
ax.set_xlim(0, top_games["owner_count"].max() * 1.15)
save(fig, "3a_top_games.png")

# ── 3b. Games per user distribution ──────────────────────────────
print("[3b] Games per user …")
games_per_user = user_games.groupby("steamid")["appid"].count()

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
axes[0].hist(games_per_user.clip(upper=500), bins=60,
             color=ACCENT, edgecolor="white", linewidth=0.4, zorder=3)
style_ax(axes[0], title="Games Owned per User",
         xlabel="Number of Games", ylabel="Number of Users")
axes[1].hist(games_per_user,
             bins=np.logspace(0, np.log10(games_per_user.max()), 60),
             color=ACCENT, edgecolor="white", linewidth=0.4, zorder=3)
axes[1].set_xscale("log")
style_ax(axes[1], title="Games Owned per User (Log Scale)",
         xlabel="Number of Games (log)", ylabel="Number of Users")
fig.suptitle(f"Median: {games_per_user.median():.0f}  |  "
             f"Mean: {games_per_user.mean():.0f}  |  "
             f"Max: {games_per_user.max():,}",
             fontsize=9, color="#555555", y=0.01)
fig.tight_layout()
save(fig, "3b_games_per_user.png")

# ── 3c. Playtime distribution ─────────────────────────────────────
print("[3c] Playtime distribution …")
pt         = user_games["playtime_minutes"].copy()
pt_nonzero = pt[pt > 0]
zero_pct   = (pt == 0).mean() * 100

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
axes[0].hist((pt / 60).clip(upper=500), bins=80,
             color=ACCENT, edgecolor="white", linewidth=0.4, zorder=3)
style_ax(axes[0], title="Playtime Distribution (clipped at 500 h)",
         xlabel="Playtime (hours)", ylabel="Number of User-Game Pairs")
pt_hours_nz = pt_nonzero / 60
axes[1].hist(pt_hours_nz,
             bins=np.logspace(np.log10(0.01), np.log10(pt_hours_nz.max()), 80),
             color=ACCENT, edgecolor="white", linewidth=0.4, zorder=3)
axes[1].set_xscale("log")
style_ax(axes[1], title="Playtime — Non-Zero Only (Log Scale)",
         xlabel="Playtime in Hours (log)", ylabel="Number of User-Game Pairs")
fig.suptitle(f"Zero playtime: {zero_pct:.1f}% of all user-game pairs",
             fontsize=9, color="#555555", y=0.01)
fig.tight_layout()
save(fig, "3c_playtime_distribution.png")

# ── 3d. Genre breakdown ───────────────────────────────────────────
print("[3d] Genre breakdown …")
genre_col = next((c for c in ["genres", "genre", "tags"]
                  if c in games.columns), None)
if genre_col:
    games["genre_group"] = games[genre_col].apply(map_genre)
    genre_counts = (games.merge(owners_per_game.reset_index(), on="appid", how="left")
                    .groupby("genre_group")["owner_count"].sum()
                    .sort_values(ascending=False))
    genre_counts = genre_counts[genre_counts.index != "Unknown"]
    colors = (PALETTE * 3)[:len(genre_counts)]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(genre_counts.index, genre_counts.values,
           color=colors, width=0.6, zorder=3)
    for i, (lbl, v) in enumerate(genre_counts.items()):
        ax.text(i, v + genre_counts.max() * 0.01,
                f"{v:,}", ha="center", va="bottom", fontsize=7.5, rotation=45)
    style_ax(ax, title="Genre Distribution (weighted by user ownership)",
             ylabel="Total User Ownership Count")
    plt.xticks(rotation=30, ha="right", fontsize=9)
    ax.set_ylim(0, genre_counts.max() * 1.22)
    save(fig, "3d_genre_distribution.png")
else:
    print("  No genre column found in games.csv — skipping.")


# ═══════════════════════════════════════════════════════════════════
# SECTION 4 — SOCIAL: FRIEND COUNT
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("SECTION 4 — Friend counts")
print("=" * 60)

fc_path = os.path.join(FINAL_PATH, "users_friend_counts.csv")
if os.path.exists(fc_path):
    fc_df         = pd.read_csv(fc_path)
    fc_col        = ("friend_count" if "friend_count" in fc_df.columns
                     else fc_df.columns[-1])
    friend_counts = fc_df[fc_col].dropna()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].hist(friend_counts.clip(upper=200), bins=60,
                 color=ACCENT, edgecolor="white", linewidth=0.4, zorder=3)
    style_ax(axes[0], title="Friend Count Distribution (clipped at 200)",
             xlabel="Number of Friends", ylabel="Number of Users")
    fc_nonzero = friend_counts[friend_counts > 0]
    axes[1].hist(fc_nonzero,
                 bins=np.logspace(0, np.log10(fc_nonzero.max() + 1), 60),
                 color=ACCENT, edgecolor="white", linewidth=0.4, zorder=3)
    axes[1].set_xscale("log")
    style_ax(axes[1], title="Friend Count Distribution (Log Scale)",
             xlabel="Number of Friends (log)", ylabel="Number of Users")
    fig.suptitle(f"Median: {friend_counts.median():.0f}  |  "
                 f"Mean: {friend_counts.mean():.0f}  |  "
                 f"Max: {friend_counts.max():,}",
                 fontsize=9, color="#555555", y=0.01)
    fig.tight_layout()
    save(fig, "4a_friend_count_distribution.png")
else:
    print(f"  File not found: {fc_path} — skipping.")


# ═══════════════════════════════════════════════════════════════════
# SECTION 5 — GRAPH / NETWORK ANALYSIS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("SECTION 5 — Graph / network analysis")
print("=" * 60)

friends = pd.read_csv(os.path.join(FINAL_PATH, "friends.csv"),
                      on_bad_lines="skip")
print(f"  friends.csv: {len(friends):,} rows")

# ── Build degree series ───────────────────────────────────────────
print("  Computing degree …")
deg_series = pd.concat([
    friends["user_steamid"],
    friends["friend_steamid"]
]).value_counts()

n_nodes    = deg_series.nunique()
n_edges    = len(friends)
density    = (2 * n_edges) / (n_nodes * (n_nodes - 1))
deg_mean   = deg_series.mean()
deg_median = deg_series.median()
deg_min    = int(deg_series.min())
deg_max    = int(deg_series.max())
deg_std    = deg_series.std()
deg_p95    = deg_series.quantile(0.95)
print(f"  Nodes: {n_nodes:,}  Edges: {n_edges:,}  Density: {density:.2e}")

# ── Clustering coefficient ────────────────────────────────────────
print(f"  Building adjacency "
      f"({'full' if SAMPLE_N is None else f'sample n={SAMPLE_N:,}'}) …")

if GRAPH_PICKLE and os.path.exists(GRAPH_PICKLE):
    import pickle
    import networkx as nx
    G         = pickle.load(open(GRAPH_PICKLE, "rb"))
    cc_values = pd.Series(nx.clustering(G))
else:
    adj = defaultdict(set)
    for u, v in zip(friends["user_steamid"], friends["friend_steamid"]):
        adj[u].add(v)
        adj[v].add(u)

    sample_nodes = deg_series.index.tolist()
    if SAMPLE_N is not None and SAMPLE_N < len(sample_nodes):
        rng          = np.random.default_rng(42)
        sample_nodes = rng.choice(sample_nodes, size=SAMPLE_N,
                                  replace=False).tolist()

    print(f"  Computing clustering for {len(sample_nodes):,} nodes …")
    cc_vals = {}
    for node in sample_nodes:
        neighbors = adj[node]
        k         = len(neighbors)
        if k < 2:
            cc_vals[node] = 0.0
            continue
        triangles     = sum(1 for nb in neighbors if adj[nb] & neighbors)
        cc_vals[node] = triangles / (k * (k - 1))
    cc_values = pd.Series(cc_vals)

avg_clustering = cc_values.mean()
print(f"  Avg clustering coefficient: {avg_clustering:.4f}")

# ── 5a. Summary stats table ───────────────────────────────────────
print("[5a] Summary stats table …")
rows_5a = [
    ["Nodes (unique users in edge list)", f"{n_nodes:,}"],
    ["Edges (friendship pairs)",          f"{n_edges:,}"],
    ["Network density",                   f"{density:.2e}"],
    ["", ""],
    ["Average degree",                    f"{deg_mean:.2f}"],
    ["Median degree",                     f"{deg_median:.0f}"],
    ["Std dev degree",                    f"{deg_std:.2f}"],
    ["95th percentile degree",            f"{int(deg_p95):,}"],
    ["Min degree",                        f"{deg_min}"],
    ["Max degree",                        f"{deg_max:,}"],
    ["", ""],
    ["Avg clustering coefficient",        f"{avg_clustering:.4f}"],
    ["Connected components",              "1"],
    ["Largest component size",            f"{n_nodes:,}"],
]
fig, ax = plt.subplots(figsize=(7, 5))
make_table(ax, rows_5a, ["Metric", "Value"],
           "Social Graph — Summary Statistics")
save(fig, "5a_graph_summary_table.png")

# ── 5b. Degree distribution log-log ──────────────────────────────
print("[5b] Degree distribution …")
deg_counts = deg_series.value_counts().sort_index()

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.scatter(deg_counts.index, deg_counts.values,
           s=6, alpha=0.5, color=ACCENT, zorder=3, label="Empirical")
mask = (deg_counts.index >= 5) & (deg_counts.values >= 5)
if mask.sum() > 5:
    slope, intercept = np.polyfit(
        np.log10(deg_counts.index[mask]),
        np.log10(deg_counts.values[mask]), 1)
    x_ref = np.logspace(np.log10(deg_counts.index.min()),
                        np.log10(deg_counts.index.max()), 100)
    ax.plot(x_ref, 10 ** intercept * x_ref ** slope,
            color=WARN_COL, linewidth=1.5, linestyle="--",
            label=f"Power-law ref. (γ ≈ {-slope:.2f})")
ax.set_xscale("log")
ax.set_yscale("log")
style_ax(ax, title="Degree Distribution (Log-Log)",
         xlabel="Degree k", ylabel="Number of Users P(k)", grid_axis=None)
ax.grid(color="#e5e5e5", linewidth=0.6, which="both")
ax.set_axisbelow(True)
ax.legend(fontsize=9)
save(fig, "5b_degree_distribution_loglog.png")

# ── 5c. CDF + CCDF ───────────────────────────────────────────────
print("[5c] CDF …")
sorted_deg = np.sort(deg_series.values)
cdf        = np.arange(1, len(sorted_deg) + 1) / len(sorted_deg)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
axes[0].plot(sorted_deg, cdf, color=ACCENT, linewidth=1.5)
style_ax(axes[0], title="CDF of User Degree",
         xlabel="Degree k", ylabel="Cumulative fraction")
axes[0].set_xlim(0, deg_p95 * 2)
axes[1].plot(sorted_deg, 1 - cdf, color=ACCENT, linewidth=1.5)
axes[1].set_xscale("log")
axes[1].set_yscale("log")
style_ax(axes[1], title="Complementary CDF (CCDF) — Log-Log",
         xlabel="Degree k (log)", ylabel="P(degree ≥ k) (log)", grid_axis=None)
axes[1].grid(color="#e5e5e5", linewidth=0.6, which="both")
axes[1].set_axisbelow(True)
fig.tight_layout()
save(fig, "5c_degree_cdf.png")

# ── 5d. Hub analysis ─────────────────────────────────────────────
print("[5d] Hub analysis …")
top20 = deg_series.nlargest(20).reset_index()
top20.columns = ["steamid", "degree"]
top20["label"] = top20["steamid"].astype(str).str[-6:]

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(top20["label"][::-1], top20["degree"][::-1],
        color=ACCENT, zorder=3)
for i, v in enumerate(top20["degree"][::-1]):
    ax.text(v + deg_max * 0.005, i, f"{v:,}", va="center", fontsize=8)
style_ax(ax, title="Top 20 Highest-Degree Users (Hubs)",
         xlabel="Degree (number of friends)",
         ylabel="User ID (last 6 digits)", grid_axis="x")
ax.set_xlim(0, top20["degree"].max() * 1.15)
save(fig, "5d_hub_analysis.png")

# ── 5e. Clustering coefficient vs degree ─────────────────────────
print("[5e] Clustering vs degree …")
cc_df = cc_values.reset_index()
cc_df.columns = ["steamid", "cc"]
deg_reset = deg_series.reset_index()
deg_reset.columns = ["steamid", "degree"]
cc_df = cc_df.merge(deg_reset, on="steamid", how="left")
cc_df = cc_df[cc_df["degree"] >= 2]

bins_cc  = np.logspace(0, np.log10(cc_df["degree"].max()), 30)
cc_df["deg_bin"] = pd.cut(cc_df["degree"], bins=bins_cc)
binned_cc = cc_df.groupby("deg_bin", observed=True)["cc"].mean().reset_index()
bin_mids_cc = [(iv.left + iv.right) / 2 for iv in binned_cc["deg_bin"]]

sample_cc = cc_df.sample(min(5000, len(cc_df)), random_state=42)
fig, ax   = plt.subplots(figsize=(7, 4.5))
ax.scatter(sample_cc["degree"], sample_cc["cc"],
           s=5, alpha=0.2, color=ACCENT, label="Individual users")
ax.plot(bin_mids_cc, binned_cc["cc"], color=WARN_COL, linewidth=2,
        marker="o", markersize=4, label="Bin mean")
ax.set_xscale("log")
style_ax(ax, title="Clustering Coefficient vs Degree",
         xlabel="Degree k (log)", ylabel="Clustering Coefficient",
         grid_axis=None)
ax.grid(color="#e5e5e5", linewidth=0.6, which="both")
ax.set_axisbelow(True)
ax.legend(fontsize=9)
save(fig, "5e_clustering_vs_degree.png")

# ── 5f. Bipartite summary table ───────────────────────────────────
print("[5f] Bipartite summary table …")
gpu = user_games.groupby("steamid")["appid"].count()
opg = user_games.groupby("appid")["steamid"].count()

rows_5f = []
for label, s in [("Games owned per user", gpu), ("Owners per game", opg)]:
    rows_5f += [
        [label, "Min",    f"{s.min():,}"],
        [label, "Median", f"{s.median():.0f}"],
        [label, "Mean",   f"{s.mean():.1f}"],
        [label, "95th %", f"{s.quantile(0.95):.0f}"],
        [label, "Max",    f"{s.max():,}"],
    ]
fig, ax = plt.subplots(figsize=(7, 4.2))
make_table(ax, rows_5f, ["Variable", "Statistic", "Value"],
           "User–Game Bipartite Graph — Descriptive Statistics")
save(fig, "5f_bipartite_summary_table.png")

# ── 5g. Bipartite distributions ───────────────────────────────────
print("[5g] Bipartite distributions …")
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
axes[0].hist(gpu, bins=np.logspace(0, np.log10(gpu.max()), 60),
             color=ACCENT, edgecolor="white", linewidth=0.4, zorder=3)
axes[0].set_xscale("log")
style_ax(axes[0], title="Games Owned per User (Log Scale)",
         xlabel="Games owned (log)", ylabel="Number of Users")
axes[1].hist(opg, bins=np.logspace(0, np.log10(opg.max()), 60),
             color=PALETTE[1], edgecolor="white", linewidth=0.4, zorder=3)
axes[1].set_xscale("log")
style_ax(axes[1], title="Owners per Game (Log Scale)",
         xlabel="Number of owners (log)", ylabel="Number of Games")
fig.tight_layout()
save(fig, "5g_bipartite_distributions.png")

# ── 5h. Playtime vs degree ────────────────────────────────────────
print("[5h] Playtime vs degree …")
total_playtime = (user_games.groupby("steamid")["playtime_minutes"]
                  .sum() / 60).rename("total_hours")
pt_deg = (total_playtime.reset_index()
          .merge(deg_reset, on="steamid", how="inner"))
pt_deg = pt_deg[pt_deg["total_hours"] > 0]

bins_pt = np.logspace(0, np.log10(pt_deg["degree"].max() + 1), 25)
pt_deg["deg_bin"] = pd.cut(pt_deg["degree"], bins=bins_pt)
binned_pt   = (pt_deg.groupby("deg_bin", observed=True)["total_hours"]
               .median().reset_index())
bin_mids_pt = [(iv.left + iv.right) / 2 for iv in binned_pt["deg_bin"]]

sample_pt = pt_deg.sample(min(8000, len(pt_deg)), random_state=42)
fig, ax   = plt.subplots(figsize=(7, 4.5))
ax.scatter(sample_pt["degree"], sample_pt["total_hours"],
           s=5, alpha=0.2, color=ACCENT, label="Individual users")
ax.plot(bin_mids_pt, binned_pt["total_hours"], color=WARN_COL,
        linewidth=2, marker="o", markersize=4, label="Bin median")
ax.set_xscale("log")
ax.set_yscale("log")
style_ax(ax, title="Total Playtime vs Social Degree",
         xlabel="Degree (number of friends, log)",
         ylabel="Total Playtime in Hours (log)", grid_axis=None)
ax.grid(color="#e5e5e5", linewidth=0.6, which="both")
ax.set_axisbelow(True)
ax.legend(fontsize=9)
save(fig, "5h_playtime_vs_degree.png")


# ═══════════════════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print(f"All figures saved to: {os.path.abspath(OUT_DIR)}")
print("=" * 60)
