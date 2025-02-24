"""Representations of nonogram clues and puzzles."""

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
        return self.height + self.width

    def __repr__(self):
        return f"{type(self).__name__}({self.rows}, {self.cols})"

    @staticmethod
    def _clue_sat_count(clues, data_iter):
        """Determine how many clues an iterator over data satisfies.

        Raises
        ------
        ValueError
            If the lengths of `clues` and `data_iter` do not match.
        """
        zipped = zip(clues, data_iter, strict=True)
        return sum(clue.satisfied_by(line) for clue, line in zipped)

    # TODO: Write fitting algorithm to call as a static method.

    def satisfied_count(self, grid):
        """Determine how many clues in the nonogram are satisfied by a nonogrid.

        Parameters
        ----------
        grid : :py:class:`nonogram.grid.Nonogrid`
            Grid to be evaluated as a solution to the nonogram.

        Raises
        ------
        ValueError
            If the height and width of the grid and nonogram do not match.
        """
        # TODO: Add 'fit' or 'strict' parameter to this method instead of always raising.
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
        grid : :py:class:`nonogram.grid.Nonogrid`
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
        # TODO: Add 'fit' or 'strict' parameter to this method.
        return self.satisfied_count(grid) == self.num_clues
