from typing import List, Union
from api.models import TSentence
from spacy.tokens import Token

"""
Symbols from the ThSL research
(+|-)   optional
(+)     required
"""

TempToken = Union[Token, None]


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
    verb = f'{subject.lemma_}-{root.lemma_}'
    return [subject.lemma_, verb]


def br3_ditransitive_sentence(sentence: TSentence) -> List[str]:
    """
    Rearrange the input text according to the grammar rule #3 (p.81)
    of a basic sentence.

    (1) SDiT = (+|-)S (+|-)DO (+|-)S (+)V
    (1) SDiT = (+|-)S (+|-)DO (+)[S1-V-doCL-IndirectObject] -> Mother gives me THB40 ('me' is indirect object)
    (2) SDiT = (+|-)S (+)V (+|-)DO

    Note: doCL = the classifier of the direct object
    """
    # if the subject is a name of sth. -> should state subject twice
    return ['Rule 3', ' '.join([token.lemma_ for token in sentence])]

# TODO: define the rules for all types of sentence
