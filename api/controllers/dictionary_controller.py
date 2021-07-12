from flask import Blueprint
from flask import jsonify

dictionary = Blueprint('dictionary', __name__)


@dictionary.route('/', methods=['GET'])
def dictionary_index():
    return {
        'message': 'Welcome to thsltrans English-SignGloss dictionary',
        'data': None
    }
