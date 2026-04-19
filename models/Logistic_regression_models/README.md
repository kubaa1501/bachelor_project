### MODEL: lr_baseline.py
  
It trains, validates, and evaluates a Logistic Regression baseline for the game recommendation task.  
  
The script builds a full sklearn pipeline that:  
- preprocesses numeric features  
- preprocesses categorical features  
- trains a Logistic Regression classifier  
- selects the best hyperparameter setting on validation data  
- evaluates the best model on the test set as a ranking model  
*Additionally, it creates learning curve experiments for the best configuration.*

--------------------------------------

Input:   
- train.csv
- val.csv
- test.csv
