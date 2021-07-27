from typing import List
from rb_system.rules import rule_1
from api.models import TextData

import logging


def apply_rules(text: str) -> List[str]:
    """Return a list of rearranged english words"""
    words = rule_1(text)
    sign_glosses = map_english_to_sign_gloss(words)
    return sign_glosses


def map_english_to_sign_gloss(words: List[str]) -> List[str]:
    """Convert a list of english words to a list of sign glosses"""
    return words


def translate_english_to_sign_gloss(text_data: TextData) -> List[List[str]]:
    results = []
    for idx, paragraph in enumerate(text_data.original):
        # TODO: perform NLP
        logging.info(f'Translating paragraph {idx + 1}')
        results.append(apply_rules(paragraph))
    text_data.translation = results
    return results
