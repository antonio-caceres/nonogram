import itertools
from unittest import TestCase

from nonogram.core import Nonogrid


class BasicPropertyInitialization(TestCase):
    def test_dims(self):
        exp_height, exp_width = 1, 2
        grid = Nonogrid(exp_height, exp_width)
        self.assertEqual(grid.dims, (exp_height, exp_width))
        self.assertEqual(grid.height, exp_height)
        self.assertEqual(grid.width, exp_width)

    def test_data_input_dims(self):
        max_side = 2 * 2
        data = [[None] * (max_side // 2)] * (max_side // 2)

        for exp_height, exp_width in itertools.product(range(max_side), range(max_side)):
            with self.subTest(height=exp_height, width=exp_width):
                grid = Nonogrid(exp_height, exp_width, data)
                self.assertEqual(grid.dims, (exp_height, exp_width))

    def test_map_default(self):
        grid = Nonogrid(0, 0)
        self.assertEqual(grid.bool_map, bool)

    def test_custom_map(self):
        f = lambda: True
        grid = Nonogrid(0, 0, bool_map=f)
        self.assertEqual(grid.bool_map, f)


class GridAccess(TestCase):
    SQUARE_DATA = [[0, 1, 2, 3, 4],
                   [5, 6, 7, 8, 9],
                   [10, 11, 12, 13, 14],
                   [15, 16, 17, 18, 19],
                   [20, 21, 22, 23, 24]]

    def test_small_grid_access(self):
        max_side = len(GridAccess.SQUARE_DATA)
        for exp_height, exp_width in itertools.product(range(max_side), range(max_side)):
            with self.subTest(height=exp_height, width=exp_width):
                grid = Nonogrid(exp_height, exp_width, GridAccess.SQUARE_DATA)
                for r, c in itertools.product(range(exp_height), range(exp_width)):
                    self.assertEqual(grid[r, c], GridAccess.SQUARE_DATA[r][c])
                    self.assertEqual(grid.get(r, c), GridAccess.SQUARE_DATA[r][c])

    def test_invalid_negative(self):
        grid = Nonogrid(0, 0)
        for r in range(-2, 0):
            self.assertRaises(IndexError, lambda: grid[r, 0])
            self.assertRaises(IndexError, grid.get, r, 0)
        for c in range(-2, 0):
            self.assertRaises(IndexError, lambda: grid[0, c])
            self.assertRaises(IndexError, grid.get, 0, c)

    def test_invalid_outside(self):
        arg_height, arg_width = 1, 1
        grid = Nonogrid(arg_height, arg_width)
        for r in range(arg_height, arg_height + 3):
            self.assertRaises(IndexError, lambda: grid[r, 0])
            self.assertRaises(IndexError, grid.get, r, 0)
        for c in range(arg_width, arg_width + 3):
            self.assertRaises(IndexError, lambda: grid[0, c])
            self.assertRaises(IndexError, grid.get, 0, c)
        
