
from nonogram import Nonogram
from nonogram.solve.abc import SolveFailure
from nonogram.solve.detsearch import NaiveSolver

from datascript import rule_input

clues = rule_input()["clues"]
if len(clues["row"]) > 4 or len(clues["col"]) > 4:
    print("Greater than 4x4 not supported.")
    exit()

progress_msg = "Solving..."
print(f"\n{progress_msg}", end="")

solver = NaiveSolver(Nonogram(clues["row"], clues["col"]))
grid = solver.solve()

match grid:
    case SolveFailure.INC:
        print("\rNo solution found.")
    case SolveFailure.DNE:
        print("\rNo solution exists.")
    case Nonogrid:
        title = "Solution"
        diff = " " * max(0, len(progress_msg) - len(title))
        print(f"\r{title}{diff}\n{"-" * len(title)}")

        for row in grid.rows():
            print("".join("■" if x else "□" for x in row))
