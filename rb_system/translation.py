from rb_system.rules import br1_transitive_sentence, br2_intransitive_sentence, br3_ditransitive_sentence
from rb_system.nlp_tools import (
    perform_nlp_process, is_transitive_sentence, is_intransitive_sentence,
    is_ditransitive_sentence
)
from models.models import TextData, TSentence, Eng2Sign, SignGloss
from typing import List, Optional

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


def map_english_to_sign_gloss(words: List[str]) -> List[str]:
    """
    Convert a list of english words to a list of sign glosses.
    Map english words to the ThSL database.
    """
    glosses: List[str] = []
    index = 0
    for idx, word in enumerate(words):
        split_word = word.split('-')

        if len(split_word) > 1:
            related_word = split_word[0]
            search_word = split_word[1]
            # TODO: mark sth and choose word outside this loop? remember index to insert later?
            index = idx
            # print('(1) ---> ', word, split_word, search_word, related_word, index)
            gloss = retrieve_sign_gloss_from_context(search_word, related_word)
            glosses.append(gloss)
        else:
            # print('(2) ---> ', word, split_word, search_word, related_word, index)
            search_word = split_word[0]
            gloss = retrieve_sign_gloss(search_word)
            glosses.append(gloss)

    return glosses
    # return words


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


def get_glosses_from_words(words: List[Eng2Sign]) -> List[str]:
    glosses = []
    for word in words:
        gloss: SignGloss
        for gloss in word.sign_glosses:
            if gloss.lang == 'en':
                logging.info(f'Found word {word.english} in the dictionary')
                glosses.append(gloss.gloss)
    return glosses


def retrieve_word(word: str) -> Optional[Eng2Sign]:
    results = Eng2Sign.objects(english=word)
    if len(results) == 0:
        logging.info(f"Word '{word}' is not found in the dictionary")
        return None

    logging.info(f"Found {len(results)} results that matches '{word}'")
    return results[0]


def retrieve_word_from_context(word: str, related_word: str) -> Optional[Eng2Sign]:
    candidate_words = Eng2Sign.objects(english=word)
    related_words = Eng2Sign.objects(english=related_word)

    if len(candidate_words) == 0:
        logging.info(f"Word '{word}' is not found in the dictionary")
        return

    for rw in related_words:
        rw: Eng2Sign
        for candidate in candidate_words:
            candidate: Eng2Sign
            print("candidate context: ", candidate.contexts)
            for context in rw.contexts:
                if context in candidate.contexts:
                    return candidate
    return


def retrieve_sign_gloss(word: str) -> str:
    result_word = retrieve_word(word)
    if not result_word:
        logging.info(f"Word '{word}' is not found in the dictionary")
        return f"word '{word}' is not found in the dictionary"

    gloss: SignGloss
    for gloss in result_word.sign_glosses:
        if gloss.lang == 'en':
            logging.info(f"Found word '{result_word.english}' in the dictionary")
            return gloss.gloss
    logging.info(f"No gloss of '{word}' is found in the dictionary")
    return f"no gloss of '{word}' is found in the dictionary"


def retrieve_sign_gloss_from_context(word: str, related_word: str) -> str:
    result_word = retrieve_word_from_context(word, related_word)
    if not result_word:
        logging.info(f"Cannot find a context of '{word}' that matches '{related_word}'")
        return f"word '{word}' is not found in the dictionary"

    gloss: SignGloss
    for gloss in result_word.sign_glosses:
        if gloss.lang == 'en':
            logging.info(f"Found word '{result_word.english}' in the dictionary")
            return gloss.gloss
    logging.info(f"No gloss of '{word}' is found in the dictionary")
    return f"no gloss of '{word}' is found in the dictionary"


"""
idea?
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

how many ThSL signs for walking?

he-walk
# search each context
he -> context = [person, singular]
walk -> context = ['use with 1 person', '1 person', 'ใช้กับคนหนึ่งคน', 'หนึ่งคน', '1 คน', 'person', 'คน']
"""
