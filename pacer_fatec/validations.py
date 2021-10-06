import mdb_connection as mdb
from bson.objectid import ObjectId

def aluno_pode_avaliar(json):
    avaliador = json['avaliador']
    avaliado = json['avaliado']
    avaliacoes_existentes = mdb.db.fatec.find({ 'avaliador': avaliador, 'avaliado': avaliado }).count()
    if avaliacoes_existentes > 0:
        return False
    return True