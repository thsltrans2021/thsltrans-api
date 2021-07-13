from flask import Flask
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.database import Database

MONGO_CLIENT: MongoClient
DB: Database


def init_database(app: Flask):
    connection_str = f"mongodb://{app.config['DB_USER']}:{app.config['DB_PASSWORD']}" \
                     f"@cluster0-shard-00-00.hhhfk.mongodb.net:27017," \
                     f"cluster0-shard-00-01.hhhfk.mongodb.net:27017," \
                     f"cluster0-shard-00-02.hhhfk.mongodb.net:27017/{app.config['DB_NAME']}" \
                     f"?ssl=true&replicaSet=atlas-mc44xa-shard-0&authSource=admin&retryWrites=true&w=majority"

    mongodb_client = MongoClient(connection_str)

    try:
        # The ismaster command is cheap and does not require auth.
        mongodb_client.admin.command('ismaster')
    except ConnectionFailure:
        print("Server not available")

    global MONGO_CLIENT, DB
    MONGO_CLIENT = mongodb_client
    DB = mongodb_client['thsltrans']
