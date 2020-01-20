from django.db.models import IntegerChoices, SmallIntegerField


class PrivacyChoices(IntegerChoices):
    NOBODY = 0, 'Only Me'
    PUBLIC = 5, 'Public'
    SIGNED_IN = 10, 'Signed-in Users'


class PrivacyField(SmallIntegerField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = PrivacyChoices.choices
        kwargs['default'] = PrivacyChoices.PUBLIC
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['choices']
        del kwargs['default']
        return name, path, args, kwargs
