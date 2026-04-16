### CODE: make_positive_splits_from_pairs.py
Inputs:  
- **baseline_features_playtime_capped_owned_semicolon.csv** 
- **validation_user_game_pairs.csv**
- **test_user_game_pairs.csv**
  
Outputs:
- train_positive.csv  
- val_positive.csv  
- test_positive.csv  
  
### CODE: make_correct_splits.py
  
It takes the already prepared positive interactions and adds negative samples, so each output file contains both:
  
games the user owns / interacted with (owned = 1)  
games the user did not own (owned = 0)  
  
Inputs:
- train_positive.csv  
- val_positive.csv  
- test_positive.csv 
- **games.csv** - game catalog

Negatives per positive:
- Train : 10 negatives / 1 positive
- Val : 100 negatives / 1 positive
- Test : 100 negatives / 1 positive

Negative sampling strategy (weighted sampling): 
Target:  
- **30 % popular games**
- **70% random**
If its not possible (user has not enough popular games to sample from for remaining negatives -> fill with random, if not enough random -> duplicates here are allowed inside a split)
  
It uses a **round robin** for processing order  
train → val → test → train → val → test ...  
  
**Why?** 
  
To make sure:  
  
- negatives are assigned fairly across splits  
- one split doesn’t “consume” all good candidates first  

Script is being very careful with data leaking:  
It builds a forbidden set:  
- all user’s positive games  
- games already used in other splits  

This prevents the same sampled negative game from appearing across train, validation, and test for the same user.  

Outputs:
- train.csv
- val.csv
- test.csv


  
