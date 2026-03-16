from django.urls import path

from . import views

app_name = 'events'
urlpatterns = [
    path('', views.EventListView.as_view(), name='list'),
    path('manage/', views.EventManageListView.as_view(), name='manage_list'),
    path('manage/create/', views.EventCreateView.as_view(), name='event_create'),
    path('manage/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_edit'),
    path('manage/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('<int:pk>/interest/', views.EventInterestToggleView.as_view(), name='interest'),
    path('<int:pk>/calendar/', views.EventICSView.as_view(), name='event_ics'),
    path('<int:year>/', views.EventListYearView.as_view(), name='list_year'),
    path('<int:year>/<slug:slug>/', views.EventDetailView.as_view(), name='detail'),
]
