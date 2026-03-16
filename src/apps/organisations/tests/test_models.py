from django.conf import settings

import pytest

from ..models import Organisation, SocialLink
from .factories import OrganisationFactory, SocialLinkFactory

pytestmark = pytest.mark.django_db


class TestOrganisationStructuredData:
    # @id is the canonical page URL
    def test_id_is_page_url(self):
        org = OrganisationFactory(slug='test-org')
        sd = org.structured_data
        assert sd['@id'] == settings.SITE_URL + org.get_absolute_url()


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

    # join_label says "Visit Website" for website platform
    def test_join_label_website(self):
        link = SocialLinkFactory.build(platform='website')
        assert link.join_label == 'Visit Website'

    # join_label says "Join on X" for chat platforms
    def test_join_label_chat(self):
        link = SocialLinkFactory.build(platform='discord')
        assert link.join_label == 'Join on Discord'

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


@pytest.mark.django_db
class TestOrganisationFeatured:
    """Featured boolean controls homepage visibility."""

    # featured defaults to False on new organisations
    def test_default_not_featured(self, organisation):
        assert organisation.featured is False

    # filtering by featured=True returns only featured organisations
    def test_filter_featured(self, organisation):
        organisation.featured = True
        organisation.save()
        assert Organisation.objects.filter(featured=True).count() == 1


class TestOrganisationGroupType:
    # group_type defaults to 'organisation'
    def test_default_group_type(self, organisation):
        assert organisation.group_type == 'organisation'

    # filter by group_type returns matching organisations
    def test_filter_by_group_type(self):
        OrganisationFactory(group_type='community')
        OrganisationFactory(group_type='interest')
        OrganisationFactory(group_type='organisation')
        assert Organisation.objects.filter(group_type='community').count() == 1
        assert Organisation.objects.filter(group_type='interest').count() == 1


class TestOrganisationAgeRequirement:
    # age_requirement defaults to blank
    def test_default_blank(self, organisation):
        assert organisation.age_requirement == ''

    # display method returns human-readable label
    def test_display_label(self):
        org = OrganisationFactory(age_requirement='18')
        assert org.get_age_requirement_display() == '18+'

    # filter by age_requirement returns matching organisations
    def test_filter_by_age(self):
        OrganisationFactory(age_requirement='18')
        OrganisationFactory(age_requirement='all')
        OrganisationFactory(age_requirement='')
        assert Organisation.objects.filter(age_requirement='18').count() == 1


class TestOrganisationRegion:
    # region can be blank
    def test_region_blank_by_default(self, organisation):
        assert organisation.region == ''

    # filter by region returns matching organisations
    def test_filter_by_region(self):
        OrganisationFactory(region='auckland')
        OrganisationFactory(region='wellington')
        OrganisationFactory(region='')
        assert Organisation.objects.filter(region='auckland').count() == 1
        assert Organisation.objects.filter(region='wellington').count() == 1
