
from nonogram import Nonogram
from nonogram.solve.abc import SolveFailure
from nonogram.solve import ClueChooser

from datascript import rule_input

max_dim, warning_dim = 16, 8

clues = rule_input()["clues"]
if len(clues["row"]) > max_dim or len(clues["col"]) > max_dim:
    print(f"Larger than {max_dim}x{max_dim} not supported.")
    exit()
if len(clues["row"]) > warning_dim or len(clues["col"]) > warning_dim:
    print(f"Nonograms larger than {warning_dim}x{warning_dim} nonograms "
          f"can take more than 5 minutes to solve.")
    if input("'Enter' to proceed; type anything to cancel."):
        print("Solve cancelled.")
        exit()

progress_msg = "Solving..."
print(f"\n{progress_msg}", end="")

solver = ClueChooser(Nonogram(clues["row"], clues["col"]))
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
