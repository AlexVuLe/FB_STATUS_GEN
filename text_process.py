# Input of the program: Two options. Option 1: -s <sentence>. You input a 
# string sentence and it prints the text processed sentence.
# Option 2: -d <input file name> <output file name>.
# Input two strings of file names and it would run text process
# the file.

# Need to download stop words first
# Go to python, and input nltk.download()
# Download 'stopwords', 'chat_words', and 'words' under corpus
# Also need to download enchant by running 'sudo pip install pyenchant'
# If you are using MacOS, unzip the pyenchant egg file in the required_pkgs
# and copy the folder enchant into your Python site-packages folder

import difflib
import enchant
import getopt
import nltk
import numpy
import pickle
import re
import sys

from multiprocessing import Pool
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer


CHAT_WORDS = nltk.corpus.nps_chat.words() 
ENGLISH_WORDS = nltk.corpus.words.words()
PWL = enchant.request_pwl_dict('chat_words')
DICT = enchant.DictWithPWL("en_US", 'chat_words')


# First removes punctuations and numbers and adds in a tag for each word.
# Then removes the list of stop words
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
        token_tags = nltk.pos_tag(token)

        new_token = []
        for word in token_tags:
            # Removes punctuations and change it to lower case
            original_word = punctuation.sub("", word[0].lower())

            # Stems each word to their roots, but using lemmatizer then Lancaster
            stemmed_word = lemmatizer.lemmatize(original_word)
            if original_word == stemmed_word:
                stemmed_word = stemmer.stem(stemmed_word)

            # Removes stopwords that are defined in the nltk library
            if stemmed_word not in nltk.corpus.stopwords.words('english') and stemmed_word != '':
                new_token.append((stemmed_word, word[1]))

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
def correct_misspelling(word_tuple):
    word, tag = word_tuple

    # Ignores words with symbols/numbers since they are probably not regular words
    SMILEY = r"[:;8=][o\-']?[()\[\]/\\\?pPdD*$]+"
    PUNCTUATION = re.compile(r'[-~ /#<>|0-9]')
    if not re.search(SMILEY, word) == None: return word_tuple
    if not re.search(PUNCTUATION, word) == None: return word_tuple


    # Checks first if the word is already correct and if not, fixes it
    if not DICT.check(word) and  word not in CHAT_WORDS and word not in ENGLISH_WORDS:
        suggestions = DICT.suggest(word)

        # Returns the closest match to the suggestion list using difflib
        suggested_word = difflib.get_close_matches(word, suggestions, 1)

        if suggested_word == []: return word_tuple
        return (suggested_word[0], tag)
    else: 
        return word_tuple

# The main method that runs text processing
def process_file(file, remove_frequent = True):

    file = remove_stems(file)
    stop_words = []
    if remove_frequent: stop_words = find_stop_words(file,.05,.97)
    file_minus_stop_words = []
    pool = Pool(processes=4)

    # Removes the words from stop_words and fixes misspellings
    for post in file:
        token = [word for word in post[1] if word not in stop_words]
        
        # Fixes misspellings using a pool creating a new thread for each one
        fixed_token = pool.map(correct_misspelling, token)
        file_minus_stop_words.append((post[0],fixed_token))
        
    return file_minus_stop_words



# Main method. Two options. Option 1: -s <sentence>. You input a 
# string sentence and it prints the text processed sentence.
# Option 2: -d <input file name> <output file name>.
# Input two strings of file names and it would run text process
# the file.
def main(argv):
    if argv[0] == '-s':
        if argv[1] == 'default':
            sentence = 'I smiled, I smile, he smile. Yestereday I killed sombody'
            print process_file([(0, sentence)], False)
        else:
            sentence = argv[1]
            file = [(0, sentence)]
            print process_file(file, False)

    if argv[0] == '-d':
        if argv[1] == 'default':
            file = pickle.load(open('Data/heidi_status.p', "rb"))
            processed_file = process_file(file)
            output_name = 'Data/heidi_processed_status_tags.p'
            pickle.dump(processed_file, open(output_name, "wb"))
        else:
            file = pickle.load(open(argv[1], "rb"))
            processed_file = process_file(file)
            output_name = argv[2]
            pickle.dump(processed_file, open(output_name, "wb"))
 
    


if  __name__ =='__main__':
    main(sys.argv[1:])


