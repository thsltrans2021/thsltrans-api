from rb_system.basic_sentence_rules import *
from rb_system.nlp_tools import *
from models.models import *
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
    # TODO: handle complex sentence here
    if is_complex_sentence(sentence):
        relative_clause_data = filter_relative_clause(sentence)
        if len(relative_clause_data[0]) > 0:
            thsl_words = apply_rule_to_sentence_with_relative_clause(sentence, relative_clause_data)
        else:
            logging.info(f'Not supported complex sentence: {sentence}')
            thsl_words = rearrange_basic_sentence(sentence)
    else:
        thsl_words = rearrange_basic_sentence(sentence)

    if is_wh_question(sentence):
        thsl_words = cf3_question(sentence, thsl_words)

    sign_glosses = map_english_to_sign_gloss(thsl_words)
    return sign_glosses


def apply_rule_to_sentence_with_relative_clause(sentence: List[Token], relcl_data: Tuple[List[Token], int, int]) -> List[Union[str, ThSLPhrase]]:
    # translate relative clause
    relcl, relcl_start_idx, relcl_end_idx = relcl_data
    relcl_subject: Optional[Token] = None
    for idx, token in enumerate(sentence):
        if idx + 1 == relcl_start_idx:
            relcl_subject = token

    assert relcl_subject is not None, f'[relcl_rule] Cannot find the real subject of relative clause {relcl}'
    relcl.pop(0)
    relcl.insert(0, relcl_subject)
    thsl_relcl = rearrange_basic_sentence(relcl)
    # print(f'--> {relcl=}\n--> {thsl_relcl=}')

    root_sentence = sentence[0:relcl_start_idx] + sentence[relcl_end_idx+1:len(sentence)]
    thsl_root_sentence = rearrange_basic_sentence(root_sentence)
    # print(f'--> {root_sentence=}\n--> {thsl_root_sentence=}')

    start_idx: Optional[int] = None
    duplicated_subj_idx: Optional[int] = None
    for idx, root_t in enumerate(thsl_root_sentence):
        for relcl_idx, relcl_t in enumerate(thsl_relcl):
            if root_t == relcl_t:
                start_idx = idx
                duplicated_subj_idx = relcl_idx
    assert start_idx is not None, f'[relcl_rule] Unexpectedly no matched subject'

    # remove subject that is duplicated with the root sentence
    thsl_relcl.remove(thsl_relcl[duplicated_subj_idx])
    thsl_sentence = thsl_root_sentence[0:start_idx+1] + thsl_relcl + thsl_root_sentence[start_idx+1:len(thsl_root_sentence)]
    # print(f'--> {thsl_sentence=}')
    return thsl_sentence


def rearrange_basic_sentence(sentence: List[Token]) -> List[Union[str, ThSLPhrase]]:
    if is_single_word(sentence):
        result = br0_single_word(sentence)
        logging.debug(f'[br0 s] {result=}')
    elif is_phrase(sentence):
        result = br0_phrase(sentence)
        logging.debug(f'[br0 p] {result=}')
    elif is_locative_sentence(sentence):
        result = br4_locative_sentence(sentence)
        logging.debug(f'[br4] {result=}')
    elif is_stative_sentence(sentence):
        result = br13_stative_sentence(sentence)
        logging.debug(f'[br13] {result=}')
    elif is_transitive_sentence(sentence):
        result = br1_transitive_sentence(sentence)
        logging.debug(f'[br1] {result=}')
    elif is_intransitive_sentence(sentence):
        result = br2_intransitive_sentence(sentence)
        logging.debug(f'[br2] {result=}')
    elif is_ditransitive_sentence(sentence):
        result = br3_ditransitive_sentence(sentence)
        logging.debug(f'[br3] {result=}')
    else:
        result = ['not supported']
    return result


def map_english_to_sign_gloss(words: List[Union[str, ThSLPhrase]]) -> List[str]:
    """
    Convert a list of english words to a list of sign glosses.
    Map english words to the ThSL database.
    """
    logging.info(f'Starting mapping: {words}')
    thsl_glosses: List[str] = []
    for word in words:
        if isinstance(word, ThSLClassifier):
            gloss = retrieve_thsl_classifier_gloss(word)
            if not gloss:
                thsl_glosses.append(f"No gloss of '{word.root_word.lemma_}' is found in the dictionary")
            else:
                thsl_glosses.append(gloss.gloss)
        elif isinstance(word, ThSLPrepositionPhrase):
            gloss = retrieve_sign_gloss_for_prep_with_context(word)
            thsl_glosses.append(gloss)
        elif isinstance(word, ThSLVerbPhrase):
            gloss = retrieve_sign_gloss_for_verb_with_context(word)
            thsl_glosses.append(gloss)
        elif isinstance(word, ThSLNounPhrase):
            # thsl_glosses.append(f'[not implemented] {word}')
            glosses = retrieve_sign_gloss_for_noun_phrase(word)
            thsl_glosses = thsl_glosses + glosses
        elif '-' in word:
            print("Ugly search!", word)
            thsl_glosses.append(f'[no map] {word}')
        else:
            gloss = retrieve_sign_gloss_for_noun(word)
            thsl_glosses.append(gloss)
    print('result -->', thsl_glosses)
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


def _get_context_combinations(contexts) -> List[set]:
    contexts_set = set(contexts)
    combinations = [set(combination) for combination in list(powerset(contexts_set, no_empty=True))]
    return combinations


def _count_possible_matches(target_word: Eng2Sign, related_ctx_combinations: List[set]) -> List[Tuple[SignGloss, int]]:
    possible_matches: List[Tuple[SignGloss, int]] = []
    gloss: SignGloss
    for gloss in target_word.sign_glosses:
        gloss_ctx_combinations = [set(combination) for combination in list(powerset(gloss.contexts, no_empty=True))]
        # print(f"gloss '{gloss.gloss}' com --> ", gloss_ctx_combinations)

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


def retrieve_sign_gloss_for_noun(word) -> str:
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


def retrieve_sign_gloss_for_noun_phrase(noun_phrase: ThSLNounPhrase) -> List[str]:
    """
    a young mouse
    a young and beautiful girl
    """
    noun = noun_phrase.noun
    candidate_words = Eng2Sign.objects(english=noun.lemma_)
    assert len(candidate_words) <= 1, f'[n_with_ctx] duplicated `english` key: {noun.lemma_}'

    if len(candidate_words) == 0:
        message = f"Noun '{noun.lemma_}' is not found in the dictionary"
        logging.info(message)
        return [message]

    result: List[SignGloss] = []

    # select sign gloss that has the matched POS
    noun_glosses = candidate_words[0].sign_glosses
    for ng in noun_glosses:
        ng: SignGloss
        if ng.lang != 'en':
            continue
        if len(noun_glosses) == 1:
            result.append(ng)
            break
        elif ng.pos == 'noun' or ng.pos == 'pronoun':
            result.append(ng)
            break

    # select sign gloss that has the matched POS
    noun_adj_lst = noun_phrase.adj_list
    unmatched_adj = []
    for adj in noun_adj_lst:
        adj_words = Eng2Sign.objects(english=adj.lemma_)
        assert len(adj_words) <= 1, f'[n_with_ctx] duplicated `english` key: {adj.lemma_}'
        if len(adj_words) == 0:
            unmatched_adj.append(adj)
            continue
        for adj_g in adj_words[0].sign_glosses:
            adj_g: SignGloss
            if adj_g.pos == 'adjective' and adj_g.lang == 'en':
                result.append(adj_g)
                break

    result_glosses = [g.gloss for g in result]
    return result_glosses + [f'not found {u.lemma_}' for u in unmatched_adj]


def retrieve_sign_gloss_for_verb_with_context(verb_phrase: ThSLVerbPhrase) -> str:
    """
    he-walk -> person-walk

    verb associates with its subj's or obj's classifier
    """
    # assume that `english` key is unique
    verb = verb_phrase.verb
    candidate_words = Eng2Sign.objects(english=verb.lemma_)
    assert len(candidate_words) <= 1, f'[v_with_ctx] duplicated `english` key: {verb.lemma_}'

    if len(candidate_words) == 0:
        message = f"Verb '{verb.lemma_}' is not found in the dictionary"
        logging.info(message)
        return message

    verb_contexts = verb_phrase.contexts
    # print("attr --> ", verb_contexts)
    additional_ctx: List[set] = []

    unwanted_pos = ['verb', 'classifier', 'preposition']
    context_glosses: List[Tuple[int, SignGloss]] = []
    related_words = []
    related_words_idx = 0
    for ctx_key, ctx_val in verb_contexts.items():
        ctx_val: Token
        # consider additional context e.g. subject is plural
        if ctx_val.tag_ == POSLabel.P_PLURAL_NOUN.value:
            if ctx_key == 'subject':
                additional_ctx.append({'multiple subjects'})
            elif ctx_key == 'direct_obj' or ctx_key == 'indirect_obj':
                additional_ctx.append({'multiple objects'})

        result_ctx = _retrieve_word(ctx_val.lemma_)
        if result_ctx is None:
            continue

        ctx_glosses = []
        for gloss in result_ctx.sign_glosses:
            if gloss.pos in unwanted_pos:
                continue
            elif gloss.lang == 'en':
                ctx_glosses.append(gloss)

        if len(ctx_glosses) > 0:
            context_glosses = context_glosses + [(related_words_idx, gloss) for gloss in ctx_glosses]
            related_words.append(result_ctx)
            related_words_idx += 1

    # if no context -> use default (highest priority)
    if len(context_glosses) == 0:
        gloss: SignGloss
        for gloss in candidate_words[0].sign_glosses:
            try:
                if gloss.priority >= 1 and gloss.lang == 'en':
                    return gloss.gloss
            # no priority field -> return whatever
            except TypeError:
                if gloss.lang == 'en':
                    return gloss.gloss

    # append all gloss' ctx of all words related to verb (sub, iobj, dobj, etc.)
    ctx_combinations: List[set] = []
    for word_idx, ctx_gloss in context_glosses:
        ctx_gloss: SignGloss
        all_contexts = ctx_gloss.contexts + related_words[word_idx].contexts
        combinations = _get_context_combinations(all_contexts)
        ctx_combinations = ctx_combinations + combinations

    # concat with additional contexts
    ctx_combinations = ctx_combinations + additional_ctx
    print('ctx com: ', ctx_combinations)

    possible_matches = _count_possible_matches(candidate_words[0], ctx_combinations)
    assert len(possible_matches) > 0, \
        f'[v_with_ctx] no possible match, please check whether {candidate_words} has glosses or not'

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
        if final_result is None:
            logging.info(f'[v_with_ctx] No final result for {results}, choose the first result')
            final_result = results[0][0]
    else:
        final_result = results[0][0]

    assert final_result is not None, f'[v_with_ctx] unexpectedly no final result for {results}'
    return final_result.gloss


def retrieve_thsl_classifier_gloss(classifier: ThSLClassifier) -> Optional[SignGloss]:
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


def retrieve_sign_gloss_for_prep_with_context(prep_phrase: ThSLPrepositionPhrase) -> str:
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
    prep_subj = retrieve_thsl_classifier_gloss(prep_phrase.preposition_subj_cl)
    prep_obj = retrieve_thsl_classifier_gloss(prep_phrase.preposition_obj_cl)

    search_results = Eng2Sign.objects(english=prep_phrase.preposition.lemma_)
    if len(search_results) == 0:
        logging.info(f"No gloss of '{prep_phrase.preposition.lemma_}' is found in the dictionary")
        return f"no gloss of '{prep_phrase.preposition.lemma_}' is found in the dictionary"

    # context must exist
    if not prep_subj or not prep_obj:
        logging.info(f"No gloss of '{prep_phrase}' is found in the dictionary")
        return f"no gloss of '{prep_phrase}' is found in the dictionary"

    prep: Eng2Sign = search_results[0]
    prep_subj_ctx_com = _get_context_combinations(prep_subj.contexts)
    prep_obj_ctx_com = _get_context_combinations(prep_obj.contexts)
    print("prep subj com -> ", prep_subj_ctx_com)
    print("prep obj com -> ", prep_obj_ctx_com)

    possible_matches_subj = _count_possible_matches(prep, prep_subj_ctx_com)
    possible_matches_obj = _count_possible_matches(prep, prep_obj_ctx_com)
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
