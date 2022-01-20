"""
Global definitions for the Wordle class.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List
from config import *


with open('../' + answer_filepath) as answer_file:
    answer_list = [line.strip('\n') for line in answer_file]

with open('../' + guess_filepath) as guess_file:
    guess_list = [line.strip('\n') for line in guess_file]


class WordleState(Enum):
    """
    An enum class to represent the current __state of the Wordle game.
    """
    Ready = auto()
    Playing = auto()
    Win = auto()
    Lose = auto()

    # Callback states.
    GameStart = auto()
    ValidGuess = auto()
    InvalidGuess = auto()
    GameWon = auto()
    GameLost = auto()
    GameEnded = auto()

    # Character states.
    Correct = auto()
    Misplaced = auto()
    Wrong = auto()


@dataclass
class WordleResponse:
    """
    A response class from the Wordle game.
    """
    game_state: WordleState
    word_response: List[WordleState]
    wrong_characters: List[str]
    misplaced_characters: Dict[str, List[int]]
    correct_characters: Dict[str, List[int]]
    guessed_words: List[str]
    guesses: int

