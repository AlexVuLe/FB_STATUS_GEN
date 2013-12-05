import pickle
import pandas as pd
import itertools
import numpy as np
import scipy.linalg as spl
from scipy.cluster.vq import kmeans, whiten, vq
from pylab import plot,show

input_file = 'Data/vu_processed_status.p'

data = pickle.load(open(input_file, 'rb'))

'''
class pair:
    def __init__(self, word1, word2):
        self.word1 = word1
        self.word2 = word2
    
    def __eq__(self, other):
        return (self.word1 == other.word1 and self.word2 == other.word2) or (self.word1 == other.word2 and self.word2 == other.word1)

    def __str__(self):
        return str((self.word1, self.word2))

    def __repr__(self):
        return str((self.word1, self.word2))
'''

def calculate_edgeweight(data):
    # generate a dataframe of unique word-pairs, the cumulative number of likes, and the number of statuses that contain each word-pair
    colnames = ['pair', 'word1', 'word2', 'cum_likes', 'count']
    df = pd.DataFrame(columns = colnames)
    i = 0
    for status in data:
        i+=1
        num_likes  = status[0]
        # all combinations of word-pairs in a given status
        word_pairs = itertools.combinations(status[1], 2)
        for word_pair in word_pairs:
            current_pair = [word_pair[0], word_pair[1]]
            current_pair.sort()
            current_pair = tuple(current_pair)
            if current_pair in df['pair'].tolist():
#                print current_pair
                df['cum_likes'][df['pair'] == current_pair] += num_likes
                df['count'][df['pair'] == current_pair] += 1

            else:
                df = df.append(pd.Series([current_pair, current_pair[0], current_pair[1], num_likes, 1], index = colnames), ignore_index = True)
    df = df[df['cum_likes'] != 0]
    df = df.dropna()
    print 'total num of statuses:', i
    return df

def build_graph(df):
    # construct the graph with a dataframe of unique word-pairs and edge-weights
    words = list(set(df['word1']) | set(df['word2']))
    graph_df = pd.DataFrame(columns = words, index = words).fillna(0)
    for row, edge in df.T.iteritems():
        graph_df[edge['word1']][edge['word2']] = edge['avg_likes']
        graph_df[edge['word2']][edge['word1']] = edge['avg_likes']
    
    return graph_df

def clustering(graph_df):
    
    d_matrix = np.diag(graph_df.sum())
    w_matrix = graph_df.as_matrix()
    l_matrix = d_matrix - w_matrix
    e_value, e_vector = spl.eig(l_matrix, d_matrix)
    U = np.matrix(e_vector[0:2]).T
    centroids, _ = kmeans(U, 2)
    idx,_ = vq(U,centroids)
    plot(U[idx==0,0],U[idx==0,1],'ob',
         U[idx==1,0],U[idx==1,1],'or')
    show()
    return idx

df = calculate_edgeweight(data)
df['avg_likes'] = df['cum_likes']/df['count']
graph_df = build_graph(df)
idx = clustering(graph_df)
