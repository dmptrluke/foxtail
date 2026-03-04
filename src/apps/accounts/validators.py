from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from the_big_username_blacklist import validate


def validate_blacklist(value):
    if validate(value) is False:
        raise ValidationError(
            "This username is not allowed.",
            params={'value': value},
        )


class UsernameValidator(RegexValidator):
    regex = r'^[\w.@ +-]+\Z'
    message = 'Enter a valid username. This value may contain only letters, spaces, ' \
              'numbers, and @/./+/-/_ characters.'

    flags = 0


username_validators = [UsernameValidator(), validate_blacklist]
