from django.conf import settings
from django.urls import path

from . import views

urlpatterns = []

if settings.DIRECTORY_ENABLED:
    urlpatterns += [

        path('', views.DirectoryIndex.as_view(), name='dir_index'),

        path('<slug:slug>/', views.ProfileView.as_view(), name='dir_profile'),
        path('edit/<slug:slug>/', views.ProfileEditView.as_view(), name='dir_profile_edit'),

        path('<slug:slug>/<int:pk>/', views.CharacterView.as_view(), name='dir_character'),
        path('edit/<slug:slug>/<int:pk>/', views.CharacterEditView.as_view(), name='dir_character_edit'),
    ]
