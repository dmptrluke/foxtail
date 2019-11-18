import bleach
import bleach_whitelist
from crispy_forms.layout import Field
from django.conf import settings
from markdownx.models import MarkdownxField
from markdown import markdown

EXTENSIONS = getattr(settings, 'MARKDOWNX_MARKDOWN_EXTENSIONS', [])
EXTENSION_CONFIGS = getattr(settings, 'MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS', [])


class NullValidator:
    sanitize = False


class StandardValidator:
    allowed_tags = bleach_whitelist.markdown_tags + ['dl', 'del', 'abbr']
    allowed_attrs = {
        **bleach_whitelist.markdown_attrs,
        'abbr': ['title']
    }
    sanitize = True


class ClassyValidator:
    allowed_tags = bleach_whitelist.markdown_tags + ['dl', 'del', 'abbr']
    allowed_attrs = {
        **bleach_whitelist.markdown_attrs,
        'abbr': ['title'],
        'img': ['src', 'alt', 'title', 'class'],
        'a': ['href', 'alt', 'title', 'class']
    }
    sanitize = True


class MarkdownField(MarkdownxField):
    def __init__(self, rendered_field=None, validator=StandardValidator):
        self.rendered_field = rendered_field
        self.validator = validator
        super(MarkdownField, self).__init__()

    def pre_save(self, model_instance, add):
        value = super(MarkdownField, self).pre_save(model_instance, add)

        if not self.rendered_field:
            return value

        dirty = markdown(
            text=value,
            extensions=EXTENSIONS,
            extension_configs=EXTENSION_CONFIGS
        )

        if self.validator.sanitize:
            clean = bleach.clean(dirty, self.validator.allowed_tags, self.validator.allowed_attrs)
            setattr(model_instance, self.rendered_field, clean)
        else:
            # danger!
            setattr(model_instance, self.rendered_field, dirty)

        return value


class CustomCheckbox(Field):
    template = 'components/custom_checkbox.html'
