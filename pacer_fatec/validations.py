import mdb_connection as mdb

def aluno_pode_avaliar(json):
    avaliador = json['avaliador']
    sprint = json['sprint']
    grupo = json['nomeGrupo']
    avaliacoes = json['avaliacoes']

    for avaliacao in avaliacoes:
        avaliado = avaliacao['avaliado']
        avaliacoes_existentes = mdb.db.fatec.find({'avaliador': avaliador, 'sprint': sprint, 'nomeGrupo': grupo}).count()
        if avaliacoes_existentes > 0:
            return False

    return True

def existe_cadastro(email):
    isEmailUsed = mdb.db.users.find({'email': email}).count()
    if not isEmailUsed:
        return False
    return True