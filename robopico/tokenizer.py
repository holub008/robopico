"""
RobotReviewer tokenizer
"""
import spacy

# note: robotreviewer used "en" which is equivalent to the small (sm) model. may be wise to stay with this, since
# training presumably occurred with this model
nlp = spacy.load('en_core_web_sm')
