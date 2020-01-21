from django.db.models import SmallIntegerField

from .constants import PrivacyChoices


class PrivacyField(SmallIntegerField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = PrivacyChoices.choices
        kwargs['default'] = PrivacyChoices.PUBLIC
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['choices']
        if kwargs['default'] == PrivacyChoices.PUBLIC:
            del kwargs['default']
        return name, path, args, kwargs
