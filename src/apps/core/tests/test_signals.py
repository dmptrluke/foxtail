from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from ..signals import _has_image, _image_fields_changed, on_post_init, on_post_save


def _make_field(name, ppoi_field=None):
    field = MagicMock()
    field.name = name
    field.formats = ['thumb']
    field.ppoi_field = ppoi_field
    return field


def _make_instance(file_name='photo.jpg'):
    file_obj = SimpleNamespace(name=file_name)
    return SimpleNamespace(
        image=file_obj,
        _meta=SimpleNamespace(app_label='core', model_name='fakemodel'),
        pk=1,
    )


class TestOnPostInit:
    # snapshots current file name into instance __dict__
    @patch('apps.core.signals.fields_by_model')
    def test_snapshots_field_values(self, mock_fbm):
        field = _make_field('image')
        mock_fbm.get.return_value = [field]

        instance = _make_instance()
        on_post_init(sender=None, instance=instance)

        assert instance.__dict__['_orig_image'] == 'photo.jpg'

    # snapshots PPOI field value when present
    @patch('apps.core.signals.fields_by_model')
    def test_snapshots_ppoi(self, mock_fbm):
        field = _make_field('image', ppoi_field='image_ppoi')
        mock_fbm.get.return_value = [field]

        instance = _make_instance()
        instance.image_ppoi = '0.5x0.5'
        on_post_init(sender=None, instance=instance)

        assert instance.__dict__['_orig_image_ppoi'] == '0.5x0.5'


class TestHasImage:
    # returns True when an image field has a file set
    @patch('apps.core.signals.fields_by_model')
    def test_with_file(self, mock_fbm):
        field = _make_field('image')
        mock_fbm.get.return_value = [field]

        instance = _make_instance(file_name='photo.jpg')
        assert _has_image(instance) is True

    # returns False when image field is empty
    @patch('apps.core.signals.fields_by_model')
    def test_without_file(self, mock_fbm):
        field = _make_field('image')
        mock_fbm.get.return_value = [field]

        instance = _make_instance(file_name='')
        assert _has_image(instance) is False


class TestImageFieldsChanged:
    # detects when file name differs from snapshot
    @patch('apps.core.signals.fields_by_model')
    def test_detects_file_change(self, mock_fbm):
        field = _make_field('image')
        mock_fbm.get.return_value = [field]

        instance = _make_instance(file_name='new.jpg')
        instance.__dict__['_orig_image'] = 'old.jpg'

        assert _image_fields_changed(instance) is True

    # detects PPOI changes
    @patch('apps.core.signals.fields_by_model')
    def test_detects_ppoi_change(self, mock_fbm):
        field = _make_field('image', ppoi_field='image_ppoi')
        mock_fbm.get.return_value = [field]

        instance = _make_instance(file_name='photo.jpg')
        instance.__dict__['_orig_image'] = 'photo.jpg'
        instance.__dict__['_orig_image_ppoi'] = '0.5x0.5'
        instance.image_ppoi = '0.3x0.7'

        assert _image_fields_changed(instance) is True

    # returns False when nothing changed
    @patch('apps.core.signals.fields_by_model')
    def test_no_change(self, mock_fbm):
        field = _make_field('image')
        mock_fbm.get.return_value = [field]

        instance = _make_instance(file_name='photo.jpg')
        instance.__dict__['_orig_image'] = 'photo.jpg'

        assert _image_fields_changed(instance) is False


class TestOnPostSave:
    # newly created instance without image does not enqueue processing
    @patch('apps.core.signals.process_imagefields')
    @patch('apps.core.signals._has_image', return_value=False)
    def test_skips_created_without_image(self, mock_has, mock_task):
        instance = MagicMock()
        on_post_save(sender=None, instance=instance, created=True)
        mock_task.assert_not_called()

    # newly created instance with an image enqueues processing
    @patch('apps.core.signals.transaction')
    @patch('apps.core.signals._has_image', return_value=True)
    def test_enqueues_created_with_image(self, mock_has, mock_txn):
        instance = MagicMock()
        instance._meta.app_label = 'events'
        instance._meta.model_name = 'event'
        instance.pk = 1

        on_post_save(sender=None, instance=instance, created=True)

        mock_txn.on_commit.assert_called_once()

    # updated instance with no field changes does not enqueue processing
    @patch('apps.core.signals.process_imagefields')
    @patch('apps.core.signals._image_fields_changed', return_value=False)
    def test_skips_unchanged_update(self, mock_changed, mock_task):
        instance = MagicMock()
        on_post_save(sender=None, instance=instance, created=False)
        mock_task.assert_not_called()

    # changed image field enqueues processing via on_commit
    @patch('apps.core.signals.transaction')
    @patch('apps.core.signals._image_fields_changed', return_value=True)
    def test_enqueues_on_change(self, mock_changed, mock_txn):
        instance = MagicMock()
        instance._meta.app_label = 'events'
        instance._meta.model_name = 'event'
        instance.pk = 42

        on_post_save(sender=None, instance=instance, created=False)

        mock_txn.on_commit.assert_called_once()
        callback = mock_txn.on_commit.call_args[0][0]

        with patch('apps.core.signals.process_imagefields') as mock_task:
            callback()
            mock_task.assert_called_once_with('events', 'event', 42)
