from django.conf import settings
from django.contrib import messages
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Count
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.dates import YearMixin

from csp_helpers.mixins import CSPViewMixin
from published.mixins import PublishedDetailMixin, PublishedListMixin
from published.utils import queryset_filter
from taggit.models import Tag

from apps.core.mixins import PermissionMixin

from .models import Comment, Post

COMMENTS_ENABLED = getattr(settings, 'BLOG_COMMENTS', False)

if COMMENTS_ENABLED:
    from .forms import CommentForm


def _blog_years():
    return queryset_filter(Post.objects).dates('created', 'year', order='DESC').values_list('created__year', flat=True)


def _sidebar_context():
    return {
        'sidebar_post_list': queryset_filter(Post.objects).all()[:3],
        'sidebar_tag_list': Post.tags.annotate(num_times=Count('taggit_taggeditem_items')).order_by('-num_times')[:8],
    }


class BlogListView(PublishedListMixin, ListView):
    model = Post
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'blog/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_sidebar_context())
        context['blog_years'] = _blog_years()

        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            try:
                context['tag'] = Tag.objects.get(slug=tag_slug)
            except Tag.DoesNotExist:
                raise Http404() from None

        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        q = self.request.GET.get('q')
        tag = self.request.GET.get('tag')

        if q:
            vector = SearchVector('title', weight='A', config='english') + SearchVector(
                'text', weight='B', config='english'
            )

            query = SearchQuery(q, config='english')
            rank = SearchRank(vector, query, weights=[0.2, 0.4, 0.6, 0.8])

            queryset = queryset.annotate(rank=rank).filter(rank__gte=0.01).prefetch_related('tags').order_by('-rank')

        elif tag:
            queryset = queryset.prefetch_related('tags').filter(tags__slug__in=[tag])
        else:
            queryset = queryset.prefetch_related('tags').all()

        return queryset


class BlogListYearView(PublishedListMixin, YearMixin, ListView):
    model = Post
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'blog/list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        year = int(self.get_year())
        return queryset.filter(created__year=year).prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_sidebar_context())
        context['blog_years'] = _blog_years()
        context['year'] = str(self.get_year())
        return context


class BlogDetailView(PublishedDetailMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    queryset = Post.objects.select_related('author').prefetch_related('tags').all()

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_sidebar_context())

        if COMMENTS_ENABLED:
            context['comment_list'] = self.object.comments.select_related('author').filter(approved=True)
            context['comments_enabled'] = True
            if form:
                context['form'] = form
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

        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            messages.success(self.request, 'Your comment has been submitted and is pending approval.')
            return redirect('blog:detail', slug=self.object.slug)
        else:
            messages.error(self.request, 'There was a problem posting your comment.')
            context = self.get_context_data(form=form, object=self.object)

        return self.render_to_response(context)


class CommentDeleteView(PermissionMixin, DeleteView):
    permission_required = 'blog.delete_comment'
    model = Comment
    template_name = 'blog/comment_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '')
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Your comment has been deleted.')
        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.POST.get('next', '')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
            return next_url
        return reverse('blog:detail', kwargs={'slug': self.object.post.slug})


# --- Management views ---


class PostManageListView(PermissionMixin, ListView):
    permission_required = 'blog.manage_posts'
    model = Post
    template_name = 'blog/post_manage_list.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        return Post.objects.select_related('author').prefetch_related('tags').order_by('-created')


class PostCreateView(CSPViewMixin, PermissionMixin, CreateView):
    permission_required = 'blog.manage_posts'
    model = Post
    template_name = 'blog/post_form.html'

    def get_form_class(self):
        from .forms import PostForm

        return PostForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        self.object.tags.set(form.cleaned_data.get('tags', []))
        messages.success(self.request, f'Post "{self.object.title}" created.')
        return HttpResponseRedirect(reverse('blog:post_edit', kwargs={'pk': self.object.pk}))


class PostUpdateView(CSPViewMixin, PermissionMixin, UpdateView):
    permission_required = 'blog.change_post'
    model = Post
    template_name = 'blog/post_form.html'

    def get_form_class(self):
        from .forms import PostForm

        return PostForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        self.object.tags.set(form.cleaned_data.get('tags', []))
        messages.success(self.request, f'Post "{self.object.title}" saved.')
        return HttpResponseRedirect(reverse('blog:post_edit', kwargs={'pk': self.object.pk}))


class PostDeleteView(PermissionMixin, DeleteView):
    permission_required = 'blog.delete_post'
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:manage_list')

    def form_valid(self, form):
        title = self.object.title
        result = super().form_valid(form)
        messages.success(self.request, f'Post "{title}" deleted.')
        return result


class CommentManageListView(PermissionMixin, ListView):
    permission_required = 'blog.manage_comments'
    model = Comment
    template_name = 'blog/comment_manage_list.html'
    context_object_name = 'comments'
    paginate_by = 20

    def get_queryset(self):
        qs = Comment.objects.select_related('author', 'post').order_by('-created')
        if self.request.GET.get('filter') == 'all':
            return qs
        return qs.filter(approved=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = self.request.GET.get('filter', 'pending')
        all_comments = Comment.objects.all()
        context['pending_count'] = all_comments.filter(approved=False).count()
        context['all_count'] = all_comments.count()
        return context


class CommentApproveView(PermissionMixin, View):
    permission_required = 'blog.manage_comments'

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.approved = not comment.approved
        comment.save(update_fields=['approved'])
        action = 'approved' if comment.approved else 'unapproved'
        messages.success(request, f'Comment {action}.')
        filter_param = request.POST.get('filter', 'pending')
        url = reverse('blog:comment_manage_list')
        if filter_param == 'all':
            url += '?filter=all'
        return redirect(url)


__all__ = [
    'BlogDetailView',
    'BlogListView',
    'BlogListYearView',
    'CommentApproveView',
    'CommentDeleteView',
    'CommentManageListView',
    'PostCreateView',
    'PostDeleteView',
    'PostManageListView',
    'PostUpdateView',
]
