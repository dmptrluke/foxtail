from unittest.mock import MagicMock

from django.core.exceptions import ValidationError

import pytest

from ..validators import file_size_validator


class TestFileSizeValidator:
    # file under the limit passes validation
    def test_accepts_file_under_limit(self):
        validate = file_size_validator(max_bytes=5 * 1024 * 1024)
        file = MagicMock(size=1 * 1024 * 1024)
        validate(file)

    # file over the limit raises ValidationError
    def test_rejects_file_over_limit(self):
        validate = file_size_validator(max_bytes=5 * 1024 * 1024)
        file = MagicMock(size=10 * 1024 * 1024)
        with pytest.raises(ValidationError):
            validate(file)

    # error message displays the limit in megabytes
    def test_error_message_shows_mb(self):
        validate = file_size_validator(max_bytes=5 * 1024 * 1024)
        file = MagicMock(size=10 * 1024 * 1024)
        with pytest.raises(ValidationError, match='5 MB'):
            validate(file)
