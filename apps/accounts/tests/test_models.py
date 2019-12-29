from django.contrib.auth import get_user_model
from django.test import TestCase

USER_USERNAME = "mrtest123"
USER_FULL_NAME = "Testy Tester"


class UserModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(USER_USERNAME, 'temporary@gmail.com', 'temporary')
        self.user.full_name = USER_FULL_NAME

    def test_string_representation(self):
        self.assertEqual(str(self.user), USER_USERNAME)

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), USER_USERNAME)

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), USER_FULL_NAME)
