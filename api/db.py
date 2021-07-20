from flask import Flask
from mongoengine import connect


def init_database(app: Flask):
    connect(host=app.config['MONGO_URI'])
