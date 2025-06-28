# WikiShield - a guard against vandalism on Wikipedia

As a source of information, Wikipedia tends to be fairly reliable for a first pass on a new subject. an open knowledge repository edited and maintained by its users that has rightfully earned its place as the first stop for anyone seeking 

This project aims to create a model that can look at a Wikipedia article and classify it as legitimate or as a possible hoax. Potentially useful data includes the text of the article, the frequency of inline citations, the text of the references cited, pageview analytics and edit history of the article, and user history of the editors responsible for the article.

Data collection:
There have been Wikipedia datasets previously curated by research projects for the express purpose of identifying hoaxes. Not all of the datasets are public however, and if we decide to augment existing public datasets, Wikipedia provides several APIs for programmatic access to its text content, as well as page analytics, edit history and so on. There are regular dumps of data at dumps.wikimedia.org that can be simply downloaded too.