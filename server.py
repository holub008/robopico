from flask import Flask, request, jsonify
import os

from pico.pico_span_robot import PICOSpanRobot
from pico.pico_robot import  PICORobot
from study_type.study_type_robot import StudyTypeRobot

app = Flask(__name__)

PICO_TIAB_BOT = PICOSpanRobot()
PICO_TEXT_BOT = PICORobot()
STUDY_TYPE_BOT = StudyTypeRobot()

# this is a guess, based on typical abstract length, of what should run in the span of a typical web request
MAX_REQUEST_SIZE = 500


def validate_length(*argv):
    if len(argv) == 0:
        return False

    all_lists = [type(x) is list for x in argv]

    if not all_lists:
        return False

    if len(argv) == 1:
        return len(argv[0]) <= MAX_REQUEST_SIZE
    else:
        n = len(argv[0])
        all_equal_length = all(len(x) == n for x in argv)
        return all_equal_length and n <= MAX_REQUEST_SIZE


@app.route('/pico', methods=['POST'])
def get_pico():
    body = request.get_json()

    if not body:
        return jsonify({
            "message": "Must supply application/json data type"
        }), 400

    results = []

    if 'abstract' in body and 'title' in body:
        if validate_length(body['title'], body['abstract']):
            for title, abstract in zip(body["title"], body["abstract"]):
                annotation = PICO_TIAB_BOT.annotate(abstract, title)
                # TODO: it may be faster to batch this (internal to StudyTypeRobot)
                annotation['study_type'] = STUDY_TYPE_BOT.annotate(abstract, title)
                results.append(annotation)
        else:
            return jsonify({
                "message": "'abstract' and 'title' must be lists of equal length, less than or equal to %d" % (MAX_REQUEST_SIZE,)
            }), 400
    elif 'full_text' in body:
        if validate_length(body['full_text']):
            for text in body['full_text']:
                results.append(PICO_TEXT_BOT.annotate(text))
        else:
            return jsonify({
                "message": "'full_text' must be a list with length less than or equal to %d" % (MAX_REQUEST_SIZE, )
            }), 400
    else:
        return jsonify({
            "message": "Must supply {'abstract', title'} or {'full_text'}"
        }), 400

    return jsonify(results)


if __name__ == "__main__":
    # this entry point should only be used in dev
    app.run(
        host=os.environ.get("RP_HOST", "localhost"),
        debug=True,
        port=os.environ.get("RP_PORT", 5050),
        threaded=True
    )
