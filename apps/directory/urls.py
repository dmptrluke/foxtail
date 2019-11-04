from django.urls import path

from . import views

urlpatterns = [
    path('characters/', views.CharacterListView.as_view(), name='character-list')
]
