from spacy import Language
from spacy.tokens import Token, Doc, Span
from models.models import TextData, TParagraph
from typing import List, Tuple
from rb_system.types import EntityLabel, POSLabel, DependencyLabel

import spacy

"""
python -m doctest -v rb_system/nlp_tools.py
token.tag_ --> ptb tag set, see: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
token.pos_ --> Universal POS tags, see: https://universaldependencies.org/u/pos/
"""
# TODO: consider using in-memory cache when matching doc with sign gloss

nlp: Language = spacy.load('en_core_web_sm')


# TODO: need to reconsider word segmentation (still have problem with words like 'next to', 'work from home'
# https://spacy.io/usage/linguistic-features#retokenization
def perform_nlp_process(text_data: TextData):
    """
    Perform necessary NLP such as part-of-speech tagging and dependency parsing.
    """
    # Split paragraph into a list of sentences
    for paragraph in text_data.original:
        p_doc: Doc = nlp(paragraph)
        sentences = list(p_doc.sents)
        processed_paragraph: TParagraph = []
        for sentence in sentences:
            sentence_token = remove_punctuations(sentence)
            sentence_token = _merge_token_by_entity(sentence_token)
            print(f"sentence_token: {sentence_token}")
            processed_paragraph.append(sentence_token)
        text_data.processed_data.append(processed_paragraph)


def is_single_word(sentence: List[Token]) -> bool:
    """
    True if the given sentence contains one word.

    >>> is_single_word(nlp('Home')[:])
    True
    >>> is_single_word(nlp('A baby')[:])
    True
    >>> is_single_word(nlp('Three babies')[:])
    False
    """
    # print(f"sentence '{sentence}': {len(sentence)}")
    determiners = ['a', 'the']
    if len(sentence) == 1:
        return True
    if len(sentence) == 2:
        if sentence[0].lemma_ in determiners:
            return True
    return False


def is_phrase(sentence: List[Token]) -> bool:
    """
    True if the given sentence should be handled as a phrase

    >>> is_phrase(nlp('once upon a time')[:])
    True
    >>> is_phrase(nlp('slowly and surely')[:])
    True
    >>> is_phrase(nlp('work from home')[:])
    True
    >>> is_phrase(nlp('I walk to school')[:])
    False
    >>> is_phrase(nlp('a baby')[:])
    False
    """
    if is_single_word(sentence):
        return False

    has_subj = False
    has_verb = False
    has_indirect_obj = False
    for token in sentence:
        token: Token
        if token.pos_ == POSLabel.U_VERB.value or token.pos_ == POSLabel.U_AUXILIARY.value:
            has_verb = True
        if token.dep_ == DependencyLabel.NOMINAL_SUBJECT.value:
            has_subj = True
        elif token.dep_ == DependencyLabel.DATIVE.value:
            has_indirect_obj = True

    # print(has_subj, has_verb, has_indirect_obj)
    if has_subj:
        # if it has both S and V, it'll be considered as an intransitive sentence
        # even though it isn't grammatically correct
        return not has_verb
    else:
        return not (has_indirect_obj and has_verb)


def _is_sentence(sentence: List[Token]) -> bool:
    return not (is_single_word(sentence) or is_phrase(sentence))


def is_transitive_sentence(sentence: List[Token]) -> bool:
    """
    A sentence that has a direct object (dobj).

    >>> is_transitive_sentence(nlp('Mary is collecting stamps.')[:])
    True
    >>> is_transitive_sentence(nlp('I like drawing.')[:])
    True
    >>> is_transitive_sentence(nlp('She eats an apple.')[:])
    True
    >>> is_transitive_sentence(nlp('They killed a lion.')[:])
    True
    >>> is_transitive_sentence(nlp('He is sleeping.')[:])
    False
    """
    if is_single_word(sentence):
        return False
    elif is_ditransitive_sentence(sentence):
        return False

    has_direct_object = False
    gerund_ancestors: List[Token] = []
    token: Token
    for token in sentence:
        if token.dep_ == DependencyLabel.DIRECT_OBJECT.value:
            has_direct_object = True
        elif (token.tag_ == POSLabel.P_VERB_PRESENT_PARTICIPLE.value) and (token.dep_ != DependencyLabel.ROOT.value):
            gerund_ancestors = list(token.ancestors)

    if has_direct_object:
        return True
    elif len(gerund_ancestors) > 0:
        # check if verb is followed by gerund
        a: Token
        for a in gerund_ancestors:
            if a.dep_ == DependencyLabel.ROOT.value:
                return True
    return False


def is_ditransitive_sentence(sentence: List[Token]) -> bool:
    """
    A sentence that has 2 objects (indirect obj followed by direct obj)

    >>> is_ditransitive_sentence(nlp('She gave some chocolates to him.')[:])
    True
    >>> is_ditransitive_sentence(nlp('Please suggest me a good movie to watch.')[:])
    True
    >>> is_ditransitive_sentence(nlp('She eats an apple.')[:])
    False
    >>> is_ditransitive_sentence(nlp('Throw me the ball.')[:])
    True
    >>> is_ditransitive_sentence(nlp('She eats')[:])
    False
    """
    # My mother taught me how to cook. (still failed)
    has_direct_object = False
    has_dative = False
    dobj_count = 0

    if len(sentence) < 3:
        return False

    for token in sentence:
        dep_relation = token.dep_
        if dep_relation == DependencyLabel.ROOT.value:
            # John bought me a phone.
            try:
                next_token: Token = token.nbor()
            except IndexError:
                # no token after the ROOT token -> clearly no obj
                return False
            if next_token.dep_ == DependencyLabel.DATIVE.value:
                return True
        elif dep_relation == DependencyLabel.DATIVE.value:
            has_dative = True
        elif dep_relation == DependencyLabel.DIRECT_OBJECT.value:
            has_direct_object = True
            dobj_count += 1
    return has_direct_object and has_dative or dobj_count > 1


def is_intransitive_sentence(sentence: List[Token]) -> bool:
    """
    Note: "she eats" is considered as an intransitive sentence in this case
    because we want to handle it as a sentence rather than a phrase.

    >>> is_intransitive_sentence(nlp('Hello')[:])
    False
    >>> is_intransitive_sentence(nlp('She eats an apple.')[:])
    False
    >>> is_intransitive_sentence(nlp('The mouse asked.')[:])
    True
    >>> is_intransitive_sentence(nlp('The chickens walk.')[:])
    True
    """
    if is_single_word(sentence):
        return False
    return not is_transitive_sentence(sentence) and not is_ditransitive_sentence(sentence)


def is_locative_sentence(sentence: List[Token]):
    """
    True if the given sentence is locative sentence.
    Locative sentence means that the sentence indicates place or direction.

    try detect preposition of place and check if it's actually talking about place (not time)
    - Check prepositional noun that comes after the preposition

    >>> is_locative_sentence(nlp('He works at Kasetsart University')[:])
    True
    >>> is_locative_sentence(nlp('Mother is at home')[:])
    True
    >>> is_locative_sentence(nlp('There is a plate of rice on the table')[:])
    True
    >>> is_locative_sentence(nlp('She buys 3 apples')[:])
    False
    >>> is_locative_sentence(nlp('I meet him at home on Sunday')[:])
    True
    >>> is_locative_sentence(nlp('She works on Monday')[:])
    False
    >>> is_locative_sentence(nlp('She gave some chocolates to him.')[:])
    False
    """
    if is_single_word(sentence):
        return False

    prep_phrases = retrieve_preposition_phrases(sentence)
    prep_phrases_of_place = filter_preposition_of_place(prep_phrases)
    # print("prep phrase: ", prep_phrases)
    # print("prep of place", prep_phrases_of_place)
    return len(prep_phrases_of_place) > 0


def is_wh_question(sentence: List[Token]) -> bool:
    if not _is_sentence(sentence):
        return False

    first_token = sentence[0]
    if first_token.tag_ == POSLabel.P_WH_ADVERB.value:
        return True
    elif first_token.tag_ == POSLabel.P_WH_PRONOUN.value:
        return True

    return False


def _has_stative_verb(sentence: List[Token]) -> bool:
    """
    True if the sentence has v.to be e.g. The shirt is blue
    """
    for token in sentence:
        if token.pos_ == POSLabel.U_AUXILIARY.value:
            return True
    return False


def is_stative_sentence(sentence: List[Token]) -> bool:
    return _has_stative_verb(sentence)


def is_complex_sentence(sentence: List[Token]):
    """
    True of the sentence has conjunction e.g. and, that, because
    """
    for token in sentence:
        if token.tag_ == POSLabel.P_WH_DETERMINER.value:
            return True
        elif token.pos_ == POSLabel.U_COORDINATING_CONJUNCTION.value:
            return True
        elif token.pos_ == POSLabel.U_SUBORDINATING_CONJUNCTION.value:
            return True
    return False


def retrieve_preposition_phrases(sentence: List[Token]) -> List[Tuple[Token, Token, int, int]]:
    """
    Finds preposition phrases from the sentence and return them
    as tuple of (prep, pobj, prep_idx, pobj_idx).
    """
    prep_phrases: List[Tuple[Token, Token, int, int]] = []
    current_prep = None
    current_prep_idx = 0

    for i in range(len(sentence)):
        token: Token = sentence[i]
        if token.dep_ == DependencyLabel.PREPOSITIONAL_MODIFIER.value or token.tag_ == POSLabel.P_PERP_OR_SUB_CON.value:
            current_prep = token
            current_prep_idx = i
        elif token.dep_ == DependencyLabel.OBJECT_OF_PREPOSITION.value:
            prep_phrases.append((current_prep, token, current_prep_idx, i))
    return prep_phrases


def filter_preposition_of_place(prep_phrases: List[Tuple[Token, Token, int, int]]):
    """
    Returns a list of preposition phrases that are not considered as prepositional phrase of time.
    """
    if len(prep_phrases) < 1:
        return []

    entity_types = [EntityLabel.DATE, EntityLabel.TIME]
    result_prep_phrases: List[Tuple[Token, Token, int, int]] = []
    for prep_p in prep_phrases:
        try:
            entity_label = EntityLabel(prep_p[1].ent_type_)
            if entity_label in entity_types:
                continue
        except ValueError:
            pass

        if prep_p[1].pos_ == POSLabel.U_PRONOUN.value:
            continue
        result_prep_phrases.append(prep_p)

    return result_prep_phrases


def has_org_entity(sentence: List[Token]) -> bool:
    org_entities = retrieve_entities(sentence, [EntityLabel.ORGANIZATION])
    return len(org_entities) > 0


def retrieve_entities(sentence: List[Token], entity_types: List[EntityLabel]) -> List[Tuple[Token, str]]:
    """
    Returns a list of the detected entities with their labels

    >>> test_sentence = nlp('He works at Kasetsart University.')[:]
    >>> retrieve_entities(test_sentence, [EntityLabel.ORGANIZATION])
    [(Kasetsart, 'ORG'), (University, 'ORG')]

    >>> test_sentence = nlp('He works at Kasetsart University and Apple on Monday')[:]
    >>> retrieve_entities(test_sentence, [EntityLabel.ORGANIZATION])
    [(Kasetsart, 'ORG'), (University, 'ORG'), (Apple, 'ORG')]

    >>> test_sentence = nlp('He works at Kasetsart University and Apple on Monday')[:]
    >>> retrieve_entities(test_sentence, [EntityLabel.ORGANIZATION, EntityLabel.DATE])
    [(Kasetsart, 'ORG'), (University, 'ORG'), (Apple, 'ORG'), (Monday, 'DATE')]
    """
    if len(entity_types) == 0:
        return [(token, token.ent_type_) for token in sentence if token.ent_type_ != '']

    entities: List[Tuple[Token, str]] = []
    for token in sentence:
        try:
            entity_label = EntityLabel(token.ent_type_)
            if entity_label in entity_types:
                entities.append((token, token.ent_type_))
        except ValueError:
            continue

    return entities


def retrieve_noun_phrases(sentence: List[Token]) -> List[str]:
    s_doc = nlp(" ".join([t.text for t in sentence]))
    return [np for np in s_doc.noun_chunks]


def _merge_token_by_entity(sentence: List[Token]) -> List[Token]:
    """
    - I work at Kasetsart University and Apple Inc.

    I work at Kasetsart and Apple Inc.
    [(Kasetsart, 'ORG'), (and, 'ORG'), (Apple, 'ORG'), (Inc., 'ORG')]
    [(3, 4, 4, 5, 5, 6)]

    Entities
    Kasetsart and Apple Inc. | ORG | 10 | 34
    """
    entity_indexes = []
    entity_indexes_groups = []
    for i in range(len(sentence)):
        if i + 1 == len(sentence):
            if len(entity_indexes) > 1:
                entity_indexes_groups.append(set(entity_indexes))
            break

        token: Token = sentence[i]
        next_token: Token = sentence[i].nbor()

        if token.ent_type_ == next_token.ent_type_:
            if token.ent_type_ != '':
                entity_indexes.append(i)
                entity_indexes.append(i + 1)
        else:
            if len(entity_indexes) > 1:
                entity_indexes_groups.append(set(entity_indexes))
                entity_indexes = []

    # print(entities)
    # print(entity_indexes_groups)

    sentence_doc = nlp(' '.join([token.text for token in sentence]))

    # print("Before: ", [t.text for t in sentence_doc])
    with sentence_doc.retokenize() as retokenizer:
        for indexes in entity_indexes_groups:
            start = min(indexes)
            end = max(indexes) + 1
            retokenizer.merge(
                sentence_doc[start:end],
                attrs={
                    "LEMMA": " ".join([sentence[i].lemma_ for i in indexes]),
                }
            )

    new_sentence = [token for token in sentence_doc]
    return new_sentence


def filter_relative_clause(sentence: List[Token]) -> Tuple[List[Token], int, int]:
    """
    >>> filter_relative_clause(nlp('The cat that attacks us is scary.')[:])
    ([that, attacks, us], 2, 4)
    >>> filter_relative_clause(nlp('I like the person who was nice to me.')[:])
    ([who, was, nice, to, me], 4, 8)
    >>> filter_relative_clause(nlp('I hate the dog that bit me.')[:])
    ([that, bit, me], 4, 6)
    >>> filter_relative_clause(nlp('I like the bike that my father gave me.')[:])
    ([that, my, father, gave, me], 4, 8)
    """
    relative_clause: List[Token] = []
    start_idx = len(sentence)
    end_idx = 0
    for idx, token in enumerate(sentence):
        if token.is_punct:
            continue

        # handle relative clause of subject
        if token.dep_ == DependencyLabel.NOMINAL_SUBJECT.value:
            if token.tag_ == POSLabel.P_WH_DETERMINER.value:
                start_idx = idx
            elif token.tag_ == POSLabel.P_WH_PRONOUN.value:
                start_idx = idx
        # handle relative clause of object
        elif token.dep_ == DependencyLabel.DATIVE.value:
            if token.tag_ == POSLabel.P_WH_DETERMINER.value:
                start_idx = idx
        elif token.dep_ == DependencyLabel.ROOT.value:
            if idx > start_idx:
                break

        if idx >= start_idx:
            relative_clause.append(token)
            end_idx = idx

    return relative_clause, start_idx, end_idx


def remove_punctuations(sentence: List[Token]) -> List[Token]:
    """
    Remove punctuations (e.g. '.', '?') from the given sentence.

    Note: it also removes "-" from "work-from-home" as well ;(
    """
    print(f"before: {sentence}")
    return [token for token in sentence if not token.is_punct]


def remove_determiners(sentence: List[Token]) -> List[Token]:
    return [token for token in sentence if not token.dep_ == 'det']


def remove_unnecessary_tokens(sentence: List[Token]) -> List[Token]:
    """
    Remove unnecessary tokens which are punctuations and determiners
    from the given sentence.
    """
    result: List[Token] = []
    for token in sentence:
        if token.is_punct:
            continue
        elif token.dep_ == 'det':
            continue
        result.append(token)
    return result


def noun_phrase_to_adjectives(noun_phrase: Span) -> List[Token]:
    adjectives = []
    for idx, t in enumerate(noun_phrase):
        t: Token
        if idx == len(noun_phrase) - 1:
            break
        elif t.pos_ == POSLabel.U_DETERMINER.value:
            continue
        else:
            adjectives.append(t)
    return adjectives


if __name__ == '__main__':
    """
    Please run the following command if it's the first time you run this module.
    `python -m spacy download en_core_web_sm`
    """
    while True:
        text = input('text (hit enter to quit): ')
        if text == '':
            break
        doc: Doc = nlp(text)
        words = [token.lemma_ for token in doc]

        # Sentence detection
        sentences = list(doc.sents)

        for s in sentences:
            # displacy.serve(s, style='dep')
            print(f'\n{s}')
            print(f'| {"token.lemma_":^10} | {"token.pos_":^7} | {"token.tag_":^5} | {"token.dep_":^10} |')
            print('-------------------------------------------------------')
            new_s = _merge_token_by_entity(s)
            token: Token
            for token in new_s:
                if not token.is_punct:
                    print(f'| {token.lemma_:<12} | {token.pos_:<10} | {token.tag_:<10} | {token.dep_:<10} | {spacy.explain(token.dep_)}')
                    # print(f'  - {token.text} is a child of {[a.text for a in token.ancestors]}')
                    # if token.dep_ == 'ROOT':
                    #     print('  ', token.is_ancestor(token.nbor()), token.nbor(), token.is_ancestor(token.nbor(-1)), token.nbor(-1))
                    # try:
                    #     print(f'{token.text} has neighbor: {token.nbor(-1)}')
                    # except IndexError:
                    #     print(f'{token.text} has neighbor: {token.nbor()}')
            print()
            print(f'Is a question? {is_wh_question(new_s)}')
            print(f'Is a single word? {is_single_word(new_s)}')
            print(f'Is a phrase? {is_phrase(new_s)}')
            print(f'Is a complex sentence? {is_complex_sentence(new_s)}')
            print(f'filter relative clause: {filter_relative_clause(new_s)}')
            print(f'Is transitive sentence? {is_transitive_sentence(new_s)}')
            print(f'Is intransitive sentence? {is_intransitive_sentence(new_s)}')
            print(f'Is ditransitive sentence? {is_ditransitive_sentence(new_s)}')
            print(f'Is locative sentence? {is_locative_sentence(new_s)}')

            print(f'Noun phrase: {", ".join([str(n) for n in s.noun_chunks])}')

            new_np = retrieve_noun_phrases(new_s)
            print(f'[2] Noun phrase: {new_np}')
            # print(f'[3] NP types: {[[type(n) for n in np] for np in new_np]}')

        print('\nEntities')
        for ent in doc.ents:
            print(f'{ent.text} | {ent.label_} | {ent.start_char} | {ent.end_char}')

        print('=============================\n')

# token.tag_ can check plural
