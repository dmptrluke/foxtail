from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import EventSeries, Organisation


class OrganisationAdmin(ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'url')}),
        ('Logo', {'fields': ('logo', 'logo_ppoi')}),
    )
    list_display = ['name', 'slug', 'url']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class EventSeriesAdmin(ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'organisation')}),
        ('Logo', {'fields': ('logo', 'logo_ppoi')}),
    )
    list_display = ['name', 'slug', 'organisation']
    search_fields = ['name']
    autocomplete_fields = ['organisation']
    list_filter = ['organisation']
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(EventSeries, EventSeriesAdmin)
