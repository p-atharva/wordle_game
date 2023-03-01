'''
Project: Service Orchestration (Project 5)
Authors: Vivek Reddy Gaddam
'''

import sqlite3 
import typing
from datetime import date
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
import uuid
import httpx
from datetime import datetime


app = FastAPI()


#Redirecting to the start new game microservice implemented in project4
@app.get("/game/new")
def new_game(username: str):
	url = "http://127.0.0.1:9999/api/v1/fetch/uuID/" + username	#Fetching the uuid from username - this is custom function defined in microserviceproj3.py as part of project-5
	r = httpx.get(url)
	uuid = r.json()["uuid"]
	today = datetime.now()
	startDate = "2022-01-01" #Considering the application's start date is January 1st, 2022
	formatStartDate = datetime.strptime(startDate,'%Y-%m-%d')
	gameID = (today - formatStartDate).days
	uuidStr = uuid[0][0]
	startUrl = "http://127.0.0.1:8000/startgame/" + uuidStr + "/" + str(gameID)	#Redirecting to the start new game 
	r2 = httpx.post(startUrl)
	startResponse = r2.json()["message"]

	return {"status": startResponse, "user_id":uuidStr, "game_id":gameID}

#Redirecting to respective microservices as mentioned
@app.post("/game/{game_id}")
def guess_validaton(uuid: str, game_id:str, guess: str):
	url1 = "http://127.0.0.1:5100/check/" + guess	#Checking if the word is valid (redirecting to microserve-1 of project-2)
	r1 = httpx.get(url1)
	isValid = r1.json()["flag"]
	url2 = "http://127.0.0.1:8000/get_guesses_rem/" + uuid + "/" + game_id  #Checking the number of guesses remaining - this is another custom function defined in gameStateService.py as part of project-5
	r2 = httpx.get(url2)	
	remGuess = r2.json()["remGuess"]
	numGuess = 6 - remGuess
	haveRemGuess = remGuess > 0
	if isValid == 0:
		return {"status":"invalid", "remaining":remGuess}
	if (haveRemGuess and isValid==1):
		url3 = "http://127.0.0.1:8000/gamestateupdate/" + uuid + "/" + game_id + "/" + guess #Recording the guess and updating the numnber of guesses - redirecting to gamestateupdate in Project 4
		r3 = httpx.post(url3)
		url2 = "http://127.0.0.1:8000/get_guesses_rem/" + uuid + "/" + game_id #Fetching in the updated guesses 
		r2 = httpx.get(url2)	
		remGuess = r2.json()["remGuess"]
		url4 = "http://127.0.0.1:5200/validateguess/" + guess + "/" + game_id #Validating the guess against the answer- redirecting to microservice2 of project2
		r4 = httpx.get(url4)
		crctPos, incrctPos, remWords = r4.json()["result"]["positions"]["letters in correct positions"], r4.json()["result"]["positions"]["present in word but not in right position"], r4.json()["result"]["positions"]["not present in word"]
		if len(crctPos) == 5:
			#Posting the record of win 
			url7 = "http://127.0.0.1:9999/api/v1/gamestatus/" +  uuid + game_id + numGuess + True #Redirecting to to microservice3 of project 3 
			r7 = httpx.post(url7)
			url5 = "http://127.0.0.1:9999/api/v1/gamestats/" + uuid	#Fetching the stats after the update - microservice3 of project3
			r5 = httpx.get(url5)
			#gamesPlayed, gamesWon, currentStreak, maxStreak = r5.json()["gamesPlayed"],r5.json()["gamesWon"], r5.json()["currentStreak"], r5.json()["maxStreak"]
			return {"status": "win", "remaining":remGuess, "stats":r5.json()}
		else: 
			if remGuess>0:
				url2 = "http://127.0.0.1:8000/get_guesses_rem/" + uuid + "/" + game_id #Fetching in the updated guesses 
				r2 = httpx.get(url2)
				return {"status": "incorrect","remaining":remGuess, "GuessList": r2.json()["Guesses"],"letters": {"Correct": crctPos, "present": incrctPos}}
	elif not haveRemGuess:
		url3 = "http://127.0.0.1:8000/gamestateupdate/" + uuid + "/" + game_id + "/" + guess #Recording the guess and updating the numnber of guesses - redirecting to gamestateupdate in Project 4
		r3 = httpx.post(url3)
		url2 = "http://127.0.0.1:8000/get_guesses_rem/" + uuid + "/" + game_id #Fetching in the updated guesses 
		r2 = httpx.get(url2)	
		remGuess = r2.json()["remGuess"]
		#Posting a record of loss
		url10 = "http://127.0.0.1:9999/api/v1/gamestatus/" +  uuid + game_id + str(numGuess) + str(False) #Redirecting to to microservice3 of project 3 
		r10 = httpx.post(url10)
		url6 = "http://127.0.0.1:9999/api/v1/gamestats/" + uuid #Fetching the stats after the update - microservice3 of project3
		client = httpx.Client(timeout=15.0)
		r6 = client.get(url6)
		#gamesPlayed, gamesWon, currentStreak, maxStreak = r6.json()["gamesPlayed"],r6.json()["gamesWon"], r6.json()["currentStreak"], r6.json()["maxStreak"]
		return {"status": "win", "remaining":remGuess, "stats":r6.json()}
		
