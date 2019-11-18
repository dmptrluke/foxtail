import bleach
import bleach_whitelist
from crispy_forms.layout import Field
from django.conf import settings
from markdownx.models import MarkdownxField
from markdown import markdown

EXTENSIONS = getattr(settings, 'MARKDOWNX_MARKDOWN_EXTENSIONS', [])
EXTENSION_CONFIGS = getattr(settings, 'MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS', [])

ALLOWED_TAGS = bleach_whitelist.markdown_tags + ['dl', 'del', 'abbr']
ALLOWED_ATTRS = {
    'abbr': ['title']
}

ALLOWED_ATTRS.update(bleach_whitelist.markdown_attrs)


class CustomCheckbox(Field):
    template = 'components/custom_checkbox.html'


class MarkdownField(MarkdownxField):
    def __init__(self, rendered_field=None, sanitize=True):
        self.rendered_field = rendered_field
        self.sanitize = sanitize
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

        if self.sanitize:
            clean = bleach.clean(dirty, ALLOWED_TAGS, ALLOWED_ATTRS)
            setattr(model_instance, self.rendered_field, clean)
        else:
            # danger!
            setattr(model_instance, self.rendered_field, dirty)

        return value
