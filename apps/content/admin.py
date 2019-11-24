from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import TextField
from django.forms import Textarea

from .models import Page


class PageAdmin(SortableAdminMixin, ModelAdmin):  # lgtm [py/conflicting-attributes]
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'body')}),
        ('Advanced options', {'fields': ('slug', 'show_in_menu'),}),
    )

    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 40, 'cols': 120})},
    }

    list_display = ('title', 'slug', 'modified', 'show_in_menu')
    list_editable = ['show_in_menu']
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Page, PageAdmin)
