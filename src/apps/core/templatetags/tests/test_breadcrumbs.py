import json

from django.test import RequestFactory

from ..breadcrumbs import breadcrumbs


class TestBreadcrumbs:
    def _make_context(self, request_factory, site_url='https://furry.nz'):
        request = request_factory.get('/')
        return {'request': request, 'SITE_URL': site_url}

    # output contains nav element with breadcrumb list items
    def test_renders_html_nav(self, request_factory: RequestFactory):
        ctx = self._make_context(request_factory)
        result = breadcrumbs(ctx, '/events/', 'Events', '/events/1/', 'My Event')
        assert '<nav aria-label="Breadcrumb">' in result
        assert '<a href="/events/">Events</a>' in result

    # last breadcrumb is marked active with no link
    def test_last_crumb_is_active(self, request_factory: RequestFactory):
        ctx = self._make_context(request_factory)
        result = breadcrumbs(ctx, '/events/', 'Events', '/events/1/', 'My Event')
        assert 'aria-current="page">My Event</li>' in result
        assert '<a href="/events/1/">' not in result

    # named URL patterns are resolved via reverse()
    def test_resolves_named_urls(self, request_factory: RequestFactory):
        ctx = self._make_context(request_factory)
        result = breadcrumbs(ctx, 'health', 'Health', '/current/', 'Current')
        assert '<a href="/health/">Health</a>' in result

    # non-reversible URL strings pass through as-is
    def test_literal_url_passthrough(self, request_factory: RequestFactory):
        ctx = self._make_context(request_factory)
        result = breadcrumbs(ctx, '/custom/path/', 'Custom', '/here/', 'Here')
        assert '<a href="/custom/path/">Custom</a>' in result

    # JSON-LD has correct position numbers and uses SITE_URL prefix
    def test_json_ld_positions(self, request_factory: RequestFactory):
        ctx = self._make_context(request_factory, site_url='https://furry.nz')
        result = breadcrumbs(ctx, '/events/', 'Events', '/events/1/', 'My Event')

        json_start = result.index('application/ld+json">') + len('application/ld+json">')
        json_end = result.index('</script>')
        ld = json.loads(result[json_start:json_end])

        assert ld['@type'] == 'BreadcrumbList'
        assert len(ld['itemListElement']) == 2
        assert ld['itemListElement'][0]['position'] == 1
        assert ld['itemListElement'][0]['item'] == 'https://furry.nz/events/'
        assert ld['itemListElement'][1]['position'] == 2
