"""Parsing url to check its SEO and availability"""
from bs4 import BeautifulSoup
from datetime import date
import requests
import urllib


def get_url_parsing_values(item, url_id):
    """Check SEO functionality of url"""
    f = urllib.request.urlopen(item)
    r = requests.get(item)
    page = BeautifulSoup(f, 'lxml')
    attrs = '(url_id, status_code'
    values_count = '(%s, %s'
    values = [f'{url_id}', r.status_code]
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
