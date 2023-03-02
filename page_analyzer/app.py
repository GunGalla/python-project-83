"""Flask app"""
from flask import Flask, request, render_template
from validators.url import url
import psycopg2

app = Flask(__name__)

try:
    # trying to connect to db
    conn = psycopg2.connect(dbname='analyser_test', user='gungalla')
except ConnectionError:
    # error in case of unable to connect to db
    print('Can`t establish connection to database')


@app.route('/')
def index():
    """Home page view"""
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls():
    """Checked urls page"""
    if request.method == 'POST':
        check_url = request.form.get('url')
        if url(check_url) and len(check_url) < 255:
            cur = conn.cursor()
            return render_template('urls.html')
        else:
            return render_template('index.html', wrong_url=check_url)

    if request.method == 'GET':
        cur = conn.cursor()
        cur.execute('SELECT * FROM urls')
        all_urls = cur.fetchall()
        return render_template('urls.html', urls=all_urls)
