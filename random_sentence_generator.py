'''
Created on Dec 8, 2013

@author: alex
'''
import random
from markov_sentence_generator import ENDINGS
import pickle
import os
os.chdir('/Users/alex/Documents/workspace/ai_fb_gen')

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
    first_word = start_double[0]
    first_word = first_word[0].upper() + first_word[1:]
    second_word =  start_double[1]
    if second_word.isalnum():
        second_word = ' ' + second_word
    sentence +=  first_word + second_word  
    while start_double[1] not in ENDINGS:
        start_words = cnt[start_double]
        start_word = random_pick(start_words)
        space = ' '
        if not start_word[0].isalnum():
            space = ''
        sentence += space + start_word
        start_double = (start_double[1],start_word)
    return sentence
    
def filter(wordbank, restricted):
    for key in wordbank.keys():
        w1, w2 = key
        for k_i in wordbank[key].keys():
            if not restricted.intersection(set([w1, w2, k_i])):
                del wordbank[key][k_i]
        if len(wordbank[key]) == 0:
            del wordbank[key]
    return wordbank

def find_sentence(start_words, markov):
    while True:
        try:
            return generate_sentence(start_words, markov)
            break
        except:
            pass

def main():
    markov = pickle.load(open('Data/markov_dict.p', 'rb'))
    start_words = pickle.load(open('Data/start_words.p', 'rb'))
    cluster = pickle.load(open('Data/vu_best_words.p', 'rb'))
    markov = filter(markov, cluster)
    print find_sentence(start_words, markov)
    
if __name__ == '__main__':
    main()