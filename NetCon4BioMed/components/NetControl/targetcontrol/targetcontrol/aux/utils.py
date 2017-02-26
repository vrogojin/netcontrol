"""Set theoretic utility functions."""

from __future__ import division

from random import choice, sample


def generate_id():
    """Generate a random ID made up of lowercase letters and digits."""
    symbols = "0123456789abcdefghijklmnopqrstuvwxyz"
    return "".join(choice(symbols) for _ in range(8))


def has_duplicates(xs):
    """Check whether a list contains duplicates."""
    return len(set(xs)) != len(xs)


def subsets(xs):
    """Return the subsets of an iterable.

    This is a recursive implementation, avoid using it for large
    iterables.
    """
    xs = list(xs)
    if xs == []:
        return [set()]
    x = xs.pop()
    ys = subsets(xs)
    return ys + [y | {x} for y in ys]


def sublists(xs):
    """Generate the sublists of a given iterable.

    This is a recursive implementation, avoid using it for large
    iterables.
    """
    xs = list(xs)
    if xs == []:
        return [[]]
    x = xs.pop()
    ys = sublists(xs)
    return ys + [y + [x] for y in ys]


def maximal(xs, lt=lambda x, y: x <= y):
    """Return the maximal elements from an iterable.

    The default comparator is the 'less than or equal to' operator,
    which stands for inclusion in the case of sets.

    This function is slow for large inputs.
    """
    xs = list(xs)
    ret = []
    for x in xs:
        if any([lt(x, y) for y in ret]):  # not maximal
            continue
        ret = [y for y in ret if not lt(y, x)] + [x]
    return ret


# =======
# package tests
# ==============

def test_subsets():
    """Test 'subsets'."""
    S = [1, 2, 3, 4]
    P_S = subsets(S)
    print '### <subsets>'
    print 'S =', S
    print 'P(S) =', P_S
    print '2^' + str(len(S)) + ' = ' + str(len(P_S)) + ' subsets'
    print


def test_sublists():
    """Test 'sublists'."""
    S = [1, 2, 3, 4]
    P_S = sublists(S)
    print '### <sublists>'
    print 'S =', S
    print 'P(S) =', P_S
    print '2^' + str(len(S)) + ' = ' + str(len(P_S)) + ' subsets'
    print


def test_maximal():
    """Test 'maximal'."""
    X = sample(subsets(range(7)), 37)
    Y = maximal(X)
    print '### <maximal>'
    # check that Y \subseteq X
    if all([y in X for y in Y]):
        print '[Pass]'
    else:
        print '[Fail]: output is not asubset of the input'
    if all([not (y <= x) or y == x for y in Y for x in X]):
        print '[Pass]'
    else:
        print '[Fail]: some elements are not maximal'
    if all([any([x <= y for y in Y]) for x in X]):
        print '[Pass]'
    else:
        print '[Fail]: some maximal elements are not in the output'
    print


# execute tests when run as a script
if __name__ == '__main__':
    test_subsets()
    test_sublists()
    test_maximal()
    print 'done'
