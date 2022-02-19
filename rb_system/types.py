from enum import Enum


class EntityLabel(Enum):
    """
    https://towardsdatascience.com/explorations-in-named-entity-recognition-and-was-eleanor-roosevelt-right-671271117218
    https://spacy.io/usage/linguistic-features#named-entities
    """
    TIME = 'TIME'
    DATE = 'DATE'
    ORGANIZATION = 'ORG'
    OTHER_LOCATION = 'LOC'
    GEOGRAPHIC_LOCATION = 'GPE'
