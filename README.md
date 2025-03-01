# Nonogram Solver

This repository hosts a program to solve and verify solutions to [nonograms](https://en.wikipedia.org/wiki/Nonogram).
I built this for my application to the [Recurse Center](https://www.recurse.com/).

## Contents

- [Instructions](#instructions) describes how to use what this repository currently provides.
- [Reading this Repository](#reading-this-repository) describes what you can look at if you
  are using this repository to judge me as a programmer, and also provides some information
  about the [project constraints](#project-constraints).
- [Project Goals and Current Status](#project-goals-and-current-status) describes what I
  wanted to achieve when beginning this project and where I currently am.

### Instructions

I use [`uv`](https://github.com/astral-sh/uv).
Clone the repo and `uv run main.py` should work out of the box.

See [Project Goals and Current Status](#project-goals-and-current-status)
for what the project currently does.

Otherwise, try running `python3 -m main` with at least Python 3.12.

### Reading this Repository

I wrote this project for my own enjoyment, but also (pretty explicitly) to demonstrate to others
how I like to program when I have full control over a project.

As of `2025FEB26`, I've spent an average of $1.5 < h < 2$ hours/day for 28 days on this project,
including programming, documenting, or algorithm design.

Since there's lots of code, here are a few notable things to look at:

- Search for the `Notes` section in Python docstrings.
  I've documented decision tradeoffs there, and I hope to reveal how much I focus on
  *the influence of current design decisions on future programmer behavior*,
  whether that's myself or another program user.
- An example of my thought process when encountering a software paradigm I'm unsure how to
  implement can be found in the docstring of the class `SolveFailure`, found in
  [`solve/abc.py`](https://github.com/antonio-caceres/nonogram/blob/main/src/nonogram/solve/abc.py).
- My independent reading (in 2023) of Riordan's *Introduction to Combinatorial Analysis* paid off
  in the method `ClueSolutions.__len__` and its proof, found in
  [`solve/utils.py`](https://github.com/antonio-caceres/nonogram/blob/main/src/nonogram/solve/utils.py).
- I'm proud of the module refactors I did in commits
  [`b4a2ecc7`](https://github.com/antonio-caceres/nonogram/commit/b4a2ecc7)
  and [`036cc912`](https://github.com/antonio-caceres/nonogram/commit/036cc912).

#### Project Constraints

Constraints were imposed both by the Recurse Center and by myself.

- *Recurse*: Program fully independently.
- *Recurse*: Program from scratch (no frameworks).
- *Self*: Only dependent on Python 3.12.
  - 2D fixed-size arrays without `numpy` and testing without `pytest` were unfortunate results.
- *Self*: No large language models.
- *Self*: No research on existing nonogram solver algorithms.
  - The algorithm development is the fun part!

### Project Goals and Current Status

The original pitch for this repository was to build *probabilistic nonogram solvers*.
I have been interested in randomized algorithms for a couple of years now,
but have only studied them from a theoretical perspective;
it's rare for use cases to demand algorithms that sometimes work and sometimes fail.

I try to make programs such that they are easily extendable by others,
which compels me to write well-documented and well-tested class and interfaces
that interact with each other in a natural way.
Most of my initial effort on this project involved trying various structures
for the program to decide what I liked the most; I've documented several of these decisions.

Follow the [instructions](#instructions) to use the best solver with a manually entered
nonogram using `main.py`.
Solve progress noted below.

- `2025FEB19`: Brute force solver with no optimizations; max size 4x4.
- `2025FEB26`: Unoptimized, but slightly more clever, brute force solver;
  max size 16x16 with warning for larger than 8x8.

Here are some of my future goals for solvers:
- Optimize the solver that searches the entire space using BnB.
- Optimize the solver that iterates the space with fixed row solutions
  - We can only check the columns that change between iterations.
  - We can also build a cache for each column.
  - Build the transpose optimization to do column iteration instead if faster.
- Build a logical bounder (I got an idea for an FSA approach that might work,
  but I do not know if it can find all solutions).
- [Probabilistic Solver](#probabilistic-solver)

### Probabilistic Solver

My working theory for a probabilistic solver will employ Bayesian inference.
We can apply probability distributions to both the rows and the columns,
sample the space, get information about how the solution failed,
and then update our distributions.

It's difficult to determine both how to sample and how to update the distributions.
My instinct is to do all the sampling for my first algorithm randomly,
and then use conditional probabilities to derandomize the algorithm.
The nonogram problem seems particularly amenable to conditional derandomization
because selection of specific squares naturally places a bunch of constraints on
the other squares that are valid selections.
