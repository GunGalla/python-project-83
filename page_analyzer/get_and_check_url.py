"""Module for getting entered url and checking it"""
from flask import flash
from urllib.parse import urlparse
from validators.url import url


def get_formatted_url(url_check):
    """Parsing and checking url"""
    parsing = urlparse(url_check)
    correct_url = f'{parsing[0]}://{parsing[1]}'
    return correct_url


def get_url_validation(url_val, url_check):
    """Check if entered url valid"""
    errors = []
    if not url(url_val) or len(url_check) > 255:
        errors.append('Некорректный URL')
    if url_check == '':
        errors.append('URL Обязателен')
    return errors
