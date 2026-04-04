from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.db import models


def _make_model_with_images(instances):
    image_field = MagicMock(spec=models.ImageField)
    image_field.name = 'image'

    meta = MagicMock()
    meta.get_fields.return_value = [image_field]
    meta.label = 'test.FakeModel'

    model = MagicMock()
    model._meta = meta
    model.objects.exclude.return_value.values_list.return_value = instances
    model.objects.filter.return_value.update = MagicMock()
    return model


class TestCleanMissingImages:
    # dry run lists missing files without clearing them
    @patch('apps.images.management.commands.clean_missing_images.default_storage')
    @patch('apps.images.management.commands.clean_missing_images.apps')
    def test_dry_run_reports_missing(self, mock_apps, mock_storage, capsys):
        model = _make_model_with_images([(1, 'missing.jpg')])
        mock_apps.get_models.return_value = [model]
        mock_storage.exists.return_value = False

        call_command('clean_missing_images', dry_run=True)

        output = capsys.readouterr().out
        assert 'Missing:' in output
        model.objects.filter.return_value.update.assert_not_called()

    # clears image fields that reference missing files
    @patch('apps.images.management.commands.clean_missing_images.default_storage')
    @patch('apps.images.management.commands.clean_missing_images.apps')
    def test_clears_missing_fields(self, mock_apps, mock_storage, capsys):
        model = _make_model_with_images([(1, 'missing.jpg')])
        mock_apps.get_models.return_value = [model]
        mock_storage.exists.return_value = False

        call_command('clean_missing_images')

        output = capsys.readouterr().out
        assert 'Cleared:' in output
        model.objects.filter.return_value.update.assert_called_once()

    # reports success when all files exist
    @patch('apps.images.management.commands.clean_missing_images.default_storage')
    @patch('apps.images.management.commands.clean_missing_images.apps')
    def test_no_missing_images(self, mock_apps, mock_storage, capsys):
        model = _make_model_with_images([(1, 'exists.jpg')])
        mock_apps.get_models.return_value = [model]
        mock_storage.exists.return_value = True

        call_command('clean_missing_images')

        output = capsys.readouterr().out
        assert 'No missing images found' in output
