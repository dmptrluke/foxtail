from hashlib import md5
from urllib.parse import urlencode

from django import template

register = template.Library()

# TEMPLATE USE:  {{ user|avatar_url:150 }}
@register.filter
def avatar_url(user, size=40):
    email = user.email

    default = "https://example.com/static/images/defaultavatar.jpg"
    return "https://www.gravatar.com/avatar/{}?{}".format(
        md5(email.lower().encode('utf-8')).hexdigest(), urlencode({'d': default, 's': str(size)}))
