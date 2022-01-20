"""
The Wordle simulator class.
"""
from core.WordleGlobals import *
from typing import Callable
import random


class Wordle:
    """
    A mock interface of a Wordle game.
    """

    char_check = 'C'
    char_quest = '?'
    char_wrong = 'x'

    max_guesses = 6

    def __init__(self, word: str = None) -> None:
        """
        Initiates a Wordle game.
        :param word: A __word to set as the __word.
        """
        self.__word = word if word else random.choice(answer_list)
        self.__word_length = len(self.__word)
        self.__state = WordleState.Ready
        self.__guesses = 0

        self.__guessed_words: List[str] = []
        self.__wrong_characters: List[str] = []
        self.__misplaced_characters: Dict[str, List[int]] = {}
        self.__correct_characters: Dict[str, List[int]] = {}

    def play(self, word: str = None) -> WordleResponse:
        """
        Starts playing a game of Wordle.
        Used for the console.
        :param word: The __word to test with.
        :return: A packaged response.
        """
        return self.__get_state_method()(word)

    def __get_state_method(self) -> Callable[[str], WordleResponse]:
        """
        Returns a method that our current __state represents.
        :return: A method.
        """
        return {
            WordleState.Ready: self.__response_ready,
            WordleState.Playing: self.__response_playing,
        }.get(self.get_state(), self.__response_over)

    """
    Game Responses
    """

    def __response_ready(self, _: str = None) -> WordleResponse:
        """
        The game's response when we're starting to play.
        :return: The response.
        """
        self.__state = WordleState.Playing
        return self.__get_wordle_response(callback_state=WordleState.GameStart)

    def __response_playing(self, word: str = None) -> WordleResponse:
        """
        The game's response during a playing condition.
        :return:
        """
        if word not in guess_list:
            return self.__get_wordle_response(callback_state=WordleState.InvalidGuess)

        # Do the round logic.
        word_response = []
        for i in range(len(word)):
            word_response.append(self.__compare_word(word, i))

        self.__guessed_words.append(word)
        self.__guesses += 1

        # Did we get the right __word?
        if not any([state for state in word_response if state != WordleState.Correct]):
            self.__state = WordleState.Win
            return self.__get_wordle_response(callback_state=WordleState.GameWon, word_response=word_response)

        # Did we lose?
        elif self.__guesses >= self.max_guesses:
            self.__state = WordleState.Lose
            return self.__get_wordle_response(callback_state=WordleState.GameLost, word_response=word_response)

        # We're still playing.
        return self.__get_wordle_response(callback_state=WordleState.ValidGuess, word_response=word_response)

    def __response_over(self, _: str = None) -> WordleResponse:
        """
        The game's response when there's no associated __state.
        :return: A generic wordle response.
        """
        return self.__get_wordle_response(callback_state=WordleState.GameEnded)

    def __get_wordle_response(self, callback_state: WordleState,
                             word_response: List[WordleState] = None) -> WordleResponse:
        """
        Makes a WordleResponse based on the current game conditions.
        :param callback_state: The __state to callback for a Wordle Response.
        :param word_response: A list of WordleStates to show as a response to input.
        :return: The generated WordleResponse.
        """
        if word_response is None:
            word_response = []
        return WordleResponse(
            game_state=callback_state,
            word_response=word_response,
            wrong_characters=self.__wrong_characters,
            misplaced_characters=self.__misplaced_characters,
            correct_characters=self.__correct_characters,
            guessed_words=self.__guessed_words,
            guesses=self.__guesses,
        )

    """
    Manipulation with character lists
    """

    def __compare_word(self, word: str, position: int) -> WordleState:
        """
        Compares the __word given to the game __word.
        :param word: The __word to test.
        :param position: The position of the __word to examine.
        :return: A character __state, representing how right it was.
        """
        if word[position] == self.__word[position]:
            # This letter is in the correct position.
            self.__add_correct_character(word[position], position)
            return WordleState.Correct
        elif word[position] in self.__word:
            # This letter is in the __word, in the wrong position.
            self.__add_misplaced_character(word[position], position)
            return WordleState.Misplaced
        else:
            # This letter is not in the __word.
            self.__add_wrong_character(word[position])
            return WordleState.Wrong

    def __add_wrong_character(self, char: str) -> None:
        """
        Marks a character for being in the wrong place.
        :param char: The character to mark.
        """
        if char in self.__wrong_characters:
            return
        self.__wrong_characters.append(char)

    def __add_misplaced_character(self, char: str, position: int) -> None:
        """
        Marks a character for being in the __word, and in the correct place.
        :param char: The character to mark.
        :param position: The position where the character is misplaced.
        """
        if char not in self.__correct_characters:
            self.__correct_characters[char] = [position]
        else:
            if position not in self.__correct_characters[char]:
                self.__correct_characters[char].append(position)

    def __add_correct_character(self, char: str, position: int) -> None:
        """
        Marks a character for being in the __word, but in the wrong place.
        :param char: The character to mark.
        :param position: The position where the character is misplaced.
        """
        if char not in self.__misplaced_characters:
            self.__misplaced_characters[char] = [position]
        else:
            if position not in self.__misplaced_characters[char]:
                self.__misplaced_characters[char].append(position)

    """
    Class Methods
    """

    @classmethod
    def response_to_characters(cls, word_response: List[WordleState]) -> str:
        """
        Makes a character response to a WordleState list.
        :param word_response: WordleStates to read.
        :return: Silly character translation.
        """
        retString = ''
        for state in word_response:
            if state == WordleState.Correct:
                retString += cls.char_check
            elif state == WordleState.Misplaced:
                retString += cls.char_quest
            elif state == WordleState.Wrong:
                retString += cls.char_wrong
            else:
                retString += ' '
        return retString

    """
    Public Attributes
    """

    def get_guesses(self) -> int:
        return self.__guesses

    def get_state(self) -> WordleState:
        return self.__state

    def get_word(self) -> str:
        # No cheating!
        if self.get_state() not in (WordleState.Win, WordleState.Lose):
            return ""
        return self.__word

    def get_guessed_words(self) -> List[str]:
        return self.__guessed_words

    def get_wrong_characters(self) -> List[str]:
        return self.__wrong_characters

    def get_misplaced_characters(self) -> Dict[str, List[int]]:
        return self.__misplaced_characters

    def get_correct_characters(self) -> Dict[str, List[int]]:
        return self.__correct_characters


if __name__ == '__main__':
    # Let's play Wordle!
    wordle = Wordle()

    # Start the game.
    response: WordleResponse = wordle.play()
    print(f"Come on, let's play Wordle!\n"
          f"GUESSES: {response.guesses}/{Wordle.max_guesses}\n"
          f"\n")

    # Do the game loop.
    guessed_word_string = ''
    while True:
        guess = input('Your guess: ')
        response: WordleResponse = wordle.play(word=guess)

        # Make sure the response was valid.
        if response.game_state == WordleState.InvalidGuess:
            print("Invalid guess.\n")
        else:
            guessed_word_string += guess + '\n'
            guessed_word_string += Wordle.response_to_characters(response.word_response) + '\n'
        print(f"GUESSES: {response.guesses}/{Wordle.max_guesses}\n"
              f"{guessed_word_string}")

        if response.game_state == WordleState.GameWon:
            print("You won!\n")
            break
        elif response.game_state == WordleState.GameLost:
            print(f"You lost! Boo-hoo.\n"
                  f"Correct word: {wordle.get_word()}\n")
            break

