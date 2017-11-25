import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy import sparse
import sys

try:
    game_indexes = np.load('game_indexes.npy').item()
    user_indexes = np.load('user_indexes.npy').item()
    user_list = np.load('users_list.npy')
    games_list = np.load('games_list.npy')
    data = np.load('data.npy')
except IOError as e:
    print(e)
    print("Data file(s) not found.")
    sys.exit()

# Username to find game recommendations for
username = 'ebreese1'

# Creating the initial Ball Tree that is used for the nearest neighbor algorithm
# is slow, but the generated tree can be saved on disk in the final
# version and after that finding the neighbors of an added user is faster
# (Uses minkowski with p=2, in other words euclidean distance, cosine similarity does not
# work with ball tree)
nbrs = NearestNeighbors(algorithm='ball_tree').fit(data)
distances, indices = nbrs.kneighbors(data)

# Find the nearest neighbors of this data point (start with 10 neighbors)
dist, u_neighbors = nbrs.kneighbors([data[user_indexes[username]]], 10)

o_row = data[user_indexes[username]]

# Search and generate new nearest neighbors, until the desired amount of games that the
# user has not reviewed are found
new_games_found = 0
new_games_limit = 3
new_game_indexes = []
i = 0
while new_games_found < new_games_limit:
    u_neighbors = u_neighbors[0]
    for k in range(len(data[u_neighbors[i]])):
        if data[u_neighbors[i]][k] != 0 and o_row[k] == 0 and k not in new_game_indexes:
            new_games_found = new_games_found + 1
            new_game_indexes.append(k)
    if new_games_found < new_games_limit:
        dist, u_neighbors = nbrs.kneighbors([data[user_indexes[username]]], i+10)
    i = i + 1

# Number of neighbors needed to find to get the amount of recommendations desired
print(i)

# Find and print the recommended game names
print("Recommended Games:")
print(new_game_indexes)
for new_game_index in new_game_indexes:
    print(games_list[new_game_index])