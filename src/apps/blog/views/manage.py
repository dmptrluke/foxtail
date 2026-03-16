from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from csp_helpers.mixins import CSPViewMixin

from apps.core.mixins import HtmxMixin, PermissionMixin

from ..models import Comment, Post


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
        from ..forms import PostForm

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
        from ..forms import PostForm

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
        comment.approved = not comment.approved  # toggles: approve and unapprove
        comment.save(update_fields=['approved'])

        if request.POST.get('context') == 'detail':
            return self.htmx_response(
                {'comment': comment},
                template='blog/_comment_item.html',
            )

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
