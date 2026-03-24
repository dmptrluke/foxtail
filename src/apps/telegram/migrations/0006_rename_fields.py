from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('telegram', '0005_backfill_telegram_links'),
    ]

    operations = [
        migrations.RenameField('TelegramLink', 'telegram_username', 'username'),
        migrations.RenameField('TelegramLink', 'first_name', 'name'),
        migrations.RenameField('LinkToken', 'telegram_username', 'username'),
        migrations.RenameField('LinkToken', 'first_name', 'name'),
    ]
