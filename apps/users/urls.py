from django.urls import path
from apps.users.views import *

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout')
]
