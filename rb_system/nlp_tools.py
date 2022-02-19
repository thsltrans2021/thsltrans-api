from spacy import Language
from spacy.tokens import Token, Doc
from models.models import TextData, TParagraph
from typing import List, Tuple
from rb_system.types import EntityLabel

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
            print(f"sentence_token: {sentence_token}")
            processed_paragraph.append(sentence_token)
        text_data.processed_data.append(processed_paragraph)


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
    if is_ditransitive_sentence(sentence):
        return False

    has_direct_object = False
    gerund_ancestors: List[Token] = []
    token: Token
    for token in sentence:
        if token.dep_ == 'dobj':
            has_direct_object = True
        elif (token.tag_ == 'VBG') and (token.dep_ != 'ROOT'):
            gerund_ancestors = list(token.ancestors)

    if has_direct_object:
        return True
    elif len(gerund_ancestors) > 0:
        # check if verb is followed by gerund
        a: Token
        for a in gerund_ancestors:
            if a.dep_ == 'ROOT':
                return True
    return False


def is_intransitive_sentence(sentence: List[Token]) -> bool:
    """
    >>> is_intransitive_sentence(nlp('Hello')[:])
    False
    >>> is_intransitive_sentence(nlp('She eats an apple.')[:])
    False
    >>> is_intransitive_sentence(nlp('The mouse asked.')[:])
    True
    >>> is_intransitive_sentence(nlp('The chickens walk.')[:])
    True
    """
    if len(sentence) <= 1:
        return False
    return not is_transitive_sentence(sentence) and not is_ditransitive_sentence(sentence)


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
    """
    # My mother taught me how to cook. (still failed)
    has_direct_object = False
    has_dative = False
    dobj_count = 0
    if len(sentence) < 3:
        return False
    for token in sentence:
        dep_relation = token.dep_
        if dep_relation == 'ROOT':
            # John bought me a phone.
            next_token: Token = token.nbor()
            if next_token.dep_ == 'dative':
                return True
        elif dep_relation == 'dative':
            has_dative = True
        elif dep_relation == 'dobj':
            has_direct_object = True
            dobj_count += 1
    return has_direct_object and has_dative or dobj_count > 1


def is_single_word(sentence: List[Token]) -> bool:
    """
    True if the given sentence contains one word.
    """
    print(f"sentence '{sentence}': {len(sentence)}")
    return len(sentence) == 1


def is_locative_sentence(sentence: List[Token]):
    """
    True if the given sentence is locative sentence.
    Locative sentence means that the sentence indicates place or direction.

    try detect preposition of place and check if it's actually talking about place (not time)
    - Check prepositional noun that comes after the preposition

    >>> is_locative_sentence(nlp('He works at Kasetsart University.')[:])
    True
    >>> is_locative_sentence(nlp('Mother is at home.')[:])
    True
    >>> is_locative_sentence(nlp('There is a plate of rice on the table.')[:])
    True
    >>> is_locative_sentence(nlp('She buys 3 apples.')[:])
    False
    >>> is_locative_sentence(nlp('I meet him at home on Sunday')[:])
    True
    >>> is_locative_sentence(nlp('She works on Monday')[:])
    False
    """
    prep_phrases: List[Tuple[Token, Token]] = []
    current_prep = None

    for i in range(len(sentence)):
        token: Token = sentence[i]
        if token.dep_ == 'prep' or token.tag_ == 'IN':
            current_prep = token
        elif token.dep_ == 'pobj':
            prep_phrases.append((current_prep, token))

    prep_phrases_of_place = _filter_preposition_of_place(prep_phrases)
    # print(prep_phrases)
    # print(prep_phrases_of_place)
    return len(prep_phrases_of_place) > 0


def _filter_preposition_of_place(prep_phrases: List[Tuple[Token, Token]]):
    """
    Returns a list of preposition phrases that are not considered as prepositional phrase of time.
    """
    if len(prep_phrases) < 1:
        return []

    entity_types = [EntityLabel.DATE, EntityLabel.TIME]
    result_prep_phrases: List[Tuple[Token, Token]] = []
    for prep_p in prep_phrases:
        try:
            entity_label = EntityLabel(prep_p[1].ent_type_)
            if entity_label in entity_types:
                continue
            result_prep_phrases.append(prep_p)
        except ValueError:
            result_prep_phrases.append(prep_p)

    return result_prep_phrases


def has_org_entity(sentence: List[Token]) -> bool:
    org_entities = retrieve_entities(sentence, [EntityLabel.ORGANIZATION])
    return len(org_entities) > 0


def retrieve_entities(sentence: List[Token], entity_types: List[EntityLabel]) -> List[Tuple[str, str]]:
    """
    Returns a list of the detected entities with their labels

    >>> test_sentence = nlp('He works at Kasetsart University.')[:]
    >>> retrieve_entities(test_sentence, [EntityLabel.ORGANIZATION])
    [('Kasetsart', 'ORG'), ('University', 'ORG')]

    >>> test_sentence = nlp('He works at Kasetsart University and Apple on Monday')[:]
    >>> retrieve_entities(test_sentence, [EntityLabel.ORGANIZATION])
    [('Kasetsart', 'ORG'), ('University', 'ORG'), ('Apple', 'ORG')]

    >>> test_sentence = nlp('He works at Kasetsart University and Apple on Monday')[:]
    >>> retrieve_entities(test_sentence, [EntityLabel.ORGANIZATION, EntityLabel.DATE])
    [('Kasetsart', 'ORG'), ('University', 'ORG'), ('Apple', 'ORG'), ('Monday', 'DATE')]
    """
    if len(entity_types) == 0:
        return [(token.text, token.ent_type_) for token in sentence]

    entities: List[Tuple[str, str]] = []
    for token in sentence:
        try:
            entity_label = EntityLabel(token.ent_type_)
            if entity_label in entity_types:
                entities.append((token.text, token.ent_type_))
        except ValueError:
            continue

    return entities


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
            token: Token
            for token in s:
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
            print(f'Is transitive sentence? {is_transitive_sentence(s)}')
            print(f'Is intransitive sentence? {is_intransitive_sentence(s)}')
            print(f'Is ditransitive sentence? {is_ditransitive_sentence(s)}')
            print(f'Is locative sentence? {is_locative_sentence(s)}')
            print(f'Noun phrase: {", ".join([str(n) for n in s.noun_chunks])}')

        print('\nEntities')
        for ent in doc.ents:
            print(f'{ent.text} | {ent.label_} | {ent.start_char} | {ent.end_char}')

        print('=============================\n')

# token.tag_ can check plural
