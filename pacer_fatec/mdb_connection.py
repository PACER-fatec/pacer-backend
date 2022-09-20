from flask import Flask
from flask_pymongo import pymongo

CONNECTION_STRING = "mongodb+srv://wesleyvin:fatec@cluster0.jltaora.mongodb.net/pacer?ssl=true&ssl_cert_reqs=CERT_NONE"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('pacer')
user_collection = pymongo.collection.Collection(db, 'fatec')