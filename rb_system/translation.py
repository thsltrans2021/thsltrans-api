from rb_system.rules import br1_transitive_sentence, br2_intransitive_sentence, br3_ditransitive_sentence
from rb_system.nlp_tools import (
    perform_nlp_process, is_transitive_sentence, is_intransitive_sentence,
    is_ditransitive_sentence
)
from models.models import TextData, TSentence, Eng2Sign, SignGloss
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
    elif is_ditransitive_sentence(sentence):
        words = br3_ditransitive_sentence(sentence)
    # can we apply a pattern of the rule to categorize a sentence
    sign_glosses = map_english_to_sign_gloss(words)
    return sign_glosses


# TODO: how to directly map chicken-walk to the dictionary
def map_english_to_sign_gloss(words: List[str]) -> List[str]:
    """
    Convert a list of english words to a list of sign glosses.
    Map english words to the ThSL database.
    """
    glosses: List[str] = []
    for word in words:
        results = Eng2Sign.objects(english=word)
        if len(results) == 0:
            logging.info(f'word {word} is not found in the dictionary')
            glosses.append(f'word {word} is not found in the dictionary')
            continue

        result_word: Eng2Sign = results[0]
        gloss: SignGloss
        for gloss in result_word.sign_glosses:
            if gloss.lang == 'en':
                logging.info(f'Found word {word} in the dictionary')
                glosses.append(gloss.gloss)

    # return glosses
    return words


def translate_english_to_sign_gloss(text_data: TextData) -> List[List[List[str]]]:
    perform_nlp_process(text_data)
    results = []
    for idx, paragraph in enumerate(text_data.processed_data):
        logging.info(f'Translating paragraph {idx + 1}...')
        thsl_sentences = []
        for sentence in paragraph:
            sentence = apply_rules(sentence)
            thsl_sentences.append(sentence)
        results.append(thsl_sentences)

    text_data.thsl_translation = results
    logging.info(f'Finished translating {len(text_data.processed_data)} paragraph(s)')
    return results


"""
walk: [
  {
    context: chicken, bird
    gloss: CHICKEN-WALK
    lang: en
  },
  {
    context: 
  }
]

classify animal to ... number
how many ThSL signs for walking?
"""
