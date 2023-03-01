import sqlite3
import typing
import contextlib
import fileinput
import string
import re
from fastapi import FastAPI, Depends, HTTPException, status


db = sqlite3.connect('wordlist.db')
db2 = sqlite3.connect('answers.db')

cursor = db.cursor()
cursor2 = db2.cursor()

#create dictionary table
cursor.execute('''CREATE TABLE IF NOT EXISTS dictionary (word_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, word text)''')

# Populate dictionary table
#Filter data and insert into DB
for line in fileinput.input(files = '/usr/share/dict/words'):
    if not line[0].isupper() and len(line) == 6 and line.isascii() and (bool(re.search('^[a-zA-Z0-9]*$',line))==True):
        cursor.execute("""INSERT INTO dictionary (word) VALUES (?)""",[line.replace("\n","")])

db.commit()

#create answers table
cursor2.execute('''CREATE TABLE IF NOT EXISTS answer (game_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, word text)''')
cursor2.execute('''CREATE TABLE IF NOT EXISTS temp (game_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, word text)''')	#Creating this temporary table to store all the values and remove the quotes before we insert into actual answer table

# Populate Answers table
f = open('answers.json')
readFile = f.read()
answerArr = readFile.split(']')
words = answerArr[0].split(',')

#Insert answers into DB
for w in words:
    cursor2.execute("""INSERT INTO temp (word) VALUES (?)""", [w])
    #print(len(w))
    
cursor2.execute('''INSERT INTO answer SELECT game_id, TRIM(word,'"') FROM temp''') #Command to trim the quotes 
    
#check if db is populated
cursor2.execute('''SELECT * FROM answer WHERE game_id = 2''')
#print(len(cur2.fetchone()[1]))

db2.commit()

db.close()
db2.close()
