from django.urls import path

from . import views

app_name = 'organisations'

urlpatterns = [
    path('<slug:slug>/', views.OrganisationDetailView.as_view(), name='organisation_detail'),
]
