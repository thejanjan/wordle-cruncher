"""
A bot that analyzes Wordle.py.
Keeps up with:
    - How many guesses each word
    - The most successful starting words (rated by score of word : guess count)

Guessing algorithms (with elimination):
    - Random (guess list)
    - Random (answer list)
    - Best Pick
"""
from copy import copy
from time import time

from core.WordleSubclasses import *
from core.Wordle import *
from collections import defaultdict


class WordleAnalyzer:
    """
    Base class for Wordle guessing tactics.
    """

    wordle_class = WordleEndless

    def __init__(self, index):
        self.index = index
        self.dictionary = {}

    @classmethod
    def get_dictionary(cls) -> dict:
        raise NotImplementedError

    def set_dictionary(self, dictionary) -> None:
        self.dictionary = dictionary

    def get_best_guess(self, useResponse: WordleResponse = None):
        raise NotImplementedError

    @classmethod
    def print_study(cls, games: int = 1, result_count: int = 20) -> None:
        """
        Does a lot of simulations with this Wordle class.
        Prints the results of such.
        :return:
        """
        def run_game(word, index, dictionary) -> WordleResponse:
            """
            Runs a game of Wordle.
            :return: The final WordleResponse.
            """
            analyzer = cls(index)
            analyzer.set_dictionary(dictionary)
            wordle = cls.wordle_class(word=word)
            response = wordle.play()
            while response.game_state not in (WordleState.GameWon, WordleState.GameLost):
                if not analysis_error_checking:
                    response = wordle.play(analyzer.get_best_guess(response))
                else:
                    try:
                        response = wordle.play(analyzer.get_best_guess(response))
                    except IndexError as e:
                        print(e)
                        print("\nAn exception was caught during analysis.\n")
                        print("Exception results:")
                        print(f"WORD: {wordle.get_word()}\n"
                              f"GUESSES: {response.guesses}\n"
                              f"GUESSED WORDS: {response.guessed_words}\n"
                              f"CORRECT: {response.correct_characters}\n"
                              f"MISPLACED: {response.misplaced_characters}\n"
                              f"WRONG: {response.wrong_characters}\n")
                        raise e
            return response

        # Init variables for study
        guesses_per_target_word = {}
        guesses_per_start_word = {}

        # Iterate over the games
        print("=== BEGIN WORDLE ANALYSIS ===")
        print("Entering game analysis phase.")
        print(f"Wordle class: {cls.__name__}")
        review_list = answer_list * games
        dictionary = cls.get_dictionary()
        time_durations = []
        for i, word in enumerate(review_list):
            a = time()
            print(f"Analyzing '{word}' - {i + 1} / {len(review_list)} ({round(((i + 1) / len(review_list)) * 100, 2)}%)")
            for game_count in range(len(review_list)):
                final_response = run_game(word=word, index=game_count, dictionary=dictionary)
                start_word = final_response.guessed_words[0]

                # Append target's result to guess dict
                if word not in guesses_per_target_word:
                    guesses_per_target_word[word] = [final_response.guesses]
                else:
                    guesses_per_target_word[word].append(final_response.guesses)
                if start_word not in guesses_per_start_word:
                    guesses_per_start_word[start_word] = [final_response.guesses]
                else:
                    guesses_per_start_word[start_word].append(final_response.guesses)
            b = time()
            time_durations.append(b - a)
            seconds_to_go = (sum(time_durations) / len(time_durations)) * (len(review_list) - (i + 1))
            time_word = 'seconds'
            if seconds_to_go > 3600:
                seconds_to_go /= 3600
                time_word = 'hours'
            elif seconds_to_go > 60:
                seconds_to_go /= 60
                time_word = 'minutes'
            print(f"Finished analyzing '{word}' in {round(b - a, 2)} seconds. "
                  f"Estimating {round(seconds_to_go, 2)} {time_word} to go.")
        print("Game results obtained.")
        print("=== END WORDLE ANALYSIS ===")
        print('')

        # Compute results
        print("Computing results...")

        sorted_guesses = list(guesses_per_target_word.keys())
        sorted_guesses.sort(
            key=lambda l: sum(guesses_per_target_word[l])/max(len(guesses_per_target_word[l]), 1)
        )

        sorted_guesses_initial = list(guesses_per_start_word.keys())
        sorted_guesses_initial.sort(
            key=lambda l: sum(guesses_per_start_word[l]) / max(len(guesses_per_start_word[l]), 1)
        )

        print("Done.")
        print('')

        # Get the guesses per target word lined up
        print(f"Top {result_count} easiest words to guess:")
        for i in range(result_count):
            word = sorted_guesses[i]
            guess_count = round(sum(guesses_per_target_word[word]) / max(len(guesses_per_target_word[word]), 1), 3)
            print(f"{i + 1}. {word} with {guess_count} guesses")
        print('')
        print(f"Top {result_count} hardest words to guess:")
        for i in range(result_count):
            word = sorted_guesses[-(i + 1)]
            guess_count = round(sum(guesses_per_target_word[word]) / max(len(guesses_per_target_word[word]), 1), 3)
            print(f"{i + 1}. {word} with {guess_count} guesses")
        print('')
        # Get the guesses per start word lined up
        print(f"Top {result_count} best guess counts from initial word:")
        for i in range(result_count):
            word = sorted_guesses_initial[i]
            guess_count = round(sum(guesses_per_start_word[word]) / max(len(guesses_per_start_word[word]), 1), 3)
            print(f"{i + 1}. {word} with {guess_count} guesses")
        print('')
        print(f"Top {result_count} worst guess counts from initial word:")
        for i in range(result_count):
            word = sorted_guesses_initial[-(i + 1)]
            guess_count = round(sum(guesses_per_start_word[word]) / max(len(guesses_per_start_word[word]), 1), 3)
            print(f"{i + 1}. {word} with {guess_count} guesses")
        print('')
        print('End of analysis.')

        # Output best initial guesses into a file
        print('Writing best initial words to file...')
        with open('../wordlist/top_initial_word_list.txt', mode='w') as file:
            for word in sorted_guesses_initial:
                file.write(word + '\n')
        print('Written.')


class WARandomAnswer(WordleAnalyzer):
    """
    Guesses the result based on randomizing the potential answers.
    """

    use_list = answer_list

    @classmethod
    def get_dictionary(cls) -> dict:
        set_list = cls.use_list[:]
        ret_dict = defaultdict(list)
        for word in set_list:
            ret_dict[word[0]].append(word)
        return dict(ret_dict)

    def get_best_guess(self, response: WordleResponse = None):
        if response.wrong_characters or response.misplaced_characters or response.correct_characters:
            potential_list = []

            # first get our shortened list based on our dictionary
            check_list = []
            for letter in self.dictionary:
                if letter in response.wrong_characters:
                    continue
                if letter in response.misplaced_characters:
                    if 0 in response.misplaced_characters[letter]:
                        continue
                if letter in response.correct_characters:
                    if 0 in response.correct_characters[letter]:
                        check_list = self.dictionary[letter]
                        break
                check_list += self.dictionary[letter]

            # check every letter of every word like a boss
            for word in check_list[:]:
                acceptableWord = True

                for letter in response.misplaced_characters:
                    if letter not in word:
                        continue

                for i, letter in enumerate(word):
                    # if it's a wrong character, then no thank you.
                    if letter in response.wrong_characters:
                        acceptableWord = False
                        break

                    # if this character is in a position known to be misplaced, then no thank you.
                    if letter in response.misplaced_characters:
                        if i in response.misplaced_characters[letter]:
                            acceptableWord = False
                            break

                    # if there is a correct character in this position,
                    # and we're not it, then no thank you.
                    for correct_letter, correct_places in response.correct_characters.items():
                        if i in correct_places:
                            if letter != correct_letter:
                                acceptableWord = False
                                break

                    if not acceptableWord:
                        break

                if acceptableWord:
                    # if it's a good word, accept it
                    potential_list.append(word)

            return random.choice(potential_list)

        # this is our first pick, so use an index from the use list
        return self.use_list[self.index % len(self.use_list)]


class WARandomGuess(WARandomAnswer):
    """
    Guesses the result based on randomizing the potential guesses.
    """

    use_list = guess_list


if __name__ == '__main__':
    WARandomAnswer.print_study()
