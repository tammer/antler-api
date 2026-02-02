from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello():
    return jsonify({"hello": "world"})

app.run(debug=True)

