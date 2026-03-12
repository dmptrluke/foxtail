from datetime import date

from django.db import connection, models

import pytest

from ..fields import AutoSlugField

pytestmark = pytest.mark.django_db


class UniqueSlugModel(models.Model):
    title = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='title', unique=True, max_length=50)

    class Meta:
        app_label = 'core'


class UniqueForYearSlugModel(models.Model):
    title = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='title', unique_for_year='pub_date', max_length=50)
    pub_date = models.DateField()

    class Meta:
        app_label = 'core'


@pytest.fixture
def unique_slug_model():
    with connection.schema_editor() as editor:
        editor.create_model(UniqueSlugModel)
    yield UniqueSlugModel
    with connection.schema_editor() as editor:
        editor.delete_model(UniqueSlugModel)


@pytest.fixture
def unique_for_year_slug_model():
    with connection.schema_editor() as editor:
        editor.create_model(UniqueForYearSlugModel)
    yield UniqueForYearSlugModel
    with connection.schema_editor() as editor:
        editor.delete_model(UniqueForYearSlugModel)


class TestAutoSlugFieldUnique:
    # empty slug is auto-populated from the source field
    def test_generates_slug_from_source(self, unique_slug_model):
        obj = unique_slug_model.objects.create(title='Hello World')
        assert obj.slug == 'hello-world'

    # existing slug value is preserved on save
    def test_preserves_existing_slug(self, unique_slug_model):
        obj = unique_slug_model.objects.create(title='Hello World', slug='custom-slug')
        assert obj.slug == 'custom-slug'

    # generated slug is truncated to max_length
    def test_truncates_to_max_length(self, unique_slug_model):
        obj = unique_slug_model.objects.create(title='a' * 200)
        assert len(obj.slug) <= 50

    # duplicate slug gets a -1 suffix
    def test_appends_suffix_on_collision(self, unique_slug_model):
        unique_slug_model.objects.create(title='Hello World')
        obj2 = unique_slug_model.objects.create(title='Hello World')
        assert obj2.slug == 'hello-world-1'

    # suffix increments to find lowest available number
    def test_finds_next_available_suffix(self, unique_slug_model):
        unique_slug_model.objects.create(title='Hello World')
        unique_slug_model.objects.create(title='Hello World')
        obj3 = unique_slug_model.objects.create(title='Hello World')
        assert obj3.slug == 'hello-world-2'

    # updating an instance does not conflict with its own slug
    def test_update_does_not_conflict_with_self(self, unique_slug_model):
        obj = unique_slug_model.objects.create(title='Hello World')
        obj.title = 'Changed Title'
        obj.save()
        assert obj.slug == 'hello-world'


class TestAutoSlugFieldUniqueForYear:
    # same title in different years gets the same slug
    def test_different_years_no_collision(self, unique_for_year_slug_model):
        unique_for_year_slug_model.objects.create(title='Annual Meetup', pub_date=date(2025, 6, 1))
        obj2 = unique_for_year_slug_model.objects.create(title='Annual Meetup', pub_date=date(2026, 6, 1))
        assert obj2.slug == 'annual-meetup'

    # same title in the same year gets a suffix
    def test_same_year_collision(self, unique_for_year_slug_model):
        unique_for_year_slug_model.objects.create(title='Annual Meetup', pub_date=date(2025, 3, 1))
        obj2 = unique_for_year_slug_model.objects.create(title='Annual Meetup', pub_date=date(2025, 9, 1))
        assert obj2.slug == 'annual-meetup-1'
