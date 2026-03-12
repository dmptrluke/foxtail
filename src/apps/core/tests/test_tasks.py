import logging
from unittest.mock import MagicMock, patch

import pytest

from ..tasks import process_imagefields


class _FakeModel:
    DoesNotExist = type('DoesNotExist', (Exception,), {})


@pytest.fixture
def fake_model():
    _FakeModel.objects = MagicMock()
    return _FakeModel


class TestProcessImagefields:
    # missing instance logs a warning and returns early
    @patch('apps.core.tasks.IMAGEFIELDS', [])
    @patch('django.apps.apps.get_model')
    def test_missing_instance_logs_warning(self, mock_get_model, fake_model, caplog):
        fake_model.objects.get.side_effect = _FakeModel.DoesNotExist
        mock_get_model.return_value = fake_model

        with caplog.at_level(logging.WARNING):
            process_imagefields('events', 'event', 999)

        assert 'not found' in caplog.text

    # processes each rendition spec for matching image fields
    @patch('apps.core.tasks.IMAGEFIELDS')
    @patch('django.apps.apps.get_model')
    def test_processes_renditions(self, mock_get_model, mock_imagefields, fake_model, caplog):
        mock_instance = MagicMock()
        fake_model.objects.get.return_value = mock_instance
        mock_get_model.return_value = fake_model

        mock_field = MagicMock()
        mock_field.model = _FakeModel
        mock_field.name = 'image'
        mock_imagefields.__iter__ = lambda self: iter([mock_field])

        file_obj = MagicMock()
        file_obj.name = 'photo.jpg'
        file_obj.field.formats = ['thumb', 'large']
        mock_instance.image = file_obj

        with caplog.at_level(logging.INFO):
            process_imagefields('events', 'event', 1)

        assert file_obj.process.call_count == 2

    # exception during one rendition does not stop processing others
    @patch('apps.core.tasks.IMAGEFIELDS')
    @patch('django.apps.apps.get_model')
    def test_exception_continues(self, mock_get_model, mock_imagefields, fake_model, caplog):
        mock_instance = MagicMock()
        fake_model.objects.get.return_value = mock_instance
        mock_get_model.return_value = fake_model

        mock_field = MagicMock()
        mock_field.model = _FakeModel
        mock_field.name = 'image'
        mock_imagefields.__iter__ = lambda self: iter([mock_field])

        file_obj = MagicMock()
        file_obj.name = 'photo.jpg'
        file_obj.field.formats = ['thumb', 'large']
        file_obj.process.side_effect = [Exception('vips error'), None]
        mock_instance.image = file_obj

        with caplog.at_level(logging.ERROR):
            process_imagefields('events', 'event', 1)

        assert file_obj.process.call_count == 2
        assert 'Failed to process' in caplog.text
