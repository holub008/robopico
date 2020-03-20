import pickle

import numpy as np
import pandas as pd
from scipy.sparse import hstack

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder

import xgboost as xgb

SYSTEMATIC_REVIEWS = {'Systematic Review', 'Meta-Analysis'}
RCTS = {'Clinical Trial, Phase I', 'Clinical Trial, Phase II', 'Clinical Trial, Phase III', 'Clinical Trial, Phase IV',
        'Randomized Controlled Trial', 'Controlled Clinical Trial'}

CLINICAL_PUBLICATION_TYPES = {'Comparative Study', 'Case Reports', 'Randomized Controoled Trial',
                              'Multicenter Study', 'Evaluation Study', 'Clinical Trial', 'Observational Study',
                              'Clinical Trial, Phase I', 'Clinical Trial, Phase II', 'Clinical Trial, Phase III',
                              'Clinical Trial, Phase IV', 'Clinical Study', 'Pragmatic Clinical Trial',
                              'Equivalence Trial'}


def resolve_publication_type(publication_types):
    if 'Case Reports' in publication_types:
        return 'Case Report'
    elif not SYSTEMATIC_REVIEWS.isdisjoint(publication_types):
        return 'Systematic Review'
    elif not RCTS.isdisjoint(publication_types):
        return 'RCT'
    else:
        return 'Other'


# this is very subjective (and I am not an expert) and not fully reliable
# we are aiming for any study that reports patient outcomes, irrelevant of study design
# meta-analyses and systematic reviews, despite not containing original data, are included due to high
# propensity to contain clinical outcomes
def resolve_is_clinical(publication_types):
    return (not CLINICAL_PUBLICATION_TYPES.isdisjoint(publication_types)) or \
           (not SYSTEMATIC_REVIEWS.isdisjoint(publication_types))


def get_labelled_data(abstracts, publications):
    matching_publications = publications.merge(abstracts[['pmid']], how='inner', on='pmid')
    labels_by_study = matching_publications.groupby('pmid')['publication_type'].apply(set).reset_index(name='publication_type')
    labels_by_study['label'] = [resolve_publication_type(pts) for pts in labels_by_study['publication_type']]
    labels_by_study['is_clinical'] = [resolve_is_clinical(pts) for pts in labels_by_study['publication_type']]

    matched_data = labels_by_study.merge(abstracts, how='inner', on='pmid')

    mask = np.random.rand(len(matched_data)) < .9
    train_data = matched_data[mask]
    test_data = matched_data[~mask]

    return train_data[['pmid', 'source', 'title', 'abstract']], train_data['label'], train_data['is_clinical'], \
        test_data[['pmid', 'source', 'title', 'abstract']], test_data['label'], test_data['is_clinical']


def get_data_from_file():
    # ptt = publication type tagged - i.e. NLM put some tag on the publication
    abstracts_ptt = pd.read_csv('train/data_archive/abstracts_all.csv', escapechar='\\',  error_bad_lines=False)

    abstracts = abstracts_ptt.(frac=1).reset_index(drop=True)
    abstracts = abstracts[~pd.isnull(abstracts['abstract']) & (abstracts['abstract'] != '') & ~pd.isnull(abstracts['title'])]

    publication_types_ptt = pd.read_csv('train/data_archive/publications_all.csv')
    publication_types = publication_types_ptt.sample(frac=1).reset_index(drop=True)

    return abstracts, publication_types


abstracts, publication_types = get_data_from_file()

model_data_text_train, labels_text_train, is_clinical_train,\
    model_data_text_test, labels_text_test, is_clinical_test = get_labelled_data(abstracts, publication_types)

abstract_vectorizer = CountVectorizer(stop_words='english', ngram_range=[1, 2],
                             max_features=20000, min_df=.001)
title_vectorizer = CountVectorizer(stop_words='english', ngram_range=[1, 2],
                             max_features=20000, min_df=.001)

abstract_tf_train = abstract_vectorizer.fit_transform(model_data_text_train['abstract'])
title_tf_train = title_vectorizer.fit_transform(model_data_text_train['title'])

model_data_train = hstack((abstract_tf_train, title_tf_train))
label_encoder = LabelEncoder()
labels_train = label_encoder.fit_transform(labels_text_train)

dtrain = xgb.DMatrix(model_data_train, labels_train)
dtrain_clinical = xgb.DMatrix(model_data_train, is_clinical_train)

params = {
    'n_estimators': 25,
    'objective': 'multi:softprob',
    'max_depth': 5,
    'num_class': len(label_encoder.classes_),
    'eval_metric': 'merror'
}

params_clinical = {
    'n_estimators': 100,
    'objective': 'binary:logistic',
    'max_depth': 5,
    'eval_metric': 'auc'
}

fold_results = xgb.cv(
    params=params,
    dtrain=dtrain,
    nfold=5,
    num_boost_round=params_clinical['n_estimators']
)

fold_results_clinical = xgb.cv(
    params=params_clinical,
    dtrain=dtrain_clinical,
    nfold=5,
    num_boost_round=params_clinical['n_estimators']
)

fold_results.mean(axis=0)
fold_results_clinical.mean(axis=0)

model = xgb.train(params, dtrain, num_boost_round=params['n_estimators'])
clinical_model = xgb.train(params_clinical, dtrain_clinical, num_boost_round=params_clinical['n_estimators'])

# now, test on some hold outs
# note, this still likely overstates accuracy in real application because:
# 1. studies that are easiest to human classify (NLM mesh) are most likely to be in the dataset. so "true" out of sample will be harder
# 2. the publication type tag may be less likely to be applied to non-clinical literature, suggesting that we will also underperform on the "other" category
# 3. we effectively undersampled the "other" category to remedy this - which may work, but also biases predictions

abstract_tf_test = abstract_vectorizer.transform(model_data_text_test['abstract'])
title_tf_test = title_vectorizer.transform(model_data_text_test['title'])

model_data_test = hstack((abstract_tf_test, title_tf_test))
labels_test = label_encoder.transform(labels_text_test)

dtest = xgb.DMatrix(model_data_test, labels_test)

preds = model.predict(dtest)
classification = preds.argmax(axis=1)
accuracy_score(labels_test, classification)
roc_auc_score(labels_test, preds, multi_class='ovr')

preds_clinical = clinical_model.predict(dtest)
roc_auc_score(is_clinical_test, preds_clinical)

# scored 95% accuracy / .95 OVR AUC , good enough for now

model.save_model("data/study_type/model.json")
clinical_model.save_model("data/study_type/clinical_model.json")

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

