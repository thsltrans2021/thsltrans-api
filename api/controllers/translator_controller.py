from flask import Blueprint, abort
from flask import jsonify

translator = Blueprint('translator', __name__)


@translator.route('/', methods=['GET'])
def translator_index():
    # TODO: send json as response
    return jsonify({
        'message': 'Welcome to thsltrans rule-based system',
        'data': None
    })


@translator.route('/404', methods=['GET'])
def example_404():
    return jsonify({
        'message': 'There is no such a thing here'
    }), 404
