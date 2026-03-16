from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import EventSeries, Organisation, SocialLink


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1
    fields = ['platform', 'url', 'is_primary']


class OrganisationAdmin(ModelAdmin):
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'slug',
                    'description',
                    'url',
                    'featured',
                    'group_type',
                    'country',
                    'region',
                    'age_requirement',
                )
            },
        ),
        ('Logo', {'fields': ('logo', 'logo_ppoi')}),
    )
    inlines = [SocialLinkInline]
    list_display = ['name', 'slug', 'group_type', 'region', 'age_requirement', 'featured']
    list_filter = ['featured', 'group_type', 'region', 'age_requirement']
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
