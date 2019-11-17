from django.core.validators import RegexValidator


class UsernameValidator(RegexValidator):
    regex = r'^[\w.@ +-]+\Z'
    message = 'Enter a valid username. This value may contain only letters, spaces, ' \
              'numbers, and @/./+/-/_ characters.'

    flags = 0


username_validators = [UsernameValidator]
