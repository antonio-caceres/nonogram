# Nonogram Solver

This repository hosts a program to solve and verify solutions to [nonograms](https://en.wikipedia.org/wiki/Nonogram).
I built this for my application to the [Recurse Center](https://www.recurse.com/).

#### Reading this Repository

I wrote this project for my own enjoyment, but also (pretty explicitly) to demonstrate to others
how I like to program when I have full control over a project.

As of `2025FEB14`, I've spent an average of ~1.5 hours/day for 16 days on this project,
including programming, documenting, or algorithm design.

Since there's lots of code, here are a few notable things to look at:

- Search for the `Notes` section in Python docstrings.
  I've documented decision tradeoffs there, and I hope to reveal how much I focus on
  *the influence of current design decisions on future programmer behavior*,
  whether that's myself or another program user.
- An example of my thought process when encountering a software paradigm I'm unsure
  how to implement can be found in the docstring of the class `SolveFailure` in the
  `src/nonogram/solve/core.py`.

#### Project Constraints

Constraints were imposed both by the Recurse Center and by myself.

- *Recurse*: Program fully independently.
- *Recurse*: Program from scratch (no frameworks).
- *Self*: Only dependent on Python 3.12.
  - 2D fixed-size arrays without `numpy` and testing without `pytest` were unfortunate results.
- *Self*: No large language models.
- *Self*: No research on existing nonogram solver algorithms.
  - The algorithm development is the fun part!

### Instructions

I use [`uv`](https://github.com/astral-sh/uv).
Clone the repo and `uv run main.py` should work out of the box.
