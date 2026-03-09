from markdownfield.validators import MARKDOWN_ATTRS, MARKDOWN_TAGS, Validator

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
