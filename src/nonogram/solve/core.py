
from enum import Enum

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
