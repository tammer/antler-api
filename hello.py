from flask import Flask, jsonify, request

from generate_ids import generate_ids
from contact_loader import load_full, load_short
from supa_from_id import supa_from_id as supa_from_id_func

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


@app.route("/supa_from_id", methods=["GET"])
def supa_from_id():
    meeting_id = request.args.get("meeting_id")
    return supa_from_id_func(meeting_id)

@app.route("/supa_from_meetgeek", methods=["POST"])
def supa_from_meetgeek():
    body = request.get_json(silent=True) or {}
    meeting_id = body.get("meeting_id")
    if not meeting_id:
        return jsonify({"error": "missing meeting_id"}), 400
    try:
        result = supa_from_id_func(meeting_id)
    except Exception as e:
        return jsonify({"error": f"Failed to process meeting: {str(e)}"}), 500
    if result is None:
        return jsonify({"message": "Meeting too short, skipped"}), 200
    return jsonify(result)


app.run(debug=True)

