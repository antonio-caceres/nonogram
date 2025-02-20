import itertools
from unittest import TestCase

from nonogram.core import Nonoclue




class InitializationErrors(TestCase):
    def test_negatives(self):
        clue = [0] * 5
        for i in range(len(clue)):
            # test multiple negative numbers at multiple different positions
            clue[i] = -(i + 1)
            with self.subTest(init_arg=clue):
                self.assertRaises(ValueError, Nonoclue, clue)


class EmptyNonoclue(TestCase):
    def test_initialization(self):
        self.assertEqual(Nonoclue([]).clue, [])
        self.assertEqual(Nonoclue([0]).clue, [])
        self.assertEqual(Nonoclue([0, 0, 0]).clue, [])

    def test_satisfied(self):
        for sol in itertools.product((False, True), repeat=4):
            with self.subTest(sequence=sol):
                self.assertEqual(Nonoclue([]).satisfied_by(sol),
                                 not any(sol))
