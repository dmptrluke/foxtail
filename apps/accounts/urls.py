from django.urls import path

from apps.accounts import views

urlpatterns = [
    path('profile', views.UserView.as_view(), name='account_profile'),
    path('consents', views.ConsentList.as_view(), name='account_concent_list')
]
