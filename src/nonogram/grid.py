"""Representations for nonogram solutions."""

# TODO: Move this into an abstract class and build
#   additional implementations for sparse grids and cached bool_map grids.
class Nonogrid:
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

    def _inf_default_gen(self, iterator, default):
        # This is an **infinite** iterator and should *not* be used in a loop.
        yield from iterator
        while True:
            yield self._default_val if default is None else default

    def __init__(self, height, width, data=(), default_val=None):
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
        self._height, self._width = height, width
        self._default_val = default_val
        self._grid = []

        row_iter = self._inf_default_gen(data, [])
        for r in range(self.height):
            self._grid.append([None] * self.width)
            self.set_row(r, next(row_iter))

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

    def __repr__(self):
        return "".join((f"{type(self).__name__}(",
                        f"{self.height}, ",
                        f"{self.width}, ",
                        f"default_val={self._default_val}, ",
                        f"data={self._grid}, ",
                        f")"))

    def __str__(self):
        # TODO can I write a smart __str__ that makes a nice grid?
        return str([list(r) for r in self.rows()])

    def _validate_idx(self, idx):
        r, c = idx
        if not (0 <= r < self.height and 0 <= c < self.width):
            raise IndexError(f"Index (row={r}, col={c}) invalid for "
                             f"grid dimensions ()")
        return r, c

    def __getitem__(self, idx: tuple[int, int]):
        """Get value in the grid at `idx` ``(row,col)``."""
        r, c = self._validate_idx(idx)
        return self._grid[r][c]

    def __setitem__(self, idx: tuple[int, int], val):
        """Set value in the grid at `idx` ``(row,col)`` to `val`."""
        r, c = self._validate_idx(idx)
        self._grid[r][c] = val

    def get(self, r, c):
        """Get value in the grid at row `r` and column `c`."""
        return self[r, c]

    def set(self, r, c, itm):
        """Set value in the grid at row `r` and column `c` to `val`."""
        self[r, c] = itm

    def row(self, r):
        """Iterator over the row of values at a given index."""
        for c in range(self.width):
            yield self[r, c]

    def col(self, c):
        """Iterator over the row of values at a given index."""
        for r in range(self.height):
            yield self[r, c]

    def set_row(self, r, data, default_val=None):
        """Fill the row `r` with values from `data`.

        Parameters
        ----------
        r : int
            Index of the row to modify.
        data : Iterable
            Data to fill into the row.
            Truncated if `data` is too long, and padded with `default_val` if `data` is too short.
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
        data_iter = self._inf_default_gen(data, default_val)
        for c in range(self.width):
            self[r,c] = next(data_iter)

    def set_col(self, c, data, default_val=None):
        """Fill the column `c` with values from `data`.

        See :py:meth:`Nonogrid.set_row` for parameter details.
        """
        data_iter = self._inf_default_gen(next(data), default_val)
        for r in range(self.height):
            self[r,c] = next(data_iter)

    def rows(self):
        """Iterator over all rows in the grid."""
        for r in range(self.height):
            yield self.row(r)

    def cols(self):
        """Iterator over all columns in the grid."""
        for c in range(self.width):
            yield self.col(c)

    def __copy__(self):
        # TODO: If Nonogrid is subclassed, will this implementation cause problems?
        return Nonogrid(self.height, self.width, self.rows())

    # TODO: add __deepcopy__() method
