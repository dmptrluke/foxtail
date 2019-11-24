from django.urls import path

from . import views

urlpatterns = [
    path('', views.EventList.as_view(), name='event_list'),
    path('<int:year>/', views.EventListYear.as_view(), name="event_list_year"),
    path('<int:year>/<int:pk>/', views.EventDetail.as_view(), name='event_detail'),
]
