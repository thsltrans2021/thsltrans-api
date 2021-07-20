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


@translator.route('/404', methods=['GET'])
def example_404():
    return jsonify({
        'message': 'There is no such a thing here'
    }), 404


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


@translator.route('/json', methods=['GET'])
def test_json():
    pass
    # from api.models import ResponseBody
    #
    # res = ResponseBody('this is message', 'this is data')
    # # TypeError: Object of type ResponseBody is not JSON serializable
    # return jsonify(res), 200
