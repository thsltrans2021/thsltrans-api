from mongoengine import *
from typing import List
from spacy.tokens import Span

# TODO: define models for request, response, and db
"""
Request body of the endpoint `add_words()`
{
    "data": [
        {
            "word": "ant",
            "gloss_en": "ANT",
            "gloss_th": "มด",
            "contexts": [""]
        }
    ]
}
"""


class SignGloss(DynamicEmbeddedDocument):
    meta = {'allow_inheritance': True}
    gloss_en = StringField()


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
        self.processed_data: List[List[Span]] = []
        self.thsl_translation: List[List[str]] = []

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
