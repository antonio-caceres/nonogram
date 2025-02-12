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
