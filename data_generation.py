import sqlite3
import json
import ast
import numpy as np

conn = sqlite3.connect('bgg_kanta.db')

# Limit the number of games to 10 for testing purposes
data = conn.execute('SELECT * FROM alldata LIMIT 600')

game_names = []
user_names = []
users = {}
game_information = {}

for row in data:
    game = ast.literal_eval(row[1])
    game_name = "`" + game['name'] + "`"
    game_names.append(game_name)
    game_information[game_name] = [game['minplayers'], game['maxplayers']]
    for c in game['comments']:
        if c['username'] not in users:
            users[c['username']] = {}
            user_names.append(c['username'])
        users[c['username']][game_name] = c['rating']
conn.close()

# Game indexes dictionary
game_indexes = {}
for i in range(0, len(game_names)):
    game_indexes[game_names[i]] = i

# User names indexes dictionary
user_indexes = {}
for i in range(0, len(user_names)):
    user_indexes[user_names[i]] = i

# Construct numpy array out of the data
data = np.empty(shape=(len(user_names), len(game_names)))
for i in range(0, len(user_names)):
    reviews = np.zeros(len(game_names))
    for key in users[user_names[i]]:
        reviews[game_indexes[key]] = users[user_names[i]][key]
    data[i] = reviews


# Save the game and user indexes and game indexes to disk
# (These can be used to get the game and user indexes by name)
np.save('user_indexes.npy', user_indexes)
np.save('game_indexes.npy', game_indexes)
np.save('games_list.npy', game_names)
np.save('users_list.npy', user_names)
np.save('game_information.npy', game_information)
np.save('data.npy', data)