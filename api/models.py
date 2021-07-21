from mongoengine import *

# TODO: define models for request, response, and db


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
