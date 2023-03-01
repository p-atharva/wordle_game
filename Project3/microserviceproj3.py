import sqlite3 
import typing
import datetime
from fastapi import FastAPI, Depends, HTTPException, status
import uuid
sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: (u.bytes_le))

app = FastAPI(servers = [
{"url":"http://127.0.0.1:5301","description":"Second Instance"},
{"url":"http://127.0.0.1:5302","description":"Third Instance"},
],
root_path = "/api/v1/")


con = sqlite3.connect("user1.db", check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
cur = con.cursor()

con1 = sqlite3.connect("game1.db", check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
cur1 = con1.cursor()

con2 = sqlite3.connect("game2.db", check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
cur2 = con2.cursor()

con3 = sqlite3.connect("game3.db", check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
cur3 = con3.cursor()

con4 = sqlite3.connect('user1.db', check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
cur4 = con4.cursor()

# After sharding
# Posting a win or loss for a particular game, along with a timestamp and number of guesses


@app.post("/gamestatus/{username}/{gameid}/{guesses}/{won}",status_code=status.HTTP_201_CREATED)
def game_status(username: str, gameid: int, guesses: int, won: bool, date: typing.Optional[datetime.date] = None):
	usr = cur.execute('''SELECT uu_id FROM users WHERE username = ?''', [username])
	uniqUser = usr.fetchone()[0]
	print(uniqUser)
	if uniqUser == None:
		return{"message":"User does not exist. Enter valid user."}
	else:
		if(date == None): #When date is not provided, insert using default date
			if(int(uniqUser)%3 == 0): #Shard1
				game = cur1.execute('''INSERT INTO games(uu_id,game_id, guesses, won) VALUES(? ,? ,? ,?)''',[uniqUser, gameid, guesses, won]) #Inserts into particular shard
				con1.commit()
				return{"message": "Row inserted  with default timestamp in shard 1"}
			elif(int(uniqUser)%3 == 1): #Shard2
				game = cur2.execute('''INSERT INTO games(uu_id,game_id, guesses, won) VALUES(? ,? ,? ,?)''',[uniqUser, gameid, guesses, won]) #Inserts into particular shard
				con2.commit()
				return{"message": "Row inserted  with default timestamp in shard 2"}
			elif(int(uniqUser)%3 == 2): #Shard3
				game = cur3.execute('''INSERT INTO games(uu_id,game_id, guesses, won) VALUES(? ,? ,? ,?)''',[uniqUser, gameid, guesses, won]) #Inserts into particular shard
				con3.commit()
				return{"message": "Row inserted  with default timestamp in shard 3"}
		elif (date <= datetime.date.today()): #IF date is provided, check if date is less than equal to current date
			if(int(uniqUser)%3 == 0): #Shard1
				game = cur1.execute('''INSERT INTO games(uu_id,game_id, finished, guesses, won) VALUES(? ,? ,? ,?, ?)''',[uniqUser, gameid, date, guesses, won]) #Inserts into particular shard
				con1.commit()
				return{"message": "Row inserted  with user provided timestamp in shard 1"}
			elif(int(uniqUser)%3 == 1): #Shard2
				game = cur2.execute('''INSERT INTO games(uu_id,game_id, finished, guesses, won) VALUES(? ,? ,? ,?, ?)''',[uniqUser, gameid, date, guesses, won]) #Inserts into particular shard
				con2.commit()
				return{"message": "Row inserted  with user provided timestamp in shard 2"}
			elif(int(uniqUser)%3 == 2): #Shard3
				game = cur3.execute('''INSERT INTO games(uu_id,game_id, finished, guesses, won) VALUES(? ,? ,? ,?, ?)''',[uniqUser, gameid, date, guesses, won]) #Inserts into particular shard
				con3.commit()
				return{"message": "Row inserted  with user provided timestamp in shard 3"}
		else: #Users with future date will not be inserted
			return{"message": "Row cannot be inserted with future timestamp"}



# Retrieving the top 10 users by number of wins


@app.get("/topusersbywins")
def top_ten_users():
	wins1 = []
	wins2 =[]
	u1 = cur1.execute("SELECT * FROM wins1 ORDER BY wins DESC LIMIT 10") # Queries Shard1 to find the top 10 users
	usr = u1.fetchall()
	for x in usr:
		wins1.append(x) # Appends results of Shard1 to wins1 list	
	
	u2 = cur2.execute("SELECT * FROM wins2 ORDER BY wins DESC LIMIT 10") # Queries Shard2 to find the top 10 users
	usr2 = u2.fetchall()
	for x in usr2:
		wins1.append(x) # Appends results of Shard1 to wins1 list
	#print(len(wins1))

	u3 = cur3.execute("SELECT * FROM wins3 ORDER BY wins DESC LIMIT 10") # Queries Shard3 to find the top 10 users
	usr3 = u3.fetchall()
	for x in usr3:
		wins1.append(x) # Appends results of Shard3 to wins1 list

	wins1.sort(key = lambda x: x[1], reverse=True) # Sort the wins1 list in descending order

	#print("Wins1:")
	#print(wins1)
	
	for x in range(0, 10):
		wins2.append(wins1[x]) # Selects only the top ten users from wins1 and append them to wins2
		
	return {"Top ten users by wins" : wins2} # return wins2
	


#Retrieving the top 10 users by longest streak


@app.get("/topusersbystreaks")
def top_ten_streaks():
	streaks1 = [] # list to store top 10 users by longest streak
	streaks2 =[]
	u1 = cur1.execute("SELECT * FROM streaks1 ORDER BY streak DESC LIMIT 10") # Queries Shard1 to find the top 10 users by longest streaks
	usr = u1.fetchall()
	for x in usr:
		streaks1.append(x)	

	u2 = cur2.execute("SELECT * FROM streaks2 ORDER BY streak DESC LIMIT 10") # Queries Shard2 to find the top 10 users by longest streaks
	usr2 = u2.fetchall()
	for x in usr2:
		streaks1.append(x)
	#print(len(wins1))

	u3 = cur3.execute("SELECT * FROM streaks3 ORDER BY streak DESC LIMIT 10") # Queries Shard3 to find the top 10 users by longest streaks
	usr3 = u3.fetchall()
	for x in usr3:
		streaks1.append(x)

	streaks1.sort(key = lambda x: x[1], reverse=True) # Sort streaks1 in desending order by the longest streak of users

	#print("Wins1:")
	#print(wins1)
	
	for x in range(0, 10):
		streaks2.append(streaks1[x]) # Select first 10 users from streaks1 and append them to streaks2

	return {"Top ten streaks" : streaks2} # return streaks2
	

#Retrieve game stats for a user

@app.get("/gamestats/{uu_id}")
def get_gameStatus(uu_id: uuid.UUID):
	#s = uuid.UUID(uu_id).hex
	shard_db = int(uu_id) % 3 	# Select the proper shard using the modulo operation
	if shard_db == 0:
		conn = sqlite3.connect("game1.db") # If Shard 0, connect to game1.db
		cursor = conn.cursor()
		maxStreak = 0	# To calculate max streak
		streaks = cursor.execute("SELECT * FROM streaks1 WHERE uu_id=?",[uu_id])
		streakList = ([x[1] for x in streaks.fetchall()]) # Select streaks for the input uuid
		if len(streakList) != 0:
			maxStreak = max(streakList) # Calculate the max streak if the length of the streak list is not zero
	
		currStreakUser = 0  # To calculate current streak
		currStreak = cursor.execute("SELECT * FROM streaks1 WHERE uu_id=?",[uu_id])
		currStreakCheck = [y[1] for y in currStreak.fetchall() if y[3] == datetime.date.today()] #Last record to be compared with today's date, current streak will be incremented
		if (len(currStreakCheck) != 0):								# if days are consecutive
			currStreakUser = currStreak
		# Calculate guesses
		guess = cursor.execute("SELECT * FROM games WHERE uu_id = ?",[uu_id])
		guessList = [ z[3] for z in guess.fetchall() if z[4] == 1]
		gamesWon = len(guessList)
		# Calculate failures
		fail = cursor.execute("SELECT * FROM games WHERE uu_id = ?",[uu_id])
		failList = [ z[3] for z in fail.fetchall() if z[4] == 0]
		gamesLost = len(failList)
	
		Dict = {
			"1": guessList.count(1),
			"2": guessList.count(2),
			"3": guessList.count(3),
			"4": guessList.count(4),
			"5": guessList.count(5),
			"6": guessList.count(6),
			"fail": len(failList)
			}
		
		winPercentage = ((gamesWon)/(gamesWon + gamesLost))*100 # Calculate win%
		gamesPlayed = (gamesWon + gamesLost)		# Calculate total games played by user
		gamesWin = gamesWon				# Calculate total games won by user
		#Calculate average guesses
		avgGuess = ((1*guessList.count(1) + 2*guessList.count(2) + 3*guessList.count(3) + 4*guessList.count(4) + 5*guessList.count(5) + 6*guessList.count(6))//gamesPlayed) 
		
		
		return { "currentStreak" : currStreakUser, "maxStreak" : maxStreak, "guesses" : Dict, "winPercentage" : int(winPercentage), "gamesPlayed" : gamesPlayed, "gamesWon" : gamesWin, "averageGuesses" : avgGuess}
	elif shard_db == 1:
		conn = sqlite3.connect("game2.db")
		cursor = conn.cursor()
		maxStreak = 0
		streaks = cursor.execute("SELECT * FROM streaks2 WHERE uu_id=?",[uu_id])
		streakList = ([x[1] for x in streaks.fetchall()])
		if len(streakList) != 0:
			maxStreak = max(streakList)
		
		currStreakUser = 0
		currStreak = cursor.execute("SELECT * FROM streaks2 WHERE uu_id=?",[uu_id])
		currStreakCheck = [y[1] for y in currStreak.fetchall() if y[3] == datetime.date.today()]
		if (len(currStreakCheck) != 0):
			currStreakUser = currStreak

		guess = cursor.execute("SELECT * FROM games WHERE uu_id = ?",[uu_id])
		guessList = [ z[3] for z in guess.fetchall() if z[4] == 1]
		gamesWon = len(guessList)
		
		fail = cursor.execute("SELECT * FROM games WHERE uu_id = ?",[uu_id])
		failList = [ z[3] for z in fail.fetchall() if z[4] == 0]
		gamesLost = len(failList)
		
		Dict = {
			"1": guessList.count(1),
			"2": guessList.count(2),
			"3": guessList.count(3),
			"4": guessList.count(4),
			"5": guessList.count(5),
			"6": guessList.count(6),
			"fail": len(failList)
			}
		
		winPercentage = ((gamesWon)/(gamesWon + gamesLost))*100
		gamesPlayed = (gamesWon + gamesLost)
		gamesWin = gamesWon
		avgGuess = ((1*guessList.count(1) + 2*guessList.count(2) + 3*guessList.count(3) + 4*guessList.count(4) + 5*guessList.count(5) + 6*guessList.count(6))//gamesPlayed)
		
		
		return { "currentStreak" : currStreakUser, "maxStreak" : maxStreak, "guesses" : Dict, "winPercentage" : int(winPercentage), "gamesPlayed" : gamesPlayed, "gamesWon" : gamesWin, "averageGuesses" : avgGuess}
	elif shard_db == 2:
		conn = sqlite3.connect("game3.db")
		cursor = conn.cursor()
		maxStreak = 0
		streaks = cursor.execute("SELECT * FROM streaks3 WHERE uu_id=?",[uu_id])
		streakList = ([x[1] for x in streaks.fetchall()])
		if len(streakList) != 0:
			maxStreak = max(streakList)
		
		currStreakUser = 0
		currStreak = cursor.execute("SELECT * FROM streaks3 WHERE uu_id=?",[uu_id])
		currStreakCheck = [y[1] for y in currStreak.fetchall() if y[3] == datetime.date.today()]
		if (len(currStreakCheck) != 0):
			currStreakUser = currStreak

		guess = cursor.execute("SELECT * FROM games WHERE uu_id = ?",[uu_id])
		guessList = [ z[3] for z in guess.fetchall() if z[4] == 1]
		gamesWon = len(guessList)
		
		fail = cursor.execute("SELECT * FROM games WHERE uu_id = ?",[uu_id])
		failList = [ z[3] for z in fail.fetchall() if z[4] == 0]
		gamesLost = len(failList)
		
		Dict = {
			"1": guessList.count(1),
			"2": guessList.count(2),
			"3": guessList.count(3),
			"4": guessList.count(4),
			"5": guessList.count(5),
			"6": guessList.count(6),
			"fail": len(failList)
			}
		
		winPercentage = ((gamesWon)/(gamesWon + gamesLost))*100
		gamesPlayed = (gamesWon + gamesLost)
		gamesWin = gamesWon
		avgGuess = ((1*guessList.count(1) + 2*guessList.count(2) + 3*guessList.count(3) + 4*guessList.count(4) + 5*guessList.count(5) + 6*guessList.count(6))//gamesPlayed)
		
		
		return { "currentStreak" : currStreakUser, "maxStreak" : maxStreak, "guesses" : Dict, "winPercentage" : int(winPercentage), "gamesPlayed" : gamesPlayed, "gamesWon" : gamesWin, "averageGuesses" : avgGuess}
	
	
