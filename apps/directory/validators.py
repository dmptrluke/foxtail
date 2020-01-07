from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from the_big_username_blacklist import validate


def validate_blacklist(value):
    if validate(value) is False:
        raise ValidationError(
            "This profile URL is not allowed.",
            params={'value': value},
        )


class URLValidator(RegexValidator):
    regex = r'^[-a-zA-Z0-9_]+\Z'
    message = 'Your profile URL may contain only letters, numbers, underscores and dashes.'
    flags = 0


validate_url = URLValidator()
