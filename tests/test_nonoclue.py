import itertools
from unittest import TestCase

from nonogram.core import Nonoclue


class EmptyNonoclue(TestCase):
    _NUM_CASES_ISH = 10  # number of test cases plus-minus one

    def test_initialization(self):
        for clue in [[0] * i for i in range(3)]:
            with self.subTest(init_arg=clue):
                self.assertEqual(Nonoclue(clue).clue, [])

    def test_satisfied_true(self):
        for sol in [[0] * i for i in range(self._NUM_CASES_ISH)]:
            with self.subTest(sequence=sol):
                self.assertTrue(Nonoclue([]).satisfied_by(sol))

    def test_satisfied_false(self):
        sols = [[1] * i for i in range(1, self._NUM_CASES_ISH)]
        for i in range(self._NUM_CASES_ISH):
            base = [0] * self._NUM_CASES_ISH
            base[i] = 1
            sols.append(base)
        for sol in sols:
            with self.subTest(sequence=sol):
                self.assertFalse(Nonoclue([]).satisfied_by(sol))
