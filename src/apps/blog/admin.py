from django.contrib import admin
from django.forms import ModelForm
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.html import format_html

from published.admin import PublishedAdmin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter
from unfold.decorators import action, display

from apps.core.admin_helpers import publish_status_badge as _publish_status_badge
from apps.core.widgets import UnfoldTagWidget

from .models import Author, Comment, Post


class PostAdminForm(ModelForm):
    class Meta:
        widgets = {
            'tags': UnfoldTagWidget,
        }


class PostAdmin(UnfoldModelAdmin, PublishedAdmin):
    warn_unsaved_form = True
    form = PostAdminForm
    fieldsets = (
        ('Metadata', {'fields': ('title', 'author', 'tags', 'description')}),
        ('Content', {'fields': ('text',)}),
        ('Related Content', {'fields': ('organisations', 'event_series', 'events')}),
        ('Publishing', {'fields': ('publish_status', 'live_as_of', 'publish_status_badge')}),
        (
            'Image',
            {
                'fields': ('image', 'image_ppoi'),
            },
        ),
        (
            'Advanced options',
            {
                'classes': ('collapse',),
                'fields': ('slug', 'allow_comments'),
            },
        ),
    )

    autocomplete_fields = ['organisations', 'event_series', 'events']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']
    readonly_fields = ['publish_status_badge']
    list_filter = [
        'created',
        'tags',
        ('author', RelatedDropdownFilter),
        ('publish_status', ChoicesDropdownFilter),
    ]
    list_display = ['title', 'author', 'created', 'show_status', 'tag_list']
    actions_detail = ['view_comments']

    @action(description='Comments', icon='chat_bubble', attrs={'target': '_blank'})
    def view_comments(self, request, object_id):
        from django.http import HttpResponseRedirect

        url = reverse('admin:foxtail_blog_comment_changelist')
        return HttpResponseRedirect(f'{url}?post__id__exact={object_id}')

    @admin.display(description='Current status')
    def publish_status_badge(self, obj):
        return _publish_status_badge(obj)

    @display(
        description='Status',
        label={
            'Never Available': 'danger',
            'Available': 'success',
            'Available after "Publish Date"': 'info',
        },
    )
    def show_status(self, obj):
        return obj.get_publish_status_display()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    @staticmethod
    def tag_list(obj):
        return ', '.join(sorted(t.name for t in obj.tags.all()))


class CommentAdmin(UnfoldModelAdmin):
    list_display = ('text_preview', 'post_link', 'author', 'approved', 'created')
    raw_id_fields = ('author',)
    actions = ['approve_comments']

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        updated = queryset.filter(approved=False).update(approved=True)
        self.message_user(request, f'{updated} comment(s) approved.')

    def post_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>', reverse('admin:foxtail_blog_post_change', args=(obj.post.pk,)), obj.post.title
        )

    def text_preview(self, obj):
        return truncatechars(obj.text, 50)

    text_preview.short_description = 'Comment'
    post_link.short_description = 'Post'


class AuthorAdmin(UnfoldModelAdmin):
    list_display = ('name', 'user', 'link')
    search_fields = ('name',)
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {'fields': ('name', 'user', 'description', 'link')}),
        ('Avatar', {'fields': ('avatar', 'avatar_ppoi')}),
    )


admin.site.register(Author, AuthorAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
