
from abc import ABC, abstractmethod
from enum import Enum

from nonogram import Nonogram, Nonogrid


class SolveFailure(Enum):
    """Flags to signal whether a solve attempt concludes that no solution to the nonogram exists.

    If :py:attr:`SolveFailure.DNE` is returned by a solver, the solver determined that
    no solution exists for the given nonogram.
    If that conclusion is incorrect, this should be considered a bug in the solver.

    If :py:attr:`SolveFailure.INC` is returned by a solver, the solver could not find
    a solution for the given nonogram, but could not conclusively determine if a solution exists.

    Rationale
    ---------
    This library intends to provide probabilistic nonogram solving algorithms.
    Specifically, if a solution exists, these algorithms return a solution with some
    probability between 0 and 1, exclusive.

    If a probabilistic algorithms does not find a solution, the algorithm offers no guarantee
    that finding a solution is impossible.
    However, in some cases, a probabilistic algorithm might reach a deterministic impasse
    that acts as a proof that no solution exists.
    For example, if the sum of the integers in some row clue is greater than the total number
    of (non-zero) column clues, a solution is impossible.

    This motivates allowing algorithms to distinguish to users which of the two scenarios
    has occurred.
    This class serves that purpose.

    Discussion of Alternative Solutions
    -----------------------------------
    I (Antonio) spent substantial time deciding how to implement this functionality,
    and here is the summary of my thought process.

    **Returning Singletons**

    My initial instinct was to return either ``False`` or ``None``,
    but it wasn't immediately obvious to me which built-in value should represent
    the DNE case, and so I concluded this would not be an intuitive solution for
    me or anybody else.

    So, I briefly considered making my own singleton objects as return values,
    allowing me to customize the name for transparency and readability.
    If I were using a functional language, I'd probably use a singleton type or
    some other algebraic datatype, but I'm building an OO program.

    **Returning a Solution Information Object**

    I started building a class that contained information about what the nonogram solution
    represents, both with options for "no solution exists" and "solution not found",
    but also with the option for lists of all valid solutions, grids that maximally
    satisfy the clues in an unsolvable nonogram, and others.

    I decided this would be enforcing a structure on how all the solvers operate,
    and every time I built a new solver, I would need to return to the information class
    to make alterations.
    I also would need to build an immutable version of the :py:class:`Nonogrid`,
    so this information class would not become corrupted or invalid.
    Better to let the solvers and their methods decide what to return on their own.

    **Raising an Exception**

    I liked the idea of raising an exception if the nonogram was unsolvable
    and returning ``False`` otherwise, but it didn't sit right with me because
    having a nonogram be unsolvable doesn't *really* represent a program failure state.

    However, I could see use cases where a program would want to crash if the nonogram
    is unsolvable. So, I wrote :py:func:`raise_if_unsolvable`.

    **Returning Tuples**

    Returning a tuple with an Enum member and the grid was an early idea,
    but I definitely didn't want solver users to have to tuple unpack every result.
    Mostly due to my own lack of imagination, I did not consider the current solution of
    "return a nonogram if a solution does exist, and otherwise return an Enum member" until
    after considering all the other solutions listed here.
    """
    DNE = "No solution exists for this nonogram."
    INC = "Cannot conclude if a solution does or does not exist."

    def __bool__(self):
        """All solve failures return ``False``.

        Solver users can use an ``if`` statement to determine if the solver returned
        a solution or a :py:class:`SolveFailure`.
        """
        return False


class NonogramSolver(ABC):
    """Abstract class of a nonogram solver.

    Provides implementations of :py:meth:`~NonogramSolver.solve` and
    :py:meth:`~NonogramSolver.solve_total` based on the abstract implementation of
    :py:meth:`~NonogramSolver.max_sat`.

    Notes
    -----
    I implemented a configuration class that carried default values for some of the keyword
    arguments to the functions provided by :py:class:`NonogramSolver`.
    This configuration class also included a parameter ``fail_on_unsolvable``
    which changed the behavior of :py:attr:`SolveFailure.DNE` returns to raising an error.

    This implementation required the use of a metaclass or a class decorator,
    and eventually, I figured that the configuration was not important enough;
    it would be better to let the user do what it wants with the return value.
    """

    def __init__(self, nonogram: Nonogram):
        """Initialize a solver with a nonogram and configuration values.

        Parameters
        ----------
        nonogram
            Nonogram that this solver will attempt to solve.
        """
        self.nonogram = nonogram

    @abstractmethod
    def solve(self) -> Nonogrid | SolveFailure:
        """Find a solution to the nonogram.

        If multiple solutions to the nonogram exist, can return any valid solution.
        Certain solver implementations can provide guarantees about which solution is returned
        if multiple exist.

        Returns
        -------
        Nonogrid
            The grid representing the solution if a solution was found.
        :py:attr:`SolveFailure.DNE`
            If the nonogram is unsolvable.
        :py:attr:`SolveFailure.INC`
            If the solver failed to solve the nonogram, but could not determine if a solution existed.
        """

    # I'm not 100% sure how I want to implement the deterministic vs probabilistic solvers
    # from a class structure perspective.
    # I am considering just having the solver class above and then having
    # subclasses with the methods below.
    # I've decided that I will know best how to proceed once I've written some solvers.
    # Leaving all my incomplete work here.

    # def solve_total(self, *, complete=True) -> set[Nonogrid] | SolveFailure:
    #     """Find all solutions to the nonogram.
    #
    #     Does not return an incomplete set of nonogram solutions; even if the solver finds
    #     a subset of valid solutions, it should return :py:attr:`SolveFailure.INC` if it
    #     cannot conclude that there exist other solutions
    #
    #     Returns
    #     -------
    #     The *complete set* of nonogram solutions if all solutions were found,
    #     :py:attr:`SolveFailure.DNE` if no solution exists, and :py:attr:`SolveFailure.INC`
    #     if the completeness of the set could not be determined.
    #     """
    #
    #
    # @abstractmethod
    # def max_sat(self, *, collect=False):
    #     """Find a grid that maximally satisfies the clues to the nonogram.
    #
    #     If the nonogram has a solution, this method will find a solution to the nonogram.
    #
    #     Parameters
    #     ----------
    #     collect : bool, default=False
    #         If this method should collect all the grids that maximally satisfy the nonogram.
    #
    #     Returns
    #     -------
    #
    #     """

