from pickle import FALSE
from unittest import skip
from xml.dom.minidom import Document
from flask import Flask, request, jsonify, send_file, request
from datetime import datetime
from flask_cors import CORS
from flask import jsonify
import os
import json
import csv
import math

import mdb_connection as mdb
import importDb as imdb
from bson import  ObjectId
from os import environ
from groupValidations import existe_alunos, existe_grupo
from validations import existe_cadastro
from validations import aluno_pode_avaliar
from service import sprints, grupoAluno, mediaAlunos
from bson import json_util
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES_DIR = BASE_DIR + '\\pacer_fatec\\resources'

@app.route("/")
def hello():
    return "PACER SERVER WORKING! (v1.10)"

@app.route("/pacer", methods=['POST'])
def enviarAvaliacao():
    request_data = request.form.to_dict()
    nome_grupo = request_data['nomeGrupo']
    sprint = request_data['sprint']
    if request_data['pontos_disponiveis'] == 'null':
        return "Erro: aguarde a avaliação da sprint pelo professor."
    else:
        pontos_disponiveis = int(request_data['pontos_disponiveis'])

    grupoSelecionado = mdb.db.grupos.find_one({'nome': request_data['grupoSelecionado']})
    alunosGrupoSelecionado = grupoSelecionado['alunos']

    # filtrar apenas os alunos válidos (com e-mails válidos)
    alunos_validos = [aluno for aluno in alunosGrupoSelecionado if aluno and "@" in aluno and "." in aluno.split("@")[-1]]
    num_alunos_validos = len(alunos_validos)
    print("numero de alunos: " + str(num_alunos_validos))

    # verificar se há alunos válidos antes de calcular a média
    if num_alunos_validos > 0:

        # buscar as avaliações dos alunos válidos
        avaliacoes_aluno = mdb.db.avaliacoes.find_one({'nomeGrupo': nome_grupo, 'sprint': sprint})
        pontos_totais = int(avaliacoes_aluno["pontos"])

        # calcular a média de pontos por aluno válido
        data = json.loads(str(json.dumps(request.form)))
        keys = list(data.keys())
        print (keys)
        valores = [data[keys[i]] for i in range(3,8)]
        pontos_gastos_pelo_aluno = sum(map(int, valores))
        print(pontos_gastos_pelo_aluno)

        # verificar se a quantidade de pontos excede o máximo permitido
        if pontos_disponiveis < pontos_gastos_pelo_aluno:
            return 'Erro: quantidade máxima de pontos excedida para este aluno.'
    else:
        return 'Erro: nenhum aluno válido encontrado no grupo.'


    request_data['data-avaliacao'] = str(datetime.now().strftime('%d/%m/%y %H:%M'))

    avaliador = mdb.db.users.find_one({'email': request_data['avaliador']})
    avaliado = mdb.db.users.find_one({'email': request_data['avaliado']})
    request_data['avaliador'] = avaliador['nome']
    request_data['avaliado'] = avaliado['nome']

    request_data.pop('grupoSelecionado')

    fullJson = json.loads(json.dumps(request_data))
    mensagem = ''
    if aluno_pode_avaliar(fullJson):
        mdb.db.fatec.insert_one(fullJson)
        mensagem = "Avaliação enviada! Obrigado."
    else:
        mensagem = "Este avaliador não pode avaliar a mesma pessoa mais de uma vez."
    return mensagem

@app.route('/pacer/cadastro', methods = ['POST'])
def cadastro ():
    requestList = request.form
    requestList = requestList.to_dict()

    fullJson = json.loads(json.dumps(requestList))

    erroAluno = existe_cadastro(fullJson['email'])

    fullJson['ROLE'] = 'ROLE_ALUNO'

    if erroAluno != False:
        return "Email já cadastrado!"
    else:
        mdb.db.users.insert_one(fullJson)
        return "Cadastro concluído!"

@app.route("/pacer/aluno")
def listarAluno ():
    alunos = []
    cursor = mdb.db.alunos.find({})
    for document in cursor:
          alunos.append(document)

    return str(alunos)

@app.route('/pacer/alunos')
def listarAlunos ():
    alunos = mdb.db.users.find({"ROLE": "ROLE_ALUNO" })
    response = []
    for aluno in alunos:
        aluno['_id'] = str(aluno['_id'])
        response.append(aluno)
    return json.dumps(response)

@app.route('/pacer/alunos/<int:grupo>')
def clearAssessedSelect (grupo):
    filt = {'grupo': grupo}
    f = mdb.db.alunos.find_one(filt)
    return json.dumps(f)

@app.route('/pacer/uploadAlunos', methods = ['POST'])
def uploadAlunos ():
    f = request.files.get('alunos')
    f.save(os.path.join(RES_DIR, f.filename))
    imdb.importAlunos()
    return ('', 204)

@app.route('/pacer/csvfile')
def relatorio():
    relatorio = mdb.db.fatec.find()
    response = []

    for doc in relatorio:
        del doc['_id']
        response.append(doc)

    filename = f"{RES_DIR}/relatorio.txt"

    with open(filename, "w", encoding='utf-8') as file:
        for doc in response:
            for key, value in doc.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")

    return send_file(filename)

@app.route('/pacer/csvfileFiltered')
def relatorioFiltrado():
    nome_grupo = request.args.get('nomeGrupo')
    sprint = request.args.get('sprint')

    query = {}
    if nome_grupo:
        query['nomeGrupo'] = nome_grupo
    if sprint:
        query['sprint'] = sprint

    relatorio = mdb.db.fatec.find(query)
    response = []

    for doc in relatorio:
        del doc['_id']
        response.append(doc)

    filename = f"{RES_DIR}/relatorio.txt"

    with open(filename, "w", encoding='utf-8') as file:
        for doc in response:
            for key, value in doc.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")

    return send_file(filename)

@app.route('/pacer/login', methods = ['POST'])
def login ():
    requestDict = request.form.to_dict()

    acessoDB = mdb.db.users.find_one({'email': requestDict['email']})
    
    if requestDict['email'] == acessoDB['email'] and requestDict['senha'] == acessoDB['senha']:
        response = {
            'nome': acessoDB['nome'],
            'email': acessoDB['email'],
            'ra': acessoDB['ra'],
            'ROLE': acessoDB['ROLE'],
            'sessionStart': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        return response
    else:
        raise ValueError('Email ou senha incorretos!')

@app.route('/pacer/login/novasenha', methods = ['POST'])
def novasenha ():
    requestDict = request.form.to_dict()

    myquery = { "nome": "professor" }
    newvalues = { "$set": { "senha": requestDict['senha'] , "primeiro-acesso": False} }

    mdb.db.professor.update_one(myquery, newvalues)
    
    return {}

@app.route('/pacer/sprints')
def numeroDeSprints():
    grupo = request.args.get('grupo')
    sprints_list = sprints(grupo)  # Obter a lista de sprints
    return json.dumps(sprints_list)  # Retornar a lista como JSON


@app.route('/pacer/media', methods=['POST'])
def mediaAluno():
    requestDict = request.form.to_dict()
    avaliacoes_aluno = list(mdb.db.fatec.find({"avaliado": requestDict['nome'], "sprint": requestDict['sprint'], "nomeGrupo": requestDict['grupo']}))

    if not avaliacoes_aluno:
        return 'Nenhuma avaliação encontrada para esses parâmetros.'

    # Obtém as habilidades e suas posições no dicionário de avaliações
    habilidades = list(avaliacoes_aluno[0].keys())[4:9]  # Supondo que as habilidades começam na quinta posição

    # Cria o dicionário de média do aluno dinamicamente usando as habilidades
    media_aluno = {habilidade: 0 for habilidade in habilidades}

    for avaliacao in avaliacoes_aluno:
        for habilidade in habilidades:
            media_aluno[habilidade] += int(avaliacao[habilidade])

    num_avaliacoes_aluno = len(avaliacoes_aluno)
    for habilidade in habilidades:
        media_aluno[habilidade] /= num_avaliacoes_aluno
        media_aluno[habilidade] = round(media_aluno[habilidade], 2)

    # Obtém a média do grupo para a mesma sprint e habilidades
    avaliacoes_grupo = list(mdb.db.fatec.find({"sprint": requestDict['sprint'], "nomeGrupo": requestDict['grupo']}))
    num_avaliacoes_grupo = len(avaliacoes_grupo)

    # Cria o dicionário de média do grupo dinamicamente usando as habilidades
    media_grupo = {habilidade: 0 for habilidade in habilidades}

    for avaliacao in avaliacoes_grupo:
        for habilidade in habilidades:
            media_grupo[habilidade] += int(avaliacao[habilidade])

    for habilidade in habilidades:
        media_grupo[habilidade] /= num_avaliacoes_grupo
        media_grupo[habilidade] = round(media_grupo[habilidade], 2)

    # Cria o dicionário com as informações de média do aluno e média do grupo
    resultado = {
        'media_aluno': media_aluno,
        'media_grupo': media_grupo,
        'num_avaliacoes_aluno': num_avaliacoes_aluno,
        'num_avaliacoes_grupo': num_avaliacoes_grupo
    }

    return jsonify(resultado)

@app.route('/pacer/cadastrarGrupo', methods = ['POST'])
def cadastrarGrupo():
    requestList = request.data

    fullJson = json.loads(requestList)

    erroAluno = existe_alunos(fullJson['alunos'])
    erroGrupo = existe_grupo(fullJson['nome'])

    if not erroAluno and not erroGrupo:
        mdb.db.grupos.insert_one(fullJson)
        return "Grupo criado com sucesso!"
    else:
        return str(erroAluno) + '<br>' + str(erroGrupo)

@app.route('/pacer/gruposAlunoLogado')
def grupoAlunoLogado():

    erroAluno = existe_cadastro(request.args.get('email'))
    grupos = []

    if erroAluno == True:
        gruposDB = mdb.db.grupos.find({'alunos': request.args.get('email')})
        for document in gruposDB:
            grupos.append(document['nome'])
            
        print(json.dumps(grupos))
        return json.dumps(grupos)
    else:
        print('null')
        return 'null'

@app.route('/pacer/grupoSelecionado')
def grupoSelecionado():
    # Obtenha o nome do grupo da solicitação
    nomeGrupo = request.args.get('grupo')

    # Encontre o grupo com base no nome
    grupo = mdb.db.grupos.find_one({'nome': nomeGrupo}, {'_id': False})

    # Verifique se o grupo existe
    if not grupo:
        return jsonify({'message': 'Grupo não encontrado'})

    # Obtenha os alunos, as habilidades e o nome do grupo
    alunos = grupo['alunos']
    habilidades = grupo['skills']
    nomeGrupo = grupo['nome']

    print(habilidades)

    # Inicialize a lista de resultados
    resultado = []

    # Para cada aluno, encontre as informações do usuário e adicione à lista de resultados
    for aluno in alunos:
        if aluno:
            print(aluno)
            usuario = mdb.db.users.find_one({'email': aluno}, {'_id': False, 'nome': True, 'email': True})
            
            resultado.append(usuario)

    print(resultado)

    # Retorne o nome do grupo, as habilidades e a lista de resultados
    return jsonify({'nome': nomeGrupo, 'skills': habilidades, 'alunos': resultado})



@app.route('/pacer/skills')
def listSkills():
    skills = []

    skillsDB = list(mdb.db.skills.find({}, {'_id': False}))

    for skill in skillsDB:
        skills.append(skill)

    return json.dumps(skills)

@app.route('/skills/descricao', methods=['GET'])
def get_skills():
    skills = request.args.getlist('skill')
    # Adicione esta linha para decodificar os parâmetros da URL:
    skills = [unquote(skill) for skill in skills]
    results = []
    for skill in skills:
        query = {f"Skills.{skill}": {"$exists": True}}
        projection = {f"Skills.{skill}": 1, "_id": 0}
        data = mdb.db.skills.find_one(query, projection)
        if data and data['Skills']:
            skill_data = {}
            for item in data['Skills']:
                if skill in item:
                    skill_data[skill] = item[skill]
            results.append(skill_data)
    return {'skills': results}

@app.route('/pacer/grupos')
def listarGrupos():
    grupos = mdb.db.grupos.find()
    response = []
    for grupo in grupos:
        grupo.pop('_id')
        response.append(grupo)
    return json.dumps(response)

@app.route('/pacer/cadastrarAvaliacao', methods=['POST'])
def cadastrar_avaliacao():
    data = request.json
    nome_grupo = data.get('nomeGrupo')
    sprint = data.get('avaliacao').get('sprint')
    nota = data.get('avaliacao').get('nota')
    pontos = data.get('avaliacao').get('pontos')
    nextSprint = int(sprint) + 1

    # Verifica se já existe um registro para o mesmo nome de grupo e sprint
    if mdb.db.avaliacoes.find_one({"nomeGrupo": nome_grupo, "sprint": sprint}):
        return jsonify({"message": "Registro duplicado. Impossível realizar a operação."}), 400

    # Insere a nova avaliação
    try:
        mdb.db.avaliacoes.insert_one({"nomeGrupo": nome_grupo, "sprint": sprint, "nota": nota, "pontos": pontos})
        return jsonify({"message": "Avaliação cadastrada com sucesso."}), 201
    except:
        return jsonify({"message": "Erro interno. Não foi possível realizar a operação."}), 500

@app.route('/pacer/pontos')
def obter_pontos():
    nome_grupo = request.args.get('grupo')
    sprint = request.args.get('sprint')
    documento = mdb.db.avaliacoes.find_one({"nomeGrupo": nome_grupo, "sprint": sprint})
    if documento:
        documento.pop('_id')
        return jsonify(documento)
    else:
        return "Documento não encontrado", 404
    
@app.route('/pacer/numeroDeAlunos', methods=['GET'])
def numero_de_alunos():
    nome_grupo = request.args.get('nome')
    grupo = mdb.db.grupos.find_one({'nome': nome_grupo})
    alunos = list(filter(lambda x: x != '', grupo['alunos']))
    return jsonify({'numero_de_alunos': len(alunos)})