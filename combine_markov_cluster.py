'''
Created on Dec 8, 2013

@author: alex
'''
import pickle
import os
os.chdir('/Users/alex/Documents/workspace/ai_fb_gen')

markov = pickle.load(open('Data/markov_dict.p', 'rb'))
start_words = pickle.load(open('Data/start_words.p', 'rb'))
