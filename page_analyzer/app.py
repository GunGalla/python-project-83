"""Flask app"""
from flask import Flask, flash, request, render_template, redirect
from validators.url import url
from datetime import date
from dotenv import load_dotenv, find_dotenv
import requests
import os
import psycopg2
import psycopg2.extras

app = Flask(__name__)

load_dotenv(find_dotenv())

db = os.getenv('DB_PATH')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def connect_db():
    """Database connection"""
    try:
        # trying to connect to db
        conn = psycopg2.connect(db)
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
                        (check_url, date.today()))
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
        cur = connect_db().cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM urls ORDER BY id DESC')
        all_urls = cur.fetchall()
        cur.execute('SELECT url_id, MAX(id) FROM url_checks GROUP BY url_id')
        latest_checks = cur.fetchall()
        ids = []
        for item in latest_checks:
            ids.append(item[1])
        cur.execute(f"SELECT * FROM url_checks WHERE id in {tuple(ids)}")
        all_checks = cur.fetchall()
        return render_template('urls.html', urls=all_urls, all_checks=all_checks)


@app.route('/urls/<url_id>')
def dist_url(url_id):
    """Dedicated url view"""
    cur = connect_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f"SELECT * FROM urls WHERE id={url_id}")
    url = cur.fetchone()
    cur.execute(f"SELECT * FROM url_checks WHERE url_id={url_id} ORDER BY id DESC")
    url_checks = cur.fetchall()
    return render_template('url.html', url=url, url_checks=url_checks)


@app.post('/urls/<url_id>/checks')
def url_check(url_id):
    """Check url"""
    db = connect_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT name FROM urls WHERE id={url_id}")
    url_name = cur.fetchone()
    try:
        r = requests.get(url_name[0])
        cur.execute("INSERT INTO url_checks (url_id, status_code, created_at)"
                    "VALUES (%s, %s, %s)",
                    (f'{url_id}', r.status_code, date.today()))
        db.commit()
        flash('Страница успешно проверена')
    except:
        flash('Произошла ошибка при проверке')
    return redirect(f'/urls/{url_id}')
