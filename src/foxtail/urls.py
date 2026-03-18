from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from allauth.idp.oidc import views as oidc_views

import apps.blog.sitemaps as blog_sitemaps
import apps.content.sitemaps as content_sitemaps
import apps.core.views as core_views
import apps.events.sitemaps as event_sitemaps
import apps.organisations.views as organisations_views

sitemaps = {
    'static': content_sitemaps.StaticSitemap,
    'page': content_sitemaps.PageSitemap,
    'post': blog_sitemaps.PostSitemap,
    'event': event_sitemaps.EventSitemap,
}

urlpatterns = [
    # Infrastructure
    path('health/', core_views.health, name='health'),
    path('robots.txt', core_views.robots, name='robots'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    # Redirects
    path('go/<int:pk>/', organisations_views.SocialLinkRedirectView.as_view(), name='social_link_redirect'),
    # Admin
    path('admin/', admin.site.urls),
    # Auth & OIDC
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('', include('allauth.idp.urls')),
    # Backward-compatible aliases for old oidc_provider paths
    path('openid/authorize', oidc_views.authorization),
    path('openid/token', oidc_views.token),
    path('openid/userinfo', oidc_views.user_info),
    path('openid/jwks', oidc_views.jwks),
    path('openid/end-session', oidc_views.logout),
    # Apps
    path('autocomplete/', include('apps.core.autocomplete_urls')),
    path('blog/', include('apps.blog.urls')),
    path('contact/', include('apps.contact.urls')),
    path('events/', include('apps.events.urls')),
    path('groups/', include('apps.organisations.urls')),
    path('series/', include('apps.organisations.series_urls')),
    path('', include('apps.content.urls')),
]

handler500 = 'apps.core.views.handler_500'

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
        path('__test__/error/<int:code>/', core_views.test_error, name='test_error'),
    ]
