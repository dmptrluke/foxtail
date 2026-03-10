from django.conf import settings
from django.core.exceptions import ValidationError

from markdownfield.validators import MARKDOWN_ATTRS, MARKDOWN_TAGS, Validator


def file_size_validator(max_bytes=None):
    if max_bytes is None:
        max_bytes = settings.MAX_IMAGE_FILE_SIZE

    def validate(value):
        if value and hasattr(value, 'size') and value.size > max_bytes:
            mb = max_bytes / (1024 * 1024)
            raise ValidationError(f'File is too large. Maximum size is {mb:.0f} MB.')

    return validate


VALIDATOR_EXTENDED = Validator(
    allowed_tags={
        *MARKDOWN_TAGS,
        'figure',
        'figcaption',
        'table',
        'thead',
        'tbody',
        'tr',
        'th',
        'td',
        'iframe',
    },
    allowed_attrs={
        **MARKDOWN_ATTRS,
        '*': {'id', 'class'},
        'a': {'href', 'alt', 'title', 'name'},
        'iframe': {'src', 'width', 'height', 'title', 'frameborder', 'allow', 'allowfullscreen', 'referrerpolicy'},
    },
)
