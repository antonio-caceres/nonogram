import itertools
from unittest import TestCase

from nonogram.core import Nonoclue


class Initialization(TestCase):
    def test_basic_init(self):
        full_clue = list(range(1, 6))
        for i in range(1, len(full_clue) + 1):
            clue = full_clue[:i]
            with self.subTest(init_arg=clue, as_args=False):
                self.assertEqual(Nonoclue(clue).clue, clue)
            with self.subTest(init_arg=clue, as_args=True):
                self.assertEqual(Nonoclue(*clue).clue, clue)

    def test_remove_zeros(self):
        exp_clue = [i * 2 + 1 for i in range(5)]
        init_arg = [i if i % 2 == 1 else 0 for i in range(11)]
        self.assertEqual(Nonoclue(init_arg).clue, exp_clue)

    def test_from_mixed(self):
        exp_clue = list(range(1, 11))
        init_args = [0, 1, [2, 3, 4], 0, 0, 5, (6, 0, 7, 0), range(8, 10), 10]
        self.assertEqual(Nonoclue(*init_args).clue, exp_clue)


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
