'''
Created on Dec 8, 2013

@author: alex
'''
import random
from markov_sentence_generator import ENDINGS
import pickle
import os
import nltk as n
import sys

from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from IPython.core import error

def random_pick(start_words):
    ''' Pick a random word or tuple of words from its freq dictionary '''
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    total = sum(start_words.values())
    for start_word in start_words:
        cumulative_probability += start_words[start_word]/float(total)
        if x < cumulative_probability: 
            break
    return start_word

def generate_sentence(start_words, cnt):
    ''' Generate a random sentence from dictionaries 
    of start words and markov chain 
    This may fail because some sequence of words may not end with a stop sign
    '''
    sentence = ''
    #Randomly pick a start word from start_words dict based on sample freq
    start_double = random_pick(start_words) 
    first_word = start_double[0]
    first_word = first_word[0].upper() + first_word[1:] #Capitalize the first word
    second_word =  start_double[1]
    if second_word.isalnum():
        second_word = ' ' + second_word #Only add space if next word is not a punctuation
    sentence +=  first_word + second_word  
    
    while start_double[1] not in ENDINGS: #Stop when reach a stop sign
        start_words = cnt[start_double] #Get a list of all possible next words
        start_word = random_pick(start_words) #Choose a random next word based on sample freq
        space = ' '
        if not start_word[0].isalnum():
            space = ''
        sentence += space + start_word
        start_double = (start_double[1],start_word) #Make next tuple
    return sentence

def reduced_form(word):
    ''' Reduce a word to its root to adequately compare with words from cluster'''
    w = WordNetLemmatizer().lemmatize(word) 
    return w.lower()
    
def filter_wordbank(wordbank, restricted):
    ''' Filter wordbank from markov chain with cluster words
    For every three consecutive words, at least one must belong to cluster words
    wordbank: markov chain dict
    restricted: cluster words 
    '''
    for key in wordbank.keys():
        w1, w2 = key
        for k_i in wordbank[key].keys():
            if not restricted.intersection(set([reduced_form(word) for word in [w1, w2, k_i]])):
                del wordbank[key][k_i]
        if len(wordbank[key]) == 0:
            del wordbank[key]
    return wordbank

def find_sentence(start_words, markov):
    ''' Keep trying to find a sentence through markov dict until success '''
    while True:
        try:
            return generate_sentence(start_words, markov)
            break
        except:
            pass
    
if __name__ == '__main__':
    #Get all cluster word files and combine 
    cluster_names = sys.argv[1:]
    if len(cluster_names) == 0:
        raise error('Need files from clustering')
    cluster = set()
    for cluster_file in cluster_names:
        cluster = cluster.union(pickle.load(open('Data/' + cluster_file, 'rb')))
    
    #Ger markov dict, start words and filter markov dict with cluster words
    markov = pickle.load(open('Data/markov_dict.p', 'rb'))
    start_words = pickle.load(open('Data/start_words.p', 'rb'))
    markov = filter_wordbank(markov, cluster)
    print find_sentence(start_words, markov)