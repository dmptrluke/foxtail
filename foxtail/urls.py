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
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^oidc/', include('mozilla_django_oidc.urls')),
    url(r'^markdownx/', include('markdownx.urls')),
    path('account/', include('apps.accounts.urls')),
    path('directory/', include('apps.directory.urls')),
    path('', include('apps.content.urls'))
]

handler400 = 'apps.core.views.handler_400'
handler403 = 'apps.core.views.handler_403'
handler404 = 'apps.core.views.handler_404'
handler500 = 'apps.core.views.handler_500'


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
