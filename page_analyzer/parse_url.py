"""Parsing url to check its SEO and availability"""
from bs4 import BeautifulSoup
from datetime import date
import urllib


def get_url_page(url):
    """Transform url to lxml page"""
    f = urllib.request.urlopen(url)
    page = BeautifulSoup(f, 'lxml')
    return page


def get_url_parsing_values(page, url_id):
    """Check SEO functionality of url"""
    success_status_code = 200
    attrs = '(url_id, status_code'
    values_count = '(%s, %s'
    values = [f'{url_id}', success_status_code]
    if page.h1:
        attrs += ', h1'
        values_count += ', %s'
        values.append(page.h1.get_text())
    if page.title:
        attrs += ', title'
        values_count += ', %s'
        values.append(page.title.get_text())
    if page.find('meta', {'name': 'description'}):
        description = \
            page.find('meta', {'name': 'description'}).get('content')
        attrs += ', description'
        values_count += ', %s'
        values.append(description)
    attrs += ', created_at)'
    values_count += ', %s)'
    values.append(date.today())
    return attrs, values_count, values
