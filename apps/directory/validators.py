from django.core.validators import RegexValidator


class URLValidator(RegexValidator):
    regex = r'^[-a-zA-Z0-9_]+\Z'
    message = 'Your profile URL may contain only letters, numbers, underscores and dashes.'

    flags = 0
