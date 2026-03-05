from django.conf import settings
from django.urls import path

from .feeds import LatestEntriesFeed
from .views import BlogDetailView, BlogListView, CommentDeleteView

COMMENTS_ENABLED = getattr(settings, 'BLOG_COMMENTS', False)

app_name = 'blog'
urlpatterns = [
    path('', BlogListView.as_view(), name='list'),
    path('feed/', LatestEntriesFeed(), name='feed'),
    path('<slug:slug>/', BlogDetailView.as_view(), name='detail'),
]

if COMMENTS_ENABLED:
    urlpatterns += [
        path('comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment_delete')
    ]
