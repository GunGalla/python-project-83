"""Flask app"""
from flask import Flask, flash, request, render_template, redirect, url_for
from datetime import date
from dotenv import load_dotenv, find_dotenv
import requests
import os
import psycopg2
import psycopg2.extras

from .get_db_conn import connect_db
from .get_and_check_url import parse_url, url_validation
from .parse_url import url_parsing

app = Flask(__name__)

load_dotenv(find_dotenv())


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    """Home page view"""
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    """Show urls list"""
    db = connect_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('''
            SELECT u.*, c.*
            FROM urls u
            LEFT JOIN (
                SELECT url_id, MAX(id) AS latest_check_id
                FROM url_checks
                GROUP BY url_id
            ) latest_checks ON u.id = latest_checks.url_id
            LEFT JOIN url_checks c ON latest_checks.latest_check_id = c.id
            ORDER BY u.id DESC;
        ''')
    results = cur.fetchall()
    cur.close()
    db.close()
    return render_template('urls.html', urls=results)


@app.post('/urls')
def urls_post():
    """Check url and show its page if url is valid"""
    entered_url = request.form.get('url')
    check = parse_url(entered_url)
    if url_validation(check, entered_url):
        return render_template('index.html'), 422

    db = connect_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT * FROM urls WHERE name='{check}'")
    not_unique = cur.fetchone()
    if not_unique:
        flash('Страница уже существует')
        return redirect(url_for('dist_url', url_id=not_unique[0]))
    cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                (check, date.today()))
    db.commit()
    cur.execute(f"SELECT * FROM urls WHERE name='{check}'")
    new_url = cur.fetchone()
    cur.close()
    db.close()
    flash('Страница успешно добавлена')
    return redirect(url_for('dist_url', url_id=new_url[0]))


@app.route('/urls/<url_id>')
def dist_url(url_id):
    """Dedicated url view"""
    db = connect_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f"SELECT * FROM urls WHERE id={url_id}")
    url = cur.fetchone()
    cur.execute(
        f"SELECT * FROM url_checks WHERE url_id={url_id} ORDER BY id DESC"
    )
    url_checks = cur.fetchall()
    cur.close()
    db.close()
    return render_template('url.html', url=url, url_checks=url_checks)


@app.post('/urls/<url_id>/checks')
def url_check(url_id):
    """Check url"""
    db = connect_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT name FROM urls WHERE id={url_id}")
    url_name = cur.fetchone()
    try:
        requests.get(url_name[0])
    except requests.ConnectionError:
        flash("Произошла ошибка при проверке")
        return redirect(url_for('dist_url', url_id=url_id))

    r = requests.get(url_name[0])

    if r.status_code != 200:
        flash('Произошла ошибка при проверке')
        return redirect(url_for('dist_url', url_id=url_id))

    parse_result = url_parsing(url_name[0], url_id)
    cur.execute("INSERT INTO url_checks "
                f"{parse_result[0]}"
                f"VALUES {parse_result[1]}",
                tuple(parse_result[2]))
    db.commit()
    flash('Страница успешно проверена')
    cur.close()
    db.close()
    return redirect(url_for('dist_url', url_id=url_id))
