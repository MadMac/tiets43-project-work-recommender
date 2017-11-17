import time
import sqlite3
import json

from boardgamegeek import BGGClient, BGGApiError, CacheBackendSqlite
# bgg = BGGClient(cache=CacheBackendSqlite(path="H:/bggcache.db", ttl=36000), requests_per_minute=30)
bgg = BGGClient()

conn = sqlite3.connect('testkanta2.db')
cursor = conn.cursor()

boardGamesConn = sqlite3.connect('database.sqlite')
c = boardGamesConn.cursor()

# startid = 1
# endid = 1001
clearTable = False

if clearTable == True:
    conn.execute('''DROP TABLE IF EXISTS alldata''')

conn.execute('''CREATE TABLE IF NOT EXISTS alldata
             (id int, gamedata text)''')


# test = []
# print(test)
retry = 0
# n = startid

allIds = []
for row in c.execute('SELECT "game.id" FROM BoardGames ORDER BY "stats.numcomments" DESC LIMIT 100'):
    allIds.append(row[0])
print(allIds)

n = 0
while n < len(allIds):
    print("n: ", n)
    try:
        print(">Select")
        cursor.execute("SELECT id FROM alldata WHERE id = ?", (allIds[n],))
        data = cursor.fetchall()
        if len(data) != 0:
            n += 1
            continue

        now = time.time()
        print(">Get game")
        g = bgg.game(game_id=allIds[n], rating_comments=True)
        print(g.name)
        # print(g.data())
        end_time = time.time()

        # print(gamedata)
        # print(g.comments)
        print(">Concat comments")
        allComments = []
        for comment in g.comments:
            allComments.append(comment.data())
        # print(allComments)

        g.data()['comments'] = allComments
        gamedata = str(g.data())

        print(">Insert")
        conn.execute("INSERT INTO alldata VALUES (?, ?)",
                     (allIds[n], gamedata,))
        conn.commit()
        print("time taken: " + str(end_time - now))
        retry = 0
        n += 1
    except BGGApiError as err:
        print(err)
        print(retry)
        # if retry < 10:
        print("Retrying")
        # n -= 1
        # else:
        #     n += 1
        retry += 1
        continue

        #  print(g.comments)
conn.close()
