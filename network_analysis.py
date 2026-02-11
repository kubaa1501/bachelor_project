import networkx as nx
import pandas as pd

# -------------------
# DataFrames
# -------------------
users_df = pd.read_csv("checkpoint_export_final/users.csv")
friends_df = pd.read_csv("checkpoint_export_final/friends.csv")
# Only users you report on (np. ~99k visited/public/etc.)
allowed_users = set(users_df["steamid"])   # <- jeśli chcesz tylko visited/public, tu filtruj

# -------------------
# Build graph from all edges where source is in allowed_users
# (friend może być spoza users.csv -> nadal liczy się do degree użytkownika)
# -------------------
edges_from_users = [
    (u, f)
    for u, f in friends_df.itertuples(index=False, name=None)
    if u in allowed_users
]

G = nx.Graph()
G.add_edges_from(edges_from_users)

# -------------------
# "Nodes" w raporcie = tylko users (ok. 99k)
# "Edges" w raporcie = wszystkie krawędzie wychodzące z users
# -------------------
num_nodes_users = len(allowed_users)
num_edges_from_users = len(edges_from_users)

# -------------------
# Degree stats: liczymy TYLKO dla users,
# ale stopień usera uwzględnia też połączenia do discovered friends
# -------------------
degrees_users = [G.degree(u) for u in allowed_users]
avg_degree_users = sum(degrees_users) / len(degrees_users) if degrees_users else 0.0
min_degree_users = min(degrees_users) if degrees_users else 0
max_degree_users = max(degrees_users) if degrees_users else 0
median_degree_users = int(pd.Series(degrees_users).median()) if degrees_users else 0

# -------------------
# Miary "grafowe" sensownie liczyć na podgrafie users-only
# (bo components/clustering/density na 6M discovered to bez sensu)
# Tu: podgraf indukowany przez users (krawędzie tylko między users)
# -------------------
G_users = G.subgraph(allowed_users).copy()

density_users = nx.density(G_users)

components_users = list(nx.connected_components(G_users))
num_components_users = len(components_users)
largest_component_size_users = len(max(components_users, key=len)) if components_users else 0

avg_clustering_users = nx.average_clustering(G_users) if G_users.number_of_nodes() > 0 else 0.0

# -------------------
# Print results (jak u Ciebie)
# -------------------
print(f"Number of nodes (users): {num_nodes_users:,}")
print(f"Number of edges (from users to anyone): {num_edges_from_users:,}")

print("\nDegree statistics (computed for users only; degree counts friends too):")
print(f"Average degree: {avg_degree_users:.2f}")
print(f"Median degree: {median_degree_users}")
print(f"Min degree: {min_degree_users}")
print(f"Max degree: {max_degree_users}")

print(f"\nNetwork density (users-only subgraph): {density_users:.8f}")
print(f"Number of connected components (users-only subgraph): {num_components_users}")
print(f"Largest connected component size (users-only subgraph): {largest_component_size_users:,}")
print(f"Average clustering coefficient (users-only subgraph): {avg_clustering_users:.4f}")
