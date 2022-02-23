from itertools import chain, combinations


def powerset(iterable, no_empty=False):
    """
    https://docs.python.org/3/library/itertools.html#itertools-recipes
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    s = list(iterable)
    if no_empty:
        return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))
