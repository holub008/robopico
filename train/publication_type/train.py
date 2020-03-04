import pickle

import pandas as pd
from scipy.sparse import hstack

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder

import xgboost as xgb

SYSTEMATIC_REVIEWS = {'Systematic Review', 'Meta-Analysis'}
RCTS = {'Clinical Trial, Phase I', 'Clinical Trial, Phase II', 'Clinical Trial, Phase III', 'Clinical Trial, Phase IV',
        'Randomized Controlled Trial', 'Controlled Clinical Trial'}


def resolve_publication_type(publication_types):
    if 'Case Reports' in publication_types:
        return 'Case Report'
    elif not SYSTEMATIC_REVIEWS.isdisjoint(publication_types):
        return 'Systematic Review'
    elif not RCTS.isdisjoint(publication_types):
        return 'RCT'
    else:
        return 'Other'


def get_labelled_data(abstracts, publications):
    matching_publications = publications.merge(abstracts[['pmid']], how='inner', on='pmid')
    labels_by_study = matching_publications.groupby('pmid')['publication_type'].apply(set).reset_index(name='publication_type')
    labels_by_study['label'] = [resolve_publication_type(pts) for pts in labels_by_study['publication_type']]

    matched_data = labels_by_study.merge(abstracts, how='inner', on='pmid')

    return matched_data[['pmid', 'title', 'abstract']], matched_data['label']


abstracts = pd.read_csv('train/abstracts_all.csv', escapechar='\\',  error_bad_lines=False,
                        nrows=100000)  # just for deving
abstracts = abstracts[~pd.isnull(abstracts['abstract']) & (abstracts['abstract'] != '') & ~pd.isnull(abstracts['title'])]
publication_types = pd.read_csv('train/publications_all.csv', escapechar='\\', error_bad_lines=False)

model_data_text, labels_text = get_labelled_data(abstracts, publication_types)

abstract_vectorizer = CountVectorizer(stop_words='english', ngram_range=[1, 2],
                             max_features=20000, min_df=.001)
title_vectorizer = CountVectorizer(stop_words='english', ngram_range=[1, 2],
                             max_features=20000, min_df=.001)

abstract_tf = abstract_vectorizer.fit_transform(model_data_text['abstract'])
title_tf = title_vectorizer.fit_transform(model_data_text['title'])

model_data = hstack((abstract_tf, title_tf))
label_encoder = LabelEncoder()
labels = label_encoder.fit_transform(labels_text)

dtrain = xgb.DMatrix(model_data, labels)

params = {
    'n_estimators': 100,
    'objective': 'multi:softprob',
    'max_depth': 3,
    'num_class': len(label_encoder.classes_),
    'eval_metric': 'merror'
}

fold_results = xgb.cv(
    params=params,
    dtrain=dtrain,
    nfold=5,
)

fold_results.mean(axis=0)

model = xgb.train(params, dtrain, num_boost_round=params['n_estimators'])

# now, test on some hold outs
# note, this still likely overstates accuracy in real application because:
# 1. studies that are easiest to human classify (NLM mesh) are most likely to be in the dataset. so "true" out of sample will be harder
# 2. the publication type tag may be less likely to be applied to non-clinical literature, suggesting that we will also underperform on the "other" category

abstracts_test = pd.read_csv('train/abstracts_all.csv', escapechar='\\',  error_bad_lines=False,
                             nrows=200000)  # just for deving
abstracts_test = abstracts_test.iloc[100000:200000]
abstracts_test = abstracts_test[~pd.isnull(abstracts_test['abstract']) & (abstracts_test['abstract'] != '') & ~pd.isnull(abstracts_test['title'])]
publication_types_test = pd.read_csv('train/publications_all.csv', escapechar='\\', error_bad_lines=False)

model_data_text_test, labels_text_test = get_labelled_data(abstracts_test, publication_types_test)

abstract_tf_test = abstract_vectorizer.transform(model_data_text_test['abstract'])
title_tf_test = title_vectorizer.transform(model_data_text_test['title'])

model_data_test = hstack((abstract_tf_test, title_tf_test))
labels_test = label_encoder.transform(labels_text_test)

dtest = xgb.DMatrix(model_data_test, labels_test)

preds = model.predict(dtest)
classification = preds.argmax(axis=1)
accuracy_score(labels_test, classification)
roc_auc_score(labels_test, preds, multi_class='ovr')

# scored 95% accuracy / .95 OVR AUC , good enough for now

model.save_model("data/study_type/model.json")

# note: this attribute gets enormous, but is not used to transform
# https://github.com/scikit-learn/scikit-learn/issues/4032
delattr(title_vectorizer, 'stop_words_')
with open('data/study_type/title_vectorizer.pickle', 'wb') as out:
    pickle.dump(title_vectorizer, out)

delattr(abstract_vectorizer, 'stop_words_')
with open('data/study_type/abstract_vectorizer.pickle', 'wb') as out:
    pickle.dump(abstract_vectorizer, out)

with open('data/study_type/label_encoder.pickle', 'wb') as out:
    pickle.dump(label_encoder, out)
