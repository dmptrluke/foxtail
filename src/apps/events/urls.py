from django.urls import path

from . import views

app_name = 'events'
urlpatterns = [
    path('', views.EventList.as_view(), name='list'),
    path('<int:year>/', views.EventListYear.as_view(), name='list_year'),
    path('<int:year>/<slug:slug>/', views.EventDetail.as_view(), name='detail'),
]
