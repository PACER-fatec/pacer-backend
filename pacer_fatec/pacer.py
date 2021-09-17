from flask import Flask, request
from flask_cors import cross_origin
from datetime import datetime
import json

app = Flask(__name__)

@app.route("/")
def hello():
    return "Pepino Denovo!"

@app.route("/pacer", methods = ['POST'])
@cross_origin()
def test():
    requestList = request.form
    fullJson = json.dumps(request.form)
    return f"inputs: {fullJson}"