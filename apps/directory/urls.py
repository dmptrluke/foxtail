from django.conf import settings
from django.urls import path

from . import views

app_name = 'directory'
urlpatterns = []

if settings.DIRECTORY_ENABLED:
    urlpatterns += [

        path('', views.DirectoryIndex.as_view(), name='index'),

        path('<slug:slug>/', views.ProfileView.as_view(), name='profile'),
        path('edit/<slug:slug>/', views.ProfileEditView.as_view(), name='profile_edit'),

        path('<slug:slug>/<int:pk>/', views.CharacterView.as_view(), name='character'),
        path('edit/<slug:slug>/<int:pk>/', views.CharacterEditView.as_view(), name='character_edit'),
    ]
