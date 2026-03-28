from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline

from .models import EventSeries, Organisation, SocialLink


class SocialLinkInline(TabularInline):
    model = SocialLink
    extra = 1
    show_count = True
    fields = ['platform', 'url', 'is_primary', 'click_count']
    readonly_fields = ['click_count']


class OrganisationAdmin(UnfoldModelAdmin):
    warn_unsaved_form = True
    compressed_fields = True
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
    list_display = ['name', 'group_type', 'region', 'featured', 'age_requirement']
    list_filter = ['featured', 'group_type', 'region', 'age_requirement']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class EventSeriesAdmin(UnfoldModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'organisation')}),
        ('Logo', {'fields': ('logo', 'logo_ppoi')}),
    )
    list_display = ['name', 'organisation_link', 'created']

    @admin.display(description='Organisation')
    def organisation_link(self, obj):
        if not obj.organisation:
            return '-'
        url = reverse('admin:organisations_organisation_change', args=[obj.organisation_id])
        return format_html('<a href="{}">{}</a>', url, obj.organisation)

    search_fields = ['name']
    autocomplete_fields = ['organisation']
    list_filter = ['organisation']
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(EventSeries, EventSeriesAdmin)
