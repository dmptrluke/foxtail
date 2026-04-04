from markdownfield.validators import MARKDOWN_ATTRS, MARKDOWN_TAGS, Validator

# Markdown validator that allows tables, figures, and embedded iframes beyond the default set
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
