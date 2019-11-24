from django.urls import path

from . import views

urlpatterns = [
    path('characters/', views.CharacterList.as_view(), name='character-list')
]
