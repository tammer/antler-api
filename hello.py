from flask import Flask, jsonify, request

from generate_ids import generate_ids
from contact_loader import load_full, load_short
from supa_from_id import supa_from_id as supa_from_id_func, summarize_transcript
from meetgeek import get_all_meetings

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


@app.route("/summary_from_id", methods=["GET"])
def summary_from_id():
    meeting_id = request.args.get("meeting_id")
    if not meeting_id:
        return jsonify({"error": "missing meeting_id"}), 400
    try:
        result = summarize_transcript(meeting_id)
    except Exception as e:
        return jsonify({"error": f"Failed to generate summary: {str(e)}"}), 500
    return jsonify(result)


@app.route("/get_all_meetings", methods=["GET"])
def get_all_meetings_route():
    try:
        meetings = get_all_meetings()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch meetings: {str(e)}"}), 500

    formatted = []
    for m in meetings:
        meeting_id = m.get("meeting_id") or m.get("id")
        if not meeting_id:
            continue
        ts = m.get("timestamp_start_utc") or ""
        dt = ts.split("T")[0] if ts else ""
        title = m.get("title") or ""
        name = f"{title} {dt} {meeting_id}".strip()
        formatted.append({"meeting_id": meeting_id, "name": name})

    return jsonify(formatted)

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

