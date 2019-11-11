from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import Post


class PostAdmin(MarkdownxModelAdmin):
    fieldsets = (
        ('Content', {
            'fields': ('title', 'tags', 'author', 'text')
        }),
        ('Image', {
            'fields': ('image',),
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('slug',),
        }),
    )

    prepopulated_fields = {"slug": ("title",)}
    list_filter = ('created', 'tags', 'author')
    list_display = ('title', 'tag_list', 'created', 'modified', 'author')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())


admin.site.register(Post, PostAdmin)

