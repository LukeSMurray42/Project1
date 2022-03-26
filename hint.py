# Main
import os, sys
def base_path(path):
    if getattr(sys, 'frozen', None):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

#HANGMAN CODE
import random

import flask
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)

# Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hangman.db'
db = SQLAlchemy(app)

# Model

def random_pk(): #Random Game ID
    return random.randint(1e9, 1e10)

def random_word():
    words = [line.strip() for line in open('words.txt') if len(line) > 10] # Defines how long a word must be - we can change the difficulty here
    return random.choice(words).upper()

class Game(db.Model):
    pk = db.Column(db.Integer, primary_key=True, default=random_pk)
    word = db.Column(db.String(50), default=random_word)
    tried = db.Column(db.String(50), default='')
    player = db.Column(db.String(50))

    def __init__(self, player):
        self.player = player

    @property
    def errors(self):
        return ''.join(set(self.tried) - set(self.word)) # Corresponds to incorrect letters guessed

    @property
    def current(self):
        return ''.join([c if c in self.tried else '_' for c in self.word]) # Corresponds to word shown on screen

    @property
    def points(self):
        return 100 + 2*len(set(self.word)) + len(self.word) - 10*len(self.errors) # POINT SYSTEM - based on: number of unique letters in word, overall length of word, number of errors made (TODO: show on screen)

    # Play

    def try_letter(self, letter):
        if not self.finished and letter not in self.tried: # already checks for duplicates here
            self.tried += letter
            db.session.commit()

    # Game status

    @property
    def won(self): 
        return self.current == self.word # Win condition - word shown on screen matches word chosen

    @property
    def lost(self):
        return len(self.errors) == 6 # LOSE CONDITION - Can change the difficulty here

    @property
    def finished(self):
        return self.won or self.lost # Checks whether game is finished


# Controller

@app.route('/')
def home():
    games = sorted(
        [game for game in Game.query.all() if game.won],
        key=lambda game: -game.points)[:10] #Leaderboard - Returns top ten games with highest points
    return flask.render_template('home.html', games=games) #Updates info at 'home.html' - see comment on file

@app.route('/play')
def new_game(): # Initialises new game, adds data (players name) into database
    player = flask.request.args.get('player')
    game = Game(player)
    db.session.add(game)
    db.session.commit()
    return flask.redirect(flask.url_for('play', game_id=game.pk))

@app.route('/play/<game_id>', methods=['GET', 'POST'])
def play(game_id):
    game = Game.query.get_or_404(game_id)

    if flask.request.method == 'POST': # Guessing a letter
        letter = flask.request.form['letter'].upper()
        if len(letter) == 1 and letter.isalpha(): # Checking for a valid input (only 1 LETTER is given)
            game.try_letter(letter)

    if flask.request.is_xhr: # This 'is_xhr' is the part that stops the program from working. I finally got it to work for my computer by downloading an earlier version of flask (1.1.2) and Werkzeug (0.16.1).
        return flask.jsonify(current=game.current,
                             errors=game.errors,
                             finished=game.finished)
    else:
        return flask.render_template('play.html', game=game) # Updates info at 'play.html'

if __name__ == '__main__':
    os.chdir(base_path(''))
    app.run(host='0.0.0.0', debug=True)
