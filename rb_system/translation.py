from rb_system.basic_sentence_rules import (
    br1_transitive_sentence, br2_intransitive_sentence, br3_ditransitive_sentence,
    br0_single_word, br4_locative_sentence
)
from rb_system.nlp_tools import (
    perform_nlp_process, is_transitive_sentence, is_intransitive_sentence,
    is_ditransitive_sentence, is_single_word, is_locative_sentence
)
from models.models import TextData, TSentence, Eng2Sign, SignGloss, ThSLClassifier, ThSLPrepositionPhrase, ThSLVerbPhrase
from typing import List, Optional, Union, Tuple
from utils.iterator import powerset

import logging

"""
The translation functions that work on a sentence level only
"""


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


def apply_rules(sentence: TSentence) -> List[str]:
    """Return a list of ThSL glosses"""
    words = ['not supported']
    if is_single_word(sentence):
        words = br0_single_word(sentence)
    elif is_locative_sentence(sentence):
        words = br4_locative_sentence(sentence)
    elif is_transitive_sentence(sentence):
        words = br1_transitive_sentence(sentence)
    elif is_intransitive_sentence(sentence):
        words = br2_intransitive_sentence(sentence)
    elif is_ditransitive_sentence(sentence):
        words = br3_ditransitive_sentence(sentence)

    # sign_glosses = map_english_to_sign_gloss(words)
    sign_glosses = new_map_english_to_sign_gloss(words)
    return sign_glosses


# TODO: know that CL is Enum and deal with it, search the correct enum by context (the word before enum)
def map_english_to_sign_gloss(words: List[Union[str, ThSLClassifier]]) -> List[str]:
    """
    Convert a list of english words to a list of sign glosses.
    Map english words to the ThSL database.
    """
    logging.info(f'Starting mapping: {words}')
    classifiers: List[str] = []
    glosses: List[str] = []
    index = 0
    for idx, word in enumerate(words):
        if isinstance(word, ThSLClassifier):
            previous_word = words[idx - 1]
            gloss = retrieve_sign_gloss_from_context(word.root_word.lemma_, previous_word)
            glosses.append(gloss)
            classifiers.append(gloss)
            continue

        split_words = word.split('-')

        if len(split_words) > 1:
            related_word = split_words[0]
            search_word = split_words[1]
            # TODO: mark sth and choose word outside this loop? remember index to insert later?
            index = idx
            # print('(1) ---> ', word, split_word, search_word, related_word, index)
            gloss = retrieve_sign_gloss_from_context(search_word, related_word)
            glosses.append(gloss)
        else:
            # print('(2) ---> ', word, split_word, search_word, related_word, index)
            search_word = split_words[0]
            gloss = retrieve_sign_gloss(search_word)
            glosses.append(gloss)

    return glosses


def new_map_english_to_sign_gloss(words: List[Union[str, ThSLClassifier]]) -> List[str]:
    """
    Convert a list of english words to a list of sign glosses.
    Map english words to the ThSL database.
    """
    logging.info(f'Starting mapping: {words}')
    thsl_glosses: List[str] = []
    for word in words:
        if isinstance(word, ThSLClassifier):
            gloss = new_retrieve_thsl_classifier_gloss(word)
            if not gloss:
                thsl_glosses.append(f"No gloss of '{word.root_word.lemma_}' is found in the dictionary")
            else:
                thsl_glosses.append(gloss.gloss)
        elif isinstance(word, ThSLPrepositionPhrase):
            gloss = new_retrieve_sign_gloss_for_prep_with_context(word)
            thsl_glosses.append(gloss)
        elif '-' in word:
            print("Ugly search!", word)
            gloss = new_retrieve_sign_gloss_for_verb_with_context(word)
            thsl_glosses.append(gloss)
        else:
            print("Normal search!", word)
            gloss = new_retrieve_sign_gloss_for_noun(word)
            thsl_glosses.append(gloss)
    return thsl_glosses


def _get_glosses_from_words(words: List[Eng2Sign]) -> List[str]:
    glosses = []
    for word in words:
        gloss: SignGloss
        for gloss in word.sign_glosses:
            if gloss.lang == 'en':
                logging.info(f'Found word {word.english} in the dictionary')
                glosses.append(gloss.gloss)
    return glosses


def _retrieve_word(word: str) -> Optional[Eng2Sign]:
    results = Eng2Sign.objects(english=word)
    if len(results) == 0:
        logging.info(f"Word '{word}' is not found in the dictionary")
        return None

    logging.info(f"Found {len(results)} results that matches '{word}'")
    return results[0]


def _retrieve_word_from_context(word: str, related_word: str) -> Optional[Eng2Sign]:
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
    result_word = _retrieve_word(word)
    if not result_word:
        logging.info(f"Word '{word}' is not found in the dictionary")
        return f"word '{word}' is not found in the dictionary"

    gloss: SignGloss
    for gloss in result_word.sign_glosses:
        if gloss.lang == 'en':
            logging.info(f"Found gloss for a word '{result_word.english}' in the dictionary")
            return gloss.gloss
    logging.info(f"No gloss of '{word}' is found in the dictionary")
    return f"no gloss of '{word}' is found in the dictionary"


def retrieve_sign_gloss_from_context(word: str, related_word: str) -> str:
    result_word = _retrieve_word_from_context(word, related_word)
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


def _count_possible_matches(target_word: Eng2Sign, related_word: Union[Eng2Sign, SignGloss]) -> List[Tuple[SignGloss, int]]:
    related_contexts = set(related_word.contexts)
    related_ctx_combinations = [set(combination) for combination in list(powerset(related_contexts, no_empty=True))]
    print("related context --> ", related_contexts)
    print("related ctx combin --> ", related_ctx_combinations)

    possible_matches: List[Tuple[SignGloss, int]] = []
    gloss: SignGloss
    for gloss in target_word.sign_glosses:
        gloss_ctx_combinations = [set(combination) for combination in list(powerset(gloss.contexts, no_empty=True))]
        print("gloss com --> ", gloss_ctx_combinations)

        match_count = 0
        # try matching related_context with gloss_ctx_combinations as much as possible
        for g_ctx in gloss_ctx_combinations:
            if g_ctx in related_ctx_combinations:
                match_count += 1
        possible_matches.append((gloss, match_count))

    print("matches --> ", possible_matches)
    return possible_matches


def _filter_highest_matched_results(possible_matches: List[Tuple[SignGloss, int]]) -> List[Tuple[SignGloss, int]]:
    results: List[Tuple[SignGloss, int]] = []
    max_match_count = 0
    for match in possible_matches:
        if match[0].lang == 'en':
            if match[1] > max_match_count:
                max_match_count = match[1]
                results = [match]
            elif match[1] == max_match_count:
                results.append(match)
    print("results --> ", [r[0].gloss for r in results])
    return results


def new_retrieve_sign_gloss_for_noun(word) -> str:
    result = _retrieve_word(word)
    if not result:
        logging.info(f"Word '{word}' is not found in the dictionary")
        return f"word '{word}' is not found in the dictionary"

    unwanted_pos = ["verb", "classifier", "preposition"]
    for gloss in result.sign_glosses:
        if gloss.pos in unwanted_pos:
            continue
        elif gloss.lang == "en":
            logging.info(f"Found gloss for a word '{result.english}' in the dictionary")
            return gloss.gloss
    logging.info(f"No gloss of '{word}' is found in the dictionary")
    return f"no gloss of '{word}' is found in the dictionary"


def new_retrieve_sign_gloss_for_verb_with_context(word_with_context: str) -> str:
    """
    he-walk -> person-walk
    """
    split_words = word_with_context.split('-')

    # separate word and context
    related_word = split_words[0]
    verb = split_words[1]

    # assume that `english` key is unique
    candidate_word = Eng2Sign.objects(english=verb)
    related_word = Eng2Sign.objects(english=related_word)
    assert len(candidate_word) <= 1, f'[v_with_ctx] duplicated `english` key: {verb}'
    assert len(related_word) <= 1, f'[v_with_ctx] duplicated `english` key: {related_word}'

    if len(candidate_word) == 0:
        message = f"Verb '{verb}' is not found in the dictionary"
        logging.info(message)
        return message

    # if no context -> use default (highest priority)
    if len(related_word) == 0:
        gloss: SignGloss
        for gloss in candidate_word[0].sign_glosses:
            if gloss.priority >= 1 and gloss.lang == "en":
                return gloss.gloss

    possible_matches = _count_possible_matches(candidate_word[0], related_word[0])
    assert len(possible_matches) > 0, \
        f'[v_with_ctx] no possible match, please check whether {candidate_word} has glosses or not'

    # get the results that have the highest matched context
    results = _filter_highest_matched_results(possible_matches)
    assert len(results) > 0, f'[v_with_ctx] unexpectedly no result'

    # if there are multiple results, final result based on its priority (assume that priority is unique)
    final_result: Optional[SignGloss] = None
    if len(results) > 1:
        max_priority = -1
        for result in results:
            result: SignGloss = result[0]
            if not result.priority:
                continue
            elif result.priority > max_priority:
                print(result.gloss, result.priority)
                max_priority = result.priority
                final_result = result
    else:
        final_result = results[0][0]

    print("final result --> ", final_result.gloss)
    return final_result.gloss


def new_retrieve_thsl_classifier_gloss(classifier: ThSLClassifier) -> Optional[SignGloss]:
    print("search for CL:", classifier.root_word.lemma_)
    search_results = Eng2Sign.objects(english=classifier.root_word.lemma_)
    if len(search_results) == 0:
        logging.info(f"No gloss of '{classifier.root_word.lemma_}' is found in the dictionary")
        return None

    assert len(search_results) > 0, f'[r_cl] no `english` key that matches for {classifier.root_word}'

    word: Eng2Sign = search_results[0]
    root_gloss: Optional[SignGloss] = None
    gloss: SignGloss
    for gloss in word.sign_glosses:
        if gloss.pos == "classifier":
            return gloss
        elif gloss.pos == "noun":
            root_gloss = gloss

    # if no CL in the database, return its root word
    return root_gloss


def new_retrieve_sign_gloss_for_prep_with_context(prep_phrase: ThSLPrepositionPhrase) -> str:
    """
    'subjCL-on-locCL'
    {
        "word": "on",
        "glosses": [
            {
                "gloss": "roundObjCL-ON-thinObjCL",
                "lang": "en",
                "contexts": [
                    "round", "object", "thin"
                ],
                "pos": "preposition"
            }, {
                "gloss": "thinObjCL-ON-thinObjCL",
                "lang": "en",
                "contexts": [
                    "object", "thin"
                ],
                "pos": "preposition"
            }
        ],
    }, {
        "word": "apple",
        "glosses": [
            {
                "gloss": "roundObjCL",
                "lang": "en",
                "pos": "classifier",
                "contexts": [
                    "round", "object"
                ]
            },
            {
                "gloss": "APPLE",
                "lang": "en",
                "pos": "noun"
            },
        ],
        "contexts": [
            "round", "object", "fruit"
        ],
    }
    """
    prep_subj = new_retrieve_thsl_classifier_gloss(prep_phrase.preposition_subj_cl)
    prep_obj = new_retrieve_thsl_classifier_gloss(prep_phrase.preposition_obj_cl)

    search_results = Eng2Sign.objects(english=prep_phrase.preposition.lemma_)
    if len(search_results) == 0:
        logging.info(f"No gloss of '{prep_phrase.preposition.lemma_}' is found in the dictionary")
        return f"no gloss of '{prep_phrase.preposition.lemma_}' is found in the dictionary"

    # context must exist
    if not prep_subj or not prep_obj:
        logging.info(f"No gloss of '{prep_phrase}' is found in the dictionary")
        return f"no gloss of '{prep_phrase}' is found in the dictionary"

    prep: Eng2Sign = search_results[0]
    possible_matches_subj = _count_possible_matches(prep, prep_subj)
    possible_matches_obj = _count_possible_matches(prep, prep_obj)
    print("matches (subj) --> ", possible_matches_subj)
    print("matches (obj) --> ", possible_matches_obj)

    # then find gloss that matches both subj's and obj's contexts
    highest_matched_subj = _filter_highest_matched_results(possible_matches_subj)
    highest_matched_obj = _filter_highest_matched_results(possible_matches_obj)
    print("h matches (subj) --> ", highest_matched_subj)
    print("h matches (obj) --> ", highest_matched_obj)

    # assume that highest matched of subj and obj always overlaps each other
    final_result: Optional[SignGloss] = None
    for h_match in highest_matched_subj:
        if h_match in highest_matched_obj:
            final_result = h_match[0]

    return final_result.gloss
