import json
import pymongo
import mdb_connection as mdb
import csv
myclient = pymongo.MongoClient()

def importAlunos():
    with open('pacer_fatec/resources/alunos.csv', 'r') as read_csv:
        csv_reader = csv.DictReader(read_csv)
        listaAlunos = list(csv_reader)
        mdb.db.alunos.insert_many(listaAlunos)
