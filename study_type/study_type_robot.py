import data
import pickle
import xgboost as xgb
from scipy.sparse import hstack


class StudyTypeRobot:
    def __init__(self):
        self._model = xgb.Booster()
        self._model.load_model(data.get_data("study_type/model.json"))

        with open(data.get_data("study_type/label_encoder.pickle"), 'rb') as fh:
            self._label_encoder = pickle.load(fh)

        with open(data.get_data("study_type/title_vectorizer.pickle"), 'rb') as fh:
            self._title_vectorizer = pickle.load(fh)

        with open(data.get_data("study_type/abstract_vectorizer.pickle"), 'rb') as fh:
            self._abstract_vectorizer = pickle.load(fh)

    def annotate(self, abstract, title):
        predictions = self._annotate([abstract], [title])[0]
        labels = self._label_encoder.inverse_transform(range(len(predictions)))
        return {
            labels[ix]: predictions[ix].item() for ix in range(len(predictions))
        }

    def _annotate(self, abstracts, titles):
        abstract_tf = self._abstract_vectorizer.transform(abstracts)
        title_tf = self._title_vectorizer.transform(titles)

        model_data = xgb.DMatrix(hstack((abstract_tf, title_tf)))

        return self._model.predict(model_data)
