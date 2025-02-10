import itertools
from unittest import TestCase

from nonogram.core import Nonoclue


_CASES_LINISH = 5  # number of test cases plus-minus one
_CASES_EXPISH = 5  # if number of cases grow exponentially


class EmptyNonoclue(TestCase):
    def test_initialization(self):
        for clue in [[0] * i for i in range(_CASES_LINISH)]:
            with self.subTest(init_arg=clue):
                self.assertEqual(Nonoclue(clue).clue, [])

    def test_satisfied(self):
        for sol in itertools.product((False, True), repeat=_CASES_EXPISH):
            with self.subTest(sequence=sol):
                self.assertEqual(Nonoclue([]).satisfied_by(sol),
                                 not any(sol))
