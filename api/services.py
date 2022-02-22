from flask import Request
from typing import List, Dict
from models.models import Eng2Sign, SignGloss, TextData

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
    """Validate the request body from `generate_translation()` controller"""
    try:
        req_body = dict(req.json)
        data = req_body['data']
        if not data:
            return False
        paragraphs = data['paragraphs']
        if not paragraphs:
            return False
    except TypeError:
        return False
    except KeyError:
        return False
    return True


def request_body_to_eng2sign(req: Request) -> List[Eng2Sign]:
    """
    Parse the request body from `add_words()` controller

    Example request body:
    {
        "data": [
            {
                "word": "money",
                "glosses": [
                    {
                        "gloss": "MONEY",
                        "lang": "en"
                    },
                    {
                        "gloss": "เงิน",
                        "lang": "th"
                    }
                ],
                "context": "object"
            }
        ]
    }
    """
    eng2signs = []
    req_body = dict(req.json)
    for wp in req_body['data']:
        eng2sign = Eng2Sign(english=wp['word'])
        glosses = []
        for gloss in wp['glosses']:
            sign_gloss = SignGloss(
                gloss=gloss['gloss'],
                lang=gloss['lang'],
                contexts=gloss['contexts']
            )

            try:
                sign_gloss.priority = gloss['priority']
            except KeyError:
                pass

            glosses.append(sign_gloss)
        eng2sign.sign_glosses = glosses

        try:
            eng2sign.en_pos = wp['en_pos']
        except KeyError:
            pass

        try:
            eng2sign.contexts = wp['contexts']
        except KeyError:
            pass

        eng2signs.append(eng2sign)
    return eng2signs


def request_to_existing_eng2sign(doc_id: str, req: Request) -> Eng2Sign:
    """
    Parse the request body from `update_words()` controller

    Example request body:
    {
        "word": "walk",
        "glosses": [
            {
                "gloss": "person-WALK",
                "lang": "en"
            },
            {
                "gloss": "เดิน",
                "lang": "th"
            }
        ],
        "contexts": ["human", "1 human", "ใช้กับคนหนึ่งคน", "หนึ่งคน", "1 คน"]
    }
    """
    req_body = dict(req.json)
    eng2sign: Eng2Sign = Eng2Sign.objects.with_id(doc_id)

    glosses = []
    for gloss in req_body['glosses']:
        glosses.append(SignGloss(gloss=gloss['gloss'], lang=gloss['lang']))
    eng2sign.sign_glosses = glosses

    try:
        eng2sign.en_pos = req_body['en_pos']
    except KeyError:
        pass

    try:
        eng2sign.contexts = req_body['contexts']
    except KeyError:
        pass

    return eng2sign


def request_body_to_text_data(req: Request) -> TextData:
    """
    Parse the request body from `generate_translation()` controller

    Example request body:
    {
        "data": {
            "paragraphs": [
                "Hello. This is your friend, John.",
                "The chickens walk.",
                "My mother gives him 4 apples."
            ],
            "lang": "US"
        }
    }
    """
    req_body = dict(req.json)
    data = req_body['data']
    trans = TextData()
    trans.original = data['paragraphs']
    return trans


def eng2sign_to_json(eng2sign: Eng2Sign) -> Dict:
    eng2sign_dict = json.loads(eng2sign.to_json())
    eng2sign_dict['id'] = eng2sign_dict['_id']['$oid']
    del eng2sign_dict['_id']
    sign_glosses: List[SignGloss] = eng2sign_dict['sign_glosses']
    for i in range(len(sign_glosses)):
        del eng2sign_dict['sign_glosses'][i]['_cls']

    return eng2sign_dict
