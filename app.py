import json
import os

from flask import Flask, render_template, request, session, redirect, url_for
from os import listdir
from os.path import isfile, join
from flask_babel import Babel, gettext

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['LANGUAGES'] = {
    'en': 'English',
    'nl': 'Dutch'
}

app.config['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)

app.config['BABEL_DEFAULT_LOCALE'] = 'en'


# app.run(debug=True, host='192.168.200.131')

@babel.localeselector
def get_locale():
    # if the user has set up the language manually it will be stored in the session,
    # so we use the locale from the user settings
    try:
        language = session['language']
    except KeyError:
        language = "en"
    if language is not None:
        return language
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())


@app.context_processor
def inject_conf_var():
    return dict(
        AVAILABLE_LANGUAGES=app.config['LANGUAGES'],
        CURRENT_LANGUAGE=session.get('language', request.accept_languages.best_match(app.config['LANGUAGES'].keys())))


@app.route('/language/<language>')
def set_language(language=None):
    if language in app.config['LANGUAGES']:
        session['language'] = language
    else:
        redirect(url_for('index'))
    return redirect(request.referrer)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/contacts/submit_contact', methods=['POST'])
def submit_contact():
    return {'res': True}


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/about/get_descriptions', methods=['GET'])
def get_descriptions():
    data = {}
    if os.path.exists('paintings_descriptions.json'):
        with open('paintings_descriptions.json') as json_file:
            data = json.load(json_file)
    return {'res': data}


@app.route('/news')
def news():
    return render_template('news.html')


@app.route('/get_paints', methods=['GET'])
def get_paints():
    try:
        file_paints = [str(f) for f in listdir('static/images/quadri/web') if
                       isfile(join('static/images/quadri/web', f))]
    except FileNotFoundError:
        return {'ret': False, 'content': None}
    return {'ret': True, 'content': file_paints}
