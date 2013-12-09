import pickle
import pandas as pd
import itertools
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

input_file = 'Data/heidi_processed_status_tags.p'
data = pickle.load(open(input_file, 'rb'))

def calculate_edgeweight(data):
    # generate a dataframe of unique word-pairs, the cumulative number of likes, and the number of statuses that contain each word-pair
    colnames = ['pair', 'word1', 'word2', 'cum_likes', 'count']
    df = pd.DataFrame(columns = colnames) # an empty data frame
    i = 0
    for status in data:
        i+=1
        num_likes = status[0]
        # find all combinations of word-pairs in a given status
        word_pairs = itertools.combinations(status[1], 2)
        for word_pair in word_pairs:
            current_pair = [word_pair[0][0], word_pair[1][0]]
            current_pair.sort()
            current_pair = tuple(current_pair)
            
            # if the current word pair has appeared in previous statuses, we want to update the cumulative number of likes and the count
            if current_pair in df['pair'].tolist():
                df['cum_likes'][df['pair'] == current_pair] += num_likes
                df['count'][df['pair'] == current_pair] += 1

            # otherwise, create a new entry for the word pair
            else:
                df = df.append(pd.Series([current_pair, current_pair[0], current_pair[1], num_likes, 1], index = colnames), ignore_index = True)

    # remove words that never got liked
    df = df[df['cum_likes'] != 0]
    df = df.dropna()
    print 'total num of statuses:', i
    return df


# construct the graph with a dataframe of unique word-pairs and edge-weights
def build_graph(df):
    words = list(set(df['word1']) | set(df['word2']))
    graph_df = pd.DataFrame(columns = words, index = words)
    
    for row, edge in df.T.iteritems():
        graph_df[edge['word1']][edge['word2']] = edge['avg_likes']
        graph_df[edge['word2']][edge['word1']] = edge['avg_likes']

    # make sure the entries are stored as numeric data
    graph_df = graph_df.convert_objects(convert_numeric = True)

    return graph_df


# cluster out the group of words contingent to edges of highest weights
def clustering_max_w(graph_df):

    num_words     = 25 # we will look at top num_words words based on average edge weight 
    num_neighbors = 10 # we will add num_neighbors neighbors of the top words to the cluster
    max_pair_dict = {}
    avg_likes     = pd.Series(index = graph_df.index)

    for word in graph_df.index:
        rank_by_likes = graph_df[word].order(ascending = False)
        # pick num_neighbors neighbors of the word. If the word has fewer than num_neighbors neighbors, pick all of its neighbors
        neighbors = min(num_neighbors, len(rank_by_likes[rank_by_likes.notnull()]))
        max_pair_dict[word] = rank_by_likes[0:neighbors]
        avg_likes[word] = rank_by_likes.mean()
    avg_likes = avg_likes.order(ascending = False)
    
    best_words = []
    for best_word in avg_likes.index[0:num_words]:
        best_words.append(best_word)
        best_words.extend(max_pair_dict[best_word].keys())
    best_words = set(best_words)
    return best_words


df = calculate_edgeweight(data)
# calculate the average number of likes for each word pair
df['avg_likes'] = df['cum_likes']/df['count'] 
graph_df = build_graph(df)
best_words = clustering_max_w(graph_df)
# the graph with only the words in the clusters
smaller_graph = graph_df.loc[best_words][list(best_words)]

pickle.dump(best_words, open('Data/heidi_best_words.p', 'wb'))


# Visualization using Networkx
G = nx.Graph()
for node in best_words:
    G.add_node(node)

for row, edge in smaller_graph.T.iteritems():
    # networkx cluster outputs clustering coefficients. Since larger
    G.add_weighted_edges_from([(edge.name, column, 1/edge[column]) for column in edge[edge.notnull()].index])
values = [nx.clustering(G).values()]

nx.draw(G,
        node_size=1300,
        font_color='blue',
        cmap = plt.get_cmap('autumn'), 
        node_color = values)
#plt.savefig('presentation/vu_top12.png')
plt.show()
