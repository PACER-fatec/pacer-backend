from flask import Flask, request, jsonify, send_file, request
from flask_cors import cross_origin
from flask_pymongo import pymongo
from datetime import datetime, timedelta
import os
import json
import csv

import mdb_connection as mdb
import importDb as imdb
from bson import json_util, ObjectId
from validations import aluno_pode_avaliar
from service import alunosGrafico, sprints, grupoAluno, mediaAlunos

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = BASE_DIR + '\\pacer_fatec\\resources'

@app.route("/")
def hello():
    return "Pepino Denovo!"

@app.route("/pacer", methods = ['POST'])
@cross_origin()
def enviarAvaliacao ():
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
def listarAluno ():
    alunos = []
    cursor = mdb.db.alunos.find({})
    for document in cursor:
          alunos.append(document)

    return str(alunos)

@app.route('/pacer/alunos')
@cross_origin()
def listarAlunos ():
    alunos = mdb.db.alunos.find()
    response = []
    for aluno in alunos:
        aluno['_id'] = str(aluno['_id'])
        response.append(aluno)
    return json.dumps(response)

@app.route('/pacer/alunos/<int:grupo>')
@cross_origin()
def clearAssessedSelect (grupo):
    filt = {'grupo': grupo}
    f = mdb.db.alunos.find_one(filt)
    return json.dumps(f)

@app.route('/pacer/uploadAlunos', methods = ['POST'])
@cross_origin()
def uploadAlunos ():
    f = request.files.get('alunos')
    f.save(os.path.join(RES_DIR, f.filename))
    imdb.importAlunos()
    return ('', 204)

@app.route('/pacer/csvfile')
@cross_origin()
def relatorio ():
    relatorio = mdb.db.fatec.find()
    response = []
    for doc in relatorio:
        del doc['_id']
        response.append(doc)

    jsonToCsv = json.dumps(response)
    jsonToCsv = json.loads(jsonToCsv)

    file = open(f"{RES_DIR}//relatorio.csv", "w", newline='', encoding='utf-8')
    f = csv.writer(file)

    f.writerow(["sprint", "avaliador", "avaliado", "proatividade", "autonomia",
                "colaboracao", "entrega-resultados", "data-avaliacao"])

    for linha in jsonToCsv:        
        f.writerow([linha["sprint"],
                    linha["avaliador"],
                    linha["avaliado"],
                    linha["proatividade"],
                    linha["autonomia"],
                    linha["colaboracao"],
                    linha["entrega-resultados"],
                    linha["data-avaliacao"]])

    file.close()

    return send_file(f'{RES_DIR}//relatorio.csv')

@app.route('/pacer/login', methods = ['POST'])
@cross_origin()
def login ():
    requestDict = request.form.to_dict()

    acessoDB = mdb.db.professor.find_one({'nome': requestDict['nome']})
    
    if requestDict['nome'] == acessoDB['nome'] and requestDict['senha'] == acessoDB['senha']:
        response = {
            'primeiroAcesso': acessoDB['primeiro-acesso'],
            'nome': acessoDB['nome'],
            'sessionStart': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        return response
    else:
        raise ValueError('Nome ou senha incorretos!')

@app.route('/pacer/login/novasenha', methods = ['POST'])
@cross_origin()
def novasenha ():
    requestDict = request.form.to_dict()

    myquery = { "nome": "professor" }
    newvalues = { "$set": { "senha": requestDict['senha'] , "primeiro-acesso": False} }

    mdb.db.professor.update_one(myquery, newvalues)
    
    return {}

@app.route('/pacer/sprints')
@cross_origin()
def numeroDeSprints():
    return json.dumps(sprints())

@app.route('/pacer/media', methods = ['POST'])
@cross_origin()
def mediaAluno ():
    requestDict = request.form.to_dict()

    avaliacoes = list(mdb.db.fatec.find({"avaliado": requestDict['nome'], "sprint": requestDict['sprint']}, {"_id": 0,"avaliado": 1, "proatividade": 1, "autonomia": 1, "colaboracao": 1, "entrega-resultados": 1}))

    grupoAlunosList = grupoAluno(requestDict)
    mediaAlunoList = mediaAlunos(avaliacoes)

    return json.dumps({'aluno': mediaAlunoList, 'grupo': grupoAlunosList})
