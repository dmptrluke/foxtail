from django.urls import path

from . import feeds
from . import views

urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('feed/', feeds.LatestEntriesFeed(), name='blog_feed'),
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail')
]
