import pickle
import pandas as pd
import itertools
import numpy as np
import scipy.linalg as spl
from scipy.cluster.vq import kmeans, whiten, vq
from pylab import plot,show
import networkx as nx

input_file = 'Data/vu_processed_status_tags.p'

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
            current_pair = [word_pair[0][0], word_pair[1][0]]
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
    graph_df = pd.DataFrame(columns = words, index = words)
    for row, edge in df.T.iteritems():
        graph_df[edge['word1']][edge['word2']] = edge['avg_likes']
        graph_df[edge['word2']][edge['word1']] = edge['avg_likes']

    graph_df = graph_df.convert_objects(convert_numeric = True)

    return graph_df


# Normalized Laplacian
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
    clusters = graph_df.copy()
    clusters['cluster'] = idx
    return clusters

df = calculate_edgeweight(data)
df['avg_likes'] = df['cum_likes']/df['count']
graph_df = build_graph(df)
#clusters = clustering(graph_df)



# density based on top 10 weights
def clustering_max_w(graph_df):
    num_words = 16
    max_pair_dict = {}
    max_likes = pd.Series(index = graph_df.index)
    for word in graph_df.index:
        rank_by_likes = graph_df[word].order(ascending = False)
        max_pair_dict[word] = rank_by_likes[0:num_words]
        max_likes[word] = sum(rank_by_likes[0:num_words])
    max_likes = max_likes.order(ascending = False)
    
    best_words = []
    for best_word in max_likes.index[0:num_words]:
        best_words.append(best_word)
        best_words.extend(max_pair_dict[best_word].keys())
    best_words = set(best_words)
    return best_words

df = calculate_edgeweight(data)
df['avg_likes'] = df['cum_likes']/df['count']
graph_df = build_graph(df)
#clusters = clustering(graph_df)
best_words = clustering_max_w(graph_df)


# DBSCAN
def dbscan_clustering(graph_df):
    graph_df2 = graph_df.replace(0, np.nan)
    db = sklearn.cluster.DBSCAN(eps = 10, min_samples = 5).fit(20/graph_df2)
    unique_labels = set(labels)
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    for k, col in zip(unique_labels, colors):%pas
        if k == -1:
            # Black used for noise.
            col = 'k'
            markersize = 4
        class_members = [index[0] for index in np.argwhere(labels == k)]
        cluster_core_samples = [index for index in core_samples
                                if labels[index] == k]
        for index in class_members:
            x = graph_df2[index]
            if index in core_samples and k != -1:
                markersize = 10
            else:
                markersize = 4
            plt.plot(x[0], x[1], 'o', markerfacecolor=col,
                     markeredgecolor='k', markersize=markersize)
#        plt.xlim(0, 22)
#       plt.ylim(0, 22)
            
    plt.title('Estimated number of clusters: %d' % n_clusters_)
    plt.show()


G = nx.Graph()
for node in best_words:
    G.add_node(node)
smaller_graph = graph_df.loc[best_words][list(best_words)]
for row, edge in smaller_graph.T.iteritems():
    G.add_weighted_edges_from([(edge.name, column, edge[column]) for
    column in edge[edge.notnull()].index])
nx.draw(G,
        node_size=1300,
        font_color='blue',
        node_color = 'white')
plt.show()
