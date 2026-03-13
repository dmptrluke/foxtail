from django.urls import path

from . import views

app_name = 'series'

urlpatterns = [
    path('<slug:slug>/', views.EventSeriesDetailView.as_view(), name='eventseries_detail'),
]
