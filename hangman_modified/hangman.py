import random
import config
import flask
from flask import Flask, render_template, url_for, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)

# Compiling into executable
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hangman.db'
db = SQLAlchemy(app)

# Model

def random_pk(): # Random game ID
    return random.randint(1e9, 1e10) # Returns random Game ID for unique identification in the database formed

# choose_word - chooses the correct function to run in order to select a word in the difficulty chosen (modification)
def choose_word():
    if config.difficulty == "easy":
        return random_easy()
    elif config.difficulty == "medium":
        return random_medium()
    else:
        return random_hard()

# If the difficulty chosen is 'easy', then a word with 4-6 letters is chosen (modification)
def random_easy():
    words = [line.strip() for line in open('words.txt') if len(line) > 4 and len(line) <= 6]
    correct_word = random.choice(words).upper()
    return correct_word

# If the difficulty chosen is 'medium', then a word with 6-10 letters with >=4 unique letters is chosen (modification)
def random_medium():    
    words = [line.strip() for line in open('words.txt') if len(line) > 6 and len(line) <= 10 and len(set(line)) >= 4]
    correct_word = random.choice(words).upper()
    return correct_word

# If the difficulty chosen is 'hard', then a word with >=10 letters with >=6 unique letters is chosen (modification)
def random_hard():
    words = [line.strip() for line in open('words.txt') if len(line) > 10 and len(set(line)) >= 6]
    correct_word = random.choice(words).upper()
    return correct_word


# Returns random Game ID for unique identification in the database formed
class Game(db.Model):
    pk = db.Column(db.Integer, primary_key=True, default=random_pk)  # Game ID (acquired from random_pk function)
    word = db.Column(db.String(50), default=choose_word) # Modification - different difficulties
    tried = db.Column(db.String(50), default='') # Letters guessed during gameplay (includes both correct and incorrect letters - hence errors made can be found here as well)
    player = db.Column(db.String(50)) # Player name (initialised in __init__)
    words_guessed = []
    config.guessword_score = 0

    def __init__(self, player):
        self.player = player # Storing player name into database

    # MODIFICATION - Errors now show on screen in the order they were entered
    @property
    def errors(self):
        errorletters = [x for x in list(dict.fromkeys(self.tried).keys()) if x not in list(dict.fromkeys(self.word).keys())]
        return ''.join(errorletters)

    @property
    def current(self):
        return ''.join([c if c in self.tried else '_' for c in self.word])
    
    # MODIFICATION - New Scoring System
    @property
    def points(self):
        uncommon_letters = ["F", "H", "J", "K", "Q", "V", "W", "X", "Y", "Z"]
        score = 100 + 2*len(set(self.word)) + len(self.word) + len([x for x in self.word if x in uncommon_letters]) - 10*len(self.errors)
        return score
    
    # Play
    def try_letter(self, letter):
        if not self.finished and letter not in self.tried: # Checks for duplicates here
            self.tried += letter # Adds letter to database
            db.session.commit() # Updates Database


    # Guess the word feature (modification)
    def try_word(self, guess):
        if not self.finished and guess not in self.words_guessed and len(guess) == len(self.current): # Checking if word is correct length and has not been already guessed
            if guess == self.word: # If guessed word is correct, add all correct letters into 'tried letters' string for the game to automatically win
                for i in range(len(self.word)):
                    self.tried += self.word[i]
                seen = set()
                config.guessword_score = len(self.word) - len([x for x in self.tried if x in seen or seen.add(x)])# No. of letters missing before correct word was guessed - Can be used for bonus points in versions following V1.0
            
            else: # Word is incorrect - Append 1-8 to self.tried to show up as an error
                self.words_guessed.append(guess)
                word_errors = 1
                for n in self.tried:
                    if n.isnumeric():
                        word_errors += 1
                self.tried += str(word_errors)
            
            db.session.commit()

    
    # Game status

    @property
    def won(self):
        return self.current == self.word # Win condition - word shown on screen matches word chosen

    # Modification - Different number of errors allowed for different difficulties
    @property
    def lost(self):
        if config.difficulty == "hard":
            return len(self.errors) == 6
        else:
            return len(self.errors) == 8

    @property
    def finished(self):
        return self.won or self.lost # Checks whether game is finished


# Controller
@app.route('/', methods=['GET', 'POST'])
def main_menu():
    return flask.render_template('main.html')

@app.route('/solo')
def solo():
    games = sorted(
        [game for game in Game.query.all() if game.won],
        key=lambda game: -game.points)[:10] #Leaderboard - Returns top ten games with highest points
    return flask.render_template('sp_dif.html', games=games)


# Modification - Receives difficulty from difficulty select page
@app.route('/spdif', methods=['GET', 'POST'])
def spdif():
    games = sorted(
        [game for game in Game.query.all() if game.won],
        key=lambda game: -game.points)[:10] #Leaderboard - Returns top ten games with highest points
    
    if request.method == 'POST':
        if request.form.get("easy") == "Easy":
            config.difficulty = 'easy'
        elif request.form.get("medium") == "Medium":
            config.difficulty = 'medium'
        elif request.form.get("hard") == "Hard":
            config.difficulty = 'hard'

    return flask.render_template('sp_name.html', games=games)

@app.route('/spplay', methods=['GET', 'POST'])
def new_game(): # Initialises new game, adds data (players name) into database
    player = flask.request.args.get('player') # Reads player name from user input
    game = Game(player) # Creates new instance of Game
    db.session.add(game) # Adds and commits new game created into database
    db.session.commit() 
    return flask.redirect(flask.url_for('play', game_id=game.pk))


# Modification - Included guess word feature
@app.route('/play/<game_id>', methods=['GET', 'POST'])
def play(game_id):
    game = Game.query.get_or_404(game_id)

    if flask.request.method == 'POST': # Guessing a letter/word
        letter = flask.request.form['letter'].upper()
        word_guess = flask.request.form['word_guess'].upper()
        if len(letter) == 1 and letter.isalpha(): # Checking for valid input
            game.try_letter(letter)
        elif len(word_guess) >= 1 and word_guess.isalpha(): # Checking for valid input
            game.try_word(word_guess)

    if flask.request.is_xhr: # This 'is_xhr' is the part that stops the program from working on current software. Must download an earlier version of flask (1.1.2) and Werkzeug (0.16.1).
        return flask.jsonify(current=game.current,
                             errors=game.errors,
                             finished=game.finished)
    else:
        return flask.render_template('play.html', game=game, difficulty=config.difficulty) # Updates info at 'play.html'

@app.route('/multi_player')
def mp():
        return flask.render_template('multi.html')


# Main
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False) # Main function
