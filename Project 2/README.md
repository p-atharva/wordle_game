Introduction
In this project, we developed two services, one for the word list of valid guesses and one for checking guesses against answers - 
1. The word validation service should expose the following operations:
•	Checking if a guess is a valid five-letter word - This service checks if the word entered is a valid dictionary word. If yes, this word can be entered to play the game. 
•	Adding and removing possible guesses - This service helps in adding and deleting possible guesses in the future.
The database used to accomplish these tasks is 'wordlist.db' and the table created to store all the valid dictionary words is 'dictionary'. We created the required endpoints to accomplish these tasks.
2. The answer checking service should expose the following operations:
•	Checking a valid guess against the answer for the current day - This service takes the guess word and the game id that the user wants to play against. It compares this guessed word with the word that corresponds to this game id. It returns a message that the word has been guessed successfully if it matches. If the guess is incorrect, it provides details of the correctly placed letters, incorrectly placed but is present in the word, and letters that are not present in the word. 
•	Changing the answers for future games - This service helps in updating the word against a particular game id. It takes two path parameters - game id (against which the word needs to be updated) and the updated word.

Steps to Initiate the Databases and Run the Processes – 
1. Run the DB initialization file by typing the command -  python3 db_init.py
2. Run the services using the commands – foreman start
3. Microservice 1 would run on 5000 port and Microservice 2 would run on 5100 port. You can access these links by copy and pasting them in your browser with “/docs” addition at the end of url.
