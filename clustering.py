import pickle
import pandas as pd
import itertools

input_file = 'Data/heidi_processed_status.p'

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

    for status in data:
        num_likes  = status[0]
        # all combinations of word-pairs in a given status
        word_pairs = itertools.combinations(status[1], 2)
        for word_pair in word_pairs:
            current_pair = [word_pair[0], word_pair[1]]
            current_pair.sort()
            if word_pair in df['pair']:
                df['cum_likes'][df['pair'] == word_pair] += num_likes
                df['count'][df['pair'] == word_pair] += 1

            else:
                df = df.append(pd.Series([current_pair, current_pair[0], current_pair[1], num_likes, 1], index = colnames), ignore_index = True)
                
    return df

def build_graph(df):
    # construct the graph with a dataframe of unique word-pairs and edge-weights
    words = list(set(df['word1']) | set(df['word2']))
    graph_df = pd.DataFrame(columns = words, index = words).fillna(0)
    for row, edge in df.T.iteritems():
        graph_df[edge['word1']][edge['word2']] = edge['avg_likes']
        graph_df[edge['word2']][edge['word1']] = edge['avg_likes']
    
    return graph_df

df = calculate_edgeweight(data)
df['avg_likes'] = df['cum_likes']/df['count']
graph_df = build_graph(df)
