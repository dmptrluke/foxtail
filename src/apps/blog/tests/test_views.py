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
        response = client.get(reverse('blog:tag', kwargs={'slug': tag.slug}))
        assert response.status_code == 200
        assert post in response.context['posts']

    # invalid tag slug returns 404
    def test_tag_filter_invalid(self, client, post: Post):
        response = client.get(reverse('blog:tag', kwargs={'slug': 'nonexistent-tag-slug'}))
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


class TestCommentDeleteView:
    # comment author can delete their own comment
    def test_owner_can_delete(self, client, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='my comment')
        client.force_login(user)
        url = reverse('blog:comment_delete', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 200
        assert not Comment.objects.filter(pk=comment.pk).exists()

    # moderator can delete any comment
    def test_moderator_can_delete(self, client, user, moderator, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='moderated')
        client.force_login(moderator)
        url = reverse('blog:comment_delete', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 200
        assert not Comment.objects.filter(pk=comment.pk).exists()

    # non-owner non-moderator gets 403
    def test_other_user_forbidden(self, client, user, third_user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='protected')
        client.force_login(third_user)
        url = reverse('blog:comment_delete', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 403

    # GET returns 405
    def test_get_not_allowed(self, client, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='test')
        client.force_login(user)
        url = reverse('blog:comment_delete', kwargs={'pk': comment.pk})
        response = client.get(url)
        assert response.status_code == 405

    # response includes updated counts for OOB swap
    def test_response_includes_counts(self, client, user, moderator, post: Post):
        Comment.objects.create(post=post, author=user, text='keep', approved=False)
        comment = Comment.objects.create(post=post, author=user, text='delete')
        client.force_login(moderator)
        url = reverse('blog:comment_delete', kwargs={'pk': comment.pk})
        response = client.post(url)
        content = response.content.decode()
        assert 'pending-count' in content
        assert '(1)' in content


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
        assert response.status_code == 200
        comment.refresh_from_db()
        assert comment.approved is True
        content = response.content.decode()
        assert 'Approved' in content

    # moderator can unapprove an approved comment
    def test_unapprove_comment(self, client, moderator, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='approved', approved=True)
        client.force_login(moderator)
        url = reverse('blog:comment_approve', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 200
        comment.refresh_from_db()
        assert comment.approved is False
        content = response.content.decode()
        assert 'Pending' in content

    # regular user gets 403
    def test_regular_user_forbidden(self, client, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='test')
        client.force_login(user)
        url = reverse('blog:comment_approve', kwargs={'pk': comment.pk})
        response = client.post(url)
        assert response.status_code == 403

    # GET is not allowed
    def test_get_not_allowed(self, client, moderator, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='test')
        client.force_login(moderator)
        url = reverse('blog:comment_approve', kwargs={'pk': comment.pk})
        response = client.get(url)
        assert response.status_code == 405

    # response includes updated tab counts via OOB swap targets
    def test_response_includes_counts(self, client, moderator, user, post: Post):
        Comment.objects.create(post=post, author=user, text='other pending')
        comment = Comment.objects.create(post=post, author=user, text='to approve')
        client.force_login(moderator)
        url = reverse('blog:comment_approve', kwargs={'pk': comment.pk})
        response = client.post(url)
        content = response.content.decode()
        assert 'pending-count' in content
        assert 'all-count' in content
        assert '(1)' in content
        assert '(2)' in content


class TestCommentVisibility:
    # anonymous users see approved comments only
    def test_anonymous_sees_approved_only(self, client, user, post: Post):
        Comment.objects.create(post=post, author=user, text='pending')
        approved = Comment.objects.create(post=post, author=user, text='visible', approved=True)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.get(url)
        assert list(response.context['comment_list']) == [approved]

    # author sees approved comments plus their own pending ones
    def test_author_sees_own_pending(self, client, user, third_user, post: Post):
        own_pending = Comment.objects.create(post=post, author=user, text='my pending')
        approved = Comment.objects.create(post=post, author=third_user, text='visible', approved=True)
        Comment.objects.create(post=post, author=third_user, text='other pending')
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.get(url)
        assert list(response.context['comment_list']) == [own_pending, approved]

    # moderator sees all comments including other users' pending
    def test_moderator_sees_all(self, client, user, moderator, post: Post):
        pending = Comment.objects.create(post=post, author=user, text='pending')
        approved = Comment.objects.create(post=post, author=user, text='approved', approved=True)
        client.force_login(moderator)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.get(url)
        assert list(response.context['comment_list']) == [pending, approved]

    # submitting a comment shows pending approval message (non-HTMX)
    def test_submission_pending_message(self, client, user, post: Post):
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': 'new comment'})
        assert response.status_code == 302
        msgs = list(get_messages(response.wsgi_request))
        assert any('pending' in str(m) for m in msgs)


class TestCommentAutoApprove:
    # moderator's comment is auto-approved
    def test_moderator_auto_approved(self, client, moderator, post: Post):
        client.force_login(moderator)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        client.post(url, {'text': 'mod comment'})
        comment = Comment.objects.get(text='mod comment')
        assert comment.approved is True

    # verified user's comment is auto-approved
    def test_verified_user_auto_approved(self, client, user, second_user, post: Post):
        from apps.accounts.models import Verification

        Verification.objects.create(user=user, verified_by=second_user)
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        client.post(url, {'text': 'verified comment'})
        comment = Comment.objects.get(text='verified comment')
        assert comment.approved is True

    # auto-approved non-HTMX comment shows "posted" not "pending"
    def test_auto_approved_message(self, client, moderator, post: Post):
        client.force_login(moderator)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': 'mod comment msg'})
        assert response.status_code == 302
        msgs = list(get_messages(response.wsgi_request))
        assert any('posted' in str(m) for m in msgs)
        assert not any('pending' in str(m) for m in msgs)

    # regular unverified user's comment is not auto-approved
    def test_regular_user_not_auto_approved(self, client, user, post: Post):
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        client.post(url, {'text': 'regular comment'})
        comment = Comment.objects.get(text='regular comment')
        assert comment.approved is False


class TestCommentHtmxPosting:
    htmx_headers = {'HTTP_HX_REQUEST': 'true'}

    # HTMX post returns comment partial, not redirect
    def test_htmx_returns_partial(self, client, user, post: Post):
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': 'htmx comment'}, **self.htmx_headers)
        assert response.status_code == 200
        content = response.content.decode()
        assert 'htmx comment' in content
        assert 'comment-item' in content

    # HTMX response includes OOB form reset
    def test_htmx_includes_oob_form_reset(self, client, user, post: Post):
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': 'oob test'}, **self.htmx_headers)
        content = response.content.decode()
        assert 'hx-swap-oob' in content
        assert 'comment-form-wrapper' in content

    # HTMX invalid form returns errors with HX-Retarget
    def test_htmx_invalid_retargets(self, client, user, post: Post):
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': ''}, **self.htmx_headers)
        assert response.status_code == 200
        assert response['HX-Retarget'] == '#comment-form-wrapper'
        assert response['HX-Reswap'] == 'outerHTML'

    # moderator comment via HTMX has no pending styling
    def test_htmx_moderator_no_pending_class(self, client, moderator, post: Post):
        client.force_login(moderator)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': 'mod htmx'}, **self.htmx_headers)
        content = response.content.decode()
        assert 'comment-pending' not in content
        assert 'Pending' not in content

    # non-HTMX post still redirects
    def test_non_htmx_still_redirects(self, client, user, post: Post):
        client.force_login(user)
        url = reverse('blog:detail', kwargs={'slug': post.slug})
        response = client.post(url, {'text': 'plain post'})
        assert response.status_code == 302


class TestCommentInlineApprove:
    # approve from detail context returns _comment_item.html
    def test_approve_from_detail_returns_item(self, client, moderator, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='to approve')
        client.force_login(moderator)
        url = reverse('blog:comment_approve', kwargs={'pk': comment.pk})
        response = client.post(url, {'context': 'detail'})
        assert response.status_code == 200
        comment.refresh_from_db()
        assert comment.approved is True
        content = response.content.decode()
        assert 'comment-item' in content
        assert 'pending-count' not in content


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
