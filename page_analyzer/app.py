"""Flask app"""
from flask import Flask, flash, request, render_template, redirect, url_for
from datetime import date
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup
import urllib
import requests
import os
import psycopg2
import psycopg2.extras


from .db_connect import get_db_connection
from .urls import normalize_url, validate_url
from .parse_url import get_url_parsing_values

app = Flask(__name__)

load_dotenv(find_dotenv())


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.errorhandler(404)
def not_found_error():
    """Handle 404 error"""
    return render_template('404.html'), 404


@app.route('/')
def index():
    """Home page view"""
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    """Show urls list"""
    db = get_db_connection()
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
    db.close()
    return render_template('urls.html', urls=results)


@app.post('/urls')
def urls_post():
    """Check url and show its page if url is valid"""
    entered_url = request.form.get('url')
    formatted_url = normalize_url(entered_url)

    errors = validate_url(formatted_url, entered_url)
    if errors:
        for error in errors:
            flash(error, 'danger')
        return render_template('index.html'), 422

    db = get_db_connection()
    cur = db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cur.execute(f"SELECT * FROM urls WHERE name='{formatted_url}'")
    not_unique = cur.fetchone()
    if not_unique:
        flash('Страница уже существует', 'info')
        return redirect(url_for('url_get', url_id=not_unique.id))
    cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                (formatted_url, date.today()))
    db.commit()
    cur.execute(f"SELECT * FROM urls WHERE name='{formatted_url}'")
    new_url = cur.fetchone()
    db.close()
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url_get', url_id=new_url.id))


@app.route('/urls/<url_id>')
def url_get(url_id):
    """Dedicated url view"""
    db = get_db_connection()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f"SELECT * FROM urls WHERE id={url_id}")
    url = cur.fetchone()
    if not url:
        return not_found_error()
    cur.execute(
        f"SELECT * FROM url_checks WHERE url_id={url_id} ORDER BY id DESC"
    )
    url_checks = cur.fetchall()
    db.close()
    return render_template('url.html', url=url, url_checks=url_checks)


@app.post('/urls/<url_id>/checks')
def check_url(url_id):
    """Check url"""
    db = get_db_connection()
    cur = db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cur.execute(f"SELECT name FROM urls WHERE id={url_id}")
    url_name = cur.fetchone()
    try:
        requests.get(url_name.name)
    except requests.ConnectionError:
        flash("Произошла ошибка при проверке", 'danger')
        return redirect(url_for('url_get', url_id=url_name.id))

    request_result = requests.get(url_name.name)

    if request_result.status_code != 200:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_get', url_id=url_id))

    file = urllib.request.urlopen(url_name.name)
    page = BeautifulSoup(file, 'lxml')

    attrs, values_replacers, values = get_url_parsing_values(page, url_id)

    cur.execute("INSERT INTO url_checks "
                f"({', '.join(attrs)})"
                f"VALUES ({', '.join(values_replacers)})",
                tuple(values))
    db.commit()
    flash('Страница успешно проверена', 'success')
    db.close()
    return redirect(url_for('url_get', url_id=url_id))
