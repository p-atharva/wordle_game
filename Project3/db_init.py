import sqlite3
import typing
import contextlib
import fileinput
import string
import re
from fastapi import FastAPI, Depends, HTTPException, status
import uuid

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: (u.bytes_le))

db  = sqlite3.connect('stats2.db')
db1 = sqlite3.connect('game1.db', detect_types=sqlite3.PARSE_DECLTYPES)
db2 = sqlite3.connect('game2.db', detect_types=sqlite3.PARSE_DECLTYPES)
db3 = sqlite3.connect('game3.db', detect_types=sqlite3.PARSE_DECLTYPES)
db4 = sqlite3.connect('user1.db', detect_types=sqlite3.PARSE_DECLTYPES)
db5 = sqlite3.connect('temp.db', detect_types=sqlite3.PARSE_DECLTYPES)

cursor = db.cursor()
cursor1 = db1.cursor()
cursor2 = db2.cursor()
cursor3 = db3.cursor()
cursor4 = db4.cursor()
cursor5 = db5.cursor()

#check entries in stats db - game table and user table
#usr = cursor.execute("SELECT * FROM users LIMIT 10")
#for usr in cursor.execute("SELECT * FROM users LIMIT 10"):
	#print ('Users in stats db:')
	#print(usr)
	

game = cursor.execute("SELECT * FROM games")
#print ('Games in stats db:')
#print(game.fetchall())

#create table for 3 game shard db's
cursor1.execute("CREATE TABLE IF NOT EXISTS games (uu_id GUID NOT NULL, game_id INTEGER NOT NULL, finished DATE DEFAULT CURRENT_TIMESTAMP, guesses INTEGER, won boolean, PRIMARY KEY(uu_id, game_id))")

cursor2.execute("CREATE TABLE IF NOT EXISTS games (uu_id GUID NOT NULL, game_id INTEGER NOT NULL, finished DATE DEFAULT CURRENT_TIMESTAMP, guesses INTEGER, won boolean, PRIMARY KEY(uu_id, game_id))")

cursor3.execute("CREATE TABLE IF NOT EXISTS games (uu_id GUID NOT NULL, game_id INTEGER NOT NULL, finished DATE DEFAULT CURRENT_TIMESTAMP, guesses INTEGER, won boolean, PRIMARY KEY(uu_id, game_id))")

cursor4.execute("CREATE TABLE IF NOT EXISTS users (uu_id GUID NOT NULL, username VARCHAR UNIQUE)")

#create views for 3 game shared dbs:
#db - game1
cursor1.execute("CREATE INDEX IF NOT EXISTS games_won_idx1 ON games(won)")
cursor1.execute("DROP VIEW wins1")
cursor1.execute("DROP VIEW streaks1")
cursor1.execute("CREATE VIEW wins1 AS SELECT uu_id, COUNT(won) AS wins FROM games WHERE won = TRUE GROUP BY uu_id ORDER BY COUNT(won) DESC")

cursor1.execute("CREATE VIEW streaks1 AS WITH ranks AS ( SELECT DISTINCT uu_id, finished, RANK() OVER(PARTITION BY uu_id ORDER BY finished) AS rank FROM games WHERE won = TRUE ORDER BY uu_id, finished), groups AS (SELECT uu_id,            finished,            rank,            DATE(finished, '-' || rank || ' DAYS') AS base_date        FROM            ranks    )    SELECT        uu_id,        COUNT(*) AS streak,        MIN(finished) AS beginning,        MAX(finished) AS ending    FROM        groups    GROUP BY        uu_id, base_date    HAVING        streak > 1    ORDER BY        uu_id,        finished")

#db - game2
cursor2.execute("CREATE INDEX IF NOT EXISTS games_won_idx2 ON games(won)")
cursor2.execute("DROP VIEW wins2")
cursor2.execute("DROP VIEW streaks2")
cursor2.execute("CREATE VIEW wins2 AS SELECT uu_id, COUNT(won) AS wins FROM games WHERE won = TRUE GROUP BY uu_id ORDER BY COUNT(won) DESC")

cursor2.execute("CREATE VIEW streaks2 AS WITH ranks AS ( SELECT DISTINCT uu_id, finished, RANK() OVER(PARTITION BY uu_id ORDER BY finished) AS rank FROM games WHERE won = TRUE ORDER BY uu_id, finished), groups AS (SELECT uu_id,            finished,            rank,            DATE(finished, '-' || rank || ' DAYS') AS base_date        FROM            ranks    )    SELECT        uu_id,        COUNT(*) AS streak,        MIN(finished) AS beginning,        MAX(finished) AS ending    FROM        groups    GROUP BY        uu_id, base_date    HAVING        streak > 1    ORDER BY        uu_id,        finished")

#db - game3
cursor3.execute("CREATE INDEX IF NOT EXISTS games_won_idx3 ON games(won)")
cursor3.execute("DROP VIEW wins3")
cursor3.execute("DROP VIEW streaks3")
cursor3.execute("CREATE VIEW wins3 AS SELECT uu_id, COUNT(won) AS wins FROM games WHERE won = TRUE GROUP BY uu_id ORDER BY COUNT(won) DESC")

cursor3.execute("CREATE VIEW streaks3 AS WITH ranks AS ( SELECT DISTINCT uu_id, finished, RANK() OVER(PARTITION BY uu_id ORDER BY finished) AS rank FROM games WHERE won = TRUE ORDER BY uu_id, finished), groups AS (SELECT uu_id,            finished,            rank,            DATE(finished, '-' || rank || ' DAYS') AS base_date        FROM            ranks    )    SELECT        uu_id,        COUNT(*) AS streak,        MIN(finished) AS beginning,        MAX(finished) AS ending    FROM        groups    GROUP BY        uu_id, base_date    HAVING        streak > 1    ORDER BY        uu_id,        finished")




#create a temp table with UUID
#cursor5.execute('''CREATE TABLE IF NOT EXISTS temp (guid GUID PRIMARY KEY, word text)''')
#data1 = (uuid.uuid4(), 'check')
#print ('Input data:', data1)
#cursor5.execute('INSERT INTO temp VALUES(?,?)', data1)

#check data in temp table
#cursor5.execute('SELECT * from temp')
#print('Result Data:', cursor5.fetchone())


#create shard db's and populate them by running through main db

#fetch entire game table
#games = cursor.execute("SELECT * FROM games")
#ids = cursor.execute("SELECT * FROM users")
#print(len(games.fetchall()))
#print(games.fetchone()[4])

#loop through all rows and add it to shards

#check number of users
#print(ids.fetchall())
#print(len(ids.fetchall()))

#cursor4.execute("ALTER TABLE users ADD COLUMN us_id GUID")

#shard db based on user id
cursor10 = db.cursor()
cursor11 = db.cursor()
cursor12 = db.cursor()
cursor13 = db.cursor()

for user in cursor10.execute("SELECT * FROM users"):
	us_id = uuid.uuid4()
	#print(us_id)
	cursor4.execute("INSERT INTO users VALUES(?,?)",[us_id, user[1]])		#insert new entry into new user db using UUID
	shard = int(us_id) % 3
	if(shard == 0):
		for game1 in cursor11.execute("SELECT * FROM games where user_id=?",[user[0]]):	#find all games associated with specific user_id
			cursor1.execute("INSERT INTO games VALUES(?,?,?,?,?)",[us_id, game1[1], game1[2], game1[3], game1[4]])		#insert new record into games shard
	elif(shard == 1):
		for game2 in cursor12.execute("SELECT * FROM games where user_id=?",[user[0]]):
			cursor2.execute("INSERT INTO games VALUES(?,?,?,?,?)",[us_id, game2[1], game2[2], game2[3], game2[4]])
	elif(shard == 2):
		for game3 in cursor13.execute("SELECT * FROM games where user_id=?",[user[0]]):
			cursor3.execute("INSERT INTO games VALUES(?,?,?,?,?)",[us_id, game3[1], game3[2], game3[3], game3[4]])

db1.commit()
db2.commit()
db3.commit()
db4.commit()
db5.commit()

