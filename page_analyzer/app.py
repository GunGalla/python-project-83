"""Flask app"""
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    """Home page view"""
    return render_template('index.html', message='Hello, Hexlet!')
