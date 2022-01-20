"""
Various subclasses of Wordle, which play the game in different ways.
"""
from core.Wordle import *


class WordleEndless(Wordle):
    """
    A variant of Wordle which has virtually unlimited guesses.
    """
    max_guesses = 1000000000
    reveals_word = True
