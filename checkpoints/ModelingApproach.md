Proposed Modeling Approach

Features

    Number of times a word appears in vandalism edits vs normal edits 
    Timestamps of edit 
    Page view counts (at time of edit occurring; there are some issues with time evolution)
    Userwarns
    User edit count
    User distinct pages
    Page category (eg. sports, science, celebrities) - easy to one hot encode
    Length of edit
Targets

    Classify an edit as fraudulent or not


Model type 
        
        Main: Classification using XGBoost and Optuna
        Compare performance of XGBoost with KNN and Baseline Logistic Regression
