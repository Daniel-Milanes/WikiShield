An active community of volunteer editors on Wikipedia ensures that instances of outright vandalism get reverted relatively quickly, but often legitimate-looking disinformation can remain undetected for a long time, in some cases for 10+ years! (see e.g. this list of hoax articles or this list of instances of citogenesis)

This project aims to create a model that can look at a Wikipedia article and classify it as legitimate or as a possible hoax. Potentially useful data includes the text of the article, the frequency of inline citations, the text of the references cited, pageview analytics and edit history of the article, and user history of the editors responsible for the article.

Data collection:
There have been Wikipedia datasets previously curated by research projects for the express purpose of identifying hoaxes. Not all of the datasets are public however, and if we decide to augment existing public datasets, Wikipedia provides several APIs for programmatic access to its text content, as well as page analytics, edit history and so on. There are regular dumps of data at dumps.wikimedia.org that can be simply downloaded too.
