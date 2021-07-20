from flask import Blueprint, request
from flask import jsonify
from pymongo.collection import Collection
from api.services import validate_dict_request_body, request_body_to_eng2sign_schema

dictionary = Blueprint('dictionary', __name__)


@dictionary.route('/', methods=['GET'])
def dictionary_index():
    return {
        'message': 'Welcome to thsltrans English-SignGloss dictionary',
        'data': None
    }


@dictionary.route('/words', methods=['POST'])
def add_words():
    from api.db import DB

    if not validate_dict_request_body(request):
        return jsonify({
            'message': 'Missing some field(s) in request body'
        }), 400

    eng2signs: Collection = DB.eng2signs
    doc = request_body_to_eng2sign_schema(request)
    result = eng2signs.insert_many(doc)
    return jsonify({
        'message': 'Success',
        'data': [str(inserted_id) for inserted_id in result.inserted_ids]
    }), 201


# TODO: use query param
def edit_words():
    pass


# TODO: use query param
def get_word():
    pass
