from enum import Enum


class EntityLabel(Enum):
    """
    https://towardsdatascience.com/explorations-in-named-entity-recognition-and-was-eleanor-roosevelt-right-671271117218
    https://spacy.io/usage/linguistic-features#named-entities
    """
    # from spacy
    TIME = 'TIME'
    DATE = 'DATE'
    ORGANIZATION = 'ORG'
    OTHER_LOCATION = 'LOC'
    GEOGRAPHIC_LOCATION = 'GPE'


class DependencyLabel(Enum):
    """
    Dependency relation from Spacy (token.dep_)

    ClearNLP / Universal Dependencies:
    https://github.com/clir/clearnlp-guidelines/blob/master/md/specifications/dependency_labels.md
    """
    ADJECTIVAL_CLAUSE = "acl"
    ADJECTIVAL_COMPLEMENT = "acomp"
    ADVERBIAL_CLAUSE_MODIFIER = "advcl"
    ADVERBIAL_MODIFIER = "advmod"
    AGENT = "agent"
    ADJECTIVAL_MODIFIER = "amod"
    APPOSITIONAL_MODIFIER = "appos"
    ATTRIBUTE = "attr"
    AUXILIARY = "aux"
    AUXILIARY_PASSIVE = "auxpass"
    CASE_MARKING = "case"
    COORDINATING_CONJUNCTION = "cc"
    CLAUSAL_COMPLEMENT = "ccomp"
    CLASSIFIER = "clf"
    COMPOUND = "compound"
    CONJUNCT = "conj"
    COPULA = "cop"
    CLAUSAL_SUBJECT = "csubj"
    CLAUSAL_SUBJECT_PASSIVE = "csubjpass"
    DATIVE = "dative"
    UNCLASSIFIED_DEPENDENT = "dep"
    DETERMINER = "det"
    DISCOURSE_ELEMENT = "discourse"
    DISLOCATED_ELEMENTS = "dislocated"
    DIRECT_OBJECT = "dobj"
    EXPLETIVE = "expl"
    FIXED_MULTIWORD_EXPRESSION = "fixed"
    FLAT_MULTIWORD_EXPRESSION = "flat"
    GOES_WITH = "goeswith"
    INTERJECTION = "intj"
    LIST = "list"
    MARKER = "mark"
    META_MODIFIER = "meta"
    NEGATION_MODIFIER = "neg"
    NOMINAL_SUBJECT = "nsubj"
    NOMINAL_SUBJECT_PASSIVE = "nsubjpass"
    MODIFIER_OF_NOMINAL = "nounmod"
    NOUN_PHRASE_AS_ADVERBIAL_MODIFIER = "npmod"
    NUMERIC_MODIFIER = "nummod"
    OBJECT_PREDICATE = "oprd"
    OBJECT = "obj"
    OBLIQUE_NOMINAL = "obl"
    ORPHAN = "orphan"
    PARATAXIS = "parataxis"
    COMPLEMENT_OF_PREPOSITION = "pcomp"
    OBJECT_OF_PREPOSITION = "pobj"
    POSSESSION_MODIFIER = "poss"
    PRE_CORRELATIVE_CONJUNCTION = "preconj"
    PREPOSITIONAL_MODIFIER = "prep"
    PARTICLE = "prt"
    PUNCTUATION = "punct"
    MODIFIER_OF_QUANTIFIER = "quantmod"
    RELATIVE_CLAUSE_MODIFIER = "relcl"
    OVERRIDDEN_DISFLUENCY = "reparandum"
    ROOT = "ROOT"
    VOCATIVE = "vocative"
    OPEN_CLAUSAL_COMPLEMENT = "xcomp"

    # deprecated labels
    DEP_MODIFIER_OF_NOMINAL = "nmod"
    DEP_NOUN_PHRASE_AS_ADVERBIAL_MODIFIER = "npadvmod"
    DEP_RELATIVE_CLAUSE_MODIFIER = "rcmod"
    DEP_COMPLEMENTIZER = "complm"
    DEP_INFINITIVAL_MODIFIER = "infmod"
    DEP_PARTICIPAL_MODIFIER = "partmod"
    DEP_MODIFIER_IN_HYPHENATION = "hmod"
    DEP_HYPHEN = "hyph"
    DEP_INDIRECT_OBJECT = "iobj"
    DEP_NUMBER_MODIFIER = "num"
    DEP_NUMBER_COMPOUND_MODIFIER = "number"
    DEP_NOUN_COMPOUND_MODIFIER = "nn"
    DEP_POSSESSIVE_MODIFIER = "possessive"


class POSLabel(Enum):
    """
    Part-of-speech tags from Universal POS tags and OntoNotes 5 / Penn Treebank

    Universal POS tags:
    https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html

    OntoNotes 5 / Penn Treebank POS tags
    https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    """

    # coarse-grained pos tag from Universal POS
    U_ADJECTIVE = 'ADJ'
    U_ADPOSITION = 'ADP'
    U_ADVERB = 'ADV'
    U_AUXILIARY = 'AUX'
    U_COORDINATING_CONJUNCTION = 'CCONJ'
    U_DETERMINER = 'DET'
    U_INTERJECTION = 'INTJ'
    U_NOUN = 'NOUN'
    U_NUMERAL = 'NUM'
    U_PARTICLE = 'PART'
    U_PRONOUN = 'PRON'
    U_PROPER_NOUN = 'PROPN'
    U_PUNCTUATION = 'PUNCT'
    U_SUBORDINATING_CONJUNCTION = 'SCONJ'
    U_SYMBOL = 'SYM'
    U_VERB = 'VERB'
    U_OTHER = 'X'

    # fine-grained pos tag from Penn Treebank
    P_CO_CONJUNCTION = 'CC'
    P_CARDINAL_NUMBER = 'CD'
    P_DETERMINER = 'DT'
    P_EXISTENTIAL_THERE = 'EX'
    P_FOREIGN_WORD = 'FW'
    P_PERP_OR_SUB_CON = 'IN'
    P_ADJECTIVE = 'JJ'
    P_COMPARATIVE_ADJECTIVE = 'JJR'
    P_SUPERLATIVE_ADJECTIVE = 'JJS'
    P_LIST_ITEM = 'LS'
    P_MODAL = 'MD'
    P_SINGULAR_NOUN = 'NN'
    P_PLURAL_NOUN = 'NNS'
    P_SINGULAR_PROPER_NOUN = 'NNP'
    P_PLURAL_PROPER_NOUN = 'NNPS'
    P_PREDETERMINER = 'PDT'
    P_POSSESSIVE_ENDING = 'POS'
    P_PERSONAL_PRONOUN = 'PRP'
    P_POSSESSIVE_PRONOUN = 'PRP$'
    P_ADVERB = 'RB'
    P_COMPARATIVE_ADVERB = 'RBR'
    P_SUPERLATIVE_ADVERB = 'RBS'
    P_PARTICLE = 'RP'
    P_SYMBOL = 'SYM'
    P_TO = 'TO'
    P_INTERJECTION = 'UH'
    P_VERB_BASE_FORM = 'VB'
    P_VERB_PAST_TENSE = 'VBD'
    P_VERB_PRESENT_PARTICIPLE = 'VBG'
    P_VERB_PAST_PARTICIPLE = 'VBN'
    P_VERB_NON3RD_PERSON_SINGULAR_PRESENT = 'VBP'
    P_VERB_3RD_PERSON_SINGULAR_PRESENT = 'VBZ'
    P_WH_DETERMINER = 'WDT'
    P_WH_PRONOUN = 'WP'
    P_POSSESSIVE_WH_PRONOUN = 'WP$'
    P_WH_ADVERB = 'WRB'


class ThSLClassifier(Enum):
    LOCATION_CL = 'locCL'
    THING_CL = 'thingCL'
    SUBJECT_CL = 'subjCL'
