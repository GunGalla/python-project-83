"""Flask app"""
from flask import Flask, flash, request, render_template, redirect, url_for
from validators.url import url
from datetime import datetime
import os
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.config['SECRET_KEY'] = 'csadsdffdgbfgbgttfewfwerbtyrrt'
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'database.sql')))


def connect_db():
    """Database connection"""
    try:
        # trying to connect to db
        conn = psycopg2.connect(dbname='analyser_test', user='gungalla')
        return conn
    except ConnectionError:
        # error in case of unable to connect to db
        print('Can`t establish connection to database')


@app.route('/')
def index():
    """Home page view"""
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls():
    """Urls checking page"""
    if request.method == 'POST':
        check_url = request.form.get('url')
        if url(check_url) and len(check_url) < 255:
            db = connect_db()
            cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(f"SELECT * FROM urls WHERE name='{check_url}'")
            not_unique = cur.fetchone()
            if not_unique:
                flash('Страница уже существует')
                return redirect(f'/urls/{not_unique[0]}')
            cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                        (check_url, datetime.today()))
            db.commit()
            cur.execute(f"SELECT * FROM urls WHERE name='{check_url}'")
            new_url = cur.fetchone()
            flash('Страница успешно добавлена')
            return redirect(f'/urls/{new_url[0]}')
        else:
            flash('Некорректный URL')
            if check_url == '':
                flash('URL Обязателен')
            return render_template('index.html')

    if request.method == 'GET':
        cur = connect_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM urls ORDER BY id DESC')
        all_urls = cur.fetchall()
        return render_template('urls.html', urls=all_urls)


@app.route('/urls/<url_id>')
def dist_url(url_id):
    """Dedicated url view"""
    cur = connect_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f"SELECT * FROM urls WHERE id={url_id}")
    url = cur.fetchone()
    return render_template('url.html', url=url)
