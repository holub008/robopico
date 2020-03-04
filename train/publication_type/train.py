import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

abstracts = pd.read_csv('train/abstracts_all.csv', escapechar='\\',  error_bad_lines=False,
                        nrows=500000)  # just for deving
publication_types = pd.read_csv('train/publications_all.csv', escapechar='\\', error_bad_lines=False)

abstracts = abstracts[~pd.isnull(abstracts['abstract']) & (abstracts['abstract'] != '')]

abstract_vectorizer = CountVectorizer(stop_words='english', ngram_range=[1, 2],
                             max_features=50000, min_df=.001)
title_vectorizer = CountVectorizer(stop_words='english', ngram_range=[1, 2],
                             max_features=50000, min_df=.001)

abstract_tf = abstract_vectorizer.fit_transform(abstracts['abstract'])
title_tf = abstract_vectorizer.fit_transform(abstracts['title'])