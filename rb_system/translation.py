from rb_system.rules import br1_transitive_sentence, br2_intransitive_sentence
from rb_system.nlp_tools import perform_nlp_process, is_transitive_sentence, is_intransitive_sentence
from api.models import TextData, TSentence
from typing import List

import logging

"""
The translation functions that work on a sentence level only
"""


def apply_rules(sentence: TSentence) -> List[str]:
    """Return a list of rearranged english words"""
    words = ['Nope']
    if is_transitive_sentence(sentence):
        words = br1_transitive_sentence(sentence)
    elif is_intransitive_sentence(sentence):
        # 'Hello.' should not be intransitive sentence
        words = br2_intransitive_sentence(sentence)

    # can we apply a pattern of the rule to categorize a sentence
    sign_glosses = map_english_to_sign_gloss(words)
    return sign_glosses


def map_english_to_sign_gloss(words: List[str]) -> List[str]:
    """
    Convert a list of english words to a list of sign glosses.
    Map english words to the ThSL database.
    """
    return words


def translate_english_to_sign_gloss(text_data: TextData) -> List[List[List[str]]]:
    perform_nlp_process(text_data)
    results = []
    for idx, paragraph in enumerate(text_data.processed_data):
        logging.info(f'Translating paragraph {idx + 1}')
        thsl_sentences = []
        for sentence in paragraph:
            thsl_sentences.append(apply_rules(sentence))
        results.append(thsl_sentences)
    text_data.thsl_translation = results
    return results
