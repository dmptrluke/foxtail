from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Page


class PageAdmin(ModelAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'body')}),
        ('Advanced options', {'fields': ('slug', )}),
    )

    list_display = ('title', 'slug', 'modified')
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Page, PageAdmin)
