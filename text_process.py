import nltk
import pickle
import re

from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer


# First removes punctuations and numbers. Then removes the list of stop words 
# given from nltk. Then uses the Lancaster stemmer in order to get the root of
# each words
def remove_stems(file):
    new_file = []
    punctuation = re.compile(r'[-.,"?!:;]')
    stemmer = LancasterStemmer()
    for raw_post in file:
        post = raw_post[1]        
        token = nltk.word_tokenize(post)
        new_token = []
        for word in token:
            # Removes punctuations and numbers
            word = punctuation.sub("", word)

            # Stems each word to their roots
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


def process_file(file_name):
    file = pickle.load(open(file_name, "rb")) 
    file = remove_stems(file)
    stop_words = find_stop_words(file,.03,.97)
    
    # Removes the words from stop_words
    file_minus_stop_words = []
    for post in file:
        token = [word for word in post[1] if word not in stop_words]
        file_minus_stop_words.append((post[0],token))
    return file_minus_stop_words


# Need to download stop words first
# Go to python, and input nltk.download()
# Download stopwords under corpus
processed_file = process_file('Data/heidi_status')
output_name = 'Data/heidi_processed_status.p'
pickle.dump(processed_file, open(output_name, "wb"))
