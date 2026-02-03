import json
import os

from flask import Flask, request, jsonify

from deduplicate_contacts import deduplicate_contacts

from hubspot import get_contacts_for_owner

app = Flask(__name__)

def _load_full():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "tammer.json")) as f:
        tammer = json.load(f)
    with open(os.path.join(base, "alexa.json")) as f:
        alexa = json.load(f)
    fresh = get_contacts_for_owner("29286558", "2026-02-01T00:00:00.000Z")
    return deduplicate_contacts(fresh + tammer + alexa)

@app.route("/", methods=["GET"])
def hello():
    return jsonify({"hello": "world!!"})

@app.route("/full", methods=["GET"])
def full():
    return jsonify(_load_full())

app.run(debug=True)

