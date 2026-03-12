from unittest.mock import patch

from django.contrib.messages import get_messages
from django.urls import reverse

import pytest
from published.constants import AVAILABLE

from ..models import Comment, Post

pytestmark = pytest.mark.django_db


class TestBlogListView:
    url = reverse('blog:list')

    # published posts are listed
    def test_renders_published_posts(self, client, post: Post):
        response = client.get(self.url)
        assert response.status_code == 200
        assert post in response.context['posts']

    # full-text search returns matching posts
    def test_search(self, client, post: Post):
        response = client.get(self.url, {'q': post.title})
        assert response.status_code == 200
        assert post in response.context['posts']

    # tag filter returns posts with that tag
    def test_tag_filter(self, client, post: Post):
        tag = post.tags.first()
        response = client.get(self.url, {'tag': tag.slug})
        assert response.status_code == 200
        assert post in response.context['posts']

    # invalid tag slug returns 404
    def test_tag_filter_invalid(self, client, post: Post):
        response = client.get(self.url, {'tag': 'nonexistent-tag-slug'})
        assert response.status_code == 404

    # sidebar context includes recent posts and tags
    def test_sidebar_context(self, client, post: Post):
        response = client.get(self.url)
        assert 'sidebar_post_list' in response.context
        assert 'sidebar_tag_list' in response.context


class TestBlogListYearView:
    # posts filtered to the requested year
    def test_filters_by_year(self, client, post: Post):
        year = post.created.year
        response = client.get(reverse('blog:list_year', kwargs={'year': year}))
        assert response.status_code == 200
        assert post in response.context['posts']
        assert response.context['year'] == str(year)


class TestBlogDetailView:
    # published post renders with comment form in context
    def test_renders_post(self, client, user, post: Post):
        client.force_login(user)
        response = client.get(reverse('blog:detail', kwargs={'slug': post.slug}))
        assert response.status_code == 200
        assert response.context['post'] == post
        assert 'form' in response.context
        assert response.context['comments_enabled'] is True

    # authenticated user can post a comment
    def test_comment_submission(self, client, user, post: Post):
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': 'Great post!'})
        assert response.status_code == 302
        assert Comment.objects.filter(post=post, author=user, text='Great post!').exists()
        messages = list(get_messages(response.wsgi_request))
        assert any('pending' in str(m) for m in messages)

    # unauthenticated user gets 403 on comment POST
    def test_comment_submission_unauthenticated(self, client, post: Post):
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': 'spam'})
        assert response.status_code == 403

    # comment POST returns 403 when post has comments disabled
    def test_comment_submission_disabled(self, client, user, post: Post):
        post.allow_comments = False
        post.save()
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': 'test'})
        assert response.status_code == 403

    # invalid comment form re-renders with error message
    def test_comment_invalid_form(self, client, user, post: Post):
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': ''})
        assert response.status_code == 200
        messages = list(get_messages(response.wsgi_request))
        assert any('problem' in str(m) for m in messages)

    # comments_enabled is False when BLOG_COMMENTS setting is disabled
    def test_comments_disabled_globally(self, client, post: Post):
        with patch('apps.blog.views.COMMENTS_ENABLED', False):
            url = reverse('blog:detail', kwargs={'slug': post.slug})
            response = client.get(url)
            assert response.context['comments_enabled'] is False

    # POST returns 403 when BLOG_COMMENTS setting is disabled
    def test_comment_post_disabled_globally(self, client, user, post: Post):
        client.force_login(user)
        with patch('apps.blog.views.COMMENTS_ENABLED', False):
            url = reverse('blog:detail', kwargs={'slug': post.slug})
            response = client.post(url, {'text': 'test'})
            assert response.status_code == 403


class TestCommentDeleteView:
    # comment author can delete their own comment
    def test_owner_can_delete(self, client, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='my comment')
        client.force_login(user)
        url = reverse('blog:comment_delete', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert not Comment.objects.filter(pk=comment.pk).exists()

    # editor can delete any comment
    def test_editor_can_delete(self, client, user, editor, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='to delete')
        client.force_login(editor)
        url = reverse('blog:comment_delete', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert not Comment.objects.filter(pk=comment.pk).exists()

    # moderator can delete any comment
    def test_moderator_can_delete(self, client, user, moderator, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='moderated')
        client.force_login(moderator)
        url = reverse('blog:comment_delete', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert not Comment.objects.filter(pk=comment.pk).exists()

    # non-owner non-editor non-moderator gets 403
    def test_other_user_forbidden(self, client, user, third_user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='protected')
        client.force_login(third_user)
        url = reverse('blog:comment_delete', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 403

    # successful delete redirects back to the post
    def test_redirects_to_post(self, client, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='bye')
        client.force_login(user)
        url = reverse('blog:comment_delete', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response['Location'] == reverse('blog:detail', kwargs={'slug': post.slug})

    # delete with ?next= redirects to specified URL
    def test_redirects_with_next(self, client, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='bye')
        client.force_login(user)
        manage_url = reverse('blog:comment_manage_list')
        url = reverse('blog:comment_delete', kwargs={'pk': comment.pk}) + f'?next={manage_url}'
        response = client.post(url, {'next': manage_url})
        assert response['Location'] == manage_url


class TestCommentManageListView:
    url = reverse('blog:comment_manage_list')

    # anonymous user gets redirected
    def test_requires_login(self, client):
        response = client.get(self.url)
        assert response.status_code == 403

    # regular user gets 403
    def test_regular_user_forbidden(self, client, user):
        client.force_login(user)
        response = client.get(self.url)
        assert response.status_code == 403

    # moderator can access
    def test_moderator_can_access(self, client, moderator, post: Post):
        Comment.objects.create(post=post, author=moderator, text='pending')
        client.force_login(moderator)
        response = client.get(self.url)
        assert response.status_code == 200

    # editor can access
    def test_editor_can_access(self, client, editor):
        client.force_login(editor)
        response = client.get(self.url)
        assert response.status_code == 200

    # staff can access
    def test_staff_can_access(self, client, staff_user):
        client.force_login(staff_user)
        response = client.get(self.url)
        assert response.status_code == 200

    # default tab shows only unapproved comments
    def test_pending_filter(self, client, moderator, user, post: Post):
        pending = Comment.objects.create(post=post, author=user, text='pending')
        Comment.objects.create(post=post, author=user, text='approved', approved=True)
        client.force_login(moderator)
        response = client.get(self.url)
        assert list(response.context['comments']) == [pending]

    # all tab shows all comments
    def test_all_filter(self, client, moderator, user, post: Post):
        Comment.objects.create(post=post, author=user, text='pending')
        Comment.objects.create(post=post, author=user, text='approved', approved=True)
        client.force_login(moderator)
        response = client.get(self.url, {'filter': 'all'})
        assert len(response.context['comments']) == 2

    # context includes correct counts
    def test_tab_counts(self, client, moderator, user, post: Post):
        Comment.objects.create(post=post, author=user, text='pending')
        Comment.objects.create(post=post, author=user, text='approved', approved=True)
        client.force_login(moderator)
        response = client.get(self.url)
        assert response.context['pending_count'] == 1
        assert response.context['all_count'] == 2


class TestCommentApproveView:
    # moderator can approve an unapproved comment
    def test_approve_comment(self, client, moderator, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='pending')
        client.force_login(moderator)
        url = reverse('blog:comment_approve', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 302
        comment.refresh_from_db()
        assert comment.approved is True
        msgs = list(get_messages(response.wsgi_request))
        assert any('approved' in str(m) for m in msgs)

    # moderator can unapprove an approved comment
    def test_unapprove_comment(self, client, moderator, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='approved', approved=True)
        client.force_login(moderator)
        url = reverse('blog:comment_approve', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 302
        comment.refresh_from_db()
        assert comment.approved is False

    # regular user gets 403
    def test_regular_user_forbidden(self, client, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='test')
        client.force_login(user)
        url = reverse('blog:comment_approve', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 403

    # preserves filter=all tab on redirect
    def test_preserves_filter(self, client, moderator, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='test')
        client.force_login(moderator)
        url = reverse('blog:comment_approve', kwargs={'pk': comment.pk})
        response = client.post(url, {'filter': 'all'})
        assert '?filter=all' in response['Location']

    # GET is not allowed
    def test_get_not_allowed(self, client, moderator, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='test')
        client.force_login(moderator)
        url = reverse('blog:comment_approve', kwargs={'pk': comment.pk})
        response = client.get(url)
        assert response.status_code == 405


class TestPublicCommentVisibility:
    # only approved comments appear on the post detail page
    def test_only_approved_visible(self, client, user, post: Post):
        Comment.objects.create(post=post, author=user, text='pending')
        approved = Comment.objects.create(post=post, author=user, text='visible', approved=True)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.get(url)
        assert list(response.context['comment_list']) == [approved]

    # submitting a comment shows pending approval message
    def test_submission_pending_message(self, client, user, post: Post):
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': 'new comment'})
        assert response.status_code == 302
        msgs = list(get_messages(response.wsgi_request))
        assert any('pending' in str(m) for m in msgs)


class TestPostManageListView:
    url = reverse('blog:manage_list')

    # regular user gets 403
    def test_requires_editor_permission(self, client, user):
        client.force_login(user)
        response = client.get(self.url)
        assert response.status_code == 403

    # editor can view management list
    def test_editor_can_access(self, client, editor, post: Post):
        client.force_login(editor)
        response = client.get(self.url)
        assert response.status_code == 200
        assert post in response.context['posts']

    # staff user can access management views
    def test_staff_can_access(self, client, staff_user, post: Post):
        client.force_login(staff_user)
        response = client.get(self.url)
        assert response.status_code == 200


class TestPostCreateView:
    url = reverse('blog:post_create')

    # regular user gets 403
    def test_requires_editor_permission(self, client, user):
        client.force_login(user)
        response = client.get(self.url)
        assert response.status_code == 403

    # editor can create a post with tags, redirects to edit view
    def test_creates_post(self, client, editor):
        client.force_login(editor)
        data = {
            'title': 'New Post',
            'slug': 'new-post',
            'text': 'Post content here.',
            'publish_status': AVAILABLE,
            'allow_comments': True,
            'tags': 'news, update',
            'image_ppoi': '0.5x0.5',
        }
        response = client.post(self.url, data)
        post = Post.objects.get(slug='new-post')
        assert response.status_code == 302
        assert response['Location'] == reverse('blog:post_edit', kwargs={'pk': post.pk})
        assert set(post.tags.names()) == {'news', 'update'}
        messages = list(get_messages(response.wsgi_request))
        assert any('created' in str(m) for m in messages)


class TestPostUpdateView:
    # regular user gets 403
    def test_requires_editor_permission(self, client, user, post: Post):
        client.force_login(user)
        url = reverse('blog:post_edit', kwargs={'pk': post.pk})
        response = client.get(url)
        assert response.status_code == 403

    # post author can edit their own post
    def test_author_can_edit_own_post(self, client, user, post: Post):
        post.author.user = user
        post.author.save()
        client.force_login(user)
        url = reverse('blog:post_edit', kwargs={'pk': post.pk})
        response = client.get(url)
        assert response.status_code == 200

    # non-author regular user cannot edit another's post
    def test_non_author_cannot_edit(self, client, third_user, post: Post):
        client.force_login(third_user)
        url = reverse('blog:post_edit', kwargs={'pk': post.pk})
        response = client.get(url)
        assert response.status_code == 403

    # editor can update a post and its tags
    def test_updates_post(self, client, editor, post: Post):
        client.force_login(editor)
        url = reverse('blog:post_edit', kwargs={'pk': post.pk})
        data = {
            'title': 'Updated Title',
            'slug': post.slug,
            'text': post.text,
            'publish_status': post.publish_status,
            'allow_comments': True,
            'tags': 'edited',
            'image_ppoi': '0.5x0.5',
        }
        response = client.post(url, data)
        assert response.status_code == 302
        post.refresh_from_db()
        assert post.title == 'Updated Title'
        assert list(post.tags.names()) == ['edited']
        messages = list(get_messages(response.wsgi_request))
        assert any('saved' in str(m) for m in messages)


class TestPostDeleteView:
    # regular user gets 403
    def test_requires_editor_permission(self, client, user, post: Post):
        client.force_login(user)
        url = reverse('blog:post_delete', kwargs={'pk': post.pk})
        response = client.post(url)
        assert response.status_code == 403

    # post author cannot delete their own post (requires editor)
    def test_author_cannot_delete_own_post(self, client, user, post: Post):
        post.author.user = user
        post.author.save()
        client.force_login(user)
        url = reverse('blog:post_delete', kwargs={'pk': post.pk})
        response = client.post(url)
        assert response.status_code == 403

    # editor can delete a post with success message
    def test_deletes_post(self, client, editor, post: Post):
        client.force_login(editor)
        url = reverse('blog:post_delete', kwargs={'pk': post.pk})
        title = post.title
        response = client.post(url)
        assert response.status_code == 302
        assert response['Location'] == reverse('blog:manage_list')
        assert not Post.objects.filter(pk=post.pk).exists()
        messages = list(get_messages(response.wsgi_request))
        assert any(title in str(m) for m in messages)
