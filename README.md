# WikiShield - a guard against vandalism on Wikipedia

As a source of information, Wikipedia tends to be fairly reliable for a first pass on a new subject. It is an open knowledge repository edited and maintained by its users that has rightfully earned its place as the first stop for anyone seeking objective and description for what they need.  

However, occasionally there are vandalism edits made on Wikipedia, by which we mean edits that are done in an intentionally disruptive or malicious manner. This could involve inserting unpleasant language, non-sequiturs or obvious misinformation. Vandalism harms both the credibility of Wikipedia and diminishes its user experience. It could also pollute downstream platforms that rely on Wikipedia to summarize information. This project presents a machine learning model designed to accurately and efficiently detect vandalism edits on Wikipedia.

# Repo guide

The **data** directory contains our trainining and testing data, together with the Python scripts we used to preview the data files and call the APIs. See the README there for further explanations to the scripts.

The **feature_engineer** directory holds our scripts for feature engineering. The details of the features can be found below. 

The **EDA** directory is about exploratory data analysis. We produced various figures to analyze the features. 

The **models** directory collects all of our models, from baselines to the final flagship.

The **results** directory gives the result summary of all the models we considered, including our flagship.

The **checkpoint** directory stores some of our reports submitted during the project.

# Data collection

Our dataset comes from the training data of ClueBot NG (https://github.com/cluebotng), a well-established anti-vandalism bot. We further enrich the dataset using the MediaWiki and Wikidata APIs to gather additional features, including the actual content of the edit, the recent number of edits to the article, and the category of the article subject.

# Feature engineering

**Features directly available from ClueBot dataset:** 

[
    "user_edit_count",
    "user_distinct_pages",
    "user_warns",
    "num_recent_edits",
    "num_recent_reversions",
    "num_edits_5d_before",
    "current_minor",
    "EditID",
]

**Features from API:**

[
    "num_edits_5d_before",
    "added_lines",
    "deleted_lines"
    "is_person"
]

**Features engineered in the first round using other information from ClueBot dataset and "added_lines", "deleted_lines":**

[
    "account_age",
    "comment_empty",
    "is_IP",
    "word_count_added",
    "word_count_deleted",
]

Each of our models is a pipeline that starts with a vandalism score calculator (we do this to avoid data leakage and overfitting in cross-validations). **We put all the features into our model pipeline:** 

[
    "user_edit_count",
    "user_distinct_pages",
    "user_warns",
    "num_recent_edits",
    "num_recent_reversions",
    "num_edits_5d_before",
    "account_age",
    "word_count_added",
    "word_count_deleted",
    "comment_empty",
    "is_IP",
    "current_minor",
    "is_person",
    "EditID",
    "added_lines",
    "deleted_lines"
]

Here, “EditID” is technically not a feature, but our vandalism score calculator needs it for indexing purposes. The last three features ("EditID", "added_lines", "deleted_lines") will be combined as the **vandalism score**. After the vandalism scores are calculated, these three features are dropped and will not go into later parts of the model. The newly engineered feature vandalism score is added and will be considered in later parts of the pipeline.

# Model

We have a list of models (all with tuned hyperparameters). With accuracy, precision, recall, and F1 scores all considered, we chose to use a voting classifier that combines three gradient boosting models (CatBoost, LightGBM, XGBoost).

<img width="882" alt="Image20250628230222" src="https://github.com/user-attachments/assets/70626720-cf02-4379-be8d-15449352bbe1" />

