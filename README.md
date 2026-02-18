### EDA 
Number of nodes (users): 99,924   
Number of edges (from users to anyone): 8,039,785  
  
Degree statistics (computed for users only; degree counts friends too):  
Average degree: 80.81  
Median degree: 48  
Min degree: 1  
Max degree: 1999  
  
Network density (users-only subgraph): 0.00002668  
Number of connected components (users-only subgraph): 1  
Largest connected component size (users-only subgraph): 99,924  
Average clustering coefficient (users-only subgraph): 0.0431  
 
## After filtering: 
  
nodes: 43614  
edges: 44508  
## LCC
  
lcc_nodes: 31021  
lcc_edges: 40204  
directed: false    

## algorithm   
- game_index_to_gameid_sq_20988.mmap (map games id)   
- user_game_01_relabelled.pkl (20988 col/gry, 31021 row/users)  
- user_edge_graph_relabelled.pkl (31021 nodes/users, 40204 edges/connections)   
- old_to_new_node_id.csv (mapping users (2) 43613/filtered data -> 31021 (LCC)   
- game_game_dists_sq_20988.mmap -> upper triangle games relationships matrix   
