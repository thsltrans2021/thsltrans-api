from typing import List
from spacy.tokens import Span, Token

"""
Symbols from the ThSL research
(+|-)   optional
(+)     required
"""


def br1_transitive_sentence(text: Span) -> List[str]:
    """
    Rearrange the input text according to the grammar rule #1 (p.80)
    of a basic sentence.

    Type 1:
        (1) ST = (+|-)S (+|-)O (+)V
        (2) ST = (+|-)S (+)V (+|-)O

    Type 2:
        ST = (+|-)S (+)[S - V - O]
    """
    return ['Rule 1', str(text)]


# TODO: define the rules for all types of sentence
