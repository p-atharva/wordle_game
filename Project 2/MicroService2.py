import sqlite3
import typing
import contextlib
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI()

#database function
def getDataBase():
     with contextlib.closing(sqlite3.connect('answers.db')) as db:
                db.row_factory = sqlite3.Row
                yield db


# Checking a valid guess against the answer
@app.get("/validateguess/{word}/{gameid}")
def check_word(word: str, gameid : int, db: sqlite3.Connection = Depends(getDataBase)):

	cursor = db.execute("SELECT * FROM answer WHERE game_id = ?", [gameid])
	actual_word = cursor.fetchone()[1]
	positions = {}
	positions["letters in correct positions"] = list()
	positions["present in word but not in right position"] = list()
	positions["not present in word"] = list()
	result = {}

	#Loop to compare the positons of all letters
	for pos in range (0,len(word)):
		if word[pos] == actual_word[pos]:
			positions["letters in correct positions"].append(word[pos])
		elif word[pos] in actual_word and word[pos] != actual_word[pos]:
			positions["present in word but not in right position"].append(word[pos])
		else:
			positions["not present in word"].append(word[pos])
	
	result["positions"] = positions
	result["gameid"] = gameid
	result["guess_word"] = word
	return {"result":result}


# Changing the answers for future games
@app.put("/update/{gameid}/{word}")
def update_word(gameid: int, word: str, db: sqlite3.Connection = Depends(getDataBase)):

	cursor = db.execute("SELECT * FROM answer WHERE game_id = ?", [gameid])
	count = cursor.fetchone()
	if count is not None:  #If we find the word in the answers
		cursor = db.execute("UPDATE answer SET word = ? WHERE game_id = ?",[word, gameid])
		db.commit()
		return {"message":"Word updated successfully"}
	else:
		return {"message":"no such GameID present in answers"}

#	
#	try:
#		cursor = db.execute("UPDATE answer SET word = ? WHERE game_id = ?",[word, gameid])
#		db.commit()
#	except sqlite3.IntegrityError as e:
#		raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail={"type": type(e).__name__, "msg": str(e)},)
#	return {"message": "Word updated successfully"} 

