from mongoengine import *
from typing import List

# TODO: define models for request, response, and db
"""
Request body of the endpoint `add_words()`
{
    "data": [
        {
            "word": "ant",
            "gloss_en": "ANT",
            "gloss_th": "มด",
            "context": ""
        }
    ]
}
"""


class SignGloss(DynamicEmbeddedDocument):
    meta = {'allow_inheritance': True}
    gloss_en = StringField()


class Eng2Sign(Document):
    english = StringField(required=True)
    context = StringField()
    sign_glosses = EmbeddedDocumentField(SignGloss)

    meta = {
        'collection': 'eng2signs'
    }


class TextData:
    def __init__(self, original=None):
        """
        :param original: a list of English sentences
        translation: [["ANT", "WALK"], [...]]
        """
        if original is None:
            original = []
        self.original = original
        self.translation = []

    def __str__(self):
        text = ''
        for idx, p in enumerate(self.original):
            text += f'p{idx + 1}: {p}\n'
        return f'*----- Original text -----*\n{text}'

    def prepare_response_data(self) -> List[dict]:
        data = []
        for i in range(len(self.translation)):
            data.append({
                'p_number': i + 1,
                'original': self.original[i],
                'translation': self.translation[i]
            })
        return data
