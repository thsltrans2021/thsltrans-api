from flask import Request
from typing import List, Dict
from api.models import Eng2Sign, SignGloss
from mongoengine import QuerySet

import json


def validate_dict_request_body(req: Request) -> bool:
    """Validate request from `add_words()` controller"""
    required_keys = ['word', 'gloss_en']
    try:
        req_body = dict(req.json)
        word_pairs = req_body['data']
        if not word_pairs:
            return False
        for wp in word_pairs:
            for key in required_keys:
                if key not in wp.keys():
                    return False
        return True
    except TypeError:
        return False
    except KeyError:
        return False


def request_body_to_eng2sign(req: Request) -> List[Eng2Sign]:
    eng2signs = []
    req_body = dict(req.json)
    for wp in req_body['data']:
        eng2sign = Eng2Sign(english=wp['word'])
        gloss = SignGloss()

        result: QuerySet = Eng2Sign.objects(english=wp['word'])[:1]
        if result:
            eng2sign = result[0]
            gloss = eng2sign.sign_glosses

        for key in wp.keys():
            if 'gloss' in key:
                setattr(gloss, key, wp[key])
        eng2sign.sign_glosses = gloss

        try:
            eng2sign.context = wp['context']
        except KeyError:
            pass

        eng2signs.append(eng2sign)
    return eng2signs


def eng2sign_to_json(eng2sign: Eng2Sign) -> Dict:
    eng2sign_dict = json.loads(eng2sign.to_json())
    del eng2sign_dict['_id']
    del eng2sign_dict['sign_glosses']['_cls']
    return eng2sign_dict
