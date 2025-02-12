from unittest import TestCase

from nonogram.core import Nonogrid


class BasicPropertyInitialization(TestCase):
    def test_dims(self):
        arg_height, arg_width = 1, 2
        result = Nonogrid(arg_height, arg_width)
        self.assertEqual(result.dims, (arg_height, arg_width))
        self.assertEqual(result.height, arg_height)
        self.assertEqual(result.width, arg_width)

    def test_map_default(self):
        result = Nonogrid(0, 0)
        self.assertEqual(result.bool_map, bool)

    def test_custom_map(self):
        f = lambda: True
        result = Nonogrid(0, 0, bool_map=f)
        self.assertEqual(result.bool_map, f)
