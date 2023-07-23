"""
Spelling Bee Trainer
"""
import pyttsx3
import os
import pickle
import numpy as np

from PyDictionary import PyDictionary

"""
Word Frequency Manager
"""
save_file = "save.pickle"
words_dir = './words'

def pickle_error_dict(dict):
    """
    Persists the word to error dict to disk, so you can load it back in next time.
    """
    with open(save_file, 'wb') as file:
        pickle.dump(dict, file)

def load_error_dict():
    with open(save_file, 'rb') as file:
        return pickle.load(file)

def init():
    """
    Loads all the words into a hashmap that tracks errors. Words with more errors
    will get picked more.
    """
    if os.path.exists(save_file):
        return load_error_dict()
    
    word_list = []
    for file_name in os.listdir(words_dir):
        with open(os.path.join(words_dir, file_name), "r") as file:
            for line in file:
                if line.rstrip('\n').isalpha():
                    word_list.append(line.strip())
    print(word_list[:100])

    word_to_error = {word: 1 for word in word_list}
    return word_to_error

"""
User Interface
"""

dictionary = PyDictionary()
def print_word_lookup(word):
    """
    Prints a definition of a word.
    """
    print(f"---------------------------------")
    definition = dictionary.meaning(word)
    if definition:
        for part_of_speech, meanings in definition.items():
            print(f"{part_of_speech.capitalize()}:")
            for index, meaning in enumerate(meanings, start=1):
                print(f"{index}. {meaning}")
    else:
        print(f"Definition not found.")
    print(f"---------------------------------")

engine = pyttsx3.init()
def read_word(word):
    """
    Text to speech a word
    """
    engine.say(word)
    engine.runAndWait()


def cli():
    """
    Main trainer loop
    """
    print("Welcome to spelling bee trainer!")
    input("Hit enter to hear the first word...")

    # TODO: chunk the words 100 at a time?
    words_to_errors = init()

    # I think they directly correspond in python 3.x
    words = list(words_to_errors.keys())

    cumsum = sum(words_to_errors.values())
    weights = [val/cumsum for val in words_to_errors.values()]
    # print(cumsum, weights[:100])

    print(words[:100])
    ordered = np.random.choice(words, p=weights, replace=False, size=len(words))

    # TODO: don't need to copy it can just update original map
    new_map = words_to_errors.copy()

    correct = 0
    idx = 0
    while idx < len(ordered):
        word = ordered[idx]

        print(f"\n")
        read_word(word)
        print_word_lookup(word)
        print("\n")
        user = input(f"Word {idx + 1}! Spell the word or hit enter to hear the word again:   ")

        if user == "quit":
            # save to disk
            break
        elif user == "":
            # repeat the word
            read_word(word)
        elif user == "report":
            # generate list of most errored words
            pass
        elif user:
            os.system('cls' if os.name=='nt' else 'clear')
            if user.lower() == word.lower():
                print("That's correct!")
                correct += 1
                if new_map[word] > 1:
                    new_map[word] -= 1
            else:
                # TODO: find some library to highlight differences between the words
                print(f"Your spelling is:                            {user}")
                print(f"That's incorrect, the correct spelling is:   {word}")
                # Weight it heavier when they get it wrong
                # TODO: new_map[word] = new_map[word] * 1.3
                new_map[word] += 3 
            idx += 1
    
    print(f"\n\n\n\n\n")
    print("Saving results to disk!")
    pickle_error_dict(new_map)
    print(f"This session you got {correct} out of {idx + 1} ({correct/(idx+1)}). ")


if __name__ == "__main__":
    cli()