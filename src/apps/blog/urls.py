from django.conf import settings
from django.urls import path

from .feeds import LatestEntriesFeed
from .views import (
    BlogDetailView,
    BlogListView,
    BlogListYearView,
    CommentApproveView,
    CommentDeleteView,
    CommentManageListView,
    PostCreateView,
    PostDeleteView,
    PostManageListView,
    PostUpdateView,
)

COMMENTS_ENABLED = getattr(settings, 'BLOG_COMMENTS', False)

app_name = 'blog'
urlpatterns = [
    path('', BlogListView.as_view(), name='list'),
    path('feed/', LatestEntriesFeed(), name='feed'),
    path('manage/', PostManageListView.as_view(), name='manage_list'),
    path('manage/create/', PostCreateView.as_view(), name='post_create'),
    path('manage/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('manage/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('manage/comments/', CommentManageListView.as_view(), name='comment_manage_list'),
    path('manage/comments/<int:pk>/approve/', CommentApproveView.as_view(), name='comment_approve'),
    path('<int:year>/', BlogListYearView.as_view(), name='list_year'),
    path('<slug:slug>/', BlogDetailView.as_view(), name='detail'),
]

if COMMENTS_ENABLED:
    urlpatterns += [path('comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment_delete')]
