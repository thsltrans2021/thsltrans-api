import spacy
from spacy.tokens import Doc, Token
from spacy import Language

"""
token.tag_ --> ptb tag set, see: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
token.pos_ --> Universal POS tags
"""
# TODO: consider using in-mem cache when matching doc with sign gloss


if __name__ == '__main__':
    nlp: Language = spacy.load('en_core_web_sm')
    doc: Doc = nlp('Apple is looking at buying U.K. startup for $1 billion.')
    words = [token.lemma_ for token in doc ]
    print(words)

    token: Token
    for token in doc:
        print(f'{token.lemma_:<10}{token.pos_:<7}{token.tag_}')
