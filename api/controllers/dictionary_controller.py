from flask import Blueprint

dictionary = Blueprint('dictionary', __name__)


@dictionary.route('/', methods=['GET'])
def dictionary_index():
    return 'Welcome to thsltrans English-SignGloss dictionary'
