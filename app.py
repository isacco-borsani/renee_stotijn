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


@app.route('/about')
def about():
    return render_template('index.html')


@app.route('/get_paints', methods=['GET'])
def get_paints():
    try:
        file_paints = [str(f) for f in listdir('static/images/quadri/') if isfile(join('static/images/quadri', f))]
        print(file_paints)
    except FileNotFoundError:
        return {'ret': False, 'content': None}
    return {'ret': True, 'content': file_paints}
