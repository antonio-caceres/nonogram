"""Representations for nonogram solutions."""

from abc import ABC, abstractmethod
from functools import wraps


class Nonogrid(ABC):
    """Fixed-size two-dimensional grid for developing and verifying a nonogram solution.

    Provide read-write access to individual elements by indexing on a tuple ``grid[r,c]``.

    Notes
    -----
    Indexing with a tuple provides numerous benefits, even though it is unintuitive for the user:

    - **Allows for flexibility in the implementation details.**
      For example, a nonogrid solving large, sparse nonograms should use a hashset instead.
    - Emphasizes that the individual elements are the only mutable pieces of the rows.
    - Enforces using the :py:meth:`~Nonogrid.row` and :py:meth:`~Nonogrid.col` methods for symmetry
      by not providing access to a row index.

    The methods :py:meth:`Nonogrid.row`, :py:meth:`Nonogrid.col`, :py:meth:`Nonogrid.rows`,
    and :py:meth:`Nonogrid.cols` all return iterators.

    - Returning a list could mislead users into thinking these methods can mutate the entire row.
    """

    def _infinite_generator(self, iterator, default=None):
        """Yield values from an iterator and then a default value ad infinitum.

        This is an **infinite** iterator and should *not* be used in a loop.

        Parameters
        ----------
        iterator : Iterator
            Yield values from `iterator` until it is empty.
        default : Any, default=None
            Yield `default` infinitely many times after `iterator` is emptied.
            Instead yield this instance's default value if `default` is ``None``.
        """
        yield from iterator
        while True:
            yield self._default_val if default is None else default

    def __init__(self, height, width, *, default_val=None):
        """Initialize a nonogrid and optionally fill in initial data.

        Parameters
        ----------
        height, width : int
            Height and width of the grid (which should match the dimensions of the nonogram).
        default_val : T, keyword, default=None
            Default value with which to fill in the initial grid.

        Notes
        -----
        Implementations of a :py:class:Nonogrid: define their own methods to input data.

        `default_val` is a keyword-only argument so subclasses can flexibly use
        positional arguments to get data in multiple different ways.
        """
        self._height, self._width = height, width
        self._default_val = default_val

    @classmethod
    def for_nonogram(cls, nonogram, *args, **kwargs):
        """Initialize a nonogrid with width and height matching the given nonogram.

        See :py:meth:`Nonogrid.__init__` for information on additional parameters.
        """
        return cls(nonogram.height, nonogram.width, *args, **kwargs)

    @property
    def height(self):
        """Number of rows in the nonogram grid."""
        return self._height

    @property
    def width(self):
        """Number of columns in the nonogram grid."""
        return self._width

    @property
    def dims(self):
        """Grid dimensions as a tuple *(height, width)*."""
        return self.height, self.width

    @staticmethod
    def _idx_validation(f):
        """Add an index validation checker to a method from a subclass of :py:class:`Nonogrid`.

        The function's first two arguments must be ``self`` and ``idx``,
        where ``self`` accepts an instance of the subclass and ``idx``
        accepts a 2-tuple ``(row, col)`` that is the index to access.

        Intended for use with consistency across subclasses' implementations
        of :py:meth:`Nonogrid.__getitem__` and :py:meth:`Nonogrid.__setitem__`
        """
        @wraps(f)
        def wrapper(self, idx, *args, **kwargs):
            r, c = idx
            if not (0 <= r < self.height and 0 <= c < self.width):
                raise IndexError(f"Index (row={r}, col={c}) invalid for "
                                 f"grid dimensions ()")
            return f(self, idx, *args, **kwargs)

        return wrapper

    @abstractmethod
    def __getitem__(self, idx: tuple[int, int]):
        """Get value in the grid at `idx` ``(row,col)``."""

    @abstractmethod
    def __setitem__(self, idx: tuple[int, int], val):
        """Set value in the grid at `idx` ``(row,col)`` to `val`."""

    def row(self, r):
        """Iterator over the row of values at a given index."""
        for c in range(self.width):
            yield self[r,c]

    def col(self, c):
        """Iterator over the row of values at a given index."""
        for r in range(self.height):
            yield self[r,c]

    def set_row(self, r, data, default_val=None):
        """Fill a row with values from an iterable.

        Parameters
        ----------
        r : int
            Index of the row to modify.
        data : Iterable
            Values to fill into the row.
            Truncated or padded with `default_val` if `data` provides the wrong number of values.
        default_val : optional, default=None
            Default value used to pad `data` to the correct length.
            If `default_val` is ``None``, falls back to the original default value
            provided in the Nonogrid's constructor.

        Notes
        -----
        If the nonogrid was provided a default value at initialization that is not ``None``,
        it is impossible to make ``None`` the default value in this method.
        This is a reasonable tradeoff so that solvers can pass in their preferred
        `default_val` at initialization and then forget it.
        If ``None`` is going to be a valid entry in a solver, we expect any reasonable use case
        to let ``None`` be the default value in the entire grid.
        """
        data_iter = self._infinite_generator(data, default_val)
        for c in range(self.width):
            self[r,c] = next(data_iter)

    def set_col(self, c, data, default_val=None):
        """Fill a column with values from an iterable.

        See :py:meth:`Nonogrid.set_row` for parameter details,
        replacing ``r`` with ``c`` and "row" with "column".
        """
        data_iter = self._infinite_generator(next(data), default_val)
        for r in range(self.height):
            self[r,c] = next(data_iter)

    def rows(self):
        """Iterate over all rows in the grid."""
        for r in range(self.height):
            yield self.row(r)

    def cols(self):
        """Iterate over all columns in the grid."""
        for c in range(self.width):
            yield self.col(c)

    def __repr__(self):
        return (f"{type(self).__name__}("
                f"{self.height}, "
                f"{self.width}, "
                f"default_val={self._default_val}"
                f")")


class NonogridArray(Nonogrid):
    """Nonogrid implemented with an data array."""

    def __init__(self, height, width, data=(), *, default_val=None):
        """Initialize a nonogrid and optionally fill in initial data.

        Parameters
        ----------
        height, width : int
            Height and width of the grid (which should match the dimensions of the nonogram).
        data : Iterable[Iterable[T]], optional, default=tuple()
            Set of values with which to initially fill in the grid.
            `data` is truncated or padded with `default_val` to match the given grid dimensions.
            Values are cast to booleans at verification.
        default_val : T, default=None
            Default value with which to fill in the initial grid.
        """
        super().__init__(height, width, default_val=default_val)
        self._grid = []

        row_iter = self._infinite_generator(data, [])
        for r in range(self.height):
            self._grid.append([None] * self.width)
            self.set_row(r, next(row_iter))

    @Nonogrid._idx_validation
    def __getitem__(self, idx: tuple[int, int]):
        r, c = idx
        return self._grid[r][c]

    @Nonogrid._idx_validation
    def __setitem__(self, idx: tuple[int, int], val):
        r, c = idx
        self._grid[r][c] = val

    def __copy__(self):
        return type(self)(self.height, self.width, self.rows(), default_val=self._default_val)

    # TODO: add __deepcopy__() method

    def __repr__(self):
        return (f"{type(self).__name__}("
                f"{self.height}, "
                f"{self.width}, "
                f"default_val={self._default_val}, "
                f"data={self._grid}"
                f")")

    def __str__(self):
        # TODO can I write a smart __str__ that makes a nice grid?
        return str([list(r) for r in self.rows()])

# TODO: Add implementation of Nonogrid for sparse grams.
