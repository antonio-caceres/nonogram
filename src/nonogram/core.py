"""Classes for representing and solving nonograms."""

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


class Nonoclue:
    """A clue to either a row or column of a nonogram puzzle.

    Takes the form of a sequence of integers.
    A clue of the form *(a, b, c)* imposes exactly lines of length *a*, *b*, and *c* filled
    squares separated by at least one empty square.

    Represents the clue *(0)* (all squares empty) as the empty list ``[]`` to minimize edge cases
    for the solver.
    """

    @staticmethod
    def _init_clue(stack):
        """Initialize a clue with a stack (LIFO).

        This implementation recurses on iterables in *args that contain iterables,
        but the user shouldn't assume that functionality.
        """
        clue = []

        while stack:
            itm = stack.pop()
            try:
                # test for integer conversion before iteration because of strings
                num = int(itm)
                if num < 0:
                    raise ValueError("Negative numbers are not valid clues.")
                if num > 0:  # 0 is a valid clue that is equivalent to an empty clue, so ignore.
                    clue.append(num)
            except TypeError:
                stack += reversed(itm)  # handle lists from low-index to high-index

        return clue


    def __init__(self, *args):
        """Create a nonoclue by concatenating any iterables in `*args` into a list of integers.

        Can concatenate iterables of integers in `*args` with integers in `*args`.

        Raises
        ------
        ValueError
            If any integer in the nonoclue is negative.
        """
        # The container list ensures *args is reversed on the stack.
        self.clue: list[int] = Nonoclue._init_clue([args])

    def __len__(self):
        """Number of continuous lines of filled-in squares in the clue."""
        return len(self.clue)

    def __repr__(self):
        return f"{type(self).__name__}({self.clue})"

    def __getitem__(self, key):
        return self.clue[key]

    @staticmethod
    def _bool_iter(sequence):
        for itm in sequence:
            yield bool(itm)
        yield False

    def satisfied_by(self, sequence):
        """Determine if a boolean sequence satisfies the nonoclue.

        Parameters
        ----------
        sequence : Sequence[T]
            Iterable over objects to match to squares.

        Returns
        -------
        If the clue's constraints are satisfied by `sequence`.

        Notes
        -----
        - Nonoclues themselves do not impose a total length.
        """
        cur_hint = 0
        line = 0

        # TODO: Fail this as early as possible.
        # DepTODO: Provide additional context around where it fails.
        for square in Nonoclue._bool_iter(sequence):
            line += square
            if not square and line > 0:  # non-empty line finished
                if (cur_hint == len(self) or  # line should not exist
                        line != self[cur_hint]):
                    return False
                cur_hint += 1
                line = 0

        # Did we see all the expected lines?
        return cur_hint == len(self)


class Nonogram:
    """The row clues and column clues that form a nonogram puzzle."""
    # TODO: Write fitting algorithm to call as a static method.

    @staticmethod
    def _init_clues(clue_seq):
        clues = [elem if isinstance(elem, Nonoclue) else Nonoclue(elem) for elem in clue_seq]

        start_idx, end_idx = 0, len(clues)
        while start_idx < end_idx and not clues[start_idx]:
            start_idx += 1
        while end_idx > start_idx and not clues[end_idx - 1]:
            end_idx -= 1

        return clues[start_idx:end_idx]

    def __init__(self, rows, cols):
        """Initialize a nonogram with a sequence of row clues and a sequence of column clues.

        Does not verify if the requirements that the clues impose have a valid solution.

        Parameters
        ----------
        rows, cols : Iterable[:py:class:`Nonoclue`]
            Clues imposed by the rows and the columns.
            Initialization removes empty nonoclues at the beginning and end of the gram
            and casts all elements to instances of :py:class:`Nonoclue`.

        Notes
        -----
        Doing any (even trivial) checks on `rows` and `cols` might misleadingly
        suggest that the class can know if a set of clues has a valid solution.

        Better to defer all solution verification to the solver.
        """
        self.rows, self.cols = Nonogram._init_clues(rows), Nonogram._init_clues(cols)

    @property
    def width(self):
        """Total number of columns (i.e., number of squares in a row)."""
        return len(self.cols)

    @property
    def height(self):
        """Total number of rows (i.e., number of squares in a column)."""
        return len(self.rows)

    @property
    def dims(self):
        """Nonogram dimensions as a tuple *(height, width)*."""
        return self.height, self.width

    @property
    def num_clues(self):
        """Total number of clues in the nonogram."""
        return self.width + self.height

    def __repr__(self):
        return f"{type(self).__name__}({self.rows}, {self.cols})"

    @staticmethod
    def _clue_sat_count(clues, data_iter):
        """Determine how many clues an iterator over data satisfies.

        Any fitting to `clues` and `data_iter` should be handled before calling this method.

        Raises
        ------
        ValueError
            If the lengths of `clues` and `data_iter` do not match.
        """
        zipped = zip(clues, data_iter, strict=True)
        return sum(clue.satisfied_by(line) for clue, line in zipped)

    def satisfied_count(self, grid):
        """Determine how many clues in the nonogram are satisfied by a nonogrid.

        Parameters
        ----------
        grid : Nonogrid
            Grid to be evaluated as a solution to the nonogram.

        Raises
        ------
        ValueError
            If the height and width of the grid and nonogram do not match.
        """
        if self.dims != grid.dims:
            raise ValueError(f"Dimensions (height, width) of grid {grid.dims} "
                             f"do not match nonogram {self.dims}.")

        row_clue_count = Nonogram._clue_sat_count(self.rows, grid.rows())
        col_clue_count = Nonogram._clue_sat_count(self.cols, grid.cols())
        return row_clue_count + col_clue_count


    def satisfied_by(self, grid):
        """Determine if a nonogrid satisfies the nonogram.

        Parameters
        ----------
        grid : Nonogrid
            Two-dimensional array of objects to match to squares.

        Returns
        -------
        If all row clue and column clue constraints are satisfied by `solution`.

        Raises
        ------
        ValueError
            If the height and width of the grid and nonogram do not match.

        See Also
        --------
        :py:meth:`Nonogram.satisfied_count`
        """
        return self.satisfied_count(grid) == self.num_clues
