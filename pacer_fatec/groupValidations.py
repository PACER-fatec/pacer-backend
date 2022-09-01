import mdb_connection as mdb

def existe_alunos(alunos):

    erro = False

    if not alunos:
        mensagem = "ERRO: Nenhum aluno encontrado"
    for aluno in alunos:
        if not mdb.db.users.find_one({'email': aluno}):
            mensagem = "ERRO: " + aluno + " não encontrado na base de dados!"
            return mensagem

    return ''

def existe_grupo(nomeGrupo):
    if mdb.db.grupos.find_one({'nome': nomeGrupo}):
        return "ERRO: Nome de grupo já utilizado!"
        
    return ''