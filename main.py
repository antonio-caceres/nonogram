
from nonogram import Nonogram
from nonogram.solve.detsearch import NaiveSolver

from datascript import rule_input

clues = rule_input()["clues"]
if len(clues["row"]) > 4 or len(clues["col"]) > 4:
    print("Greater than 4x4 not supported.")
    exit()

solver = NaiveSolver(Nonogram(clues["row"], clues["col"]))
grid = solver.solve()

title = "Solution"
print(f"\n\n{title}\n{"-" * len(title)}")

for row in grid.rows():
    print("".join("■" if x else "□" for x in row))
