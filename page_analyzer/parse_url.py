"""Parsing url to check its SEO and availability"""
from datetime import date


def get_url_parsing_values(page, url_id):
    """Check SEO functionality of url"""
    success_status_code = 200
    attrs = ['url_id', 'status_code', 'created_at']
    values_replacers = ['%s'] * 3
    values = [f'{url_id}', success_status_code]
    if page.h1:
        attrs.insert(-1, 'h1')
        values_replacers.append('%s')
        values.append(page.h1.get_text())
    if page.title:
        attrs.insert(-1, 'title')
        values_replacers.append('%s')
        values.append(page.title.get_text())
    if page.find('meta', {'name': 'description'}):
        description = \
            page.find('meta', {'name': 'description'}).get('content')
        attrs.insert(-1, 'description')
        values_replacers.append('%s')
        values.append(description)
    values.append(date.today())
    return attrs, values_replacers, values
