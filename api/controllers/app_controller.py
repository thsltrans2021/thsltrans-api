from flask import Blueprint

entry_point = Blueprint('entry_point', __name__)


@entry_point.route('/', methods=['GET'])
def index():
    return 'Welcome to ThSL Translator Application APIs. ' \
           'To access English-to-SignGloss dictionary and perform a translation, ' \
           'please go to `api/dict/` and `api/trans/` respectively.', 200
