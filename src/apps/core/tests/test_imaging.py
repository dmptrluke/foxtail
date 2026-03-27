from io import BytesIO
from unittest.mock import MagicMock, patch

import pyvips

from ..imaging import downscale_fieldfile, downscale_image


def _make_jpeg(width, height, quality=75):
    """Generate a real JPEG at the given dimensions."""
    image = pyvips.Image.black(width, height, bands=3)
    return image.write_to_buffer('.jpg', Q=quality)


def _make_png(width, height):
    """Generate a real PNG at the given dimensions."""
    image = pyvips.Image.black(width, height, bands=3)
    return image.write_to_buffer('.png')


def _make_webp(width, height, quality=75):
    """Generate a real WebP at the given dimensions."""
    image = pyvips.Image.black(width, height, bands=3)
    return image.write_to_buffer('.webp', Q=quality)


class TestDownscaleImage:
    # returns None when image is within limits
    def test_no_resize_needed(self):
        data = _make_jpeg(2000, 1500)
        assert downscale_image(data, max_dimension=4096) is None

    # returns None when image is exactly at the limit
    def test_exact_limit(self):
        data = _make_jpeg(4096, 3000)
        assert downscale_image(data, max_dimension=4096) is None

    # downscales landscape image exceeding limit
    def test_downscales_landscape(self):
        data = _make_jpeg(6000, 4000)
        result = downscale_image(data, max_dimension=4096)
        assert result is not None

        image = pyvips.Image.new_from_buffer(result, '')
        assert image.width == 4096
        assert image.height == 2731

    # downscales portrait image exceeding limit
    def test_downscales_portrait(self):
        data = _make_jpeg(4000, 6000)
        result = downscale_image(data, max_dimension=4096)
        assert result is not None

        image = pyvips.Image.new_from_buffer(result, '')
        assert image.width == 2731
        assert image.height == 4096

    # preserves JPEG format
    def test_preserves_jpeg(self):
        data = _make_jpeg(6000, 4000)
        result = downscale_image(data, max_dimension=4096)

        image = pyvips.Image.new_from_buffer(result, '')
        assert image.get('vips-loader') == 'jpegload_buffer'

    # preserves PNG format
    def test_preserves_png(self):
        data = _make_png(6000, 4000)
        result = downscale_image(data, max_dimension=4096)

        image = pyvips.Image.new_from_buffer(result, '')
        assert image.get('vips-loader') == 'pngload_buffer'

    # preserves WebP format
    def test_preserves_webp(self):
        data = _make_webp(6000, 4000)
        result = downscale_image(data, max_dimension=4096)

        image = pyvips.Image.new_from_buffer(result, '')
        assert image.get('vips-loader') == 'webpload_buffer'

    # output is smaller than input for oversized JPEG
    def test_output_smaller(self):
        data = _make_jpeg(6000, 4000)
        result = downscale_image(data, max_dimension=4096)
        assert len(result) < len(data)

    # returns None for unsupported formats (e.g. TIFF)
    def test_unsupported_format(self):
        image = pyvips.Image.black(6000, 4000, bands=3)
        data = image.write_to_buffer('.tif')
        assert downscale_image(data, max_dimension=4096) is None

    # uses MAX_IMAGE_DIMENSION from settings when no max_dimension given
    @patch('apps.core.imaging.settings')
    def test_uses_settings_default(self, mock_settings):
        mock_settings.MAX_IMAGE_DIMENSION = 2000
        data = _make_jpeg(3000, 2000)
        result = downscale_image(data)
        assert result is not None


class TestDownscaleFieldfile:
    # skips committed files (already in storage)
    def test_skips_committed(self):
        fieldfile = MagicMock()
        fieldfile.name = 'photo.jpg'
        fieldfile._committed = True
        assert downscale_fieldfile(fieldfile) is False

    # skips empty fields
    def test_skips_empty(self):
        assert downscale_fieldfile(None) is False

        fieldfile = MagicMock()
        fieldfile.name = ''
        assert downscale_fieldfile(fieldfile) is False

    # replaces file contents on oversized upload
    def test_replaces_oversized(self):
        data = _make_jpeg(6000, 4000)
        upload = BytesIO(data)
        fieldfile = MagicMock()
        fieldfile.name = 'photo.jpg'
        fieldfile._committed = False
        fieldfile.file = upload

        assert downscale_fieldfile(fieldfile, max_dimension=4096) is True

        # file attribute was replaced with a new BytesIO
        new_file = fieldfile.file
        assert isinstance(new_file, BytesIO)
        result = pyvips.Image.new_from_buffer(new_file.read(), '')
        assert result.width == 4096

    # leaves small uploads untouched
    def test_leaves_small_upload(self):
        data = _make_jpeg(2000, 1500)
        upload = BytesIO(data)
        fieldfile = MagicMock()
        fieldfile.name = 'photo.jpg'
        fieldfile._committed = False
        fieldfile.file = upload

        assert downscale_fieldfile(fieldfile, max_dimension=4096) is False

    # handles pyvips errors gracefully (corrupt file)
    def test_handles_corrupt_file(self):
        upload = BytesIO(b'not an image')
        fieldfile = MagicMock()
        fieldfile.name = 'corrupt.jpg'
        fieldfile._committed = False
        fieldfile.file = upload

        assert downscale_fieldfile(fieldfile, max_dimension=4096) is False
