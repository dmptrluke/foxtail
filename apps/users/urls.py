from django.contrib.auth.urls import views as auth_views
from django.urls import path

urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]