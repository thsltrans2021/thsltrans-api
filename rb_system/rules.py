from typing import List, Union
from api.models import TSentence
from spacy.tokens import Token, Span

"""
Symbols from the ThSL research
(+|-)   optional
(+)     required
"""

TempToken = Union[Token, None]
TempSpan = Union[Span, None]


def br1_transitive_sentence(sentence: TSentence) -> List[str]:
    """
    Rearrange the input text according to the grammar rule #1 (p.80)
    of a basic sentence.

    Type 1:
        (1) ST = (+|-)S (+|-)O (+)V
        (2) ST = (+|-)S (+)V (+|-)O

    Type 2:
        ST = (+|-)S (+)[S - V - O]

    Type 3:
        ST = (+)O (+|-)S (+)[S - V - O]
    """
    return ['Rule 1', ' '.join([token.lemma_ for token in sentence])]


def br2_intransitive_sentence(sentence: TSentence) -> List[str]:
    """
    Rearrange the input text according to the grammar rule #2 (p.81)
    of a basic sentence.

    SInT = (+)S (+)[S - V]
    """
    subject: TempToken = None
    root: TempToken = None
    for idx, token in enumerate(sentence):
        try:
            if idx > 0 and token.dep_ == 'ROOT':
                subject = token.nbor(-1)
                root = token
        except IndexError:
            continue
    assert subject is not None, '[b2] Sentence must contain subject'
    assert root is not None, '[b2] Sentence must contain verb'
    verb = f'{subject.lemma_}-{root.lemma_}'
    return [subject.lemma_, verb]


def br3_ditransitive_sentence(sentence: TSentence) -> List[str]:
    """
    Rearrange the input text according to the grammar rule #3 (p.81)
    of a basic sentence.

    (1) SDiT = (+|-)S (+|-)DO (+)V
        SDiT = (+|-)DO (+|-)S (+)V
    (2) SDiT = (+|-)S (+|-)DO (+)[S-V-doCL-IndirectObject] -> Mother gives me THB40 ('me' is indirect object)

    Note: doCL = the classifier of the direct object
    """
    # dative that follows ROOT -> indirect object
    # the second dobj -> real direct object
    # if the subject is a name of sth. -> should state subject twice
    subject: TempToken = None
    direct_object_str = ''
    indirect_object: TempToken = None
    root: TempToken = None
    sentence_span: TempSpan = None
    for token in sentence:
        if token.dep_ == 'ROOT':
            sentence_span = token.sent
            root = token
            break
    noun_phrases = [[t for t in span] for span in sentence_span.noun_chunks]
    for idx, np in enumerate(noun_phrases):
        # TODO: should we cut possessive modifiers (e.g. 'my', 'her', 'him') out?
        if idx > 1:
            direct_object_str = ' '.join([t.lemma_ for t in np if t.dep_ != 'det'])
            break
        for token in np:
            if token.dep_ == 'nsubj':
                subject = token
            elif token.dep_ == 'dative':
                indirect_object = token
    assert direct_object_str != '', '[b3] Sentence must contain indirect object'
    assert indirect_object is not None, '[b3] Sentence must contain direct object'
    # TODO: choose CL for the direct object
    dobj_cl = 'thingCL'
    # TODO: classify whether the pronoun is first or third person
    verb = f'{subject.lemma_}-{root.lemma_} {dobj_cl}-{indirect_object.lemma_}'
    return [subject.lemma_, direct_object_str, verb]


def br4_locative_sentence(sentence: TSentence) -> List[str]:
    return ['Rule 4', ' '.join([token.lemma_ for token in sentence])]

# TODO: define the rules for all types of sentence
# I got the kids their favorite toys.
