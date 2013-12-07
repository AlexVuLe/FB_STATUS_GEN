# Need to download stop words first
# Go to python, and input nltk.download()
# Download 'stopwords', 'chat_words', and 'words' under corpus
# Also need to download enchant by running 'sudo pip install pyenchant'
# If you are using MacOS, unzip the pyenchant egg file in the required_pkgs
# and copy the folder enchant into your Python site-packages folder

import difflib
import enchant
import nltk
import pickle
import re

from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

# First removes punctuations and numbers. Then removes the list of stop words
# given from nltk. Then uses the lemmatizer then the Lancaster stemmer in
# order to get the root of each words. Lemmatizer forms actual words
# from the word list dictionary so the words it forms are actual words,
# but it doesn't get rid of every stems. However, the Lancaster removes
# more stems, but it doesn't check with a dictionary and many of the words
# changed are not actual words.
def remove_stems(file):
    new_file = []
    punctuation = re.compile(r'[.,"?!:;]')
    lemmatizer = WordNetLemmatizer()
    stemmer = LancasterStemmer()

    for raw_post in file:
        post = raw_post[1]
        token = nltk.word_tokenize(post)
        new_token = []
        for word in token:
            # Removes punctuations and change it to lower case
            original_word = punctuation.sub("", word.lower())

            # Stems each word to their roots, but using lemmatizer then Lancaster
            word = lemmatizer.lemmatize(original_word)
            if original_word == word:
                word = stemmer.stem(word)

            # Removes stopwords that are defined in the nltk library
            if word not in nltk.corpus.stopwords.words('english') and word != '':
                new_token.append(word)

        new_file.append((raw_post[0], new_token))
    return new_file


# Input is (the list of posts, lower bound, upper bound)
# Lower and upper bound are the percentiles of words that we wish to ignore
def find_stop_words(file, lower_bound, upper_bound):
    all_posts = []
    stop_words = []
    for raw_post in file:
        all_posts += raw_post[1]

    frequency = FreqDist(all_posts)
    total_count = frequency.B()
    lower_bound = total_count * lower_bound
    upper_bound = total_count * (1 - upper_bound)

    stop_words += frequency.keys()[-int(lower_bound):]
    stop_words += frequency.keys()[:int(upper_bound)]

    return stop_words

# Uses Enchant to correct misspellings. Use the enchant english dictionary
# and the chat words dictionary as reference.
def correct_misspelling(word):
    pwl = enchant.request_pwl_dict(nltk.corpus.nps_chat.words())
    dict = enchant.DictWithPWL("en_US", 'nltk.corpus.nps_chat.words()')

    # Ignores words with symbols/numbers since they are probably not regular words
    punctuation = re.compile(r'[-~ /#<>|0-9]')
    if not re.search(punctuation, word) == None: return word

    # Checks first if the word is already correct and if not, fixes it
    if not dict.check(word):
        suggestions = dict.suggest(word)
        if suggestions == []: return word

        # Returns the closest match to the suggestion list using difflib
        suggested_word = difflib.get_close_matches(word, suggestions, 1)

        if suggested_word == []: return word
        return suggested_word[0]


# The main method that runs text processing
def process_file(file_name):
    file = pickle.load(open(file_name, "rb"))
    file = remove_stems(file)
    #stop_words = find_stop_words(file,.03,.97)
    file_minus_stop_words = []

    # Removes the words from stop_words and fixes misspellings
    for post in file:
        #token = [word for word in post[1] if word not in stop_words]

        # Fixes misspellings
        fixed_token = []
        for word in post[1]:  #token:
            if word not in nltk.corpus.nps_chat.words() and word not in nltk.corpus.words.words():
                word = correct_misspelling(word)
            fixed_token.append(word)

        file_minus_stop_words.append((post[0],fixed_token))

    return file_minus_stop_words


# Need to download stop words first
# Go to python, and input nltk.download()
# Download stopwords under corpus
processed_file = process_file('Data/vu_status.p')
output_name = 'Data/vu_processed_status_misspellings.p'
pickle.dump(processed_file, open(output_name, "wb"))

