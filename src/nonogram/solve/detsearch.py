"""Nonogram solvers that search a space which must contain the solution if one exists."""

from itertools import product

from nonogram import NonogridArray
from nonogram.solve.abc import SolveFailure, NonogramSolver



# TODO: Add branch and bound optimizations to both these classes.


class NaiveSolver(NonogramSolver):
    """Solver which finds solutions with unconstrained iteration over grid combinations."""

    def solve(self, *, collect=False):
        frac_sat, sol = self.max_sat(collect=collect)
        if frac_sat == len(self.nonogram.rows) + len(self.nonogram.cols):
            return sol
        else:
            return SolveFailure.DNE

    def _grid_iterator(self):
        rows = product([False, True], repeat=self.nonogram.width)
        grid_data = product(list(rows), repeat=self.nonogram.height)
        for data in grid_data:
            yield NonogridArray.for_nonogram(self.nonogram, data)

    def max_sat(self, *, collect=False):
        maxim_num, maxim_list = 0, []
        for grid in self._grid_iterator():
            clue_sat = self.nonogram.satisfied_count(grid)
            # if list(grid.rows())[0] == [True, False, True]:
            #     print(clue_sat)
            if clue_sat == maxim_num:
                maxim_list.append(grid)
            if clue_sat > maxim_num:
                maxim_num, maxim_list = clue_sat, [grid]
        if not collect:
            return maxim_num, maxim_list[0] if maxim_list else SolveFailure.DNE
        return maxim_num, maxim_list
