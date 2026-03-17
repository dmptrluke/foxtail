from django.db import migrations


def seed_settings(apps, schema_editor):
    SiteSettings = apps.get_model('core', 'SiteSettings')
    SiteSettings.objects.get_or_create(
        pk=1,
        defaults={
            'org_name': 'furry.nz',
            'org_description': 'The resource for New Zealand furries.',
            'theme_color': '#281e33',
            'facebook_app_id': '538473223430196',
            'telegram_url': 'https://t.me/nzfurries',
            'bluesky_url': 'https://bsky.app/profile/furry.nz',
            'x_url': 'https://x.com/furrynz',
            'contact_email': 'website@furry.nz',
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_settings, migrations.RunPython.noop),
    ]
