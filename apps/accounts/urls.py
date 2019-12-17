from django.urls import path

from apps.accounts import views

urlpatterns = [
    path('', views.UserView.as_view(), name='account_profile'),
    path('applications/', views.ConsentList.as_view(), name='account_application_list')
]
