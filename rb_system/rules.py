from typing import List
from rb_system.types import Sentence

"""
Symbols from the ThSL research
(+|-)   optional
(+)     required
"""


def br1_transitive_sentence(sentence: Sentence) -> List[str]:
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


def br2_intransitive_sentence(sentence: Sentence) -> List[str]:
    """
    Rearrange the input text according to the grammar rule #2 (p.81)
    of a basic sentence.

    SInT = (+)S (+)[S - V]

    """
    return ['Rule 2', ' '.join([token.lemma_ for token in sentence])]

# TODO: define the rules for all types of sentence
