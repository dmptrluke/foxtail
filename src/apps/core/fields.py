from functools import reduce
from operator import or_

from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class AutoSlugField(models.SlugField):
    """Auto-populating slug field with uniqueness handling.

    Replacement for django-slugger's AutoSlugField.
    """

    def __init__(self, populate_from, *args, **kwargs):
        self.populate_from = populate_from
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['populate_from'] = self.populate_from
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        return super().formfield(required=False, **kwargs)

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)

        if not value:
            from_field_value = getattr(model_instance, self.populate_from)
            value = slugify(from_field_value)[: self.max_length]

            if any(
                (
                    self.unique,
                    self.unique_for_date,
                    self.unique_for_month,
                    self.unique_for_year,
                    self.model._meta.unique_together,
                )
            ):
                value = self._get_unique_slug(value, model_instance)

            setattr(model_instance, self.attname, value)

        return value

    def _get_unique_lookups(self, instance):
        if self.unique:
            return Q()

        lookups = []

        if self.unique_for_date:
            lookup_value = getattr(instance, self.unique_for_date)
            lookups.append(
                {
                    f'{self.unique_for_date}__day': lookup_value.day,
                    f'{self.unique_for_date}__month': lookup_value.month,
                    f'{self.unique_for_date}__year': lookup_value.year,
                }
            )

        if self.unique_for_month:
            lookup_value = getattr(instance, self.unique_for_month)
            lookups.append(
                {
                    f'{self.unique_for_month}__month': lookup_value.month,
                }
            )

        if self.unique_for_year:
            lookup_value = getattr(instance, self.unique_for_year)
            lookups.append(
                {
                    f'{self.unique_for_year}__year': lookup_value.year,
                }
            )

        for field_group in self.model._meta.unique_together:
            if self.attname in field_group:
                lookups.append(
                    {
                        field_name: getattr(instance, field_name)
                        for field_name in field_group
                        if field_name != self.attname
                    }
                )

        return reduce(or_, (Q(**lookup) for lookup in lookups), Q())

    def _get_unique_slug(self, slug, instance):
        conflicts = self.model._default_manager.filter(
            ~Q(pk=instance.pk),
            self._get_unique_lookups(instance),
        )

        taken_slugs = sorted(
            conflicts.filter(**{f'{self.attname}__regex': rf'^{slug}(-\d+)?$'}).values_list(self.attname, flat=True)
        )

        if slug not in taken_slugs:
            return slug

        taken_slugs.remove(slug)

        i = 1
        for value in taken_slugs:
            if not value.endswith(str(i)):
                break
            i += 1

        return f'{slug}-{i}'
