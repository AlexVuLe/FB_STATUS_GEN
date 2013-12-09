'''
Created on Dec 8, 2013

@author: alex
'''
import random
from markov_sentence_generator import ENDINGS

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
    '''
    sentence = ''
    start_double = random_pick(start_words)
    sentence += start_double[0] + ' ' + start_double[1] 
    while start_double[1] not in ENDINGS:
        start_words = cnt[start_double]
        start_word = random_pick(start_words)
        space = ' '
        if not start_word[0].isalnum():
            space = ''
        sentence += space + start_word
        start_double = (start_double[1],start_word)
    return sentence


