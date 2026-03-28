from django.contrib import admin

from unfold.admin import ModelAdmin as UnfoldModelAdmin

from .models import Page


class PageAdmin(UnfoldModelAdmin):
    warn_unsaved_form = True
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'body')}),
        ('Advanced options', {'fields': ('slug',)}),
    )

    list_display = ('title', 'slug', 'modified')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Page, PageAdmin)
