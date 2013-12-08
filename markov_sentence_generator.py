'''
Created on Dec 8, 2013

@author: alex
'''
import pickle
import re
import nltk as n
from collections import Counter
import random

import os
os.chdir('/Users/alex/Documents/workspace/ai_fb_generator')

ENDINGS = set(['\n', '.', '!', '?'])

def random_pick(start_words):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    total = sum(start_words.values())
    for start_word in start_words:
        cumulative_probability += start_words[start_word]/float(total)
        if x < cumulative_probability: 
            break
    return start_word

def separate_sentences(s):
    list_of_s = []
    initial = 0
    for l, i in zip(s, range(len(s))): 
        if l in ENDINGS:
            list_of_s.append(s[initial:i+1])
            initial = i+1
    list_of_s = [s for s in list_of_s if s not in ENDINGS]
    return list_of_s

file = []
for file_name in ['Data/vu_status.p']:
    file = file + pickle.load(open(file_name, "rb"))
    

sents = [s[1] for s in file]
cnt = dict()
start_words = Counter()

for s in sents:
    s = separate_sentences(s)
    for s_i in s:
        s_i = n.word_tokenize(s_i)
        if len(s_i) >= 3:
            if s_i[-1] not in ENDINGS:
                s_i.append('.')
            w1 = s_i[0]
            w2 = s_i[1]
            start_words[(w1,w2)] += 1.
            for next in s_i[2:]:
                if (w1,w2) in cnt:
                    next_words = cnt[(w1,w2)] 
                    if next in next_words:
                        next_words[next] += 1.
                    else:
                        next_words[next] = 1.
                else:
                    cnt[(w1,w2)] = {next:1.}
                w1 = w2
                w2 = next

sentence = ''
start_double = random_pick(start_words)
sentence += start_double[0] + ' ' + start_double[1] 
while start_double[1] not in ENDINGS:
    start_words = cnt[start_double]
    start_word = random_pick(start_words)
    space = ' '
    if start_word in ENDINGS:
        space = ''
    sentence += space + start_word
    start_double = (start_double[1],start_word)
print sentence
