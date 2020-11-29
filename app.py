from flask import Flask, render_template
from os import listdir
from os.path import isfile, join

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_paints', methods=['GET'])
def get_paints():
    try:
        file_paints = [str(f) for f in listdir('static/images/quadri/') if isfile(join('static/images/quadri', f))]
    except FileNotFoundError:
        return {'ret': False, 'content': None}
    return {'ret': True, 'content': file_paints}
