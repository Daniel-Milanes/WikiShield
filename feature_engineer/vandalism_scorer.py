import re
from collections import defaultdict
from typing import Iterable, Set
from sklearn.base import BaseEstimator, TransformerMixin, _fit_context
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import MultinomialNB





class VandalismScorer(TransformerMixin, BaseEstimator):
    """
    A simple Naive Bayes inspired scorer that estimates the probability
    that a given edit is vandalism based on the words added in that edit.
    Implementation of class based on the template implementation given at
    https://github.com/scikit-learn-contrib/project-template/blob/main/skltemplate/_template.py
    (template file as of June 25, 2025)

    Parameters
    ----------
    smoothing : int, default=1
        Smoothing parameter for Laplace smoothing.
    
    Attributes
    ----------
    vandalism_counts_ : defaultdict(int)
        Dictionary to store counts of words in vandalism edits.
    constructive_counts_ : defaultdict(int)
        Dictionary to store counts of words in constructive edits.
    word_probs_ : dict
        Dictionary to store probabilities of words in vandalism edits.
    
    """

    # This is a dictionary allowing to define the type of parameters.
    # It is used to validate parameters within the `_fit_context` decorator.
    _parameter_constraints = {"smoothing": [int], "n_splits": [int], "fit_prior": [bool], "random_state": [int]}

    def __init__(self, smoothing: int = 1, n_splits: int = 4, random_state = 42, fit_prior=False) -> None:
        """
        Initialize the scorer with Laplace smoothing parameter.
        """
        self.smoothing = smoothing
        self.n_splits = n_splits
        self.random_state = random_state
        self.vectorizer_ = CountVectorizer()
        self.fit_prior = fit_prior
        self.nb_ = MultinomialNB(fit_prior=fit_prior)

    @_fit_context(prefer_skip_nested_validation=True)
    def fit(
        self, X, labels
    ) -> None:
        """
        Train the Naive Bayes classifier by building a vocabulary of all words seen.

        Parameters:
            X: dataset of WP Edits. Must have the columns "added_lines" and "deleted_lines"
            labels: Iterable of bools associated to each WP Edit. A value of True indicates vandalism.

        Returns:
            self
        """

        # `_validate_data` is defined in the `BaseEstimator` class.
        # self.X_ = self._validate_data(X.replace(np.nan, ''), accept_sparse=True)
        self.X_ = X.replace(np.nan, '')
        self.labels_ = labels

        self.vectorizer_.fit(pd.concat([self.X_['added_lines'], self.X_['deleted_lines']], axis=0))

        return self
    
    def transform(
        self, X
    ) -> pd.DataFrame:
        """
        Compute vandalism scores for new edits based on
        learned word probabilities.

        Parameters:
            X: dataset of WP Edits, shape (n_samples, n_features). Must have the columns "added_lines" and "deleted_lines"
            n_splits: number of splits to use for training Naive Bayes.

        Returns:
            X_transformed: dataset of WP Edits augmented with pred_proba output from Naive Bayes, shape (n_samples, n_features+1). Adds a column called "vandalism_score".
        """
        X_transformed = X.copy().replace(np.nan, '') # In keeping with sklearn API, we don't want to directly modify the input data

        cv = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)

        X_counts_added = pd.DataFrame.sparse.from_spmatrix(self.vectorizer_.transform(X_transformed['added_lines']), columns=self.vectorizer_.vocabulary_)
        X_counts_deleted = pd.DataFrame.sparse.from_spmatrix(self.vectorizer_.transform(X_transformed['deleted_lines']), columns=self.vectorizer_.vocabulary_)   
        X_counts_diff = (X_counts_added - X_counts_deleted).clip(lower=0)

        nb = self.nb_
        for train_idx, target_idx in cv.split(X_transformed, self.labels_):
            fit_data = X_counts_diff.iloc[train_idx]
            scored_data = X_counts_diff.iloc[target_idx]
            fit_targets = self.labels_.iloc[train_idx]

            nb.fit(fit_data, fit_targets)
            X_transformed.loc[X_transformed.index[target_idx], 'vandalism_score'] = nb.predict_proba(scored_data)[:, nb.classes_]
            # nb.classes_ is a list of the classes seen by nb.fit, in the order it saw them.
            # The only two class labels are True and False, so this indexing selects the column
            # of predict_proba with the probabilities for True, irrespective of whether nb saw
            # True first or False first.
        
        return X_transformed