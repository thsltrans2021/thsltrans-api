from flask import Request
from typing import List
from api.models import Eng2Sign, SignGloss


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


def request_body_to_eng2sign(req: Request) -> List[Eng2Sign]:
    eng2signs = []
    req_body = dict(req.json)
    for wp in req_body['word_pairs']:
        eng2sign = Eng2Sign(english=wp['word'])
        gloss = SignGloss()
        setattr(gloss, f'gloss_{req_body["gloss_lang"]}', wp['gloss'])
        try:
            eng2sign.context = wp['context']
        except KeyError:
            pass
        eng2signs.append(eng2sign)
    return eng2signs
