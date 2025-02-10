"""Utilities for interacting with the nonograms in my JSON files."""

import json
from typing import NamedTuple, Required, Sequence, TypedDict
from enum import Enum, nonmember
from pathlib import Path


# TODO: Replace with a JSON schema?
class NonogramJSON(TypedDict, total=False):
    """Expectation for a JSON object to be initialized into a nonogram."""
    name: Required[str]
    clues: Required[dict[str, Sequence[Sequence[int]]]]  # clues.keys() == { 'row', 'col' }
    desc: str
    height: int
    width: int
    # Nonograms with explicit solutions included to test the solution verification methods.
    # We assume the solution verification method works for test cases without a solution.
    sol: Sequence[Sequence[bool]]


class NonogramDataset(NamedTuple):
    name: str
    desc: str
    data: list[NonogramJSON]


# TODO: Maybe extract the data outside of the tests/ framework and move
#  the JSON methods into a separate utilities file that comes with the package.
class NonogramDatasetLoader(Enum):
    BASIC = "basegrams.json"
    EDGE = "edgegrams.json"
    LARGE_WITH_UNIQUE = "uniquegrams.json"

    _DATA_FILE_PREFIX = nonmember(Path("data"))

    def load(self):
        # noinspection PyUnresolvedReferences
        filepath = NonogramDatasets._DATA_FILE_PREFIX.joinpath(self.value)
        with open(filepath, mode="rt") as f:
            return json.load(f)
