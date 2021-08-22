import spacy
from spacy.tokens import Doc, Token
from spacy import Language
from api.models import TextData

"""
token.tag_ --> ptb tag set, see: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
token.pos_ --> Universal POS tags, see: https://universaldependencies.org/u/pos/
"""
# TODO: consider using in-memory cache when matching doc with sign gloss

nlp: Language = spacy.load('en_core_web_sm')


def perform_nlp_process(text_data: TextData):
    """
    Perform necessary NLP such as part-of-speech tagging and dependency parsing.
    """
    # Split paragraph into a list of sentences
    for paragraph in text_data.original:
        p_doc: Doc = nlp(paragraph)
        sentence = list(p_doc.sents)
        text_data.processed_data.append(sentence)


def contain_transitive_verb(sentence: str) -> bool:
    # a children node of a verb contains dobj
    # https://stackoverflow.com/questions/49271730/how-to-parse-verbs-using-spacy
    return False


if __name__ == '__main__':
    """
    Please run the following command if it's the first time you run this module.
    `python -m spacy download en_core_web_sm`
    """
    while True:
        text = input('text: ')
        if text == '':
            break
        doc: Doc = nlp(text)
        words = [token.lemma_ for token in doc]
        print()

        # Sentence detection
        sentences = list(doc.sents)
        for s in sentences:
            print(s)
            token: Token
            for token in s:
                if not token.is_punct:
                    print(f'{token.lemma_:<10}{token.pos_:<7}{token.tag_:<5}{token.dep_:<10}{spacy.explain(token.dep_)}')

            print(f'Noun phrase: {", ".join([str(n) for n in s.noun_chunks])}')
            print()
        print('----------------------------')

# dobj: A direct object is a noun phrase that is the accusative object of a (di)transitive verb
