from enum import Enum

from mongoengine import *
from spacy.tokens import Token
from typing import List, Union, Optional

TSentence = List[Token]
TParagraph = List[TSentence]


class SignGloss(DynamicEmbeddedDocument):
    meta = {'allow_inheritance': True}
    gloss = StringField()
    lang = StringField()  # ISO 639-1 codes
    contexts = ListField()
    priority = FloatField(min_value=0, max_value=1)
    pos = StringField()

    def __repr__(self):
        return f'SignGloss(gloss={self.gloss})'


class Eng2Sign(Document):
    english = StringField(required=True)
    en_pos = StringField()
    contexts = ListField()
    sign_glosses = ListField(EmbeddedDocumentField(SignGloss))

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
            paragraph = []
            for sentence in self.thsl_translation[i]:
                paragraph.append(",".join(sentence))
            data.append({
                'p_number': i + 1,
                'original': self.original[i],
                'thsl_translation': paragraph
            })
        return data


class ThSLClassifier:

    def __init__(self, root_word: Token):
        self.root_word = root_word
        self.entity_label = root_word.ent_type_

    def __str__(self):
        return f'{self.root_word.lemma_}CL'

    def __repr__(self):
        return f'ThSLClassifier(root_word={self.root_word})'


class ThSLVerbPhrase:

    def __init__(
            self,
            verb: Token,
            subj_of_verb=None, dobj_of_verb=None, iobj_of_verb=None,
            dobj_phrase=None,
            direction=None
    ):
        self.verb = verb
        self.subject: Optional[Token] = subj_of_verb
        self.direct_obj: Optional[Token] = dobj_of_verb
        self.direct_obj_phrase: Optional[str] = dobj_phrase
        self.indirect_obj: Optional[Token] = iobj_of_verb
        self.direction: Optional[Token] = direction

    @property
    def root_verb(self):
        return self.verb

    @property
    def contexts(self) -> dict:
        contexts = {}
        if self.subject is not None:
            contexts['subject'] = self.subject
        if self.direct_obj is not None:
            contexts['direct_obj'] = self.direct_obj
        if self.direct_obj_phrase is not None:
            contexts['direct_obj_phrase'] = self.direct_obj_phrase
        if self.indirect_obj is not None:
            contexts['indirect_obj'] = self.indirect_obj
        if self.direction is not None:
            contexts['direction'] = self.direction

        return contexts

    def __repr__(self):
        return f'ThSLVerbPhrase(verb={self.verb.lemma_},ctx={self.contexts})'


class ThSLPrepositionPhrase:

    def __init__(self, prep: Token, prep_subj_cl: ThSLClassifier, prep_obj_cl: ThSLClassifier):
        self.preposition = prep
        self.preposition_subj_cl = prep_subj_cl
        self.preposition_obj_cl = prep_obj_cl

    def __str__(self):
        return '-'.join([
            str(self.preposition_subj_cl),
            self.preposition,
            str(self.preposition_obj_cl)
        ])

    def __repr__(self):
        return f'ThSLPrepositionPhrase({self.preposition_subj_cl},{self.preposition},{self.preposition_obj_cl})'


class ThSLNounPhrase:
    def __init__(self, noun: Token, adj_lst: Optional[List[Token]] = None):
        self.noun = noun
        self.adj_list = []

        if adj_lst is not None:
            self.adj_list = adj_lst

    def __repr__(self):
        return f'ThSLNounPhrase(noun={self.noun.lemma_},ctx={self.adj_list})'

    def add_adjectives(self, adj_lst: List[Token]):
        self.adj_list = self.adj_list + adj_lst


ThSLPhrase = Union[ThSLVerbPhrase, ThSLPrepositionPhrase, ThSLClassifier, ThSLNounPhrase]
