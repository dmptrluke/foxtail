import pytest

from ..forms import EventForm
from ..models import Event

pytestmark = pytest.mark.django_db


class TestEventForm:
    # existing event's tags are loaded into the initial field
    def test_tags_loaded_on_edit(self, event: Event):
        event.tags.add('meetup', 'social')
        form = EventForm(instance=event)
        assert set(form.fields['tags'].initial) == set(event.tags.all())

    # image_ppoi field is included (required for ProcessedImageField validation)
    def test_image_ppoi_in_fields(self):
        form = EventForm()
        assert 'image_ppoi' in form.fields
