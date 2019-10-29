from django.urls import path
from apps.users.views import *

urlpatterns = [
    path('logout', LogoutView.as_view(), name='user-logout'),
    path('profile', UserView.as_view(), name='user-profile')
]
