from flask import Blueprint
from flask import jsonify

translator = Blueprint('translator', __name__)


@translator.route('/', methods=['GET'])
def translator_index():
    return jsonify({
        'message': 'Welcome to thsltrans rule-based system',
        'data': None
    })


@translator.route('/404', methods=['GET'])
def example_404():
    return jsonify({
        'message': 'There is no such a thing here'
    }), 404


@translator.route('/create', methods=['GET'])
def test_db():
    from api.db import DB

    result = DB.tests.insert_one({
        'title': 'test 2.5',
        'body': 'test body'
    })
    print(result.inserted_id)

    return jsonify({
        'message': 'Success',
        'data': str(result.inserted_id)
    }), 201
