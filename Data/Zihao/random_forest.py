import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, root_mean_squared_error
from sklearn.model_selection import train_test_split, KFold



df_train = pd.read_csv("train_data_with_editcounts_isperson.csv")

num_splits = 5
num_models = 4
kfold = KFold(num_splits, random_state=216, shuffle=True)

## This array will hold the mse for each model and split
rmses = np.zeros((num_models, num_splits))

accs = np.zeros(3)

## sets a split counter
i = 0

## loop through the kfold here
for train_index, test_index in kfold.split(df_train):
    ## cv training set
    df_tt = df_train.iloc[train_index]

    ## cv holdout set
    df_ho = df_train.iloc[test_index]

    log_reg = LogisticRegression(penalty=None)
    log_reg.fit(df_tt[["user_warns", "num_recent_reversions", "num_edits_5d_before", "is_person"]], df_tt.isvandalism)
    log_pred = log_reg.predict(df_ho[["user_warns", "num_recent_reversions", "num_edits_5d_before", "is_person"]])

    rmses[0, i] = root_mean_squared_error(df_ho.isvandalism, log_pred)


    tree = DecisionTreeClassifier(
        #max_depth = 10, 
        min_samples_leaf = 5, # minimum number of samples in each leaf, to prevent overfitting
        random_state= 216
        )
    tree.fit(df_tt[["user_warns", "num_recent_reversions", "num_edits_5d_before", "is_person"]], df_tt.isvandalism)
    tree_pred = tree.predict(df_ho[["user_warns", "num_recent_reversions", "num_edits_5d_before", "is_person"]])

    rmses[1, i] = root_mean_squared_error(df_ho.isvandalism, tree_pred)


    rf = RandomForestClassifier(
        n_estimators = 500, # number of trees in ensemble
        #max_depth = 10, # max_depth of each tree
        min_samples_leaf = 5, 
        #max_features = 2, # default is round(sqrt(num_features)), which in this case is 1.
        bootstrap= True, # sampling with replacement
        max_samples = 500, # number of training samples selected with replacement to build tree
        random_state = 216 # for consistency
        )
    
    rf.fit(df_tt[["user_warns", "num_recent_reversions", "num_edits_5d_before", "is_person"]], df_tt.isvandalism)
    rf_pred = rf.predict(df_ho[["user_warns", "num_recent_reversions", "num_edits_5d_before", "is_person"]])

    rmses[2, i] = root_mean_squared_error(df_ho.isvandalism, rf_pred)

    et = ExtraTreesClassifier(
        n_estimators = 500, 
        #max_depth = 10, 
        min_samples_leaf = 5, 
        #max_features = 2, 
        bootstrap= True, 
        max_samples = 500, 
        random_state = 216 
        )
    
    et.fit(df_tt[["user_warns", "num_recent_reversions", "num_edits_5d_before", "is_person"]], df_tt.isvandalism)
    et_pred = et.predict(df_ho[["user_warns", "num_recent_reversions", "num_edits_5d_before", "is_person"]])

    rmses[3, i] = root_mean_squared_error(df_ho.isvandalism, et_pred)

    acc = np.array([accuracy_score(df_ho.isvandalism, tree_pred),  accuracy_score(df_ho.isvandalism, rf_pred), accuracy_score(df_ho.isvandalism, et_pred)])
    accs = accs + acc

    i = i + 1

accs = accs / num_splits

    ## Find the avg cv mse for each model here
print(f"Logistic Regression Avg. CV RMSE: {np.mean(rmses[0,:])} and STD: {np.std(rmses[0,:])}")
print(f"Decision Tree Avg. CV MSE: {np.mean(rmses[1,:])} and STD: {np.std(rmses[1,:])}")
print(f"Random Forest Avg. CV MSE: {np.mean(rmses[2,:])} and STD: {np.std(rmses[2,:])}")
print(f"Extra Tree Avg. CV MSE: {np.mean(rmses[3,:])} and STD: {np.std(rmses[3,:])}")

print(pd.DataFrame(accs, index= ['tree', 'rf', 'et'], columns = ['avg_accuracy']))


