"""Classes and functions to assist nonogram solvers."""

import math

from nonogram.gram import Nonoclue


class ClueSolutions:
    """Iterable over all the possible solutions to a nonoclue."""

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

    # TODO: Run some speed tests, if this computation is a constraining factor
    #  add caching and/or add a new method that approximates length.
    def __len__(self):
        """Number of solutions of length `n` that satisfy the clue.

        Correctness Proof
        -----------------
        Let the clue have length :math:`p` and hints :math:`(x_1, ..., x_p)`,
        and let the sum of the hints be :math:`X = \\sum_j x_j`
        Let a solution of length :math:`n` be a sequence of integers :math:`(g_0, ..., g_p)`
        satisfying (a) and (b).

        .. math::
            \\text{(a)} \\forall i g_i > 0

            \\text{(b)} \\sum_i g_i + X = n + 2

        **Justification**:
        Each :math:`g_i` represents the length of the gap after line :math:`j` matching hint :math:`x_j`.
        :math:`g_0` represents the gap before the first line.
        Since the lines can---but don't have to---begin at the start or end of the solution,
        for convenience we let all gaps have positive length by "adding squares" at the start
        and end that must be empty, hence :math:`n + 2`.

        The number of valid solutions is then equal to the number of sequences satisfying (a) and (b).
        We will reformulate this as a combinatorial problem by constructing a sequence with
        a series of choices.

        We consider a sequence of :math:`T = n + 2 - X` objects and
        place :math:`p` dividers in the :math:`T - 1` positions between the objects.
        (This formulation of the like objects and unlike cells problem is not original.) [1]_

        We can take the number of objects between the dividers as our sequence :math:`(g_0, ..., g_p)`.
        If :math:`p` dividers are positioned at :math:`l_0 = 0, l_1, ..., l_p, l_{p + 1} = T`
        satisfying :math:`\\forall k l_k < l_{k + 1}`, we let :math:`g_i = l_{i + 1} - l_i`.

        Since :math:`\\forall k l_k < l_{k + 1}`, we satisfy (a),
        and our construction satisfies (b), as shown below.

        .. math::
            \\therefore \\sum_i g_i = \\sum_i l_{i + 1} - l_i = T = n + 2 - X

        There are :math:`_{n + 1 - X}\\text{C}_{p}` ways to choose positions of dividers,
        and to show this is also the number of ways to choose a sequence,
        we only need to show our construction is one-to-one.

        We can show this by inverting our construction; given :math:`(g_0, ..., g_p)`,
        let :math:`l_0 = 0, l_{p + 1} = T`, and for all :math:`k` between 1 and :math:`p`,
        let :math:`l_k = \sum_{i = 0}^{k} g_i`.
        We have :math:`l_0 = 0, l_1, ..., l_p, l_{p + 1} = T` satisfying :math:`g_i = l_{i + 1} - l_i`.

        Therefore, our construction is one-to-one,
        and so the number of unique sequences is :math:`_{n + 1 - X}\\text{C}_{p}`

        .. [1] Riordan, John. *Introduction to Combinatorial Analysis.* Unabridged Dover. 2002.
            Proof modified from Chapter 5, Section 3: **Like Objects and Unlike Cells**.
        """
        # Pycharm's typechecker doesn't know defining __len__ and __getitem__ makes a class iterable?
        # noinspection PyTypeChecker
        return math.comb(self.target_length + 1 - sum(self.clue), len(self.clue))

    # TODO: implement iterable functionality.
