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


def _gen_getter_lambdas():
    """Generate callables to test getter interfaces for a nonogrid."""
    return [("__getitem__", lambda grid, r, c: grid[r, c]),
            (".get", lambda grid, r, c: grid.get(r, c))]


def _gen_setter_lambdas():
    """Generate callables to test setter interfaces for a nonogrid."""
    return [("__setitem__", lambda grid, r, c, itm: grid.__setitem__((r, c), itm)),
            (".set", lambda grid, r, c, itm: grid.set(r, c, itm))]


class GridAccess(TestCase):
    # 0 should not be in the grid because it is falsey and we compare against False.
    SQUARE_DATA = [[1, 2, 3, 4, 5],
                   [6, 7, 8, 9, 10],
                   [11, 12, 13, 14, 15],
                   [16, 17, 18, 19, 20],
                   [21, 22, 23, 24, 25]]

    def _verify_against_data(self, grid, bounds, getter, exp_default):
        for r, c in itertools.product(range(bounds[0]), range(bounds[1])):
            if r >= len(GridAccess.SQUARE_DATA) or c >= len(GridAccess.SQUARE_DATA):
                self.assertEqual(getter(grid, r, c), exp_default)
            else:
                self.assertEqual(getter(grid, r, c), GridAccess.SQUARE_DATA[r][c])

    def test_small_grid_access(self):
        max_side = len(GridAccess.SQUARE_DATA)
        for desc, getter in _gen_getter_lambdas():
            for exp_height, exp_width in itertools.product(range(max_side), range(max_side)):
                with self.subTest(getter=desc, height=exp_height, width=exp_width):
                    grid = Nonogrid(exp_height, exp_width, GridAccess.SQUARE_DATA)
                    self._verify_against_data(grid, (exp_height, exp_width), getter, None)

    def test_default_val(self):
        side_len = len(GridAccess.SQUARE_DATA) + 1
        for desc, getter in _gen_getter_lambdas():
            for args in [(side_len, side_len, GridAccess.SQUARE_DATA),
                         (side_len, side_len, GridAccess.SQUARE_DATA, False)]:
                exp_default = None if len(args) < 4 else args[3]
                with self.subTest(getter=desc, default_val=exp_default):
                    grid = Nonogrid(*args)
                    self._verify_against_data(grid, (side_len, side_len), getter, exp_default)


class InvalidAccess(TestCase):
    @staticmethod
    def _callable_iter_sym(grid, coord_range, fixed_pt):
        for x in coord_range:
            for _, getter in _gen_getter_lambdas():
                yield lambda: getter(grid, x, fixed_pt)
                yield lambda: getter(grid, fixed_pt, x)
            for _, setter in _gen_setter_lambdas():
                yield lambda: setter(grid, x, fixed_pt, None)
                yield lambda: setter(grid, fixed_pt, x, None)

    def test_invalid_negative(self):
        grid = Nonogrid(0, 0)
        for f in InvalidAccess._callable_iter_sym(grid, (-2, 0), 0):
            self.assertRaises(IndexError, f)

    def test_invalid_outside(self):
        arg_height, arg_width = 1, 1
        grid = Nonogrid(arg_height, arg_width)
        for f in InvalidAccess._callable_iter_sym(grid,
                                                  (arg_height, arg_height + 3),
                                                  0):
            self.assertRaises(IndexError, f)
