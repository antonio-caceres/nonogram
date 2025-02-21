
import itertools
from unittest import TestCase

from nonogram.grid import NonogridArray


class BasicPropertyInitialization(TestCase):
    def test_dims(self):
        exp_height, exp_width = 1, 2
        grid = NonogridArray(exp_height, exp_width)
        self.assertEqual(grid.dims, (exp_height, exp_width))
        self.assertEqual(grid.height, exp_height)
        self.assertEqual(grid.width, exp_width)

    def test_data_input_dims(self):
        max_side = 2 * 2
        data = [[None] * (max_side // 2)] * (max_side // 2)

        for exp_height, exp_width in itertools.product(range(max_side), range(max_side)):
            with self.subTest(height=exp_height, width=exp_width):
                grid = NonogridArray(exp_height, exp_width, data)
                self.assertEqual(grid.dims, (exp_height, exp_width))


def _verify_against_data(testcase, data, bounds, grid, exp_default):
    for r, c in itertools.product(range(bounds[0]), range(bounds[1])):
        if r >= len(data) or c >= len(data[0]):
            testcase.assertEqual(grid[r, c], exp_default)
        else:
            testcase.assertEqual(grid[r, c], data[r][c])


class GridAccess(TestCase):
    # 0 should not be in the grid because it evaluates to False, which we compare against.
    SQUARE_DATA = [[1, 2, 3, 4, 5],
                   [6, 7, 8, 9, 10],
                   [11, 12, 13, 14, 15],
                   [16, 17, 18, 19, 20],
                   [21, 22, 23, 24, 25]]

    def test_small_grid_access(self):
        max_side = len(GridAccess.SQUARE_DATA)
        for exp_height, exp_width in itertools.product(range(max_side), range(max_side)):
            with self.subTest(height=exp_height, width=exp_width):
                grid = NonogridArray(exp_height, exp_width, GridAccess.SQUARE_DATA)
                _verify_against_data(self,
                                     GridAccess.SQUARE_DATA,
                                     (exp_height, exp_width),
                                     grid,
                                     None)

    def test_default_val(self):
        side_len = len(GridAccess.SQUARE_DATA) + 1
        init_args = (side_len, side_len, GridAccess.SQUARE_DATA)
        verify_args = (self, GridAccess.SQUARE_DATA, (side_len, side_len))
        with self.subTest(default_val=None):
            grid = NonogridArray(*init_args)
            _verify_against_data(*verify_args, grid, exp_default=None)
        with self.subTest(default_val=False):
            grid = NonogridArray(*init_args, default_val=False)
            _verify_against_data(*verify_args, grid, exp_default=False)


class GridManipulation(TestCase):
    def test_change_values(self):
        ...


class InvalidAccess(TestCase):
    @staticmethod
    def _grid_set(grid, r, c, val):
        grid[r, c] = val

    @staticmethod
    def _callable_iter_sym(grid, coord_range, fixed_pt):
        for x in coord_range:
            yield lambda: grid[x, fixed_pt]
            yield lambda: grid[fixed_pt, x]
            yield lambda: InvalidAccess._grid_set(grid, x, fixed_pt, None)
            yield lambda: InvalidAccess._grid_set(grid, fixed_pt, x, None)

    def test_invalid_negative(self):
        grid = NonogridArray(0, 0)
        for f in InvalidAccess._callable_iter_sym(grid, (-2, 0), 0):
            self.assertRaises(IndexError, f)

    def test_invalid_outside(self):
        arg_height, arg_width = 1, 1
        grid = NonogridArray(arg_height, arg_width)
        for f in InvalidAccess._callable_iter_sym(grid,
                                                  (arg_height, arg_height + 3),
                                                  0):
            self.assertRaises(IndexError, f)
