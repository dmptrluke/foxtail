from django.contrib import messages
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.cache import cache
from django.db.models import Count, Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.dates import YearMixin

from published.mixins import PublishedDetailMixin, PublishedListMixin
from published.utils import queryset_filter
from structured_data.views import StructuredDataMixin
from taggit.models import Tag

from apps.core.mixins import HtmxMixin, PermissionMixin
from apps.core.models import SiteSettings

from ..forms import CommentForm
from ..models import Comment, Post


def _blog_years():
    result = cache.get('blog_years')
    if result is None:
        result = list(
            queryset_filter(Post.objects).dates('created', 'year', order='DESC').values_list('created__year', flat=True)
        )
        cache.set('blog_years', result, 3600)
    return result


class BlogListView(StructuredDataMixin, PublishedListMixin, ListView):
    model = Post
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'blog/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog_years'] = _blog_years()
        return context

    def get_structured_data(self):
        q = self.request.GET.get('q')
        org_name = SiteSettings.get_solo().org_name

        if q:
            name = f'Search results for "{q}"'
            description = f'Search results for {q} on {org_name}'
        else:
            name = 'Community News'
            description = 'Community news and updates for New Zealand furries'

        return {
            '@type': 'CollectionPage',
            'name': name,
            'description': description,
            'url': self.request.build_absolute_uri(),
        }

    def get_queryset(self):
        queryset = super().get_queryset()

        q = self.request.GET.get('q')
        if q:
            vector = SearchVector('title', weight='A', config='english') + SearchVector(
                'text', weight='B', config='english'
            )

            query = SearchQuery(q, config='english')
            rank = SearchRank(vector, query, weights=[0.2, 0.4, 0.6, 0.8])

            queryset = queryset.annotate(rank=rank).filter(rank__gte=0.01).prefetch_related('tags').order_by('-rank')
        else:
            queryset = queryset.prefetch_related('tags').all()

        return queryset


class BlogTagView(StructuredDataMixin, PublishedListMixin, ListView):
    model = Post
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'blog/list.html'

    def get_tag(self):
        if not hasattr(self, '_tag'):
            try:
                self._tag = Tag.objects.get(slug=self.kwargs['slug'])
            except Tag.DoesNotExist:
                raise Http404 from None
        return self._tag

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog_years'] = _blog_years()
        context['tag'] = self.get_tag()
        return context

    def get_structured_data(self):
        tag = self.get_tag()
        org_name = SiteSettings.get_solo().org_name
        return {
            '@type': 'CollectionPage',
            'name': f'News tagged "{tag.name}"',
            'description': f'News posts tagged {tag.name} on {org_name}',
            'url': self.request.build_absolute_uri(),
        }

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('tags').filter(tags__slug__in=[self.kwargs['slug']])


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
        context['blog_years'] = _blog_years()
        context['year'] = str(self.get_year())
        return context

    def get_structured_data(self):
        year = self.get_year()
        return {
            '@type': 'CollectionPage',
            'name': f'Community News from {year}',
            'description': f'Community news and updates from {year}',
            'url': self.request.build_absolute_uri(),
        }


class BlogDetailView(HtmxMixin, PublishedDetailMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    queryset = Post.objects.select_related('author').prefetch_related('tags').with_related_content().all()

    def _comment_queryset(self):
        # Authors see their own pending comments so they know submission worked
        qs = self.object.comments.with_author_display().order_by('created')
        user = self.request.user
        if user.has_perm('blog.manage_comments'):
            return qs
        if user.is_authenticated:
            return qs.filter(Q(approved=True) | Q(author=user))
        return qs.filter(approved=True)

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.object
        context['related_organisations'] = post.organisations.all()
        context['related_series'] = post.event_series.all()
        context['related_events'] = post.events.all()

        context['comment_list'] = self._comment_queryset()
        context['form'] = form or CommentForm()

        return context

    def _should_auto_approve(self, user):
        # is_verified = identity confirmed in person, not just email verification
        return user.has_perm('blog.manage_comments') or user.is_verified

    def post(self, request, *args, **kwargs):
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
            if self._should_auto_approve(request.user):
                comment.approved = True
            comment.save()

            if self.is_htmx():
                return self.htmx_response(
                    {'comment': comment, 'post': self.object, 'form': CommentForm()},
                    template='blog/_comment_post_response.html',
                )

            if comment.approved:
                messages.success(request, 'Your comment has been posted.')
            else:
                messages.success(request, 'Your comment has been submitted and is pending approval.')
            return redirect('blog:detail', slug=self.object.slug)

        if self.is_htmx():
            response = self.htmx_response(
                {'form': form, 'post': self.object},
                template='blog/_comment_form.html',
            )
            response['HX-Retarget'] = '#comment-form-wrapper'
            response['HX-Reswap'] = 'outerHTML'
            return response

        messages.error(request, 'There was a problem posting your comment.')
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
