from django.conf import settings
from django.contrib import messages
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Count, Q
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.dates import YearMixin

from csp_helpers.mixins import CSPViewMixin
from published.mixins import PublishedDetailMixin, PublishedListMixin
from published.utils import queryset_filter
from structured_data.views import StructuredDataMixin
from taggit.models import Tag

from apps.core.mixins import HtmxMixin, PermissionMixin

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


class BlogListView(StructuredDataMixin, PublishedListMixin, ListView):
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

    def get_structured_data(self):
        q = self.request.GET.get('q')
        tag = self.request.GET.get('tag')
        if q:
            description = f'Search results for {q} on furry.nz'
        elif tag:
            description = f'News posts tagged {tag} on furry.nz'
        else:
            description = 'Community news and updates for New Zealand furries'
        return {
            '@type': 'CollectionPage',
            'name': 'News',
            'description': description,
            'url': self.request.build_absolute_uri(),
        }

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


class BlogListYearView(StructuredDataMixin, PublishedListMixin, YearMixin, ListView):
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

    def get_structured_data(self):
        year = self.get_year()
        return {
            '@type': 'CollectionPage',
            'name': f'News from {year}',
            'description': f'Furry community news from {year}',
            'url': self.request.build_absolute_uri(),
        }


class BlogDetailView(PublishedDetailMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    queryset = (
        Post.objects.select_related('author').prefetch_related('tags', 'organisations', 'event_series', 'events').all()
    )

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_sidebar_context())

        post = self.object
        context['related_organisations'] = post.organisations.all()
        context['related_series'] = post.event_series.all()
        context['related_events'] = post.events.all()

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


class CommentDeleteView(HtmxMixin, PermissionMixin, View):
    permission_required = 'blog.delete_comment'
    htmx_template = 'blog/manage/_comment_counts.html'

    def get_permission_object(self):
        if not hasattr(self, '_comment'):
            self._comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        return self._comment

    def post(self, request, pk):
        comment = self._comment
        comment.delete()
        counts = Comment.objects.aggregate(
            pending_count=Count('pk', filter=Q(approved=False)),
            all_count=Count('pk'),
        )
        return self.htmx_response(counts)


# --- Management views ---


class PostManageListView(PermissionMixin, ListView):
    permission_required = 'blog.manage_posts'
    model = Post
    template_name = 'blog/manage/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        return Post.objects.select_related('author').prefetch_related('tags').order_by('-created')


class PostCreateView(CSPViewMixin, PermissionMixin, CreateView):
    permission_required = 'blog.manage_posts'
    model = Post
    template_name = 'blog/manage/post_edit.html'

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
    template_name = 'blog/manage/post_edit.html'

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
    template_name = 'blog/manage/post_delete.html'
    success_url = reverse_lazy('blog:manage_list')

    def form_valid(self, form):
        title = self.object.title
        result = super().form_valid(form)
        messages.success(self.request, f'Post "{title}" deleted.')
        return result


class CommentManageListView(PermissionMixin, ListView):
    permission_required = 'blog.manage_comments'
    model = Comment
    template_name = 'blog/manage/comment_list.html'
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
        counts = Comment.objects.aggregate(
            pending_count=Count('pk', filter=Q(approved=False)),
            all_count=Count('pk'),
        )
        context['pending_count'] = counts['pending_count']
        context['all_count'] = counts['all_count']
        return context


class CommentApproveView(HtmxMixin, PermissionMixin, View):
    permission_required = 'blog.manage_comments'
    htmx_template = 'blog/manage/_comment_row.html'

    def post(self, request, pk):
        comment = get_object_or_404(Comment.objects.select_related('author', 'post'), pk=pk)
        comment.approved = not comment.approved
        comment.save(update_fields=['approved'])
        counts = Comment.objects.aggregate(
            pending_count=Count('pk', filter=Q(approved=False)),
            all_count=Count('pk'),
        )
        return self.htmx_response(
            {
                'comment': comment,
                'current_filter': request.POST.get('filter', 'pending'),
                **counts,
            }
        )


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
