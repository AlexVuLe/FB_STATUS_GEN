'''
Created on Dec 8, 2013

@author: alex
'''
import pickle
import os
os.chdir('/Users/alex/Documents/workspace/ai_fb_gen')

markov = pickle.load(open('Data/markov_dict.p', 'rb'))
start_words = pickle.load(open('Data/start_words.p', 'rb'))
cluster = pickle.load(open('Data/vu_best_words.p', 'rb'))

def filter():
for key in markov.keys:
    w1, w2 = key
    if w1 not in cluster and w2 not in cluster:
        del markov[key]