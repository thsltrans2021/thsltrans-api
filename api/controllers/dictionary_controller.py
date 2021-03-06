from flask import Blueprint, request
from flask import jsonify
from api.services import *
from models.models import Eng2Sign
from mongoengine import QuerySet

dictionary = Blueprint('dictionary', __name__)


@dictionary.route('/', methods=['GET'])
def dictionary_index():
    return {
        'message': 'Welcome to thsltrans English-SignGloss dictionary',
        'data': None
    }


@dictionary.route('/words', methods=['POST'])
def add_words():
    """Add and update the specified words"""
    if not validate_dict_request_body(request):
        return jsonify({
            'message': 'Missing some field(s) in request body'
        }), 400

    eng2signs = request_body_to_eng2sign(request)
    results = map(lambda e: e.save(), eng2signs)
    return jsonify({
        'message': 'Success',
        'ids': [str(eng2sign.id) for eng2sign in results]
    }), 201


@dictionary.route('/words/word', methods=['GET'])
def get_word():
    """Search sign glosses of the specified word"""
    word = request.args.get('word')
    if word is None:
        return jsonify({
            'message': 'Missing some parameter(s)'
        }), 400
    results: QuerySet = Eng2Sign.objects(english=word)
    return jsonify({
        'message': 'Success',
        'data': [eng2sign_to_json(r) for r in results]
    }), 200


@dictionary.route('/words/word', methods=['PUT'])
def update_word():
    """Update the existing sign glosses of the specified word"""
    doc_id = request.args.get('id')
    if doc_id is None:
        return jsonify({
            'message': 'Missing some parameter(s)'
        }), 400
    result = request_to_existing_eng2sign(doc_id, request)
    result.save()
    return jsonify({
        'message': 'Success',
        'data': eng2sign_to_json(result)
    }), 200


@dictionary.route('/words', methods=['PUT'])
def add_gloss_to_word():
    if not is_request_body_valid(request):
        return jsonify({
            'message': 'Missing some field(s) in request body'
        }), 400

    result = append_gloss_to_word(request)
    result.save()
    return jsonify({
        'message': 'Success',
        'data': eng2sign_to_json(result)
    }), 200
