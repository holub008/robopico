import data
import pickle
import xgboost as xgb
from scipy.sparse import hstack


class StudyTypeRobot:
    def __init__(self):
        self._type_model = xgb.Booster()
        self._type_model.load_model(data.get_data("study_type/model.json"))

        self._clinical_model = xgb.Booster()
        self._clinical_model.load_model(data.get_data("study_type/clinical_model.json"))

        with open(data.get_data("study_type/label_encoder.pickle"), 'rb') as fh:
            self._label_encoder = pickle.load(fh)

        with open(data.get_data("study_type/title_vectorizer.pickle"), 'rb') as fh:
            self._title_vectorizer = pickle.load(fh)

        with open(data.get_data("study_type/abstract_vectorizer.pickle"), 'rb') as fh:
            self._abstract_vectorizer = pickle.load(fh)

    def annotate(self, abstract, title):
        type_predictions, clinical_prediction = self._annotate([abstract], [title])
        labels = self._label_encoder.inverse_transform(range(len(type_predictions)))
        return {labels[ix]: type_predictions[ix].item() for ix in range(len(type_predictions))}, clinical_prediction.item()

    def _annotate(self, abstracts, titles):
        abstract_tf = self._abstract_vectorizer.transform(abstracts)
        title_tf = self._title_vectorizer.transform(titles)

        model_data = xgb.DMatrix(hstack((abstract_tf, title_tf)))

        return self._type_model.predict(model_data)[0], self._clinical_model.predict(model_data)[0]
