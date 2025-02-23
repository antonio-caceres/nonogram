
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

    Configuration Values
    --------------------
    I implemented a configuration class that carried default values for some of the keyword
    arguments to the functions provided by :py:class:`NonogramSolver`.
    This configuration class also included a parameter ``fail_on_unsolvable``
    which changed the behavior of :py:attr:`SolveFailure.DNE` returns to raising an error.

    This implementation required the use of a metaclass or a class decorator,
    and eventually, I figured that the configuration was not important enough;
    it would be better to let the user do what it wants with the return value.
    """
    DNE = "No solution exists for this nonogram."
    INC = "Cannot conclude if a solution does or does not exist."

    def __bool__(self):
        """All solve failures return ``False``.

        Solver users can use an ``if`` statement to determine if the solver returned
        a solution or a :py:class:`SolveFailure`.
        """
        return False


    # TODO: add __repr__ and __str__ methods


class NonogramBounder(ABC):
    """Nonogram solving algorithm that can provide lower bounds on how many clues can be satisfied.

    Implements :py:meth:`NonogramBounder.solve` based on the abstract implementation of
    :py:meth:`NonogramBounder.max_sat`.

    Notes
    -----
    This abstract class is intended for solvers which search a (random or deterministic) subset
    of the space of nonogrids for a solution.

    Therefore, these solvers **prove lower bounds on the number of clues in a nonogram
    that can be satisfied simultaneously**.
    These solvers can also provide a :py:meth:`~NonogramBounder.solve` method that only works
    when the solvers prove a lower bound of 1 on the satisfiability ratio.

    These solvers cannot prove upper bounds, so cannot prove solution nonexistence.

    If a solver subclass searches a deterministic subset of the space of nonogrids,
    it must search a space that is guaranteed to have a solution if one exists,
    but does not need to search a space with a solution that is guaranteed to
    maximally satisfy the nonogram if the nonogram has no solution.
    (This ensures the  :py:meth:`~NonogramBounder.solve` function works
    with non-zero probability on all nonograms.)

    There is no abstract class which searches for a solution and
    """

    def __init__(self, nonogram: Nonogram):
        """Initialize a solver with a nonogram.

        Parameters
        ----------
        nonogram
            Nonogram that this solver will attempt to solve.
        """
        self.nonogram = nonogram

    def solve(self,
              *,
              collect: bool = False,
              ) -> Nonogrid | list[Nonogrid] | SolveFailure :
        """Attempt to solve a nonogram.

        This function does not guarantee that it will find a solution if one exists,
        but does guarantee that if a nonogram has a solution, then it will find it with
        non-zero probability.
        (As a corollary, even if this function finds a solution, it does not guarantee
        it will find all solutions that exist.)

        Parameters
        ----------
        collect : bool, default=False
            If the method should return all solutions it finds (as opposed to just one).

        Returns
        -------
        Nonogrid | list[Nonogrid]
            If `collect`, returns a list of discovered solutions to the nonogram.
            If not `collect`, returns just one solution to the nonogram.
        SolveFailure
            If no solution was found, returns :py:attr:`SolveFailure.DNE` if
            the solver concludes that no solution exists and :py:attr:`SolveFailure.INC`
            if the solver cannot decide existence of a solution.

        Notes
        -----
        This function imposes no constraints on which grid is returned if multiple grids
        are discovered that all solve the nonogram.

        :py:class:`NonogramBounder`'s implementation of this method always returns
        :py:attr:`SolveFailure.INC` if no solution was found.
        If the subclass intends to implement a :py:meth:`~NonogramBounder.max_sat`
        that always maximally satisfies the Nonogram, then it should subclass
        :py:class:`NonogramSolver` instead (which is a subclass of :py:class:`NonogramBounder`).
        """
        n_sat, result = self.max_sat(collect=collect)
        return result if n_sat == self.nonogram.num_clues else SolveFailure.INC

    @abstractmethod
    def max_sat(self,
                *,
                # As a programmer, I'd usually use collect=True,
                # but I'm keeping the default as False for consistency with the solve method.
                collect: bool = False,
                ) -> tuple[int, Nonogrid | list[Nonogrid]] :
        """Find solution to the nonogram that lower bound the nonogram's satisfiability.

        If the goal is to maximize the number of clues in the nonogram that can be satisfied
        with a solution, this function searches *some* of the possible grids, and returns
        the best solutions it finds along with the number of clues those satisfy.

        Parameters
        ----------
        collect : bool, keyword, default=False
            If this method should return all nonograms found that meet the satisfiability lower bound.

        Returns
        -------
        (n_sat : int, grid : Nonogrid) | (n_sat : int, grids : list[Nonogrid])
            ``n_sat`` is the number of clues the grids satisfy in the nonogram,
            and therefore the lower bound on satisfiability.
            If `collect`, then returns a list ``grids`` of all discovered grids that satisfy
            ``n_sat`` clues; otherwise, returns one ``grid``.

        Notes
        -----
        This function imposes no constraints on which grid is returned if multiple grids
        are discovered that all equally satisfy the nonogram's clues.

        This function also does not guarantee that the list of returned nonograms is in
        any sense a complete list, regardless of the number of clues satisfied by the
        returned nonograms.
        """


# Should resolve methods from NonogramBounder first.
class NonogramSolver(NonogramBounder, ABC):
    """Nonogram solving algorithm that solves all nonograms.

    Provides an implementation of :py:meth:`~NonogramSolver.solve`
    based on the abstract implementation of :py:meth:`~NonogramSolver.max_sat`.

    Notes
    -----
    This abstract class is intended for solvers which do not arbitrarily restrict the
    space of nonogrids for a solution.

    Here, "arbitrarily" means without a mathematical proof that the restriction does not
    compromise the guarantees of :py:meth:`~NonogramSolver.solve`
    and :py:meth:`~NonogramSolver.max_sat`.
    In other words, if a subclass of :py:class:`NonogramSolver` missed a solution to
    a nonogram or fails to maximally satisfy a nonogram, **it is considered a bug**.
    """

    def solve(self,
              *,
              collect: bool = False,
              ) -> Nonogrid | list[Nonogrid] | SolveFailure:
        """Find any solution or all solutions to the nonogram.

        If multiple solutions to the nonogram exist, can return any valid solution
        if `collect` is False.

        Parameters
        ----------
        collect : bool, default=False
            Whether to collect all solutions instead of returning the first one.

        Returns
        -------
        Nonogrid | list[Nonogrid]
            A solution to the nonogram or the list of all solutions to the nonogram.
        :py:attr:`SolveFailure.DNE`
            If the nonogram is unsolvable.
        """
        if (result := super().solve(collect=collect)) == SolveFailure.INC:
            return SolveFailure.DNE
        # TODO: PyCharm's typechecker is broken or this is bugged?
        # noinspection PyTypeChecker
        return result

    @abstractmethod
    def max_sat(self,
                *,
                collect: bool = False,
                ) -> tuple[int, Nonogrid | list[Nonogrid]] :
        """Find a grid or all grids that maximally satisfy the clues in the nonogram.

        Parameters
        ----------
        collect : bool, keyword, default=False
            If this method should return a list of all the nonograms that maximally satisfy.

        Returns
        -------
        (n_sat : int, grid : Nonogrid) | (n_sat : int, grids : list[Nonogrid])
            ``n_sat`` is the maximum number of clues the grid can satisfy.
            If `collect`, then returns a list ``grids`` of all discovered grids that satisfy
            ``n_sat`` clues; otherwise, returns one ``grid``.

        Notes
        -----
        This function imposes no constraints on which grid is returned if multiple grids
        are discovered that all equally satisfy the nonogram's clues.
        """
