import sqlite3
import json
import ast

conn = sqlite3.connect('bgg_kanta.db')

data = conn.execute('SELECT * FROM alldata')

game_names = []
users = {}

for row in data:
    game = ast.literal_eval(row[1])
    # Back ticks, because the game names contain spaces
    game_name = "`" + game['name'] + "`"
    game_names.append(game_name)
    for c in game['comments']:
        if c['username'] not in users:
            users[c['username']] = {}
        users[c['username']][game_name] = c['rating']
conn.close()

conn = sqlite3.connect('user_reviews.db')
sql = 'CREATE TABLE IF NOT EXISTS user_reviews(name, {0} {1}'.format(" DEFAULT 0, ".join(game_names), " DEFAULT 0)")
conn.execute(sql)

for user in users:
    columns = ['name']
    values = ["'" + user + "'"]
    for key in users[user]:
        columns.append(key)
        values.append(users[user][key])
    columns = ', '.join(columns)
    values = ', '.join(values)
    conn.execute("INSERT INTO user_reviews (%s) VALUES (%s)" % (columns, values))

conn.commit()
conn.close()