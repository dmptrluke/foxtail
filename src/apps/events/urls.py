from django.urls import path

from . import views

app_name = 'events'
urlpatterns = [
    path('', views.EventListView.as_view(), name='list'),
    path('<int:year>/', views.EventListYearView.as_view(), name='list_year'),
    path('<int:year>/<slug:slug>/', views.EventDetailView.as_view(), name='detail'),
]
