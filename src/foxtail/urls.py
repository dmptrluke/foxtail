from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import RedirectView

import apps.blog.sitemaps as blog_sitemaps
import apps.content.sitemaps as content_sitemaps
import apps.core.views as core_views
import apps.events.sitemaps as event_sitemaps

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
    # Admin
    path('admin/', admin.site.urls),
    # Auth & OIDC
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('', include('allauth.idp.urls')),
    # Backward-compatible redirects for old oidc_provider paths
    path('openid/authorize', RedirectView.as_view(pattern_name='idp:oidc:authorization', query_string=True)),
    path('openid/token', RedirectView.as_view(pattern_name='idp:oidc:token')),
    path('openid/userinfo', RedirectView.as_view(pattern_name='idp:oidc:userinfo')),
    path('openid/jwks', RedirectView.as_view(pattern_name='idp:oidc:jwks')),
    path('openid/end-session', RedirectView.as_view(pattern_name='idp:oidc:logout', query_string=True)),
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

    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
