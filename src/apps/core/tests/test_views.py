from textwrap import dedent

from django.test import RequestFactory

from ..views import robots


def test_robots_enabled(request_factory: RequestFactory, settings):
    settings.ROBOTS_ALLOWED = True

    request = request_factory.get('/robots.txt')

    response = robots(request)

    expected_response = dedent(f"""\
        User-agent: *
        Disallow:

        Sitemap: {settings.SITE_URL}/sitemap.xml
    """)

    assert response.content.decode('utf-8') == expected_response
    assert response['content-type'] == 'text/plain'


def test_robots_disabled(request_factory: RequestFactory, settings):
    settings.ROBOTS_ALLOWED = False

    request = request_factory.get('/robots.txt')

    response = robots(request)

    expected_response = dedent("""\
        User-agent: *
        Disallow: /
    """)

    assert response.content.decode('utf-8') == expected_response
    assert response['content-type'] == 'text/plain'
