from flask import Flask, jsonify

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


@app.route("/text", methods=["GET"])
def text():
    list = load_short()
    rv=[]
    for item in list:
        if item['name'] is None:
            continue
        rv.append(item['name'] + " is " + item['hubspot_id'])
    return "\n".join(rv)


app.run(debug=True)

