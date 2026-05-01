
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
<img width="2520" height="2040" alt="01_scatter_emb0_emb1_color_usercount_size_playtime_v2" src="https://github.com/user-attachments/assets/f8816dba-4d33-4ef3-867b-e644fd2c85b1" />

  <img width="3600" height="1488" alt="02_hexbin_emb0_vs_user_count_raw_and_log" src="https://github.com/user-attachments/assets/a187ebf7-cd37-495e-8746-f45ff45861b6" />
    
<img width="2520" height="1728" alt="04_hist_emb0_by_popularity_group_v2" src="https://github.com/user-attachments/assets/781c506b-7933-4484-8ca0-a4a80e2be2b4" />

  <img width="3600" height="1488" alt="05_binned_emb0_vs_user_count_raw_and_log" src="https://github.com/user-attachments/assets/9b70b617-b768-48c0-b65c-c7729a7774d1" />

  <img width="1800" height="1560" alt="07_spearman_correlation_heatmap_v2" src="https://github.com/user-attachments/assets/2558a8be-56eb-45ab-9155-19acb486c546" />
  
<img width="4293" height="4306" alt="genre_one_vs_rest_panels_mapped_v2" src="https://github.com/user-attachments/assets/ad5acd8c-5708-4c4c-98cf-5cbe6bafb491" />
  
<img width="3720" height="1800" alt="genre_share_across_emb0_bins_heatmap_mapped_v2_equal_width" src="https://github.com/user-attachments/assets/683d6112-d782-4b35-be90-4e5ce1bf9059" />
  
<img width="3720" height="1800" alt="genre_share_across_emb0_bins_heatmap_mapped_v2_quantile" src="https://github.com/user-attachments/assets/213404f9-eba1-4b54-8a27-819ea427a4c2" />

</details>

