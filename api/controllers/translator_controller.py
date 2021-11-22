from flask import Blueprint, request
from flask import jsonify
from models.models import SignGloss, Eng2Sign
from api.services import validate_trans_request_body, request_body_to_text_data
from rb_system.translation import translate_english_to_sign_gloss

translator = Blueprint('translator', __name__)


@translator.route('/', methods=['GET'])
def translator_index():
    return jsonify({
        'message': 'Welcome to thsltrans rule-based system',
        'data': None
    })


@translator.route('/translate', methods=['POST'])
def generate_translation():
    if not validate_trans_request_body(request):
        return jsonify({
            'message': 'Missing some field(s) in request body'
        }), 400

    text_data = request_body_to_text_data(request)
    translate_english_to_sign_gloss(text_data)

    return jsonify({
        'message': 'Success',
        'data': text_data.prepare_response_data()
    }), 200


@translator.route('/create', methods=['POST'])
def test_db():
    gloss = SignGloss(gloss='TEST', lang='TH')
    eng2sign = Eng2Sign(
        english='test2',
        sign_glosses=gloss,
        contexts=['test1', 'test2']
    ).save()
    return jsonify({
        'id': str(eng2sign.id)
    }), 201
