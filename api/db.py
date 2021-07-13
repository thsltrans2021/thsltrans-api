from flask import Flask
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.database import Database

MONGO_CLIENT: MongoClient
DB: Database


def init_database(app: Flask):
    connection_str = app.config['MONGO_URI']
    mongodb_client = MongoClient(connection_str)

    try:
        # The ismaster command is cheap and does not require auth.
        mongodb_client.admin.command('ismaster')
    except ConnectionFailure:
        print("Server not available")

    global MONGO_CLIENT, DB
    MONGO_CLIENT = mongodb_client
    DB = mongodb_client[app.config['DB_NAME']]
