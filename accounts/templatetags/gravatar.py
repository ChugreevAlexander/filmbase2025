import hashlib
from urllib.parse import urlencode
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def gravatar_url(email, size=80, rating='g', default='mp'):
    """
    Возвращает URL аватара Gravatar для заданного email.
    """
    email = email.strip().lower()
    email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
    url = 'https://www.gravatar.com/avatar/'
    params = {
        's': str(size),      # размер (в пикселях)
        'd': default,        # изображение по умолчанию
        'r': rating,         # рейтинг (g, pg, r, x)
    }
    query_string = urlencode(params)
    return mark_safe(f'{url}{email_hash}?{query_string}')