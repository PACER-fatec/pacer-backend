from flask import Flask, request, jsonify
from flask_cors import cross_origin
from flask_pymongo import pymongo
from datetime import datetime
import json
import mdb_connection as mdb
import importDb as imdb
from bson import json_util, ObjectId
from validations import aluno_pode_avaliar

#Importar alunos do arquivo /resources/alunos.csv
#DESCOMENTE A LINHA 11 SE A TABELA ALUNOS ESTIVER VAZIA. COMENTE PARA NÃO TER ERRO DE DUPLICIDADE.
#imdb.importAlunos()

app = Flask(__name__)

@app.route("/")
def hello():
    return "Pepino Denovo!"

@app.route("/pacer", methods = ['POST'])
@cross_origin()
def enviarAvaliacao():
    requestList = request.form
    requestList = requestList.to_dict()
    requestList['data-avaliacao'] = str(datetime.now().strftime('%d/%m/%y %H:%M'))

    avaliador = mdb.db.alunos.find_one({'_id': ObjectId(requestList['avaliador'])})
    avaliado = mdb.db.alunos.find_one({'_id': ObjectId(requestList['avaliado'])})
    requestList['avaliador'] = avaliador['nome']
    requestList['avaliado'] = avaliado['nome']

    fullJson = json.loads(json.dumps(requestList))
    mensagem = ''
    if aluno_pode_avaliar(fullJson):
        mdb.db.fatec.insert_one(fullJson)
        mensagem = "Avaliação enviada! Obrigado."
    else:
        mensagem = "Este avaliador não pode avaliar a mesma pessoa mais de uma vez."
    return mensagem

@app.route("/pacer/aluno")
@cross_origin()
def listarAluno():
    alunos = []
    cursor = mdb.db.alunos.find({})
    for document in cursor:
          alunos.append(document)

    return str(alunos)

@app.route('/pacer/alunos')
@cross_origin()
def listarAlunos():
    alunos = mdb.db.alunos.find()
    response = []
    for aluno in alunos:
        aluno['_id'] = str(aluno['_id'])
        response.append(aluno)
    return json.dumps(response)

@app.route('/pacer/alunos/<int:grupo>')
@cross_origin()
def clearAssessedSelect(grupo):
    filt = {'grupo': grupo}
    f = mdb.db.alunos.find_one(filt)
    return json.dumps(f)