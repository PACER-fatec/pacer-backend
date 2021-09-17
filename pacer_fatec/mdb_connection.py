from flask import Flask
from flask_pymongo import pymongo

CONNECTION_STRING = "mongodb+srv://app:fatec@cluster0.bag2v.mongodb.net/pacer?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('pacer')
user_collection = pymongo.collection.Collection(db, 'fatec')