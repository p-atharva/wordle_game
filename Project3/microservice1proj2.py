import sqlite3
import typing
import contextlib
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI()

#database function
def getDataBase():
     with contextlib.closing(sqlite3.connect('wordlist.db')) as db:
                db.row_factory = sqlite3.Row
                yield db


#function to check if guess is valid or not
@app.get("/check/{word}")
def check_word(word: str, db:sqlite3.Connection = Depends(getDataBase)):
    cursor = db.execute("SELECT * FROM dictionary WHERE word=?", [word])
    word = cursor.fetchone()[1]
    if len(word) == 0:
    	flag = 0
    	raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not in dictionary")
    else:
    	flag = 1	
    return {"flag":flag, "message": "Guessed word is a valid dictionary word","word":word}
    

# Adding possible guesses
@app.post("/addword/{word}", status_code=status.HTTP_201_CREATED)
def add_word(word : str, db: sqlite3.Connection = Depends(getDataBase)):
	cursor = db.execute("SELECT * FROM dictionary WHERE word = ?",[word])
	count = cursor.fetchone()

	if count is None:    #If we find the word in dictionary
		cursor = db.execute("INSERT INTO dictionary VALUES(?,?)",[None,word])
		db.commit()
	else:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Word already present in dictionary")
	return {"message":"Word added successfully"}


# Removing possible guesses
@app.delete("/deleteword/{word}")
def delete_word(word:str, db:sqlite3.Connection = Depends(getDataBase)):
    cursor = db.execute("SELECT * FROM dictionary WHERE word = ?", [word])
    count = cursor.fetchone()
    if count is not None:  #If we find the word in the dictionary
        cursor = db.execute("DELETE FROM dictionary WHERE word = ?", [word])
        db.commit()
        return {"message":"deleted"}
    else:
        return {"message":"no such word present in dictionary"}


