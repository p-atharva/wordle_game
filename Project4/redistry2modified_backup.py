import redis
import json
import datetime
import typing
import contextlib
import fileinput
import string
from fastapi import FastAPI, Depends, Response, HTTPException, status
import uuid
import sqlite3

conn = redis.Redis(host='localhost', port=6379, db=0)
usergames = []

app = FastAPI()



usergames =[{"id": "e4300b9b-56fo-47ca-b205-28459-5fo747a", "game":{"gameid": 123, "numguesses": 0, "guesses": []}}] # Adding debugging data to Redis

conn.set("Games",json.dumps(usergames))


@app.post("/startgame/{userid}/gameid}")
def startgame(userid: str, gameid: int):
	flag = False
	users = json.loads(conn.get("Games"))
	for i in range(len(users)):
		if (users[i]["id"] == userid and users[i]["game"]["gameid"] == gameid):
			flag = True
			return {"message": "Cannot start the game newly"}
			#break

	if flag == False:
		users.append({"id":userid, "game":{"gameid":gameid , "numguesses" : 0, "guesses":[]}})
		conn.set("Games",json.dumps(users))
		list_of_users = json.loads(conn.get("Games"))
		return {"message": "User added", "id": userid, "gameid":gameid }



@app.post("/gamestateupdate/{userid}/gameid}/{guessword}")
def updategamestatus(userid: str, gameid: int, guessword: str):
	usergm = json.loads(conn.get("Games"))
	present = False
	for i in range(len(usergm)):
		gamestatus = conn.get("Games")
		
		print("Gamestatus:")
		print(json.loads(gamestatus))
		if(usergm[i]["id"] == userid and usergm[i]["game"]["gameid"] == gameid):
			present = True
			numguesses = json.loads(gamestatus)[i]["game"]["numguesses"]
			if(numguesses < 6):
				#gm = {}
				numguesses += 1
				usergm[i]["game"]["numguesses"] = numguesses
				usergm[i]["game"]["guesses"].append(guessword)
				conn.set("Games",json.dumps(usergm))
				return {"User ID": usergm[i]["id"],"Game ID": usergm[i]["game"]["gameid"], "NumGuesses": usergm[i]["game"]["numguesses"], "Guesses": usergm[i]["game"]["guesses"]}
			else:
				return {"message": "Cannot enter any more guesses"}
		else:
			present = False

	if present == False:	
			usergame ={"id": userid, "game":{"gameid": gameid, "numguesses": 1, "guesses": [guessword]}}
			usergm.append(usergame)
			conn.append("Games",json.dumps(usergm))
			return {"message":"User has not started the game"}


	
@app.get("/gamestaterestore/{userid}/gameid}")
def restoregamestatus(userid: str, gameid: int):
	usergames1 = json.loads(conn.get("Games"))
	#return {"len":type(usergames1)}
	#for i in range(len(usergames1)):
	for i in usergames1:
		if i["id"] == userid and i["game"]["gameid"] == gameid:
			
			numguesses = i["game"]["numguesses"]
			numguesses = int(numguesses)
			guessesremain = 6 - numguesses
			
			return {"message" : "Requested information", "User ID": i["id"], "Game ID": i["game"]["gameid"], "NumGuesses": i ["game"]["numguesses"], "Guesses": i["game"]["guesses"], "Guesses Reamining": guessesremain}

	return {"message" : "The user hasn't played the game"}	
			
			
		
	
		

