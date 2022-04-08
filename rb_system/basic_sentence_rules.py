from typing import List, Union
from models.models import *
from spacy.tokens import Token, Span
from rb_system.nlp_tools import *
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


def br1_transitive_sentence(sentence: TSentence) -> List[Union[str, ThSLPhrase]]:
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
    # ending_marker = 'nodding'
    subject: TempToken = None
    direct_object: TempToken = None
    verb: TempToken = None
    for idx, token in enumerate(sentence):
        if token.dep_ == DependencyLabel.NOMINAL_SUBJECT.value:
            subject = token
        elif token.dep_ == DependencyLabel.DIRECT_OBJECT.value:
            direct_object = token
        elif token.tag_ == POSLabel.P_VERB_PRESENT_PARTICIPLE.value:
            # gerund is considered as obj
            direct_object = token
        elif token.pos_ == POSLabel.U_VERB.value:
            # collect verb idx here
            verb = token

    assert subject is not None, '[b1] Sentence must contain subject'
    assert verb is not None, '[b1] Sentence must contain verb'
    assert direct_object is not None, '[b1] Sentence must contain direct object'

    thsl_subject = ThSLNounPhrase(noun=subject)
    thsl_dobj = ThSLNounPhrase(noun=direct_object)
    noun_phrases = retrieve_noun_phrases(sentence)
    for np in noun_phrases:
        np: Span
        if subject.text in str(np):
            adj_lst = noun_phrase_to_adjectives(np)
            thsl_subject.add_adjectives(adj_lst)
        elif direct_object.text in str(np):
            adj_lst = noun_phrase_to_adjectives(np)
            thsl_dobj.add_adjectives(adj_lst)

    thsl_verb = ThSLVerbPhrase(verb=verb, subj_of_verb=subject, dobj_of_verb=direct_object)
    if thsl_subject.noun.lemma_ == POSLabel.U_PRONOUN.value:
        if thsl_dobj.noun.lemma_ == 'I':
            # if it's the action toward "I" -> omit "me" and put "me" as a verb context
            thsl_sentence = [thsl_subject, thsl_verb]
        else:
            # Use SOV when S is pronoun
            thsl_sentence = [thsl_subject, thsl_dobj, thsl_verb]
    else:
        # Use SOV when S is pronoun, else use OSV
        thsl_sentence = [thsl_dobj, thsl_subject, thsl_verb]

    return thsl_sentence


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

    thsl_subject = ThSLNounPhrase(noun=subject)
    noun_phrases = retrieve_noun_phrases(sentence)
    for np in noun_phrases:
        np: Span
        if subject.text in str(np):
            adj_lst = noun_phrase_to_adjectives(np)
            thsl_subject.add_adjectives(adj_lst)

    thsl_verb = ThSLVerbPhrase(verb=root, subj_of_verb=subject)
    thsl_sentence = [thsl_subject, thsl_verb]
    return thsl_sentence


# TODO: use ThSLNounPhrase
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


# TODO: use ThSLNounPhrase
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


# TODO: append WH at the end of the translated sentence
def cf3_question(ori_sentence: TSentence, trans_sentence: List[Union[str, ThSLPhrase]]):
    """
    pg.111
    """
    wh: str = ori_sentence[0].lemma_
    trans_sentence.append(wh.upper())
    print("==>", trans_sentence)
    return trans_sentence.append(wh.upper())

# TODO: define the rules for all types of sentence
# I got the kids their favorite toys.
