from django.urls import path

from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.OrganisationListView.as_view(), name='organisation_list'),
    path('<slug:slug>/', views.OrganisationDetailView.as_view(), name='organisation_detail'),
]
