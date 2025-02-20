
import itertools
from unittest import TestCase

from nonogram.core import Nonoclue

from .utils import NonogramDatasetLoader as Loader


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


class DunderMethods(TestCase):
    def setUp(self):
        self.all_cases = []
        full_clue = list(range(1, 6))
        for i in range(1, len(full_clue) + 1):
            clue = full_clue[:i]
            self.all_cases.append((Nonoclue(clue), clue))

    def test_len(self):
        for clue, lst in self.all_cases:
            self.assertEqual(len(clue), len(lst))

    def test_repr(self):
        for clue, lst in self.all_cases:
            self.assertEqual(repr(clue), f"Nonoclue({lst})")

    def test_getitem(self):
        for clue, lst in self.all_cases:
            for i, x in enumerate(lst):
                self.assertEqual(clue[i], lst[i])


class SatisfiedBy(TestCase):
    def setUp(self):
        basic_grams = Loader.BASIC.load()["data"]
        self.all_cases = set()  # remove duplicate clues across nonograms
        for gram in basic_grams:
            row_clues = gram["clues"]["row"]
            col_clues = gram["clues"]["col"]
            solution = gram["sol"]
            # turn all of the lists into tuples so they are hashable
            for i, clue in enumerate(row_clues):
                row = tuple(solution[i])
                self.all_cases.add((tuple(clue), row))
            for j, clue in enumerate(col_clues):
                col = tuple([solution[i][j] for i in range(len(solution))])
                self.all_cases.add((tuple(clue), col))

    def test_satisfied_by(self):
        for clue, sol in self.all_cases:

            with self.subTest(clue=clue, sequence=sol):
                self.assertTrue(Nonoclue(clue).satisfied_by(sol))
