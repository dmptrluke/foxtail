from django.contrib.admin.apps import AdminConfig


class CustomAdminConfig(AdminConfig):
    default_site = 'apps.admin.admin.CustomAdminSite'
