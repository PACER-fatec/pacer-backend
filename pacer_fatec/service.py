import mdb_connection as mdb

def sprints():
    return mdb.db.fatec.distinct('sprint')

def alunosGrafico():
    alunos = []
    cursor = mdb.db.alunos.find({}, {'nome': 1})
    for document in cursor:
        alunos.append(document)
    return str(alunos)