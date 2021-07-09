from api.controllers.translator_controller import translator
from api.controllers.dictionary_controller import dictionary
from flask import Flask


def register_routes(app: Flask):
    """
    A place for registering all blueprint of application's routes
    """
    app.register_blueprint(translator, url_prefix='/api/trans')
    app.register_blueprint(dictionary, url_prefix='/api/dict')
