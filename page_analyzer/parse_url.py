"""Parsing url to check its SEO and availability"""
from datetime import date


def get_url_parsing_values(page):
    """Check SEO functionality of url"""

    result = {'status_code': 200}

    result['h1'] = page.h1.get_text() if page.h1 else ''

    result['title'] = page.title.get_text() if page.title else ''

    result['description'] = page.find(
        'meta', {'name': 'description'}
    ).get('content') if page.find('meta', {'name': 'description'}) else ''

    result['created_at'] = date.today()

    return result
