import json
import os

from flask import Flask, request, jsonify

from deduplicate_contacts import deduplicate_contacts

from hubspot import get_contacts_for_owner
from supa import get_contacts_from_supabase

app = Flask(__name__)


@app.after_request
def cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    return response


def _load_full():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "tammer.json")) as f:
        tammer = json.load(f)
    with open(os.path.join(base, "alexa.json")) as f:
        alexa = json.load(f)
    fresh = get_contacts_for_owner("29286558", "2026-02-01T00:00:00.000Z")
    return deduplicate_contacts(fresh + tammer + alexa)

@app.route("/full", methods=["GET"])
def full():
    return jsonify(_load_full())

def _load_short():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "tammer.json")) as f:
        tammer = json.load(f)
    supa = get_contacts_from_supabase()
    fresh = get_contacts_for_owner("29286558", "2026-02-01T00:00:00.000Z")
    return deduplicate_contacts(fresh + tammer + supa)

@app.route("/short", methods=["GET"])
def short():
    return jsonify(_load_short())

@app.route("/text", methods=["GET"])
def text():
    list = _load_short()
    rv=[]
    for item in list:
        if item['name'] is None:
            continue
        rv.append(item['name'] + " is " + item['hubspot_id'])
    return "\n".join(rv)


app.run(debug=True)

