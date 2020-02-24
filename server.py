from flask import Flask, request, jsonify
import os

from pico.pico_span_robot import PICOSpanRobot
from pico.pico_robot import  PICORobot

app = Flask(__name__)

PICO_TIAB_BOT = PICOSpanRobot()
PICO_TEXT_BOT = PICORobot()


def validate_list(x):
    return type(x) is list


@app.route('/pico', methods=['POST'])
def get_pico():
    body = request.get_json()

    if not body:
        return jsonify({
            "message": "Must supply application/json data type"
        }), 400

    results = []

    if 'abstract' in body and 'title' in body:
        if validate_list(body['abstract']) and validate_list(body['title']) \
                and len(body['title']) == len(body['abstract']):
            for title, abstract in zip(body["title"], body["abstract"]):
                results.append(PICO_TIAB_BOT.annotate(abstract, title))
        else:
            return jsonify({
                "message": "'abstract' and 'title' must be lists of equal length"
            }), 400
    elif 'full_text' in body:
        if validate_list(body['full_text']):
            for text in body['full_text']:
                results.append(PICO_TEXT_BOT.annotate(body['full_text']))
        else:
            return jsonify({
                "message": "'full_text' must be a list"
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
