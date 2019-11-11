from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.views import generic

from .models import Post


class BlogListView(generic.ListView):
    model = Post
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'blog_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_post_list'] = Post.objects.all()[:5]
        return context

    def get_queryset(self):
        q = self.request.GET.get('q')
        tag = self.request.GET.get('tag')

        if q:
            # user is doing a search query
            query = SearchQuery(q)
            vector = SearchVector('text', 'title')
            queryset = self.model.objects.annotate(rank=SearchRank(vector, query)) \
                .prefetch_related('tags') \
                .order_by('-rank')

        elif tag:
            # user is doing a tag query
            queryset = self.model.objects \
                .prefetch_related('tags') \
                .filter(tags__slug__in=[tag])
        else:
            queryset = self.model.objects.prefetch_related('tags').all()

        return queryset


class BlogDetailView(generic.DetailView):
    model = Post
    template_name = 'blog_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_post_list'] = Post.objects.all()[:5]
        context['sidebar_tag_list'] = Post.tags.most_common()[:8]
        return context
