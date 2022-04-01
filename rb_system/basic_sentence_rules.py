from typing import List, Union
from models.models import TSentence, ThSLClassifier, ThSLPhrase, ThSLPrepositionPhrase, ThSLVerbPhrase
from spacy.tokens import Token, Span
from rb_system.nlp_tools import retrieve_preposition_phrases, filter_preposition_of_place
from rb_system.types import DependencyLabel, POSLabel, EntityLabel

"""
This code contains rules of basic simple sentence structure (the obligatory part of ThSL sentence).
Simple sentence is a sentence that doesn't have conjunction.

Symbols from the ThSL research
(+|-)   optional
(+)     required
"""

TempToken = Union[Token, None]
TempSpan = Union[Span, None]


def br0_single_word(sentence: TSentence) -> List[str]:
    return [token.lemma_ for token in sentence]


def br0_phrase(sentence: TSentence) -> List[str]:
    phrase = [' '.join(token.lemma_ for token in sentence)]
    return phrase


def br1_transitive_sentence(sentence: TSentence) -> List[str]:
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


def br2_intransitive_sentence(sentence: TSentence) -> List[Union[str, ThSLPhrase]]:
    """
    Rearrange the input text according to the grammar rule #2 (p.81)
    of a basic sentence.

    SInT = (+)S (+)[S - V]
    """
    subject: TempToken = None
    root: TempToken = None
    for idx, token in enumerate(sentence):
        try:
            if idx > 0 and token.dep_ == DependencyLabel.ROOT.value:
                subject = token.nbor(-1)
                root = token
        except IndexError:
            continue
    assert subject is not None, '[b2] Sentence must contain subject'
    assert root is not None, '[b2] Sentence must contain verb'
    verb = ThSLVerbPhrase(verb=root, subj_of_verb=subject)
    thsl_sentence = [subject.lemma_, verb]
    return thsl_sentence


def br3_ditransitive_sentence(sentence: TSentence) -> List[Union[str, ThSLPhrase]]:
    """
    Rearrange the input text according to the grammar rule #3 (p.81)
    of a basic sentence.

    (1) SDiT = (+|-)S (+|-)DO (+)V   -> want to identify subject
        SDiT = (+|-)DO (+|-)S (+)V

    (2) SDiT = (+|-)S (+|-)DO (+)[S-V-doCL-IndirectObject] -> Mother gives me THB40 ('me' is indirect object)

    Note: verb of this type of sentence already describes subject and indirect object
    Note: doCL = the classifier of the direct object
    """
    # dative that follows ROOT -> indirect object
    # the second dobj -> real direct object
    # if the subject is a name of sth. -> should state subject twice
    subject: TempToken = None
    direct_object: TempToken = None
    indirect_object: TempToken = None
    root: TempToken = None
    quantity: TempToken = None

    for token in sentence:
        if token.dep_ == DependencyLabel.NOMINAL_SUBJECT.value:
            subject = token
        elif token.dep_ == DependencyLabel.ROOT.value:
            root = token
        elif token.dep_ == DependencyLabel.DIRECT_OBJECT.value:
            direct_object = token
        elif token.dep_ == DependencyLabel.DATIVE.value:
            indirect_object = token
        elif token.ent_type_ == EntityLabel.CARDINAL.value:
            quantity = token

    assert subject is not None, '[b3] Sentence must contain subject'
    assert root is not None, '[b3] Sentence must contain verb'
    assert direct_object is not None, '[b3] Sentence must contain direct object'
    assert indirect_object is not None, '[b3] Sentence must contain indirect object'

    # TODO: add more context for multiple types of `give` (e.g. give to many ppl)
    verb = ThSLVerbPhrase(subj_of_verb=subject, verb=root, iobj_of_verb=indirect_object, dobj_of_verb=direct_object)
    thsl_sentence = [direct_object.lemma_, verb]

    if quantity is not None:
        thsl_sentence.insert(0, quantity.lemma_)

    # if subj is not Pron, explicitly specify subject
    if subject.pos_ != POSLabel.U_PRONOUN.value:
        thsl_sentence.insert(0, subject.lemma_)

    # print("new b3 --> ", thsl_sentence)
    return thsl_sentence


def br4_locative_sentence(sentence: TSentence) -> List[Union[str, ThSLPhrase]]:
    """
    Rearrange the input text according to the grammar rule #4 (p.83)
    of a basic sentence.

    Slocative = (+)Location (+)S (+)Vlocative

    "I work at Kasesart University.",
            "Mother is at home.",
    """
    set_scene = False
    special_prep = ['in', 'on', 'under']
    subject: TempToken = None
    root: TempToken = None
    prep: TempToken = None

    prep_phrases = retrieve_preposition_phrases(sentence)
    prep_phrases_of_place = filter_preposition_of_place(prep_phrases)
    assert len(prep_phrases_of_place) < 2, f'[b4] Expected to find 1 perp phrase but found {len(prep_phrases_of_place)}'
    location = prep_phrases_of_place[0][1]

    for token in sentence:
        if token.dep_ == DependencyLabel.ROOT.value:
            root = token
        elif token.dep_ == DependencyLabel.NOMINAL_SUBJECT.value:
            subject = token
        elif token.lemma_ in special_prep:
            set_scene = True
            prep = token

    assert subject is not None, '[b4] Sentence must contain subject'

    thsl_sentence: List[Union[str, ThSLClassifier]]
    if set_scene:
        location_classifier = ThSLClassifier(location)
        subject_classifier = ThSLClassifier(subject)
        thsl_sentence = [
            location.lemma_, location_classifier,
            subject.lemma_, subject_classifier,
            ThSLPrepositionPhrase(prep, subject_classifier, location_classifier),
        ]
    else:
        thsl_sentence = [location.lemma_, subject.lemma_, root.lemma_]

    return thsl_sentence

# TODO: define the rules for all types of sentence
# I got the kids their favorite toys.
