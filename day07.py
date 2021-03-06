"""
http://adventofcode.com/2017/day/7
"""

import collections
import re

import pytest


TEST = """\
pbga (66)
xhth (57)
ebii (61)
havc (66)
ktlj (57)
fwft (72) -> ktlj, cntj, xhth
qoyq (66)
padx (45) -> pbga, havc, qoyq
tknk (41) -> ugml, padx, fwft
jptl (61)
ugml (68) -> gyxo, ebii, jptl
gyxo (61)
cntj (57)
"""


def oddity(iterable, key=None):
    """
    Find the element that is different.

    The iterable has at most one element different than the others.   If a
    `key` function is provided, it is a function used to extract a comparison
    key from each element, otherwise the elements themselves are compared.

    Two values are returned: the common comparison key, and the different
    element.

    If all of the elements are equal, then the returned different element is
    None.  If there is more than one different element, an error is raised.

    """
    if key is None:
        key = lambda v: v
    summary = collections.defaultdict(list)
    for element in iterable:
        summary[key(element)].append(element)

    if len(summary) == 1:
        k, _ = summary.popitem()
        return k, None
    elif len(summary) == 2:
        common, different = list(summary.items())
        if len(common[1]) == 1:
            common, different = different, common
        return common[0], different[1][0]
    else:
        raise ValueError("Wrong number of distinct values")

@pytest.mark.parametrize("iterable, key, answer", [
    ("aaaaba", None, ("a", "b")),
    ("aaaaaa", None, ("a", None)),
    ([10, 11, 12, 23, 14, 10], lambda v: v // 10, (1, 23)),
])
def test_oddity(iterable, key, answer):
    assert oddity(iterable, key) == answer

@pytest.mark.parametrize("iterable, key", [
    ("aaaaaabc", None),
    ("", None),
])
def test_oddity_error(iterable, key):
    with pytest.raises(ValueError):
        oddity(iterable, key)


class Towers:
    def __init__(self):
        self.weights = {}
        self.supporting = {}

    def read(self, lines):
        for line in lines:
            m = re.search(r"^(\w+) \((\d+)\)(?: -> (.*))?$", line)
            if m:
                name, weight, supporting = m.groups()
                self.weights[name] = int(weight)
                if supporting:
                    self.supporting[name] = supporting.split(", ")

    def bottom_program(self):
        bottoms = set(name for name in self.weights if not any(name in v for v in self.supporting.values()))
        assert len(bottoms) == 1
        return bottoms.pop()

    def total_weight(self, program):
        weight = self.weights[program]
        weight += sum(w for w, p in self.supporting_weights(program))
        return weight

    def supporting_weights(self, program):
        for support in self.supporting.get(program, ()):
            yield self.total_weight(support), support

    def imbalance(self, program=None, goal=0):
        """Find the program with the wrong weight, return the name and correct weight."""
        if program is None:
            program = self.bottom_program()
        weights = list(self.supporting_weights(program))
        if len(weights) == 0:
            odd = None
        else:
            common, odd = oddity(weights, key=lambda pair: pair[0])
        if odd is None:
            # My children (if any) are balanced, i'm the problem
            return program, goal - common * len(weights)
        else:
            # Children are different.
            if len(weights) == 2:
                new_goal = (goal - self.weights[program]) // len(weights)
                if weights[0][0] == new_goal:
                    return weights[1][1]
                else:
                    return weigths[0][1]
            else:
                return self.imbalance(odd[1], common)


@pytest.fixture
def test_towers():
    towers = Towers()
    towers.read(TEST.splitlines())
    return towers

def test_bottom_program(test_towers):
    assert test_towers.bottom_program() == "tknk"

def test_total_weight(test_towers):
    assert test_towers.total_weight('ugml') == 251

def test_imbalance(test_towers):
    assert test_towers.imbalance() == ('ugml', 60)


if __name__ == '__main__':
    with open("day07_input.txt") as finput:
        towers = Towers()
        towers.read(finput)

    bottom = towers.bottom_program()
    print(f"Part 1: the bottom program is {bottom}")

    who, how_much = towers.imbalance()
    print(f"Part 2: {who} should be {how_much} to balance")
