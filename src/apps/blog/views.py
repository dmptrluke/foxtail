from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.views.generic import DeleteView, DetailView, ListView

from published.mixins import PublishedDetailMixin, PublishedListMixin
from published.utils import queryset_filter
from rules.contrib.views import AutoPermissionRequiredMixin

from .models import Comment, Post, reverse

COMMENTS_ENABLED = getattr(settings, 'BLOG_COMMENTS', False)

if COMMENTS_ENABLED:
    from .forms import CommentForm


class BlogListView(PublishedListMixin, ListView):
    model = Post
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'blog/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_post_list'] = queryset_filter(Post.objects).all()[:3]
        context['sidebar_tag_list'] = Post.tags.annotate(
            num_times=Count('taggit_taggeditem_items')
        ).order_by('-num_times')[:8]
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        q = self.request.GET.get('q')
        tag = self.request.GET.get('tag')

        if q:
            vector = SearchVector('title', weight='A', config='english') + \
                SearchVector('text', weight='B', config='english')

            query = SearchQuery(q, config='english')
            rank = SearchRank(vector, query, weights=[0.2, 0.4, 0.6, 0.8])

            queryset = queryset.annotate(rank=rank) \
                .filter(rank__gte=0.01) \
                .prefetch_related('tags') \
                .order_by('-rank')

        elif tag:
            # user is doing a tag query
            queryset = queryset \
                .prefetch_related('tags') \
                .filter(tags__slug__in=[tag])
        else:
            queryset = queryset.prefetch_related('tags').all()

        return queryset


class BlogDetailView(PublishedDetailMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    queryset = Post.objects.prefetch_related('comments__author').prefetch_related('tags').all()

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_post_list'] = queryset_filter(Post.objects.all())[:3]
        context['sidebar_tag_list'] = Post.tags.most_common()[:8]

        if COMMENTS_ENABLED:
            context['comment_list'] = self.object.comments.all()
            context['comments_enabled'] = True
            if form:
                context['form'] = form
            else:
                if hasattr(self.request, 'csp_nonce'):
                    context['form'] = CommentForm(csp_nonce=self.request.csp_nonce)
                else:
                    context['form'] = CommentForm()
        else:
            context['comments_enabled'] = False

        return context

    def post(self, request, *args, **kwargs):
        if not COMMENTS_ENABLED:
            return HttpResponseForbidden()

        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        # noinspection PyAttributeOutsideInit
        self.object = self.get_object()

        if not self.object.allow_comments:
            return HttpResponseForbidden()

        if hasattr(self.request, 'csp_nonce'):
            form = CommentForm(request.POST, csp_nonce=self.request.csp_nonce)
        else:
            form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            messages.success(self.request, 'Your comment has been posted!')
            return redirect('blog:detail', slug=self.object.slug)
        else:
            messages.error(self.request, 'There was a problem posting your comment.')
            context = self.get_context_data(form=form, object=self.object)

        return self.render_to_response(context)


class CommentDeleteView(AutoPermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_delete.html'

    def form_valid(self, form):
        messages.success(self.request, 'Your comment has been deleted.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:detail', kwargs={'slug': self.object.post.slug})


__all__ = ['BlogListView', 'BlogDetailView', 'CommentDeleteView']
