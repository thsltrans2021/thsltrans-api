from mongoengine import *
from spacy.tokens import Token
from typing import List

# TODO: define models for request, response, and db
"""
Request body of the endpoint `add_words()`
{
    "data": [
        {
            "word": "I",
            "glosses": [
                {
                    "gloss": "Pron1",
                    "lang": "US"
                },
                {
                    "gloss": "ฉัน",
                    "lang": "TH"
                }
            ],
            "en_pos": "1st personal pronoun"
        }
    ]
}
"""
TSentence = List[Token]
TParagraph = List[TSentence]


class SignGloss(DynamicEmbeddedDocument):
    meta = {'allow_inheritance': True}
    gloss = StringField()
    # country code alpha-2
    lang = StringField()


class Eng2Sign(Document):
    english = StringField(required=True)
    en_pos = StringField()
    contexts = ListField()
    sign_glosses = EmbeddedDocumentField(SignGloss)

    meta = {
        'collection': 'eng2signs'
    }


class TextData:
    """
    :ivar original: A list of the paragraphs of English text
    :ivar processed_data: A list of the processed English sentences.
    :ivar thsl_translation: A list of ThSL sentences, each sentence contains a list of ThSL words.
    """

    def __init__(self, original=None):
        """
        :param original: a list of the paragraphs of English sentences
        """
        if original is None:
            original = []
        self.original: List[str] = original
        # [[[Hello], [This, is, your, friend, A.]], [[Minna, hit, Joe, when, the, teacher, turned]]]
        self.processed_data: List[TParagraph] = []
        self.thsl_translation: List[List[List[str]]] = []

    def __str__(self):
        text = ''
        for idx, p in enumerate(self.original):
            text += f'p{idx + 1}: {p}\n'
        return f'*----- Original text -----*\n{text}'

    def prepare_response_data(self) -> List[dict]:
        data = []
        for i in range(len(self.thsl_translation)):
            data.append({
                'p_number': i + 1,
                'original': self.original[i],
                'thsl_translation': self.thsl_translation[i]
            })
        return data
