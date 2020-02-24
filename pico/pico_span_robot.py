"""
the PICOSpanRobot class takes the title and abstract of a clinical trial as
input, and returns Population, Comparator/Intervention Outcome
information in the same format, which can easily be converted to JSON.

The model was described using the corpus and methods reported in our
ACL 2018 paper "A corpus with multi-level annotations of patients,
interventions and outcomes to support language processing for medical
literature": https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6174533/.
"""
import string
import os

from ml.ner.ner_model import NERModel
from ml.ner.ner_config import Config
import ml.text.tokenizer as tokenizer
import ml.text.minimap as minimap
import ml.text.schwartz_hearst as schwartz_hearst
import data as rpd
from itertools import chain
# from bert_serving.client import BertClient


def cleanup(spans):
    """
    A helper (static) function for prettifying / deduplicating
    the PICO snippets extracted by the model.
    """
    def clean_span(s):
        s_clean = s.strip()
        # remove punctuation
        s_clean = s_clean.strip(string.punctuation)

        # remove 'Background:' when we pick it up
        s_clean = s_clean.replace("Background", "")
        return s_clean

    cleaned_spans = [clean_span(s) for s in spans]
    # remove empty
    cleaned_spans = [s for s in cleaned_spans if s]
    # dedupe
    return list(set(cleaned_spans))


class PICOSpanRobot:
    def __init__(self):
        """
        This bot tags sequences of words from abstracts as describing
        P,I, or O elements.
        """
        config = Config()
        # build model
        self.model = NERModel(config)
        self.model.build()

        self.model.restore_session(os.path.join(rpd.DATA_ROOT, "pico_spans/model.weights/"))
        # self.bert = BertClient()

    def annotate(self, title, abstract):
        ti = tokenizer.nlp(title)
        ab = tokenizer.nlp(abstract)

        return self._annotate({"title": ti, "abstract": ab})

    def _annotate(self, article, get_berts=True, get_meshes=True):
        """
        Annotate abstract of clinical trial report
        """
        label_dict = {"1_p": "population", "1_i": "interventions", "1_o": "outcomes"}

        out = {"population": [],
               "interventions": [],
               "outcomes": []}

        for sent in chain(article['title'].sents, article['abstract'].sents):
            words = [w.text for w in sent]
            preds = self.model.predict(words)

            last_label = "N"
            start_idx = 0

            for i, p in enumerate(preds):

                if p != last_label and last_label != "N":
                    out[label_dict[last_label]].append(sent[start_idx: i].text.strip())
                    start_idx = i

                if p != last_label and last_label == "N":
                    start_idx = i

                last_label = p

            if last_label != "N":
                out[label_dict[last_label]].append(sent[start_idx:].text.strip())

        for e in out:
            out[e] = cleanup(out[e])

        if get_meshes:
            abbrev_dict = schwartz_hearst.extract_abbreviation_definition_pairs(doc_text=article['abstract'].text)
            for k in ['population', 'interventions', 'outcomes']:
                out[f"{k}_mesh"] = minimap.get_unique_terms(out[k], abbrevs=abbrev_dict)

        return out


if __name__ == '__main__':
    pass
