from django.contrib import admin
from django.contrib.auth.decorators import login_required

# ensure users go through the allauth workflow when logging into admin.
admin.site.login = login_required(admin.site.login)

# customise admin text
admin.site.site_header = 'Foxtail Admin'
admin.site.site_title = 'Foxtail Admin'

# run the standard admin set-up.
admin.autodiscover()
