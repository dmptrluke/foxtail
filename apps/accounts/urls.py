from django.urls import path, include

from apps.accounts import views

urlpatterns = [

    path('profile', views.UserView.as_view(), name='profile')
]
