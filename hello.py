from flask import Flask, jsonify, request

from generate_ids import generate_ids
from contact_loader import load_full, load_short

app = Flask(__name__)


@app.after_request
def cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    return response


@app.route("/full", methods=["GET"])
def full():
    return jsonify(load_full())


@app.route("/short", methods=["GET"])
def short():
    return jsonify(load_short())


@app.route("/ids", methods=["GET"])
def ids():
    # id is a parameter
    meeting_id = request.args.get("meeting_id")
    return generate_ids(meeting_id)


app.run(debug=True)

