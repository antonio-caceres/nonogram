"""Classes for representing and solving nonograms."""


class Nonoclue:
    """A clue to either a row or column of a nonogram puzzle.

    Takes the form of a sequence of integers.
    A clue of the form `(a, b, c)` imposes exactly lines of length `a`, `b`, and `c` filled
    squares separated by at least one empty square.

    Represents the clue `(0)` (all squares empty) as the empty list `[]` to minimize edge cases
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
        """Instantiate a nonogram with a sequence of row clues and a sequence of column clues.

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
        Nonoclue.satisfied_by
        """
        if not row_major:  # reduce to the row-major case
            return Nonogram(self.cols, self.rows).satisfied_by(solution, bool_map)

        # TODO: This rotation is the only component actually enforcing a square `solution`.
        #  Can I build an algorithm where `solution` just is a HashSet of coordinate membership?
        #  Probably unwise. Nonograms are generally dense so a hashset seems inefficient.
        # TODO: Maybe I can build a NonoSol class to abstract away the 2D array behind a class,
        #  and just have this method instantiate a NonoSol from `solution`.
        col_data = []
        for i in range(len(solution[0])):
            col_data.append([solution[j][i] for j in range(len(solution))])

        return all([
            Nonogram._rows_satisfied(self.rows, solution, bool_map),
            Nonogram._rows_satisfied(self.cols, col_data, bool_map)
        ])
