import redis
import sqlite3
import uuid
import json
from fastapi import FastAPI, Depends, HTTPException, status

r = redis.Redis(host='localhost', port=6379, db=0)

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: (u.bytes_le))

db1 = sqlite3.connect('game1.db', detect_types=sqlite3.PARSE_DECLTYPES)
db2 = sqlite3.connect('game2.db', detect_types=sqlite3.PARSE_DECLTYPES)
db3 = sqlite3.connect('game3.db', detect_types=sqlite3.PARSE_DECLTYPES)

cur1 = db1.cursor()
cur2 = db2.cursor()
cur3 = db3.cursor()

cursor1 = db1.cursor()
cursor2 = db2.cursor()
cursor3 = db3.cursor()

usrDict = {}


def appendUsrByWinsRedis():
	u1 = cur1.execute("SELECT * FROM wins1 ORDER BY wins DESC LIMIT 10") # Queries Shard1 to find the top 10 users
	usr = u1.fetchall()
	for x in usr:
		#print(x[0])		
		#users.append({"uuid":str(x[0]), "wins": x[1]}) # Appends results of Shard1 to wins1 list
		usrDict[str(x[0])] = x[1]
		
	u2 = cur2.execute("SELECT * FROM wins2 ORDER BY wins DESC LIMIT 10") # Queries Shard2 to find the top 10 users
	usr2 = u2.fetchall()
	for x in usr2:
		usrDict[str(x[0])] = x[1] # Appends results of Shard1 to wins1 list
	#print(len(wins1))

	u3 = cur3.execute("SELECT * FROM wins3 ORDER BY wins DESC LIMIT 10") # Queries Shard3 to find the top 10 users
	usr3 = u3.fetchall()
	for x in usr3:
		usrDict[str(x[0])] = x[1] # Appends results of Shard3 to wins1 list

appendUsrByWinsRedis()
r.zadd("wins",usrDict)	
print("Leaderboard by number of wins")
print(r.zrange("wins", 0, 10,desc=True))



usrStreaks = {}


def appendUsrByStreaksRedis():
	s1 = cursor1.execute("SELECT * FROM streaks1 ORDER BY streak DESC LIMIT 10") # Queries Shard1 to find the top 10 users by longest streaks
	streaks1 = s1.fetchall()
	for x in streaks1:
		usrStreaks[str(x[0])] = x[1]
	s2 = cursor2.execute("SELECT * FROM streaks2 ORDER BY streak DESC LIMIT 10") # Queries Shard2 to find the top 10 users by longest streaks
	streaks2 = s2.fetchall()
	for x in streaks2:
		usrStreaks[str(x[0])] = x[1]

	s3 = cursor3.execute("SELECT * FROM streaks3 ORDER BY streak DESC LIMIT 10") # Queries Shard3 to find the top 10 users by longest streaks
	streaks3 = s3.fetchall()
	for x in streaks3:
		usrStreaks[str(x[0])] = x[1]

appendUsrByStreaksRedis()


r.zadd("streaks1",usrStreaks)	
print("Leaderboard by number of wins")
print(r.zrange("streaks1", 0, 10,desc=True))

	



