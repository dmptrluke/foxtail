import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    replaces = [
        ('telegram', '0001_initial'),
        ('telegram', '0002_link_token'),
        ('telegram', '0003_drop_botaction'),
        ('telegram', '0004_linktoken_first_name'),
        ('telegram', '0005_backfill_telegram_links'),
        ('telegram', '0006_rename_fields'),
        ('telegram', '0007_fix_socialaccount_uids'),
    ]

    initial = True

    dependencies = [
        ('socialaccount', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(db_index=True, unique=True)),
                ('username', models.CharField(blank=True, max_length=32)),
                ('name', models.CharField(blank=True, max_length=64)),
                ('linked_at', models.DateTimeField(auto_now_add=True)),
                (
                    'is_blocked',
                    models.BooleanField(default=False, help_text='Bot received 403 when sending to this user'),
                ),
                (
                    'user',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='telegram_link',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'telegram link',
            },
        ),
        migrations.CreateModel(
            name='LinkToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField()),
                ('username', models.CharField(blank=True, max_length=32)),
                ('name', models.CharField(blank=True, max_length=64)),
                ('token', models.CharField(max_length=86, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'link token',
                'indexes': [models.Index(fields=['telegram_id'], name='telegram_li_telegra_ce78b5_idx')],
            },
        ),
    ]
