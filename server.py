from flask import Flask, request, jsonify
import os

from pico.pico_span_robot import PICOSpanRobot
from pico.pico_robot import  PICORobot

app = Flask(__name__)

PICO_TIAB_BOT = PICOSpanRobot()
PICO_TEXT_BOT = PICORobot()


@app.route('/pico', methods=['POST'])
def get_pico():
    body = request.get_json()

    if not body:
        return jsonify({
            "message": "Must supply application/json data type"
        }), 500

    if 'abstract' in body and 'title' in body:
        result = PICO_TIAB_BOT.annotate(body['abstract'], body['title'])
    elif 'full_text' in body:
        result = PICO_TEXT_BOT.annotate(body['full_text'])
    else:
        return jsonify({
            "message": "Must supply {'abstract', title'} or {'full_text'}"
        }), 500

    return jsonify({
        "todo": result
    })


if __name__ == "__main__":
    # this entry point should only be used in dev
    app.run(
        host=os.environ.get("RP_HOST", "localhost"),
        debug=True,
        port=os.environ.get("RP_PORT", 5050),
        threaded=True
    )
