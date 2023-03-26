import mdb_connection as mdb
import json

def sprints():
    if mdb.db.fatec.distinct('sprint') == []:
        return ["1"]
    else:
        return mdb.db.fatec.distinct('sprint')

def alunosGrafico():
    alunos = []
    cursor = mdb.db.alunos.find({}, {'nome': 1})
    for document in cursor:
        alunos.append(document)
    return str(alunos)

def mediaAlunos(avaliacoes):
    if avaliacoes:
        proatividade = sum([int(a['proatividade']) for a in avaliacoes]) / len(avaliacoes)
        autonomia = sum([int(a['autonomia']) for a in avaliacoes]) / len(avaliacoes)
        colaboracao = sum([int(a['colaboracao']) for a in avaliacoes]) / len(avaliacoes)
        entrega_resultados = sum([int(a['entrega-resultados']) for a in avaliacoes]) / len(avaliacoes)

        return [round(proatividade, 2), round(autonomia, 2), round(colaboracao, 2), round(entrega_resultados, 2)]

    return []


def grupoAluno(requestDict):
    grupoAlunoSelecionado = requestDict['grupo']
    alunosGrupoSelecionado = list(mdb.db.grupos.find({'nome': grupoAlunoSelecionado}, {'alunos': 1, '_id': 0}))[0]
    alunosGrupoSelecionado = [aluno for aluno in alunosGrupoSelecionado['alunos'] if '@' in aluno]

    nomes = []
    for email in alunosGrupoSelecionado:
        user = mdb.db.users.find_one({'email': email})
        nomes.append(user['nome'])

    alunosGrupoSelecionado = nomes

    print(alunosGrupoSelecionado)

    mediaGrupo = []
    proatividadeList = []
    autonomiaList = []
    colaboracaoList = []
    entregaResultadoList = []

    for aluno in alunosGrupoSelecionado:
        avaliacoes = mdb.db.fatec.find({"avaliado": aluno['nome'], "sprint": requestDict['sprint']}, {"_id": 0,"avaliado": 1, "proatividade": 1, "autonomia": 1, "colaboracao": 1, "entrega-resultados": 1})
        for avaliacao in avaliacoes:
            proatividadeList.append(int(avaliacao['proatividade']))
            autonomiaList.append(int(avaliacao['autonomia']))
            colaboracaoList.append(int(avaliacao['colaboracao']))
            entregaResultadoList.append(int(avaliacao['entrega-resultados']))

    return [round(sum(proatividadeList)/len(proatividadeList), 2), round(sum(autonomiaList)/len(autonomiaList), 2),
    round(sum(colaboracaoList)/len(colaboracaoList), 2), round(sum(entregaResultadoList)/len(entregaResultadoList), 2)]