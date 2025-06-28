# WikiShield - a guard against vandalism on Wikipedia

As a source of information, Wikipedia tends to be fairly reliable for a first pass on a new subject. It is an open knowledge repository edited and maintained by its users that has rightfully earned its place as the first stop for anyone seeking objective and description for what they need.  

However, occasionally there are vandalism edits made on Wikipedia, by which we mean edits that are done in an intentionally disruptive or malicious manner. This could involve inserting unpleasant language, non-sequiturs or obvious misinformation. Vandalism harms both the credibility of Wikipedia and diminishes its user experience. It could also pollute downstream platforms that rely on Wikipedia to summarize information. This project presents a machine learning model designed to accurately and efficiently detect vandalism edits on Wikipedia.

# Data collection

Our dataset comes from the training data of ClueBot NG (https://github.com/cluebotng), a well-established anti-vandalism bot. We further enrich the dataset using the MediaWiki and Wikidata APIs to gather additional features, including the actual content of the edit, the recent number of edits to the article, and the category of the article subject. The data files and scripts are contained in the "data" directory. See the README there for further explanations to the scripts.

# Feature engineering

Features from ClueBot dataset:...
Features from API:...
Vandalism score:...
Final features:...

# Model
