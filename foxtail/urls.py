# flake8: noqa

"""foxtail URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

import apps.content.sitemaps as content_sitemaps
import apps.core.views as core_views
import apps.events.sitemaps as event_sitemaps
import foxtail_blog.sitemaps as blog_sitemaps

sitemaps = {
    'static': content_sitemaps.StaticSitemap,
    'page': content_sitemaps.PageSitemap,
    'post': blog_sitemaps.PostSitemap,
    'event': event_sitemaps.EventSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', core_views.robots, name='robots'),
    path('.well-known/openid-configuration/', core_views.redirect_provider_info),
    path('admin/django-rq/', include('django_rq.urls')),
    path('admin/', admin.site.urls),
    path('openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('directory/', include('apps.directory.urls')),
    path('events/', include('apps.events.urls')),
    path('contact/', include('foxtail_contact.urls')),
    path('blog/', include('foxtail_blog.urls')),
    path('', include('apps.content.urls'))
]

handler500 = 'apps.core.views.handler_500'


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

    if not settings.AZURE_MEDIA:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
