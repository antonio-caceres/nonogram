"""Classes for representing and solving nonograms."""


class Nonogrid:
    """Fixed-size two-dimensional grid for developing and verifying a nonogram solution.

    Provide read-write access to individual elements by indexing on a tuple ``grid[r,c]``.

    Notes
    -----
    Indexing with a tuple provides numerous benefits, even though it is unintuitive for the user:

    - **Allows for flexibility in the implementation details.**
      For example, a nonogrid solving large, sparse nonograms should use a hashset instead.
    - Emphasizes that the individual elements are the only mutable pieces of the rows.
    - Enforces using the :attr:`~Nonogrid.row` and :attr:`~Nonogrid.col` methods for symmetry
      by not providing access to a row index.

    The methods :attr:`Nonogrid.row`, :attr:`Nonogrid.col`, :attr:`Nonogrid.rows`,
    and :attr:`Nonogrid.cols` all return iterators.

    - Returning a list could mislead users into thinking these methods can mutate the
    """

    def _inf_default_gen(self, iterator, default):
        # This is an **infinite** iterator and should *not* be used in a loop.
        yield from iterator
        while True:
            yield self._default_val if default is None else default

    def __init__(self, height, width, data=(), default_val=None, bool_map=bool):
        """Initialize a nonogrid and optionally fill in initial data.

        Parameters
        ----------
        height, width : int
            Height and width of the grid (which should match the dimensions of the nonogram).
        data : Sequence[Sequence[T]], optional, default=tuple()
            Set of values with which to initially fill in the grid.
            `data` is truncated or padded with `default_val` to match the given grid dimensions.
            Values are mapped to booleans at verification using `bool_map`.
        default_val : T, default=None
            Default value with which to fill in the initial grid.
        bool_map : Callable[[T], bool], default=bool
            Return whether a grid value represents a filled or empty square.
        """
        self._width, self._height = width, height
        self._default_val = default_val
        self._bool_map = bool_map
        # We need the dimensions of the grid to be ready for the calls to set_row.
        self._grid = [[None] * self.width] * self.height

        row_iter = self._inf_default_gen(data, [])
        for r in range(self.height):
            self.set_row(r, next(row_iter))

    @classmethod
    def for_nonogram(cls, nonogram, *args, **kwargs):
        """Initialize a nonogrid with width and height matching the given nonogram.

        See :attr:`Nonogrid.__init__` for information on additional parameters.
        """
        return cls(nonogram.height, nonogram.width, *args, **kwargs)

    @property
    def dims(self):
        """Grid dimensions as a tuple *(height, width)*."""
        return self._height, self._width

    @property
    def height(self):
        """Number of rows in the nonogram grid."""
        return self._height

    @property
    def width(self):
        """Number of columns in the nonogram grid."""
        return self._width

    @property
    def bool_map(self):
        """Function used to map values in the grid to booleans."""
        return self._bool_map

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

        See :attr:`Nonogrid.set_row` for parameter details.
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

    def __getitem__(self, key):
        return self.clue[key]

    def satisfied_by(self, sequence, bool_map=bool):
        """Determine if a boolean sequence satisfies the nonoclue.

        Optionally use `bool_map` to map arbitrary objects to booleans.

        Parameters
        ----------
        sequence : Sequence[T]
            Iterable over objects to match to squares.
        bool_map : Callable[[T], bool], default=bool
            Return whether an object represents a filled or empty square.

        Returns
        -------
        If the clue's constraints are satisfied by `sequence`.

        Notes
        -----
        - Nonoclues themselves do not impose a total length.
        """
        # TODO: Build an iterator to do this computation lazily if bool_map is expensive.
        bool_sequence = [bool_map(x) for x in sequence] + [False]  # add fencepost for last line

        cur_hint = 0
        line = 0

        # TODO: Fail this as early as possible.
        # DepTODO: Provide additional context around where it fails.
        for square in bool_sequence:
            line += square
            if not square and line > 0:  # non-empty line finished
                if (cur_hint == len(self) or  # line should not exist
                        line != self[cur_hint]):
                    return False
                cur_hint += 1

        # Did we see all the expected lines?
        return cur_hint == len(self)


class Nonogram:
    """The row clues and column clues that form a nonogram puzzle."""

    def __init__(self, rows, cols):
        """Initialize a nonogram with a sequence of row clues and a sequence of column clues.

        Does not verify if the requirements that the clues impose have a valid solution.

        Parameters
        ----------
        rows, cols : Sequence[Nonoclue]
            Clues imposed by the rows and the columns.

        Notes
        -----
        Doing any (even trivial) checks on `rows` and `cols` might misleadingly
        suggest that the class can know if a set of clues has a valid solution.

        Better to defer all solution verification to the solver.
        """
        # TODO: Do empty Nonoclue trimming at the beginning and end.
        self.rows, self.cols = rows, cols

    @property
    def width(self) -> int:
        """Total number of columns (i.e., number of squares in a row)."""
        return len(self.cols)


    @property
    def height(self) -> int:
        """Total number of rows (i.e., number of squares in a column)."""
        return len(self.rows)

    @staticmethod
    def _rows_satisfied(row_clues, row_data, bool_map):
        """Determine if an ordered set of row data satisfies an ordered set of clues."""
        # TODO: Build a more rigorous fitter by removing all empty rows from
        #  the beginning and end of both clue and data.
        if (diff := len(row_data) > len(row_clues)) > 0:
            # Extra rows of squares satisfy iff they are empty.
            row_clues = list(row_clues) + [Nonoclue()] * diff

        for i, clue in enumerate(row_clues):
            # The empty list matches only with the empty clue (no lines).
            row = row_data[i] if i < len(row_data) else []

            if not clue.satisfied_by(row, bool_map):
                return False

        return True

    def satisfied_by(self, solution, bool_map=bool, row_major=True):
        """Determine if a boolean array satisfies the nonogram.

        Parameters
        ----------
        solution : Sequence[Sequence[T]]
            Two-dimensional array of objects to match to squares.
        bool_map : Callable[[T], bool], default=bool
            Return whether an object represents a filled or empty square.
        row_major : bool, default=True
            If the solution is in row-major order.

        Returns
        -------
        If all row clue and column clue constraints are satisfied by `solution`.

        See Also
        --------
        :attr:`Nonoclue.satisfied_by`
        """
        if not row_major:  # reduce to the row-major case
            return Nonogram(self.cols, self.rows).satisfied_by(solution, bool_map)

        # TODO: This rotation is the only component actually enforcing a square `solution`.
        #  Can I build an algorithm where `solution` just is a HashSet of coordinate membership?
        #  Probably unwise. Nonograms are generally dense so a hashset seems inefficient.
        # TODO: Maybe I can build a NonoSol class to abstract away the 2D array behind a class,
        #  and just have this method create a NonoSol from `solution`.
        col_data = []
        for i in range(len(solution[0])):
            col_data.append([solution[j][i] for j in range(len(solution))])

        return all([
            Nonogram._rows_satisfied(self.rows, solution, bool_map),
            Nonogram._rows_satisfied(self.cols, col_data, bool_map)
        ])
