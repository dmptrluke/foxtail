from django.conf import settings

import pytest

from ..models import SocialLink
from .factories import OrganisationFactory, SocialLinkFactory

pytestmark = pytest.mark.django_db


class TestOrganisationStructuredData:
    # structured data includes @id as a fragment URI
    def test_id_present(self):
        org = OrganisationFactory()
        sd = org.structured_data
        expected_id = settings.SITE_URL + org.get_absolute_url() + '#org'
        assert sd['@id'] == expected_id

    # @id is stable and can be used as a cross-reference
    def test_id_matches_url_fragment(self):
        org = OrganisationFactory(slug='test-org')
        sd = org.structured_data
        assert sd['@id'].endswith('/organisations/test-org/#org')


class TestSocialLink:
    # __str__ includes platform display name and organisation
    def test_str(self):
        org = OrganisationFactory(name='Wellington Furries')
        link = SocialLinkFactory(organisation=org, platform='telegram')
        assert str(link) == 'Telegram - Wellington Furries'

    # icon_name maps platform to correct icon
    def test_icon_name_known_platform(self):
        link = SocialLinkFactory.build(platform='twitter')
        assert link.icon_name == 'x'

    # icon_name falls back to link_variant for unknown platform
    def test_icon_name_fallback(self):
        link = SocialLinkFactory.build(platform='unknown')
        assert link.icon_name == 'link_variant'

    # primary links sort before non-primary, then alphabetically by platform
    def test_ordering(self):
        org = OrganisationFactory()
        secondary = SocialLinkFactory(organisation=org, platform='twitter', is_primary=False)
        primary = SocialLinkFactory(organisation=org, platform='discord', is_primary=True)
        tertiary = SocialLinkFactory(organisation=org, platform='bluesky', is_primary=False)
        result = list(SocialLink.objects.filter(organisation=org))
        assert result == [primary, tertiary, secondary]

    # all platform choices have a corresponding icon mapping
    def test_all_platforms_have_icons(self):
        for platform_code, _ in SocialLink.PLATFORM_CHOICES:
            assert platform_code in SocialLink.PLATFORM_ICONS
