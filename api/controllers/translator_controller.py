from flask import Blueprint
from flask import jsonify
from api.models import SignGloss, Eng2Sign

translator = Blueprint('translator', __name__)


@translator.route('/', methods=['GET'])
def translator_index():
    return jsonify({
        'message': 'Welcome to thsltrans rule-based system',
        'data': None
    })


@translator.route('/translate', methods=['POST'])
def get_translation():
    return jsonify({
        'message': 'Success',
        'data': []
    }), 200


@translator.route('/create', methods=['GET'])
def test_db():
    gloss = SignGloss(gloss_en='TEST')
    eng2sign = Eng2Sign(
        english='test2',
        context='',
        sign_glosses=gloss
    ).save()
    return jsonify({
        'id': str(eng2sign.id)
    }), 201
