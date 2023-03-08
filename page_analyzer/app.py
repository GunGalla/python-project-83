"""Flask app"""
from flask import Flask, flash, request, render_template, redirect
from bs4 import BeautifulSoup
from validators.url import url
from datetime import date
from dotenv import load_dotenv, find_dotenv
import urllib
import requests
import os
import psycopg2
import psycopg2.extras

app = Flask(__name__)

load_dotenv(find_dotenv())

user = os.getenv('PGUSER')
database = os.getenv('PGDATABASE')
host = os.getenv('PGHOST')
port = os.getenv('PGPORT')
password = os.getenv('PGPASSWORD')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = f'postgresql://{user}:{password}@{host}:{port}/{database}'


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
        if latest_checks:
            for item in latest_checks:
                ids.append(item[1])
            if len(ids) > 1:
                cur.execute(f"SELECT * FROM url_checks"
                            f"WHERE id in {tuple(ids)}")
                all_checks = cur.fetchall()
            else:
                cur.execute(f"SELECT * FROM url_checks WHERE id={ids[0]}")
                all_checks = cur.fetchall()
            return render_template(
                'urls.html',
                urls=all_urls,
                all_checks=all_checks
            )
        else:
            return render_template('urls.html', urls=all_urls)


@app.route('/urls/<url_id>')
def dist_url(url_id):
    """Dedicated url view"""
    cur = connect_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f"SELECT * FROM urls WHERE id={url_id}")
    url = cur.fetchone()
    cur.execute(
        f"SELECT * FROM url_checks WHERE url_id={url_id} ORDER BY id DESC"
    )
    url_checks = cur.fetchall()
    return render_template('url.html', url=url, url_checks=url_checks)


@app.post('/urls/<url_id>/checks')
def url_check(url_id):
    """Check url"""
    db = connect_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT name FROM urls WHERE id={url_id}")
    url_name = cur.fetchone()
    r = requests.get(url_name[0])
    if r.status_code == 200:
        f = urllib.request.urlopen(url_name[0])
        page = BeautifulSoup(f, 'lxml')
        attrs = '(url_id, status_code'
        values_count = '(%s, %s'
        values = [f'{url_id}', r.status_code]
        description = page.find('meta', {'name': 'description'}).get('content')
        if page.h1:
            attrs += ', h1'
            values_count += ', %s'
            values.append(page.h1.get_text())
        if page.title:
            attrs += ', title'
            values_count += ', %s'
            values.append(page.title.get_text())
        if description:
            attrs += ', description'
            values_count += ', %s'
            values.append(description)
        attrs += ', created_at)'
        values_count += ', %s)'
        values.append(date.today())
        cur.execute("INSERT INTO url_checks "
                    f"{attrs}"
                    f"VALUES {values_count}",
                    tuple(values))
        db.commit()
        flash('Страница успешно проверена')
    else:
        flash('Произошла ошибка при проверке')
    return redirect(f'/urls/{url_id}')
