from typing import List
from rb_system.rules import br1_transitive_sentence
from rb_system.nlp_tools import perform_nlp_process
from api.models import TextData
from spacy.tokens import Span

import logging

"""
The translation functions that work on a sentence level only
"""


def apply_rules(text: Span) -> List[str]:
    """Return a list of rearranged english words"""
    words = br1_transitive_sentence(text)
    # can we apply a pattern of the rule to categorize a sentence
    sign_glosses = map_english_to_sign_gloss(words)
    return sign_glosses


def map_english_to_sign_gloss(words: List[str]) -> List[str]:
    """
    Convert a list of english words to a list of sign glosses.
    Map english words to the ThSL database.
    """
    return words


def translate_english_to_sign_gloss(text_data: TextData) -> List[List[str]]:
    perform_nlp_process(text_data)
    results = []
    for idx, paragraph in enumerate(text_data.processed_data):
        logging.info(f'Translating paragraph {idx + 1}')
        for sentence in paragraph:
            results.append(apply_rules(sentence))
    text_data.thsl_translation = results
    return results
