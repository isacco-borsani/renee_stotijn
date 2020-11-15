from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<word>', defaults={'word': 'bird'})
def word_up(word):
    return render_template('whatstheword.html', word=word)
