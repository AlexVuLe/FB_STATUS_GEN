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
os.chdir('/Users/alex/Documents/workspace/ai_fb_gen')

ENDINGS = set(['\n', '.', '!', '?'])

def separate_sentences(s):
    ''' Take in s, a chunk of sentences, 
    and separate it into a list of sentences 
    '''
    list_of_s = []
    initial = 0
    for l, i in zip(s, range(len(s))): 
        if l in ENDINGS:
            list_of_s.append(s[initial:i+1])
            initial = i+1
    list_of_s = [s for s in list_of_s if s not in ENDINGS]
    return list_of_s


def markov_chain(filename, cap=0.03, chunk_size=2048):
    ''' Read in a dataset of tweets and learn to write sentences '''
    cnt = dict()
    start_words = Counter()
    
    # Read in large training set trunk by trunk
    file = open(filename, "rb") 
    filesize = os.stat(filename).st_size
    bytes = 0.
    pct_complete = 0
    while True:
        chunk = file.read(chunk_size)
        if not chunk or pct_complete > cap:
            break
        bytes += float(chunk_size)
        pct_complete = bytes/filesize
        print round(pct_complete*100,1), '%'
        
        # Separate chunk into clean sentences
        chunks = chunk.split('TEXT:\t')
        sents = []
        
        # Because we read by chunks, the first and last sentences might be cut off. Remove
        for t in chunks[1:-1]: 
            LABEL_index = t.find('\r\nLABEL')
            sents.append(t[:LABEL_index]) 
        
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
    file.close()
    return start_words, cnt

def main():
    start_words, cnt = markov_chain('Data/Tweets.txt')
    pickle.dump(start_words, open( "Data/start_words.p", "wb" ))
    pickle.dump(cnt, open( "Data/markov_dict.p", "wb" ))

if __name__ == '__main__':
    main()
