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
- user_edge_graph_relabelled.pkl (31021 nodes/users, 40204 edges/connections)   
- old_to_new_node_id.csv (mapping users (2) 43613/filtered data -> 31021 (LCC)   
- game_game_dists_sq_20988.mmap -> upper triangle games relationships matrix   


## games: (enriched_games_filtered.scv)
20988 games (cols)  
<img width="810" height="121" alt="obraz" src="https://github.com/user-attachments/assets/6a438470-5956-41ad-8898-50e5e458e97f" />

## users: (users_filtered.csv)
43675 users (rows)   WHY??????   
  
|             steamid  | public  | country |  account_created |   last_logoff |
|---------------------:|--------:|--------:|-----------------:|--------------:|
|  **76561198064675174** |  True   |   IT    |  1.338658e+09    |      NaN      |
|   76561198109425210  |  True   |   BE    |  1.380726e+09    |      NaN      |
|   76561198281198045  |  True   |  NaN    |  1.454511e+09    |      NaN      |

## matrix (user_game_01_steam_users_appid_games.pkl) 
31021 users (rows)  
20988 games (cols)   

|   steam_id\app_id |   10 |   20 |   30 |   40 |   50 |   60 |   70 |   80 |   100 |   130 |
|------------------:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|------:|
|**76561198064675174**|    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198109425210 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198281198045 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561197994839969 |    1 |    0 |    1 |    1 |    0 |    1 |    1 |    1 |     1 |     0 |
| 76561197972380369 |    1 |    1 |    1 |    1 |    1 |    1 |    1 |    0 |     0 |     1 |
| 76561197992826872 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198362520139 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198859934865 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198011971157 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |    0 |     0 |     0 |
| 76561198004594504 |    0 |    1 |    0 |    0 |    1 |    0 |    1 |    0 |     0 |     1 |
