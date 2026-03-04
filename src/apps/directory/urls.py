from django.conf import settings
from django.urls import path

from . import views

app_name = 'directory'
urlpatterns = []

if settings.DIRECTORY_ENABLED:
    urlpatterns += [
        path('', views.ProfileListView.as_view(), name='index'),

        # creation
        path('create/', views.ProfileCreateView.as_view(), name='profile_create'),

        # modification
        path('<slug:slug>/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
        path('<slug:slug>/<int:pk>/edit/', views.CharacterEditView.as_view(), name='character_edit'),

        # placed at the end to not override earlier views
        path('<slug:slug>/', views.ProfileView.as_view(), name='profile'),
        path('<slug:slug>/<int:pk>/', views.CharacterView.as_view(), name='character'),
    ]
