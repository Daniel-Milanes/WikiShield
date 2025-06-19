#!/usr/bin/env python
""" Provides helper function _word_counter that counts words in added_lines and deleted_lines, and _comment_emptyTo be used in a FunctionGenerator """
import pandas as pd
from sys import argv

def _wc(str) -> int:
    """ Returns number of words if string, 0 if NaN """
    if pd.isna(str):
        return 0
    else:
        return len(str.split())

def _word_counter(data : pd.DataFrame) -> pd.DataFrame:
    """ Helper function for FunctionTransformer. Counts words in added and deleted lines"""
    data['added_word_count'] = data['added_lines'].map(_wc)
    data['deleted_word_count'] = data['deleted_lines'].map(_wc)
    return data

def _comment_empty(data : pd.DataFrame) -> pd.DataFrame:
    """ Helper function for FunctionTransformer. Checks if comment is empty"""
    data['comment_empty'] = data['comment'].isna()
    return data


if __name__ == '__main__':
    assert(_wc(float('nan')) == 0) # Sanity checks
    assert(_wc('hello world') == 2)
    args = argv[1:] # In case I need to quickly check its output on the terminal
    for count in map(_wc, args):
        print(count)