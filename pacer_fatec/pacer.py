from flask import Flask, request
from flask_cors import cross_origin

app = Flask(__name__)

@app.route("/pacer")
def hello():
    return "Pepino Denovo!"

@app.route("/pacer/test", methods = ['POST'])
@cross_origin()
def test():
    campo1 = request.form.get("campo1")
    campo2 = request.form.get("campo2")
    return f"O primeiro input foi: {campo1} e o segundo input foi: {campo2}"