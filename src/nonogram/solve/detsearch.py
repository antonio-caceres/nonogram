"""Nonogram solvers that search a space which must contain the solution if one exists."""

from itertools import chain, product

from nonogram import Nonogrid
from nonogram.core import Nonoclue
from nonogram.solve.core import SolveFailure, NonogramSolver


# TODO: this method needs to go somewhere else :((
# TODO: this method does not consider if the dimensions of the two do not match :(
# TODO: caching what
def check_max_sat(grid, gram):
    total_clues = 0

    for data, clue in chain(zip(grid.rows(), gram.rows), zip(grid.cols(), gram.cols)):
        total_clues += Nonoclue(clue).satisfied_by(data, bool_map=grid.bool_map)
        if grid._grid == [[True, False, True]]:
            print(total_clues)

    return total_clues


# TODO: Add branch and bound optimizations to both these classes.


class NaiveSolver(NonogramSolver):
    """Solver which finds solutions with unconstrained iteration over grid combinations."""

    def solve(self):
        # TODO: It doesn't do this right now lol
        """Find a solution to the nonogram, if it exists.

        If multiple solutions exist, choose the solution that, when considering all filled blocks,
        minimizes first the sum of the row indices, and second the sum of the column indices,
        of all filled blocks.
        """
        frac_sat, sol = self.max_sat(collect=False)
        if frac_sat == len(self.nonogram.rows) + len(self.nonogram.cols):
            return sol

    def _grid_iterator(self):
        rows = product([False, True], repeat=self.nonogram.width)
        grid_data = product(list(rows), repeat=self.nonogram.height)
        for data in grid_data:
            yield Nonogrid.for_nonogram(self.nonogram, data)


    def max_sat(self, collect=False):
        """Find a grid that maximizes the number of satisfied clues in the nonogram."""
        maxim_num, maxim_list = 0, []
        for grid in self._grid_iterator():
            clue_sat = check_max_sat(grid, self.nonogram)
            # if list(grid.rows())[0] == [True, False, True]:
            #     print(clue_sat)
            if clue_sat == maxim_num:
                maxim_list.append(grid)
            if clue_sat > maxim_num:
                maxim_num, maxim_list = clue_sat, [grid]
        if not collect:
            if not maxim_list:
                return SolveFailure.DNE
            return maxim_num, maxim_list[0]
        return maxim_num, maxim_list



# TODO: I don't like this name.
class FixCluesSolver(NonogramSolver):
    """Solver which finds solutions with unconstrained iteration over grid combinations."""

