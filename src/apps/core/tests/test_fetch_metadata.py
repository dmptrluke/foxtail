from django.test import TestCase

import pytest
from fetch_metadata.test import FetchMetadataTestMixin

pytestmark = pytest.mark.django_db


class TestFetchMetadata(FetchMetadataTestMixin, TestCase):
    """Integration tests for fetch metadata resource isolation policy."""

    URL = '/health/'

    # same-origin POST is allowed
    def test_same_origin_post_allowed(self):
        self.assert_allows(self.URL, site='same-origin')

    # same-origin GET is allowed
    def test_same_origin_get_allowed(self):
        self.assert_allows(self.URL, method='GET', site='same-origin')

    # cross-site POST is blocked
    def test_cross_site_post_blocked(self):
        self.assert_blocks(self.URL, site='cross-site')

    # cross-site GET navigation is allowed (link clicks, bookmarks)
    def test_cross_site_navigation_allowed(self):
        self.assert_allows(self.URL, method='GET', site='cross-site', mode='navigate')

    # cross-site POST navigation is blocked (form submissions from other sites)
    def test_cross_site_post_navigation_blocked(self):
        self.assert_blocks(self.URL, method='POST', site='cross-site', mode='navigate')

    # no-origin requests are allowed (browser bar, bookmarks)
    def test_no_origin_allowed(self):
        self.assert_allows(self.URL, site='none')

    # missing fetch metadata headers are allowed (fail-open default)
    def test_missing_headers_allowed(self):
        self.assert_allows(self.URL, site=None, mode=None, dest=None)

    # same-site GET navigation is allowed (cross-site navigations permitted)
    def test_same_site_navigation_allowed(self):
        self.assert_allows(self.URL, method='GET', site='same-site', mode='navigate')

    # same-site non-navigate GET is blocked (e.g. fetch/XHR from a subdomain)
    def test_same_site_get_blocked(self):
        self.assert_blocks(self.URL, method='GET', site='same-site', mode='cors')

    # same-site POST is blocked
    def test_same_site_post_blocked(self):
        self.assert_blocks(self.URL, site='same-site')

    # OIDC discovery path is exempt from fetch metadata checks
    def test_exempt_path_well_known(self):
        self.assert_allows('/.well-known/openid-configuration', site='cross-site')

    # OIDC endpoint path is exempt from fetch metadata checks
    def test_exempt_path_openid(self):
        self.assert_allows('/openid/jwks', site='cross-site')

    # non-exempt path is still checked
    def test_non_exempt_path_blocked(self):
        self.assert_blocks(self.URL, site='cross-site')
