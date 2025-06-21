import re
from collections import defaultdict
from typing import Iterable, Set


class VandalismScorer:
    """
    A simple Naive Bayes inspired scorer that estimates the probability
    that a given edit is vandalism based on the words added in that edit.
    """

    def __init__(self, smoothing: int = 1) -> None:
        """
        Initialize the scorer with Laplace smoothing parameter.
        """
        self.smoothing = smoothing
        self.vandalism_counts = defaultdict(int)
        self.constructive_counts = defaultdict(int)
        self.word_probs = {}

    def _get_words_added(self, added_line: str, deleted_line: str) -> Set[str]:
        """
        Extracts the set of words added in the edit by removing punctuation,
        converting to lowercase, and subtracting deleted words.

        Parameters:
            added_line (str): Text of the added lines.
            deleted_line (str): Text of the deleted lines.

        Returns:
            set: Words present in added_line but not in deleted_line.
        """
        added = set(re.sub(r"[^\w\s]", " ", str(added_line)).lower().split())
        deleted = set(re.sub(r"[^\w\s]", " ", str(deleted_line)).lower().split())
        return added - deleted

    def fit(
        self,
        added_lines: Iterable[str],
        deleted_lines: Iterable[str],
        labels: Iterable[bool],
    ) -> None:
        """
        Train the scorer by counting word occurrences in
        vandalism and constructive edits.

        Parameters:
            added_lines (iterable): Iterable of added line texts.
            deleted_lines (iterable): Iterable of deleted line texts.
            labels (iterable): Iterable of binary labels (True if vandalism).
        """
        for added, deleted, label in zip(added_lines, deleted_lines, labels):
            words = self._get_words_added(added, deleted)
            for word in words:
                if label:
                    self.vandalism_counts[word] += 1
                else:
                    self.constructive_counts[word] += 1

        all_words = set(self.vandalism_counts) | set(self.constructive_counts)
        self.word_probs = {
            word: (self.vandalism_counts[word] + self.smoothing)
            / (
                self.vandalism_counts[word]
                + self.constructive_counts[word]
                + 2 * self.smoothing
            )
            for word in all_words
        }

    def score(
        self, added_lines: Iterable[str], deleted_lines: Iterable[str]
    ) -> list[float]:
        """
        Compute vandalism scores for new edits based on
        learned word probabilities.

        Parameters:
            added_lines (iterable): Iterable of added line texts.
            deleted_lines (iterable): Iterable of deleted line texts.

        Returns:
            list of float: Vandalism probability scores between 0 and 1.
        """
        scores = []
        for added, deleted in zip(added_lines, deleted_lines):
            words = self._get_words_added(added, deleted)
            probs = [self.word_probs.get(word, 0.5) for word in words]

            prod_p = 1
            prod_1_minus_p = 1
            for p in probs:
                prod_p *= p
                prod_1_minus_p *= 1 - p

            score = (
                prod_p / (prod_p + prod_1_minus_p)
                if (prod_p + prod_1_minus_p) != 0
                else 1
            )
            scores.append(score)
        return scores
