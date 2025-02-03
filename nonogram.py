"""Classes for representing and solving nonograms."""


class Nonoclue:
    """A clue to either a row or column of a nonogram puzzle.

    Takes the form of a sequence of integers.
    A clue of the form `[a, b, c]` imposes exactly lines of length `a`, `b`, and `c` filled
    squares separated by at least one empty square.

    Represents the clue `[0]` (all squares empty) as the empty list to minimize edge cases
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
                    raise TypeError("Negative numbers are not valid clues.")
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
        self.rows, self.cols = rows, cols

    @property
    def width(self) -> int:
        """Total number of columns (i.e., number of squares in a row)."""
        return len(self.cols)


    @property
    def height(self) -> int:
        """Total number of rows (i.e., number of squares in a column)."""
        return len(self.rows)
