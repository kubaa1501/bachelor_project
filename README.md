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

 
### GENRE BUCKETS:
-20813 records (+) with no genre "" from the training set ( ~0,5 % of all (+))  
  
| steamid           |   appid | country | total_games_owned | total_playtime_minutes | median_playtime_minutes | unique_genres_played | name              | genres                       | developer       | publisher               | platforms         | release_date | user_count | game_total_playtime_minutes | owned | user_playtime_group_Action | user_playtime_group_Adventure | user_playtime_group_RPG | user_playtime_group_Casual | user_playtime_group_Indie | user_playtime_group_Racing | user_playtime_group_Simulation | user_playtime_group_Strategy | user_playtime_group_Sports | user_playtime_group_Violent | user_playtime_group_Adult | user_playtime_group_Non-gameplay_Tools | user_playtime_group_Other |
| ----------------- | ------: | ------- | ----------------: | ---------------------: | ----------------------: | -------------------: | ----------------- | ---------------------------- | --------------- | ----------------------- | ----------------- | ------------ | ---------: | --------------------------: | ----: | -------------------------: | ----------------------------: | ----------------------: | -------------------------: | ------------------------: | -------------------------: | -----------------------------: | ---------------------------: | -------------------------: | --------------------------: | ------------------------: | -------------------------------------: | ------------------------: |
| 76561197960266945 |      10 | RU      |              1503 |              1091628.0 |                    60.0 |                   27 | Counter-Strike    | Action                       | Valve           | Valve                   | windows;mac;linux | 2000-11-01   |     8366.0 |                 107248640.0 |     1 |              575679.447619 |                 126260.064286 |            62692.183333 |               25453.047619 |              55046.947619 |                1200.797619 |                   17330.330952 |                 76800.397619 |                1220.666667 |                   86.000000 |                 86.000000 |                           62053.000000 |              84251.116667 |
| 76561197960266945 | 1517290 | RU      |              1503 |              1091628.0 |                    60.0 |                   27 | Battlefield™ 2042 | Action;Adventure;Casual      | DICE            | Electronic Arts         | windows           | 19 Nov, 2021 |       6312 |                             |     0 |              577897.447619 |                 126260.064286 |            62692.183333 |               25453.047619 |              55046.947619 |                1200.797619 |                   17330.330952 |                 76800.397619 |                1220.666667 |                   86.000000 |                 86.000000 |                           62053.000000 |              84251.116667 |
| 76561197960266945 | 1361000 | RU      |              1503 |              1091628.0 |                    60.0 |                   27 | In Silence        | Action                       | Ravenhood Games | Ravenhood Games         | windows;mac       | 29 Oct, 2021 |        753 |                             |     0 |              577897.447619 |                 126260.064286 |            62692.183333 |               25453.047619 |              55046.947619 |                1200.797619 |                   17330.330952 |                 76800.397619 |                1220.666667 |                   86.000000 |                 86.000000 |                           62053.000000 |              84251.116667 |
| 76561197960266945 |  575550 | RU      |              1503 |              1091628.0 |                    60.0 |                   27 | Hell Girls        | Adventure;Indie;RPG;Strategy | Athena Works    | Athena Works;SakuraGame | windows;mac       | 12 Jan, 2017 |       1009 |                             |     0 |              577897.447619 |                 126260.064286 |            62692.183333 |               25453.047619 |              55046.947619 |                1200.797619 |                   17330.330952 |                 76800.397619 |                1220.666667 |                   86.000000 |                 86.000000 |                           62053.000000 |              84251.116667 |
| 76561197960266945 |  793400 | RU      |              1503 |              1091628.0 |                    60.0 |                   27 | Fist of Brave     | Action;Adventure;Indie       | ALOOF PROJECT   | Beliebrave              | windows           | 19 Feb, 2018 |          6 |                             |     0 |              577897.447619 |                 126260.064286 |            62692.183333 |               25453.047619 |              55046.947619 |                1200.797619 |                   17330.330952 |                 76800.397619 |                1220.666667 |                   86.000000 |                 86.000000 |                           62053.000000 |              84251.116667 |





    
</details>

<details>
  <summary><b>feature importance</b></summary> 
    
## xgb baseline:
  
| Feature                                  | Mean drop in NDCG@10 |        Std | Mean permuted NDCG@10 |
| ---------------------------------------- | -------------------: | ---------: | --------------------: |
| `game_total_playtime_minutes`            |       **0.58292324** | 0.00155112 |            0.25105577 |
| `user_count`                             |       **0.56902361** | 0.00164226 |            0.26495539 |
| `release_date`                           |       **0.16499448** | 0.00050787 |            0.66898453 |
| `genres`                                 |       **0.13768380** | 0.00051125 |            0.69629521 |
| `developer`                              |       **0.12377001** | 0.00068134 |            0.71020900 |
| `publisher`                              |       **0.10204180** | 0.00037157 |            0.73193721 |
| `platforms`                              |           0.03544365 | 0.00036427 |            0.79853536 |
| `total_games_owned`                      |           0.01032169 | 0.00031582 |            0.82365732 |
| `user_playtime_group_Violent`            |           0.00204458 | 0.00009196 |            0.83193443 |
| `median_playtime_minutes`                |           0.00137048 | 0.00010929 |            0.83260853 |
| `user_playtime_group_Non-gameplay_Tools` |           0.00067957 | 0.00015038 |            0.83329944 |
| `unique_genres_played`                   |           0.00054665 | 0.00010147 |            0.83343236 |
| `user_playtime_group_Other`              |           0.00032175 | 0.00011275 |            0.83365725 |
| `country`                                |           0.00022009 | 0.00014627 |            0.83375892 |
| `user_playtime_group_Casual`             |           0.00009159 | 0.00003826 |            0.83388742 |
| `user_playtime_group_Sports`             |           0.00007552 | 0.00000640 |            0.83390349 |
| `user_playtime_group_Indie`              |           0.00006984 | 0.00004772 |            0.83390917 |
| `user_playtime_group_Action`             |           0.00005110 | 0.00012138 |            0.83392790 |
| `total_playtime_minutes`                 |           0.00004807 | 0.00000985 |            0.83393094 |
| `user_playtime_group_Simulation`         |           0.00002744 | 0.00001835 |            0.83395157 |
| `user_playtime_group_Strategy`           |           0.00000271 | 0.00002659 |            0.83397629 |
| `user_playtime_group_RPG`                |          -0.00001566 | 0.00001532 |            0.83399467 |
| `user_playtime_group_Racing`             |          -0.00001622 | 0.00002376 |            0.83399523 |
| `user_playtime_group_Adult`              |          -0.00002528 | 0.00001999 |            0.83400429 |
| `user_playtime_group_Adventure`          |          -0.00005992 | 0.00006962 |            0.83403893 |

## xgb network:
| Rank | Feature                                | Feature group | Mean drop in NDCG@10 | Std drop |
| ---: | -------------------------------------- | ------------- | -------------------: | -------: |
|    1 | game_emb_0                             | embedding     |             0.987965 | 0.000272 |
|    2 | game_emb_1                             | embedding     |             0.916040 | 0.000843 |
|    3 | user_count                             | numeric       |             0.450489 | 0.000141 |
|    4 | game_emb_2                             | embedding     |             0.009604 | 0.000182 |
|    5 | game_total_playtime_minutes            | numeric       |             0.002632 | 0.000014 |
|    6 | game_emb_4                             | embedding     |             0.002138 | 0.000151 |
|    7 | game_emb_12                            | embedding     |             0.002096 | 0.000074 |
|    8 | game_emb_6                             | embedding     |             0.001822 | 0.000081 |
|    9 | game_emb_7                             | embedding     |             0.001739 | 0.000090 |
|   10 | game_emb_8                             | embedding     |             0.000758 | 0.000043 |
|   11 | game_emb_14                            | embedding     |             0.000637 | 0.000083 |
|   12 | total_games_owned                      | numeric       |             0.000410 | 0.000021 |
|   13 | game_emb_18                            | embedding     |             0.000406 | 0.000030 |
|   14 | game_emb_11                            | embedding     |             0.000280 | 0.000022 |
|   15 | release_date                           | numeric       |             0.000265 | 0.000025 |
|   16 | game_emb_30                            | embedding     |             0.000245 | 0.000031 |
|   17 | game_emb_29                            | embedding     |             0.000242 | 0.000023 |
|   18 | genres                                 | categorical   |             0.000216 | 0.000007 |
|   19 | game_emb_5                             | embedding     |             0.000215 | 0.000037 |
|   20 | game_emb_10                            | embedding     |             0.000204 | 0.000034 |
|   21 | game_emb_17                            | embedding     |             0.000192 | 0.000024 |
|   22 | game_emb_28                            | embedding     |             0.000177 | 0.000016 |
|   23 | game_emb_20                            | embedding     |             0.000166 | 0.000028 |
|   24 | publisher                              | categorical   |             0.000140 | 0.000009 |
|   25 | game_emb_3                             | embedding     |             0.000132 | 0.000010 |
|   26 | game_emb_26                            | embedding     |             0.000126 | 0.000028 |
|   27 | game_emb_22                            | embedding     |             0.000120 | 0.000001 |
|   28 | game_emb_24                            | embedding     |             0.000118 | 0.000021 |
|   29 | country                                | categorical   |             0.000115 | 0.000014 |
|   30 | game_emb_19                            | embedding     |             0.000109 | 0.000023 |
|   31 | game_emb_9                             | embedding     |             0.000109 | 0.000033 |
|   32 | game_emb_13                            | embedding     |             0.000108 | 0.000017 |
|   33 | game_emb_15                            | embedding     |             0.000107 | 0.000007 |
|   34 | user_playtime_group_Violent            | numeric       |             0.000095 | 0.000031 |
|   35 | developer                              | categorical   |             0.000094 | 0.000026 |
|   36 | game_emb_31                            | embedding     |             0.000093 | 0.000018 |
|   37 | game_emb_27                            | embedding     |             0.000090 | 0.000030 |
|   38 | median_playtime_minutes                | numeric       |             0.000090 | 0.000017 |
|   39 | friend_count                           | numeric       |             0.000081 | 0.000020 |
|   40 | user_playtime_group_Action             | numeric       |             0.000070 | 0.000011 |
|   41 | user_playtime_group_Non-gameplay_Tools | numeric       |             0.000060 | 0.000003 |
|   42 | game_emb_25                            | embedding     |             0.000058 | 0.000004 |
|   43 | game_emb_16                            | embedding     |             0.000056 | 0.000009 |
|   44 | user_playtime_group_Casual             | numeric       |             0.000053 | 0.000020 |
|   45 | user_playtime_group_Racing             | numeric       |             0.000043 | 0.000030 |
|   46 | game_emb_21                            | embedding     |             0.000036 | 0.000022 |
|   47 | unique_genres_played                   | numeric       |             0.000036 | 0.000001 |
|   48 | user_playtime_group_Other              | numeric       |             0.000035 | 0.000018 |
|   49 | user_playtime_group_RPG                | numeric       |             0.000035 | 0.000012 |
|   50 | user_playtime_group_Adult              | numeric       |             0.000034 | 0.000009 |
|   51 | game_emb_23                            | embedding     |             0.000026 | 0.000014 |
|   52 | user_playtime_group_Simulation         | numeric       |             0.000017 | 0.000006 |
|   53 | total_playtime_minutes                 | numeric       |             0.000010 | 0.000001 |
|   54 | user_playtime_group_Adventure          | numeric       |             0.000006 | 0.000019 |
|   55 | user_playtime_group_Strategy           | numeric       |             0.000003 | 0.000013 |
|   56 | user_playtime_group_Indie              | numeric       |             0.000000 | 0.000012 |
|   57 | platforms                              | categorical   |             0.000000 | 0.000000 |
|   58 | user_playtime_group_Sports             | numeric       |            -0.000005 | 0.000004 |


## xgb one embedding:
| Rank | Feature                                | Feature group | Mean drop in NDCG@10 | Std drop |
| ---: | -------------------------------------- | ------------- | -------------------: | -------: |
|    1 | game_emb_0                             | embedding     |             0.974195 | 0.000577 |
|    2 | user_count                             | numeric       |             0.475076 | 0.000497 |
|    3 | release_date                           | numeric       |             0.015984 | 0.000390 |
|    4 | game_total_playtime_minutes            | numeric       |             0.009521 | 0.000013 |
|    5 | genres                                 | categorical   |             0.002683 | 0.000014 |
|    6 | publisher                              | categorical   |             0.001548 | 0.000036 |
|    7 | total_games_owned                      | numeric       |             0.001159 | 0.000127 |
|    8 | platforms                              | categorical   |             0.000920 | 0.000024 |
|    9 | developer                              | categorical   |             0.000853 | 0.000078 |
|   10 | user_playtime_group_Violent            | numeric       |             0.000353 | 0.000050 |
|   11 | user_playtime_group_Action             | numeric       |             0.000108 | 0.000063 |
|   12 | user_playtime_group_Indie              | numeric       |             0.000093 | 0.000025 |
|   13 | median_playtime_minutes                | numeric       |             0.000091 | 0.000008 |
|   14 | country                                | categorical   |             0.000062 | 0.000012 |
|   15 | friend_count                           | numeric       |             0.000047 | 0.000002 |
|   16 | user_playtime_group_Racing             | numeric       |             0.000044 | 0.000017 |
|   17 | user_playtime_group_Strategy           | numeric       |             0.000044 | 0.000025 |
|   18 | user_playtime_group_Other              | numeric       |             0.000039 | 0.000036 |
|   19 | user_playtime_group_RPG                | numeric       |             0.000032 | 0.000019 |
|   20 | user_playtime_group_Non-gameplay_Tools | numeric       |             0.000030 | 0.000022 |
|   21 | user_playtime_group_Adult              | numeric       |             0.000012 | 0.000012 |
|   22 | user_playtime_group_Simulation         | numeric       |             0.000005 | 0.000011 |
|   23 | user_playtime_group_Adventure          | numeric       |             0.000001 | 0.000001 |
|   24 | user_playtime_group_Casual             | numeric       |            -0.000001 | 0.000019 |
|   25 | user_playtime_group_Sports             | numeric       |            -0.000001 | 0.000017 |
|   26 | unique_genres_played                   | numeric       |            -0.000002 | 0.000037 |
|   27 | total_playtime_minutes                 | numeric       |            -0.000005 | 0.000006 |


## xgb only embeddings:
| Rank | Feature     | Mean drop in NDCG@10 | Std drop |
| ---: | ----------- | -------------------: | -------: |
|    1 | game_emb_0  |             0.142242 | 0.001715 |
|    2 | game_emb_1  |             0.061443 | 0.001368 |
|    3 | game_emb_6  |             0.003491 | 0.001691 |
|    4 | game_emb_8  |             0.003253 | 0.000030 |
|    5 | game_emb_3  |             0.001473 | 0.000186 |
|    6 | game_emb_15 |             0.001169 | 0.000062 |
|    7 | game_emb_28 |             0.000887 | 0.000172 |
|    8 | game_emb_29 |             0.000887 | 0.000116 |
|    9 | game_emb_2  |             0.000811 | 0.000082 |
|   10 | game_emb_16 |             0.000803 | 0.000070 |
|   11 | game_emb_14 |             0.000633 | 0.000066 |
|   12 | game_emb_31 |             0.000514 | 0.000091 |
|   13 | game_emb_24 |             0.000392 | 0.000090 |
|   14 | game_emb_25 |             0.000387 | 0.000070 |
|   15 | game_emb_23 |             0.000345 | 0.000143 |
|   16 | game_emb_26 |             0.000243 | 0.000020 |
|   17 | game_emb_27 |             0.000220 | 0.000021 |
|   18 | game_emb_22 |             0.000192 | 0.000085 |
|   19 | game_emb_20 |             0.000180 | 0.000047 |
|   20 | game_emb_21 |             0.000119 | 0.000020 |
|   21 | game_emb_18 |             0.000077 | 0.000138 |
|   22 | game_emb_19 |             0.000059 | 0.000052 |
|   23 | game_emb_30 |            -0.000185 | 0.000020 |
|   24 | game_emb_12 |            -0.000357 | 0.000026 |
|   25 | game_emb_13 |            -0.000601 | 0.000129 |
|   26 | game_emb_7  |            -0.000646 | 0.000231 |
|   27 | game_emb_9  |            -0.000673 | 0.000108 |
|   28 | game_emb_17 |            -0.000716 | 0.000091 |
|   29 | game_emb_10 |            -0.001774 | 0.000206 |
|   30 | game_emb_11 |            -0.001938 | 0.000110 |
|   31 | game_emb_5  |            -0.002663 | 0.000114 |
|   32 | game_emb_4  |            -0.004330 | 0.000589 |
  


## xgb embeddings +basic info:
| Rank | Feature                | Feature group | Mean drop in NDCG@10 | Std drop |
| ---: | ---------------------- | ------------- | -------------------: | -------: |
|    1 | game_emb_0             | embedding     |             0.182333 | 0.001732 |
|    2 | game_emb_1             | embedding     |             0.053929 | 0.000746 |
|    3 | unique_genres_played   | basic_info    |             0.037141 | 0.000784 |
|    4 | total_playtime_minutes | basic_info    |             0.014159 | 0.000115 |
|    5 | game_emb_17            | embedding     |             0.007152 | 0.000132 |
|    6 | game_emb_7             | embedding     |             0.003677 | 0.000489 |
|    7 | game_emb_6             | embedding     |             0.003302 | 0.000177 |
|    8 | game_emb_3             | embedding     |             0.001395 | 0.000153 |
|    9 | game_emb_11            | embedding     |             0.001337 | 0.000128 |
|   10 | game_emb_13            | embedding     |             0.001320 | 0.000048 |
|   11 | game_emb_14            | embedding     |             0.001127 | 0.000311 |
|   12 | game_emb_30            | embedding     |             0.000920 | 0.000134 |
|   13 | game_emb_25            | embedding     |             0.000871 | 0.000065 |
|   14 | game_emb_8             | embedding     |             0.000858 | 0.000140 |
|   15 | game_emb_4             | embedding     |             0.000770 | 0.000161 |
|   16 | game_emb_15            | embedding     |             0.000633 | 0.000177 |
|   17 | game_emb_12            | embedding     |             0.000442 | 0.000170 |
|   18 | game_emb_28            | embedding     |             0.000383 | 0.000231 |
|   19 | game_emb_16            | embedding     |             0.000339 | 0.000029 |
|   20 | game_emb_18            | embedding     |             0.000330 | 0.000071 |
|   21 | game_emb_19            | embedding     |             0.000291 | 0.000166 |
|   22 | game_emb_20            | embedding     |             0.000235 | 0.000077 |
|   23 | game_emb_21            | embedding     |             0.000210 | 0.000064 |
|   24 | game_emb_29            | embedding     |             0.000173 | 0.000055 |
|   25 | game_emb_27            | embedding     |             0.000027 | 0.000084 |
|   26 | game_emb_26            | embedding     |            -0.000029 | 0.000112 |
|   27 | game_emb_24            | embedding     |            -0.000090 | 0.000301 |
|   28 | game_emb_22            | embedding     |            -0.000143 | 0.000032 |
|   29 | game_emb_10            | embedding     |            -0.000168 | 0.000043 |
|   30 | game_emb_23            | embedding     |            -0.000205 | 0.000092 |
|   31 | game_emb_5             | embedding     |            -0.000265 | 0.000200 |
|   32 | game_emb_31            | embedding     |            -0.000423 | 0.000205 |
|   33 | game_emb_2             | embedding     |            -0.000507 | 0.000345 |
|   34 | game_emb_9             | embedding     |            -0.001481 | 0.000092 |


</details> 

<details>
  <summary><b>plots</b></summary> 
  <img width="2200" height="1760" alt="01_scatter_emb0_emb1_color_usercount_size_playtime" src="https://github.com/user-attachments/assets/6ea5bd7e-9be7-4d49-98ef-d1f47ed00ce7" />
<img width="2200" height="1760" alt="emb0_emb1_hexbin_mean_log_playtime" src="https://github.com/user-attachments/assets/aedd45fb-4272-4cce-b93a-a625d8fae93b" />
<img width="2200" height="1760" alt="emb0_emb1_hexbin_mean_log_user_count" src="https://github.com/user-attachments/assets/cd0b3244-1322-4792-a770-695a94042884" />
  <img width="1980" height="1540" alt="02_hexbin_emb0_vs_log_user_count" src="https://github.com/user-attachments/assets/93d10fd9-77da-4a54-94f7-75662162c3e4" />
<img width="1980" height="1540" alt="03_hexbin_emb0_vs_log_game_total_playtime" src="https://github.com/user-attachments/assets/da779f39-2c55-4cfd-bd28-26600146993d" />
<img width="2200" height="1540" alt="04_hist_emb0_by_popularity_group" src="https://github.com/user-attachments/assets/d76bf7a0-76e4-4d37-9e40-a17af4a31ac0" />
<img width="1980" height="1320" alt="05_binned_emb0_vs_mean_log_user_count" src="https://github.com/user-attachments/assets/b68f66d3-39c8-47bb-a4fe-83b26b2edf55" />
<img width="1980" height="1320" alt="06_binned_emb0_vs_mean_log_playtime" src="https://github.com/user-attachments/assets/0cb9d3c7-4552-44bf-b7d0-25a9eeaf6131" />
<img width="1540" height="1320" alt="07_spearman_correlation_heatmap" src="https://github.com/user-attachments/assets/98ae00d4-f02e-4ade-9e30-56e3c6dd4969" />
<img width="3937" height="3773" alt="genre_one_vs_rest_panels_mapped" src="https://github.com/user-attachments/assets/c4922a68-89de-4816-bf66-0f094bc8f2d9" />
<img width="3080" height="1540" alt="genre_share_across_emb0_bins_heatmap_mapped" src="https://github.com/user-attachments/assets/70907484-79a0-4fba-a812-1b754a87b5c2" />

## NEW
<img width="2520" height="2040" alt="01_scatter_emb0_emb1_color_usercount_size_playtime_v2" src="https://github.com/user-attachments/assets/f8816dba-4d33-4ef3-867b-e644fd2c85b1" />

  <img width="3600" height="1488" alt="02_hexbin_emb0_vs_user_count_raw_and_log" src="https://github.com/user-attachments/assets/a187ebf7-cd37-495e-8746-f45ff45861b6" />
    
<img width="2520" height="1728" alt="04_hist_emb0_by_popularity_group_v2" src="https://github.com/user-attachments/assets/781c506b-7933-4484-8ca0-a4a80e2be2b4" />

  <img width="3600" height="1488" alt="05_binned_emb0_vs_user_count_raw_and_log" src="https://github.com/user-attachments/assets/9b70b617-b768-48c0-b65c-c7729a7774d1" />

  <img width="1800" height="1560" alt="07_spearman_correlation_heatmap_v2" src="https://github.com/user-attachments/assets/2558a8be-56eb-45ab-9155-19acb486c546" />
  
<img width="4293" height="4306" alt="genre_one_vs_rest_panels_mapped_v2" src="https://github.com/user-attachments/assets/ad5acd8c-5708-4c4c-98cf-5cbe6bafb491" />
  
<img width="3720" height="1800" alt="genre_share_across_emb0_bins_heatmap_mapped_v2_equal_width" src="https://github.com/user-attachments/assets/683d6112-d782-4b35-be90-4e5ce1bf9059" />
  
<img width="3720" height="1800" alt="genre_share_across_emb0_bins_heatmap_mapped_v2_quantile" src="https://github.com/user-attachments/assets/213404f9-eba1-4b54-8a27-819ea427a4c2" />

</details>
<details>
  <summary><b>SHAP</b></summary> 

### Interaction structure changes after adding the embedding
  
For the baseline model:  
- `num__user_count` interacts most strongly with `num__release_date`  
- `num__game_total_playtime_minutes` interacts most strongly with `num__user_count`  
  
For the embedding model:  
- `num__user_count` interacts most strongly with `num__game_emb_0`  
- `num__game_emb_0` interacts most strongly with `num__user_count`  
- `num__release_date` also interacts strongly with `num__game_emb_0`  

    
This suggests the embedding is used together with popularity and recency signals.  

  ## Top features from `xgb_baseline`
  
| rank | feature | mean_abs_shap | importance_share |
|---:|---|---:|---:|
| 1 | `num__user_count` | 12.1596 | 0.7326 |
| 2 | `num__game_total_playtime_minutes` | 2.4655 | 0.1485 |
| 3 | `num__release_date` | 0.6611 | 0.0398 |
| 4 | `num__user_playtime_group_Other` | 0.1495 | 0.0090 |
| 5 | `num__total_games_owned` | 0.1493 | 0.0090 |
| 6 | `num__median_playtime_minutes` | 0.1449 | 0.0087 |
| 7 | `num__user_playtime_group_Indie` | 0.1285 | 0.0077 |
| 8 | `num__user_playtime_group_Strategy` | 0.1064 | 0.0064 |
| 9 | `num__user_playtime_group_RPG` | 0.0942 | 0.0057 |
| 10 | `num__user_playtime_group_Sports` | 0.0777 | 0.0047 |

## Plots:
<img width="1588" height="1078" alt="scatter_num__game_total_playtime_minutes" src="https://github.com/user-attachments/assets/baeacf80-2809-40fa-8997-a6096a564988" />
popular game (user_count (popularity) playtime (game activity) -> models score goes up 
<img width="1593" height="1078" alt="scatter_num__median_playtime_minutes" src="https://github.com/user-attachments/assets/788c58c2-5169-4145-993b-87ca07ea8c85" />
no stabile sygnal  if SHAP score <0 -> prediction goes down
<img width="1588" height="1078" alt="scatter_num__release_date" src="https://github.com/user-attachments/assets/eaba991d-06fd-425a-a9a3-99ef4cdca300" />
old games -> SHAP lower  
new games -> SHAP up   
<img width="1588" height="1078" alt="scatter_num__total_games_owned" src="https://github.com/user-attachments/assets/d99ada5d-56eb-40f4-b196-31092a52f51d" />
more games owned = higher SHAP   
player with 2000 games is more likely to have that particular game
<img width="1571" height="1078" alt="scatter_num__user_count" src="https://github.com/user-attachments/assets/b29e9f40-09fc-497f-983f-d72e8eafaee8" />
biggr user_count -> lower SHAP -> model score lower (punishing)
baseline without user_count (0.32 MRR)  
baseline (0.82 MRR)  
popularity (0.60 MRR)   
<img width="1616" height="1078" alt="scatter_num__user_playtime_group_Indie" src="https://github.com/user-attachments/assets/c935377a-7cb9-4409-b80b-2610f5e3b371" />
indie -> lower score
<img width="1583" height="1078" alt="scatter_num__user_playtime_group_Other" src="https://github.com/user-attachments/assets/28862e96-4a84-4245-aa89-ea2f9cd7886e" />
weak signal
<img width="1620" height="1078" alt="scatter_num__user_playtime_group_Strategy" src="https://github.com/user-attachments/assets/25208743-7a74-45fc-ad27-c365f79e8b32" />
strategy -> lower score.
### Model prediction is here about popularity - not about what fits your preferences

<img width="1795" height="2509" alt="shap_bar" src="https://github.com/user-attachments/assets/2e69c181-7575-405f-b632-b8dade2868eb" />
core of model : user_count+playtime+release_date - rest is minor 
<img width="1789" height="2068" alt="shap_beeswarm" src="https://github.com/user-attachments/assets/b2ca6660-6431-4a65-9ab2-0004cd28a70c" />
(one dot = user-game pair)
-> right -> score goes up (more "owned")  
<- left <- lowering the score  
<img width="1789" height="2068" alt="shap_violin" src="https://github.com/user-attachments/assets/e7b174a7-9c72-46cf-a67c-9c2a443669db" />
<img width="1844" height="2494" alt="waterfall_highest_prediction" src="https://github.com/user-attachments/assets/0e07d31d-9239-4ddb-a77a-2091592b2ca4" />
HIGHEST PREDICTION
<img width="1854" height="2494" alt="waterfall_lowest_prediction" src="https://github.com/user-attachments/assets/2cc59862-1890-4164-96fe-ebd22a5d2c92" />
LOWEST PREDICTION
<img width="1784" height="2494" alt="waterfall_median_prediction" src="https://github.com/user-attachments/assets/c146c054-4239-4330-b98e-21dbbd2a7de0" />
MEDIAN PREDICTION 

## SO IT IS ABOUT:
- for high prediction - low popularity -> boost  
- for lowest prediction - big popularity -> decrease  
  so if the game is popular- decrease it, if the game is neeshe- boost. so user_count works like a correction.  
  
## Top features from `xgb_one_embedding`
    
| rank | feature | mean_abs_shap | importance_share |
|---:|---|---:|---:|
| 1 | `num__user_count` | 16.3508 | 0.6112 |
| 2 | `num__game_emb_0` | 8.1138 | 0.3033 |
| 3 | `num__release_date` | 0.7825 | 0.0292 |
| 4 | `num__game_total_playtime_minutes` | 0.5668 | 0.0212 |
| 5 | `num__median_playtime_minutes` | 0.2307 | 0.0086 |
| 6 | `num__total_games_owned` | 0.1022 | 0.0038 |
| 7 | `num__user_playtime_group_RPG` | 0.0899 | 0.0034 |
| 8 | `num__friend_count` | 0.0638 | 0.0024 |
| 9 | `num__user_playtime_group_Other` | 0.0623 | 0.0023 |
| 10 | `num__user_playtime_group_Casual` | 0.0606 | 0.0023 |

## Plots:
<img width="1604" height="1078" alt="scatter_num__friend_count" src="https://github.com/user-attachments/assets/e040682b-b99d-4361-9ef5-50be27cdb8db" />
friend_count ↑ → prediction ↑
- if a user has a lot of friends -> he is active? -> buys/has more games THEORY 
<img width="1592" height="1078" alt="scatter_num__game_emb_0" src="https://github.com/user-attachments/assets/9e4d597f-7e95-419b-a852-a0c3186bc063" />
emb0 = popularity + data structrure
<img width="1596" height="1078" alt="scatter_num__game_total_playtime_minutes" src="https://github.com/user-attachments/assets/04e7d5a3-8989-484e-a023-ba5a169222ca" />
<img width="1572" height="1078" alt="scatter_num__median_playtime_minutes" src="https://github.com/user-attachments/assets/5b7135ff-9220-40c8-bacb-ab9bbdabd966" />
<img width="1595" height="1078" alt="scatter_num__release_date" src="https://github.com/user-attachments/assets/b2c52f73-4f4a-41d8-bc5b-ef3fb7ea3f95" />
<img width="1596" height="1078" alt="scatter_num__total_games_owned" src="https://github.com/user-attachments/assets/40e68f64-7fdb-442d-a3f3-096c96b67cfd" />
<img width="1599" height="1078" alt="scatter_num__user_count" src="https://github.com/user-attachments/assets/57da74ad-2485-4e87-bb54-ec734bc31943" />
<img width="1601" height="1078" alt="scatter_num__user_playtime_group_RPG" src="https://github.com/user-attachments/assets/0128e440-31cc-4825-80e6-0dbf92081385" />
<img width="1795" height="2509" alt="shap_bar" src="https://github.com/user-attachments/assets/d46021e6-8573-49f9-a278-aa1425855f77" />
<img width="1789" height="2068" alt="shap_beeswarm" src="https://github.com/user-attachments/assets/62bc47ce-4cf9-4659-a8ad-1d865a69b3e4" />
<img width="1789" height="2068" alt="shap_violin" src="https://github.com/user-attachments/assets/e4df8edb-82c3-4b7d-8bb5-b6fc80584f24" />
<img width="1739" height="2494" alt="waterfall_highest_prediction" src="https://github.com/user-attachments/assets/678044a0-cc2e-4fef-92b0-5d4165914a19" />
<img width="1739" height="2494" alt="waterfall_lowest_prediction" src="https://github.com/user-attachments/assets/f71ae827-61cc-42b6-a28b-48207ffdb111" />
<img width="1787" height="2494" alt="waterfall_median_prediction" src="https://github.com/user-attachments/assets/5458fcd6-a0a2-47fe-9645-612d32a7e490" />


## Feature importance comparison (SHAP)

| Rank | Feature | Baseline mean\|SHAP\| | Baseline share | Baseline top interaction | Embedding mean\|SHAP\| | Embedding share | Embedding top interaction | Combined mean\|SHAP\| |
|---:|---|---:|---:|---|---:|---:|---|---:|
| 1 | `num__user_count` | 12.1596 | 73.26% | `num__release_date` | 16.3508 | 61.12% | `num__game_emb_0` | 28.5105 |
| 2 | `num__game_emb_0` | – | – | – | 8.1138 | 30.33% | `num__user_count` | 8.1138 |
| 3 | `num__game_total_playtime_minutes` | 2.4655 | 14.85% | `num__user_count` | 0.5668 | 2.12% | `num__game_emb_0` | 3.0323 |
| 4 | `num__release_date` | 0.6611 | 3.98% | `num__user_count` | 0.7825 | 2.92% | `num__game_emb_0` | 1.4436 |
| 5 | `num__median_playtime_minutes` | 0.1449 | 0.87% | `num__user_count` | 0.2307 | 0.86% | `num__release_date` | 0.3756 |
| 6 | `num__total_games_owned` | 0.1493 | 0.90% | `num__user_count` | 0.1022 | 0.38% | `num__game_emb_0` | 0.2516 |
| 7 | `num__user_playtime_group_Other` | 0.1495 | 0.90% | `num__unique_genres_played` | 0.0623 | 0.23% | – | 0.2117 |
| 8 | `num__user_playtime_group_RPG` | 0.0942 | 0.57% | – | 0.0899 | 0.34% | `num__game_emb_0` | 0.1841 |
| 9 | `num__user_playtime_group_Indie` | 0.1285 | 0.77% | `num__user_playtime_group_Casual` | 0.0069 | 0.03% | – | 0.1354 |
| 10 | `num__user_playtime_group_Strategy` | 0.1064 | 0.64% | `num__total_playtime_minutes` | 0.0288 | 0.11% | – | 0.1352 |
| 11 | `num__user_playtime_group_Non-gameplay_Tools` | 0.0705 | 0.42% | – | 0.0552 | 0.21% | – | 0.1258 |
| 12 | `num__user_playtime_group_Casual` | 0.0601 | 0.36% | – | 0.0606 | 0.23% | – | 0.1207 |
| 13 | `num__user_playtime_group_Racing` | 0.0755 | 0.45% | – | 0.0381 | 0.14% | – | 0.1136 |
| 14 | `num__user_playtime_group_Sports` | 0.0777 | 0.47% | – | 0.0275 | 0.10% | – | 0.1052 |
| 15 | `num__user_playtime_group_Adventure` | 0.0535 | 0.32% | – | 0.0487 | 0.18% | – | 0.1022 |
  
Jak to czytać:
  
*mean|SHAP| mówi, jak silnie dana cecha wpływa na predykcję średnio w całym zbiorze.
share mówi, jaki procent całkowitej ważności przypada na tę cechę.
top interaction pokazuje, z jaką inną cechą dana cecha najczęściej współdziała w modelu.*
  
SHAP analysis showed that in both XGBoost models the dominant predictor was `user_count`, indicating a strong popularity effect. In the baseline model the second most important feature was `game_total_playtime_minutes`, whereas after adding the embedding this feature lost much of its importance. At the same time, `game_emb_0` became the second most important feature overall in the embedding-based model, accounting for roughly 30% of total SHAP importance. This suggests that the embedding provides substantial additional information beyond simple popularity and activity statistics. The results also indicate that the model relies not only on game-level features but also on user preference signals, such as historical playtime across genre groups and the diversity of played genres.
  
  </details> 
