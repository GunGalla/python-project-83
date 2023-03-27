"""Getting db connection module."""
from dotenv import load_dotenv, find_dotenv
import psycopg2
import os

load_dotenv(find_dotenv())

DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    """Database connection"""
    try:
        # trying to connect to db
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except ConnectionError:
        # error in case of unable to connect to db
        print('Can`t establish connection to database')
