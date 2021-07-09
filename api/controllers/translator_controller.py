from flask import Blueprint

translator = Blueprint('translator', __name__)


@translator.route('/', methods=['GET'])
def translator_index():
    return 'Welcome to thsltrans rule-based system'
