import ast
import re
import requests
import typing

hangman_stages: list[str] = [
    '''
      |
      |
      |
      |
      |
=========\n''', '''
  +---+
      |
      |
      |
      |
      |
=========\n''', '''
  +---+
  |   |
      |
      |
      |
      |
=========\n''', '''
  +---+
  |   |
  O   |
      |
      |
      |
=========\n''', '''
  +---+
  |   |
  O   |
  |   |
      |
      |
=========\n''', '''
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========\n''', '''
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========\n''', '''
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========\n''', '''
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========\n''']


def init() -> None:
    """
    Begins the hangman program for the user.
    """

    print("Welcome to Hangman!")
    start: str = input("Would you like to start the game? (y/n): ").lower()

    if start == "yes" or start == "y":
        print("Generating word, this may take a while...")
        word: str = generate_word()
        run_guesses(word)
    else:
        print("Cancelling game...")
        exit(0)


def generate_word() -> str:
    """
    Generates a random word for the hangman game.
    """

    response: requests.models.Response = requests.get(
        "https://random-word-api.herokuapp.com/word")
    word: str = ast.literal_eval(response.content.decode("utf-8"))[0].lower()

    while len(word) < 4 or len(word) > 7:
        response: requests.models.Response = requests.get(
            "https://random-word-api.herokuapp.com/word")
        word: str = ast.literal_eval(
            response.content.decode("utf-8"))[0].lower()

    return word


def display_info(guessed_word: str, used_letters: list[str], used_words: list[str]) -> None:
    """
    Displays the current state of the hangman game.
    """

    used_letters.sort()
    used_words.sort()

    print("\n" + "Current word: " + guessed_word)
    print("Used letters: " + (", ".join(used_letters)
          if len(used_letters) > 0 else "none"))
    print("Used words: " + (", ".join(used_words)
          if len(used_words) > 0 else "none") + "\n")


def run_guess(guess: str, guessed_word: str, correct_word: str) -> dict[str, list[str]]:
    """
    Parses a single guess and updates the game accordingly.
    """

    if len(guess) > 1:
        if " ".join(guess) == correct_word:
            guessed_word: str = " ".join(guess)
    elif len(guess) == 1:
        correct_letters: list[dict[str, typing.Any]] = [{
            "letter": guess,
            "index": i
        } for i in [m.start() for m in re.finditer(
            guess, correct_word)]]

        for letter in correct_letters:
            guessed_word: str = guessed_word[:letter["index"]] + \
                letter["letter"] + guessed_word[letter["index"] + 1:]

    return guessed_word


def run_guesses(word: str) -> None:
    """
    Runs the actual game itself.
    """

    tries: int = 0
    guessed_word: str = ("_ " * (len(word) - 1)) + "_"
    correct_word: str = " ".join(word)
    used_words: list[str] = []
    used_letters: list[str] = []

    display_info(guessed_word, used_letters, used_words)
    guess: str = input("Guess a letter/word: ").lower().strip()

    while len(guess.split(" ")) > 1:
        guess: str = input(
            "Please provide a single letter/word: ").lower().strip()

    tries += 1
    guessed_word: str = run_guess(guess, guessed_word, correct_word)

    while guessed_word != correct_word:
        if tries == len(hangman_stages):
            used_letters.sort()
            used_words.sort()

            print(f"You have lost the game! The correct word was {word}.")
            print(
                f"It took you {tries} {'tries' if tries > 1 else 'try'} to attempt to guess the word.")
            print("Used letters: " + (", ".join(used_letters)
                                      if len(used_letters) > 0 else "none"))
            print("Used words: " + (", ".join(used_words)
                                    if len(used_words) > 0 else "none"))
            exit(0)

        if len(guess) > 1:
            tries += 1

            if guess in used_words:
                print("You have already used that word!")
            else:
                print("The word you provided was incorrect.")
                used_words.append(guess)

            display_info(guessed_word, used_letters, used_words)
            print(hangman_stages[tries - 1])

            if tries < len(hangman_stages):
                guess: str = input(
                    "Please provide another single letter/word: ").lower().strip()
                guessed_word: str = run_guess(
                    guess, guessed_word, correct_word)
        elif len(guess) == 1:
            tries += 1

            if guess in used_letters:
                print("You have already used that letter!")
            else:
                if not guess in correct_word.split(" "):
                    print("The letter you provided is not in the word.")
                else:
                    print(
                        f"Correct! The letter {guess} has {correct_word.count(guess)} {'occurences' if correct_word.count(guess) > 1 else 'occurence'} in the word.")

                used_letters.append(guess)

            display_info(guessed_word, used_letters, used_words)
            print(hangman_stages[tries - 1])

            if tries < len(hangman_stages):
                guess: str = input(
                    "Please provide another single letter/word: ").lower().strip()
                guessed_word: str = run_guess(
                    guess, guessed_word, correct_word)

    used_letters.sort()
    used_words.sort()

    print(f"\nCorrect! The word was {word}.")
    print(
        f"It took you {tries} {'tries' if tries > 1 else 'try'} to guess the word.")
    print("Used letters: " + (", ".join(used_letters)
          if len(used_letters) > 0 else "none"))
    print("Used words: " + (", ".join(used_words)
          if len(used_words) > 0 else "none"))


init()
