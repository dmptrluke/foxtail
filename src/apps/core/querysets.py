from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db.models import ForeignKey, Model


def filter_by_parent(queryset, parent_field, value):
    """Filter choices by a parent ForeignKey, returning an empty queryset for empty or invalid keys"""
    field = queryset.model._meta.get_field(parent_field)
    if not isinstance(field, ForeignKey):
        raise ImproperlyConfigured('Parent filters require a ForeignKey field.')
    if isinstance(value, Model):
        value = field.target_field.value_from_object(value)
    if value in (None, ''):
        return queryset.none()
    try:
        value = field.target_field.clean(value, None)
    except ValidationError:
        return queryset.none()
    return queryset.filter(**{field.attname: value})
