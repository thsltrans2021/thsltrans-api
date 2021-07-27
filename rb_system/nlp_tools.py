import spacy
from spacy.tokens import Doc, Token
from spacy import Language
from api.models import TextData

"""
token.tag_ --> ptb tag set, see: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
token.pos_ --> Universal POS tags, see: https://universaldependencies.org/u/pos/
"""
# TODO: consider using in-mem cache when matching doc with sign gloss


def perform_nlp_process(text_data: TextData) -> Doc:
    """
    Perform necessary NLP such as part-of-speech tagging and dependency parsing.
    """
    pass


if __name__ == '__main__':
    nlp: Language = spacy.load('en_core_web_sm')

    while True:
        text = input('text: ')
        if text == '':
            break
        doc: Doc = nlp(text)
        words = [token.lemma_ for token in doc]
        print()
        print(words)

        token: Token
        for token in doc:
            print(f'{token.lemma_:<10}{token.pos_:<7}{token.tag_:<7}{token.dep_}')
        print('----------------------------')
