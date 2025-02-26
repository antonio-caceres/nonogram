"""Nonogram solvers that search a space which must contain the solution if one exists."""

from itertools import product

from nonogram import Nonogram, NonogridArray
from nonogram.solve.abc import SolveFailure, NonogramSolver
from nonogram.solve.utils import ClueSolutions


# TODO: Add branch and bound optimizations to both these classes.
class ClueChooser(NonogramSolver):
    """Solver which iterates over possible grid combinations by fixing individual clues."""

    class _FoundSolution(Exception):
        """Helper class to end recursion early."""

    @staticmethod
    def _num_combs(clue_lst, length):
        """Return number of possible solutions to the clues."""
        prod = 1
        for clue in clue_lst:  # clue_lst should never be empty
            prod *= len(ClueSolutions(clue, length))
        return prod

    # TODO: Refactor this solution method to use class attributes?
    def _find_solution_rec(self, grid_builder, cur_idx, row_sols, collector, collect):
        for sol in row_sols[cur_idx]:
            grid_builder.append(sol)
            if cur_idx + 1 == self.nonogram.height:
                grid = NonogridArray(self.nonogram.height, self.nonogram.width, grid_builder)
                if self.nonogram.satisfied_by(grid):
                    collector.append(grid)
                    if not collect:
                        raise ClueChooser._FoundSolution()
            else:
                self._find_solution_rec(grid_builder,
                                        cur_idx + 1,
                                        row_sols,
                                        collector,
                                        collect)
            grid_builder.pop()

    def _find_solution(self, collect):
        row_sols = [ClueSolutions(row, self.nonogram.width) for row in self.nonogram.rows]
        collector = []
        try:
            self._find_solution_rec([], 0, row_sols, collector, collect)
        except ClueChooser._FoundSolution:
            return collector[0]
        return collector

    def solve(self, *, collect=False):
        row_leaves = ClueChooser._num_combs(self.nonogram.rows, self.nonogram.width)
        col_leaves = ClueChooser._num_combs(self.nonogram.cols, self.nonogram.height)
        if 0 in {row_leaves, col_leaves}:
            return SolveFailure.DNE

        if col_leaves > row_leaves:
            ...
            # transposed_gram = Nonogram(self.nonogram.cols, self.nonogram.rows)
            # transposed_solver = type(self)(transposed_gram)
            # transposed_result = transposed_solver.solve(collect=collect)
            # transposed_sols = [sols]

        if not (result := self._find_solution(collect)):
            return SolveFailure.DNE
        return result

    def max_sat(self, *, collect=False):
        # TODO: I think a generalization of the above algorithm exists
        #  by fixing an arbitrary subset of the clues instead of specifically
        #  the rows or the columns, but I haven't developed it yet.
        raise NotImplementedError


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
