from flask import Flask, request
from flask_cors import cross_origin
from flask_pymongo import pymongo
from datetime import datetime
import json
import mdb_connection as mdb
import importDb as imdb

#Importar alunos do arquivo /resources/alunos.csv
imdb.importAlunos()

app = Flask(__name__)

@app.route("/")
def hello():
    return "Pepino Denovo!"

@app.route("/pacer", methods = ['POST'])
@cross_origin()
def test():
    requestList = request.form
    requestList = requestList.to_dict()
    requestList['data-avaliacao'] = str(datetime.now().strftime('%d/%m/%y %H:%M'))
    fullJson = json.loads(json.dumps(requestList))
    mdb.db.fatec.insert_one(fullJson)
    
    return "Avaliação enviada! Obrigado."