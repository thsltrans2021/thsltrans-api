from flask import Request
from typing import List


def validate_dict_request_body(req: Request) -> bool:
    expected_keys = ['word_pairs', 'gloss_lang']
    try:
        req_body = dict(req.json)
        for k in expected_keys:
            if k not in req_body.keys():
                return False
        return True
    except TypeError:
        return False


def request_body_to_eng2sign_schema(req: Request) -> List:
    eng2sign_schemas = []
    req_body = dict(req.json)
    for wp in req_body['word_pairs']:
        eng2sign_schema = {
            'english': wp['word'],
            'sign_glosses': {
                f'gloss_{req_body["gloss_lang"]}': wp['gloss'],
            },
            'context': None,
        }
        try:
            eng2sign_schema['context'] = wp['context']
        except KeyError:
            pass
        eng2sign_schemas.append(eng2sign_schema)
    return eng2sign_schemas
