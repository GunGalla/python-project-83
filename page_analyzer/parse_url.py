"""Parsing url to check its SEO and availability"""
from datetime import date
from bs4 import BeautifulSoup


def get_page_data(response):
    """Check SEO functionality of url"""

    result = {'status_code': response.status_code}

    page = BeautifulSoup(response.text, 'html.parser')

    result['h1'] = page.h1.get_text() if page.h1 else ''

    result['title'] = page.title.get_text() if page.title else ''

    result['description'] = page.find(
        'meta', {'name': 'description'}
    ).get('content') if page.find('meta', {'name': 'description'}) else ''

    result['created_at'] = date.today()

    return result
