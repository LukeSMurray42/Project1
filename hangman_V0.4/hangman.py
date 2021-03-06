import random
from threading import Timer
from webbrowser import get

import flask
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import time

app = flask.Flask(__name__)

# Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hangman.db'
db = SQLAlchemy(app)

# Model

def random_pk():
    return random.randint(1e9, 1e10)

def random_word():
    words = [line.strip() for line in open('words.txt') if len(line) > 10]
    correct_word = random.choice(words).upper()
    return correct_word


class Game(db.Model):
    pk = db.Column(db.Integer, primary_key=True, default=random_pk)
    word = db.Column(db.String(50), default=random_word)
    tried = db.Column(db.String(50), default='')
    player = db.Column(db.String(50))
    try_again = 0
    words_guessed = []

    def __init__(self, player):
        self.player = player

    @property
    def errors(self):
        return ''.join(set(self.tried) - set(self.word))

    @property
    def current(self):
        return ''.join([c if c in self.tried else '_' for c in self.word])

    @property
    def points(self):
        return 100 + 2*len(set(self.word)) + len(self.word) - 10*len(self.errors)

    # Play

    def try_letter(self, letter):
        if not self.finished and letter not in self.tried:
            self.tried += letter
            self.try_again = 0
            db.session.commit()
        else:
            self.try_again = 1
            db.session.commit()

    # Guess the word feature (modification)
    def try_word(self, guess):
        if not self.finished and guess not in self.words_guessed:
            self.try_again = 0

            if guess == self.word:
                for i in range(len(self.word)):
                    #print("Iteration {}: {}".format(i, self.word[i])) # Debug
                    self.tried += self.word[i]
                db.session.commit()
                #print("word correct") # Debug
            
            else:
                self.words_guessed.append(guess)
                word_errors = 1
                for n in self.tried:
                    if n.isnumeric():
                        word_errors += 1
                self.tried += str(word_errors)
                db.session.commit()
                #print("word incorrect (error {})".format(word_errors)) #debug

        else:
            self.try_again = 1
            db.session.commit()            

    # Game status

    @property
    def won(self):
        return self.current == self.word

    @property
    def lost(self):
        return len(self.errors) == 6

    @property
    def finished(self):
        return self.won or self.lost

'''
    @property
    def timer(self):
        for i in range(t):
            time.sleep(set_time)
        #return self.timer

        def countdown(t):
            while t:
                mins, secs = divmod(t, 60)
                timer = '{:02d}:{:02d}'.format(mins, secs)
                print(timer, end="\r")
                yield timer
                time.sleep(1)
                T = -1
                return timer

'''



# Controller
@app.route('/', methods=['GET', 'POST'])
def main_menu():
    return flask.render_template('main.html')

@app.route('/solo')
def solo():
    games = sorted(
        [game for game in Game.query.all() if game.won],
        key=lambda game: -game.points)[:10]
    return flask.render_template('sp.html', games=games)

@app.route('/multi_player')
def mp():
        return flask.render_template('multi.html')

@app.route('/spplay')
def new_game():
    player = flask.request.args.get('player')
    game = Game(player)
    db.session.add(game)
    db.session.commit()
    return flask.redirect(flask.url_for('play', game_id=game.pk))

@app.route('/play/<game_id>', methods=['GET', 'POST'])
def play(game_id):
    game = Game.query.get_or_404(game_id)

    if flask.request.method == 'POST':
        letter = flask.request.form['letter'].upper()
        word_guess = flask.request.form['word_guess'].upper()
        if len(letter) == 1 and letter.isalpha():
            game.try_letter(letter)
        elif len(word_guess) >= 1 and word_guess.isalpha():
            game.try_word(word_guess)

    if flask.request.is_xhr:
        return flask.jsonify(current=game.current,
                             errors=game.errors,
                             finished=game.finished)
    else:
        return flask.render_template('play.html', game=game)



# Main

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

