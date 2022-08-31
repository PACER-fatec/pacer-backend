from asyncio.windows_events import NULL
from pickle import FALSE, TRUE
from queue import Empty
import mdb_connection as mdb

def existe_alunos(alunos):

    erro = FALSE

    if not alunos:
        mensagem = "ERRO: Nenhum aluno encontrado"
    for aluno in alunos:
        if not mdb.db.users.find_one({'email': aluno}):
            mensagem = "ERRO: " + aluno + " não encontrado na base de dados!"
            return mensagem

    return NULL

def existe_grupo(nomeGrupo):
    if mdb.db.grupos.find_one({'nome': nomeGrupo}):
        return "ERRO: Nome de grupo já utilizado!"
        
    return NULL