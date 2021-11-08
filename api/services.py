from flask import Request
from typing import List, Dict
from api.models import Eng2Sign, SignGloss, TextData
from mongoengine import QuerySet

import json


def validate_dict_request_body(req: Request) -> bool:
    """Validate request from `add_words()` controller"""
    required_keys = ['word', 'glosses']
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


def validate_trans_request_body(req: Request) -> bool:
    try:
        req_body = dict(req.json)
        paragraphs = req_body['data']
        if not paragraphs:
            return False
        for k in paragraphs.keys():
            if k[0] != 'p':
                return False
    except TypeError:
        return False
    except KeyError:
        return False
    return True


def request_body_to_eng2sign(req: Request) -> List[Eng2Sign]:
    eng2signs = []
    req_body = dict(req.json)
    for wp in req_body['data']:
        eng2sign = Eng2Sign(english=wp['word'])

        # update the existing document if any
        result: QuerySet = Eng2Sign.objects(english=wp['word'])[:1]
        if result:
            eng2sign = result[0]

        for gloss in wp['glosses']:
            eng2sign.sign_glosses = SignGloss(gloss=gloss['gloss'], lang=gloss['lang'])

        try:
            eng2sign.en_pos = wp['en_pos']
            eng2sign.contexts = wp['contexts']
        except KeyError:
            pass

        eng2signs.append(eng2sign)
    return eng2signs


def request_body_to_text_data(req: Request) -> TextData:
    req_body = dict(req.json)
    data = req_body['data']
    trans = TextData()
    for key in data.keys():
        trans.original.append(data[key])
    return trans


def eng2sign_to_json(eng2sign: Eng2Sign) -> Dict:
    eng2sign_dict = json.loads(eng2sign.to_json())
    del eng2sign_dict['_id']
    del eng2sign_dict['sign_glosses']['_cls']
    return eng2sign_dict
