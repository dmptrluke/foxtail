from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.forms import ModelForm, Textarea
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.html import format_html

from published.admin import PublishedAdmin, add_to_fieldsets, add_to_list_display, add_to_readonly_fields

from .models import Author, Comment, Post


class PostAdminForm(ModelForm):
    class Meta:
        widgets = {
            'description': Textarea(attrs={'cols': 60, 'rows': 4}),
        }


class PostAdmin(PublishedAdmin):
    form = PostAdminForm
    fieldsets = (
        ('Metadata', {'fields': ('title', 'author', 'tags', 'description')}),
        ('Content', {'fields': ('text',)}),
        add_to_fieldsets(section=True, collapse=False),
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

    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']
    raw_id_fields = ('author',)
    readonly_fields = add_to_readonly_fields()
    list_filter = ('created', 'tags', 'author')
    list_display = ['title', 'tag_list', 'created', 'modified', 'author'] + add_to_list_display()

    @staticmethod
    def tag_list(obj):
        return ', '.join(o.name for o in obj.tags.all().order_by('name'))


class CommentAdmin(ModelAdmin):
    list_display = ('text_preview', 'post_link', 'author', 'created')
    raw_id_fields = ('author',)

    def post_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>', reverse('admin:foxtail_blog_post_change', args=(obj.post.pk,)), obj.post.title
        )

    def text_preview(self, obj):
        return truncatechars(obj.text, 50)

    text_preview.short_description = 'Comment'
    post_link.short_description = 'Post'


class AuthorAdmin(ModelAdmin):
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
