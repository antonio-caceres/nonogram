"""Classes and functions to assist nonogram solvers."""

import itertools
import math

from nonogram.gram import Nonoclue


class ClueSolutions:
    """Iterable over all the possible solutions to a nonoclue.

    :py:class:`ClueSolutions` generates its solutions with a combinatorial construction.

    The documentation in this class constitutes a proof of correctness of
    this construction as well as corollary properties.

    Correctness
    ===========
    Let the clue have length :math:`p` and hints :math:`(x_1, ..., x_p)`,
    and let the sum of the hints be :math:`X = \\sum_j x_j`.
    Let a solution of length :math:`n` be a sequence of integers :math:`(g_0, ..., g_p)`
    satisfying (a) and (b).

    .. math::
        \\text{(a)} \\forall i g_i > 0

        \\text{(b)} \\sum_i g_i + X = n + 2

    **Justification**:
    Since any solution to a clue must fix the lengths of the filled lines in a specific order,
    the malleable part of the solution is the *lengths of the gaps between the filled lines*.
    Therefore, to define a unique solution, we must define the lengths of those gaps.

    Each :math:`g_i` represents the length of the gap after line :math:`j` matching hint :math:`x_j`.
    :math:`g_0` represents the gap before the first line.
    Since the lines can---but don't have to---begin at the start or end of the solution,
    for convenience we let all gaps have positive length by "adding squares" at the start
    and end that must be empty, hence :math:`n + 2`.

    Construction
    ------------
    **Intuition**:
    To find a solution, we need gap lengths :math:`(g_0, ..., g_p)` that sum to :math:`n + 2 - X`
    and are all positive.
    We can formulate the problem of finding a solution to a sequence of choices:
    place empty squares into gaps until the total solution has the intended length.

    John Riordan described this combinatorial problem as placing like objects in unlike cells
    with all cells having at least one object, and described the following solution.
    Take the total number of objects (empty squares) and place them in a row,
    and then choose the positions of dividers between those objects;
    the unlike cells (gaps) are formed from the objects between those dividers.
    Since the dividers are placed at unique positions, each cell has at least one object. [1]_

    I formalize this approach below.

    **Correctness Proof**:
    We consider :math:`T = n + 2 - X` like objects and place :math:`p` dividers in
    the :math:`T - 1` positions between the objects.

    Let :math:`l_0 = 0`, :math:`l_{p + 1} = T`, and let the positions of our dividers
    be :math:`l_1, ..., l_p` satisfying :math:`\\forall k l_k < l_{k + 1}`.
    To construct our sequence, we let :math:`g_i = l_{i + 1} - l_i`.

    Since :math:`\\forall k l_k < l_{k + 1}`, we satisfy (a),
    and our construction satisfies (b), as shown below.

    .. math::
        \\therefore \\sum_i g_i = \\sum_i l_{i + 1} - l_i = T = n + 2 - X

    Therefore, we can map positions :math:`l_1, ..., l_p` to solutions :math:`(g_0, ..., g_p)`.
    To show that each position corresponds to a unique solution,
    we need to show our map is one-to-one.

    We invert our construction; given :math:`(g_0, ..., g_p)`,
    let :math:`l_0 = 0, l_{p + 1} = T` and, for all :math:`k` between 1 and :math:`p`,
    let :math:`l_k = \sum_{i = 0}^{k - 1} g_i`.
    We satisfy :math:`g_i = l_{i + 1} - l_i`.
    All :math:`g_i` are positive and their total sum is :math:`T`,
    so :math:`l_0 = 0 < l_1 < ... < l_p < l_{p + 1} = T`.

    Therefore, by choosing integers :math:`l_1, ..., l_p`, we can construct a unique
    solution :math:`(g_0, ..., g_p)` by letting :math:`g_i = l_{i + 1} - l_i`
    with :math:`l_0 = 0` and :math:`l_{p + 1} = T`.

    .. [1] Riordan, John. *Introduction to Combinatorial Analysis.* Unabridged Dover. 2002.
        Proof modified from Chapter 5, Section 3: **Like Objects and Unlike Cells**.
    """

    def __init__(self, clue, target_length):
        """Initialize a new iterable for solutions of a specific length.

        Parameters
        ----------
        clue : :py:class:`~nonogram.gram.Nonoclue`
            Nonoclue to solve.
        target_length : int
            Length of solutions to generate.
        """
        self.clue = clue if isinstance(clue, Nonoclue) else Nonoclue(clue)
        self.target_length = target_length

    def _iterate(self):
        """Reusable iteration method.

        See :py:meth:`~ClueSolutions.__iter__` for algorithm and documentation.
        """
        # Pycharm's typechecker doesn't know defining __len__ and __getitem__ makes a class iterable?
        # noinspection PyTypeChecker
        divider_indices = range(self.target_length + 1 - sum(self.clue))
        for positions in itertools.combinations(divider_indices, len(self.clue)):
            # itertools.combinations guarantees that positions is sorted
            pos_pairs = itertools.pairwise([0] + list(positions) + [self.target_length])
            gap_lengths = [b - a for a, b in pos_pairs]
            # TODO: helper method to map gap lengths in a solution
            yield ...

    def __iter__(self):
        """Iterate over all solutions of the desired length that satisfy the nonoclue.

        TODO: Come up with a formal description of how this method yields solutions.

        Returns
        -------
        Iterator object yielding values described in [Yields]_.

        Yields
        ------
        TODO: Come up with a formal description of how this method yields solutions.

        Notes
        -----
        :py:meth:`itertools.combinations` yields in a sorted order;
        individually, each chosen set is provided as a sorted tuple
        (e.g., the set :math:`{7, 2, 5}` is represented by the tuple ``(2, 5, 7)``)
        and the first sets returned are the sets with the lowest indicies
        (e.g., 2-tuples chosen from ``(1, 2, 3)`` are ordered
        ``[(1, 2), (1, 3), (2, 3)]``).

        TODO: Come up with a formal description of how this method yields solutions.

        Intuitively, this method first returns a solution with all lines placed as early
        as possible, then iterates over solutions moving the last line back,
        and then moves the second to last line back one step before
        iterating over the last line again.
        """
        return self._iterate_solutions()

    # TODO: Run some speed tests, if this computation is a constraining factor
    #  add caching and/or add a new method that approximates length.
    def __len__(self):
        """Number of solutions of length `n` that satisfy the clue.

        Correctness
        -----------
        Our construction chooses divider positions :math:`l_1, ..., l_p` from
        the set of integers :math:`{1, ..., T - 1}` for :math:`T = n + 2 - X`
        There are :math:`_{n + 1 - X}\\text{C}_{p}` ways to choose such positions.

        Notes
        -----
        This method exists to speed up computation of the number of solutions for
        branching and bounding algorithms, since :py:meth:`ClueSolutions.__iter__` is expensive.
        """
        # noinspection PyTypeChecker
        return math.comb(self.target_length + 1 - sum(self.clue), len(self.clue))
