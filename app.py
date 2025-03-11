import json
import os
import time
from datetime import datetime, timedelta
from gevent.pywsgi import WSGIServer

from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory
from os import listdir
from os.path import isfile, join
from flask_babel import Babel, gettext
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['LANGUAGES'] = {
    'en': 'English',
    'nl': 'Dutch'
}

data = {}
if os.path.exists('data.json'):
    with open('data.json') as json_file:
        data = json.load(json_file)

app.config['BABEL_DEFAULT_LOCALE'] = 'en'
# Initialize Babel with a locale selector
babel = Babel(app, locale_selector=lambda: session.get('language') or
                               request.accept_languages.best_match(app.config['LANGUAGES'].keys()))

app.config['BABEL_DEFAULT_LOCALE'] = 'en'
QUESTIONS_FOLDER = os.path.join(app.root_path, 'questions')
app.config['QUESTIONS_FOLDER'] = QUESTIONS_FOLDER
BACKUP_FOLDER = os.path.join(app.root_path, 'backups')
app.config['BACKUP_FOLDER'] = BACKUP_FOLDER
STATIC_FOLDER = os.path.join(app.root_path, 'static')
app.config['STATIC_FOLDER'] = STATIC_FOLDER


def get_locale():
    return session.get('language') or request.accept_languages.best_match(app.config['LANGUAGES'].keys())


def current_milli_time():
    return round(time.time() * 1000)


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


@app.route('/favicon.ico')
@app.route('/robots.txt')
@app.route('/sitemap.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/contacts/prepare_backup', methods=['POST'])
def prepare_backup():
    if request.form['username'] == data['username'] and request.form['pass_email'] == data['pass_email']:
        questions_to_send = []
        yesterday = datetime.today() - timedelta(days=1)
        path_to_exam = os.path.join(app.config['QUESTIONS_FOLDER'], yesterday.strftime('%Y%m%d'))

        if os.path.exists(path_to_exam):
            questions = os.listdir(path_to_exam)
            for f in questions:
                with open(os.path.join(app.config['QUESTIONS_FOLDER'], yesterday.strftime('%Y%m%d'), f)) as json_file:
                    questions_to_send.append(json.load(json_file))

        msg_text = ''
        for single in questions_to_send:
            for key, val in single.items():
                msg_text += str(key) + ": " + str(val) + "\n"
            msg_text += "\n\n\n"

        if not os.path.exists(os.path.join(app.config['BACKUP_FOLDER'], yesterday.strftime('%Y%m%d'))):
            os.makedirs(os.path.join(app.config['BACKUP_FOLDER'], yesterday.strftime('%Y%m%d')))

        f = open(os.path.join(app.config['BACKUP_FOLDER'], yesterday.strftime('%Y%m%d'), 'backup.txt'), "w+")
        f.write(msg_text)
        f.close()

        return {'res': True}
    return {'res': False}


@app.route('/contacts/submit_contact', methods=['POST'])
def submit_contact():
    params = {}
    for a in json.loads(request.form['form']):
        if len(a['value']) > 0 != '':
            params[a['name']] = a['value']

    if request.method == "POST" and (("name" in params) and ("surname" in params) and (
            "email" in params) and ("description" in params)):
        if not os.path.exists(app.config['QUESTIONS_FOLDER']):
            os.makedirs(app.config['QUESTIONS_FOLDER'])
        if not os.path.exists(os.path.join(app.config['QUESTIONS_FOLDER'], datetime.today().strftime('%Y%m%d'))):
            os.makedirs(os.path.join(app.config['QUESTIONS_FOLDER'], datetime.today().strftime('%Y%m%d')))
        # if os.path.exists(os.path.join(app.config['QUESTIONS_FOLDER'], datetime.today().strftime('%Y%m%d'),
        #                                params['email'] + '.json')):
        #     return {'res': False, 'msg': gettext("You already sent a question with this email, try tomorrow :)")}
        millis = current_milli_time()
        with open(
                os.path.join(app.config['QUESTIONS_FOLDER'], datetime.today().strftime('%Y%m%d'),
                             str(millis) + '.json'), 'w', encoding='utf-8') as f:
            json.dump(params, f, ensure_ascii=False, indent=4)
        return {'res': True}
    return {'res': False, 'msg': gettext('General error')}


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
    return render_template('news.html', current_locale=get_locale())

@app.route('/nft')
def nft():
    return render_template('nft.html')


@app.route('/news/lindapdf')
def lindapdf():
    path_to_file = os.path.join(app.config['STATIC_FOLDER'], 'documents', 'new')
    if not os.path.exists(path_to_file):
        return redirect(url_for('news'))

    return send_from_directory(path_to_file,
                               'linda.pdf',
                               as_attachment=True)


@app.route('/news/nrz')
def nrzpdf():
    path_to_file = os.path.join(app.config['STATIC_FOLDER'], 'documents', 'new')
    if not os.path.exists(path_to_file):
        return redirect(url_for('news'))

    return send_from_directory(path_to_file,
                               'NRZ.pdf',
                               as_attachment=True)


@app.route('/get_paints', methods=['GET'])
def get_paints():
    try:
        file_paints = [str(f) for f in listdir('static/images/quadri/web/compressed') if
                       isfile(join('static/images/quadri/web/compressed', f))]
    except FileNotFoundError:
        return {'ret': False, 'content': None}
    return {'ret': True, 'content': file_paints}


@app.route('/for-sale', methods=['GET'])
def sell_paints():
    """Sell paints endpoint"""
    with open('paints_for_sale.json') as json_file:
        paints = json.load(json_file)


    return render_template('sell-paints.html', paints=paints)


if __name__ == "__main__":
    app.run('0.0.0.0', 8080, True)
    # app.run('0.0.0.0', 5000, True)
    # app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    # http_server = WSGIServer(('0.0.0.0', 5000), app)
    # http_server.serve_forever()
