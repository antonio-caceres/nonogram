
import itertools
from unittest import TestCase

from nonogram.gram import Nonoclue
from nonogram.solve.utils import ClueSolutions


class Initialization(TestCase):
    def test_clue(self):
        target_lengths = [2, 4, 8]
        for clue_arg in itertools.product([3, 5, 9], repeat=3):
            nonoclue = Nonoclue(clue_arg)
            for l in target_lengths:
                self.assertEqual(ClueSolutions(nonoclue, l).clue, nonoclue)

    def test_clue_casting(self):
        for clue_arg in ([4, 5, 7],
                         (3, 4),
                         [],
                         [0, 0]):
            with self.subTest(clue_arg=clue_arg):
                self.assertEqual(ClueSolutions(clue_arg, 1).clue, Nonoclue(clue_arg))

    def test_target_len(self):
        for target_len in range(11):
            for clue in (Nonoclue(), Nonoclue([3, 9, 2])):
                self.assertEqual(ClueSolutions(clue, target_len).target_length, target_len)

    def test_repr(self):
        for l in range(5):
            for clue_arg in itertools.product([1, 5, 10], repeat=3):
                nonoclue = Nonoclue(clue_arg)
                self.assertEqual(repr(ClueSolutions(nonoclue, l)),
                                 f"ClueSolutions({repr(nonoclue)}, {l})")


class NumSolutionCalculations(TestCase):
    def test_empty_clue(self):
        for l in range(1, 11):
            self.assertEqual(len(ClueSolutions([], l),), 1)

    def test_too_short(self):
        for clue in ([1, 1, 1],
                     [10],
                     [7, 1, 3]):
            for l in range(sum(clue) + len(clue) - 1):
                with self.subTest(clue=clue, target_length=l):
                    self.assertEqual(len(ClueSolutions(clue, l)), 0)

    def test_exact_fit(self):
        for l in range(1, 6):
            # T = 2 cases
            self.assertEqual(len(ClueSolutions(l, l)), 1)

    def test_len(self):
        for clue, l, exp_count in (
                ([1, 1, 1], 5, 1),
                ([1, 1, 1], 7, 10),
                ([5], 10, 6),
                ([2, 3], 10, 15),
        ):
            self.assertEqual(len(ClueSolutions(clue, l)), exp_count)
