import apps.core.fields
import django.db.models.deletion
import markdownfield.models
from django.db import migrations, models


class Migration(migrations.Migration):
    replaces = [
        ('organisations', '0001_initial'),
        ('organisations', '0002_sociallink'),
        ('organisations', '0003_organisation_country'),
        ('organisations', '0004_organisation_featured'),
        ('organisations', '0005_organisation_type_region'),
        ('organisations', '0006_organisation_country_choices'),
        ('organisations', '0007_organisation_region_choices_update'),
        ('organisations', '0008_age_requirement'),
        ('organisations', '0009_add_sociallink_click_count'),
    ]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', apps.core.fields.AutoSlugField(populate_from='name', unique=True)),
                ('description', markdownfield.models.MarkdownField(blank=True, rendered_field='description_rendered')),
                ('description_rendered', markdownfield.models.RenderedMarkdownField()),
                (
                    'logo',
                    models.ImageField(
                        blank=True, height_field='logo_height', upload_to='organisations', width_field='logo_width'
                    ),
                ),
                ('url', models.URLField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('logo_width', models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ('logo_height', models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ('logo_ppoi', models.CharField(default='0.5x0.5', max_length=20)),
                (
                    'country',
                    models.CharField(blank=True, choices=[('NZ', 'New Zealand'), ('AU', 'Australia')], max_length=2),
                ),
                ('featured', models.BooleanField(default=False)),
                (
                    'group_type',
                    models.CharField(
                        choices=[
                            ('organisation', 'Organisation'),
                            ('community', 'Community Group'),
                            ('interest', 'Interest Group'),
                        ],
                        default='organisation',
                        max_length=20,
                    ),
                ),
                (
                    'region',
                    models.CharField(
                        blank=True,
                        choices=[
                            ('northland', 'Northland'),
                            ('auckland', 'Auckland'),
                            ('waikato', 'Waikato'),
                            ('bay-of-plenty', 'Bay of Plenty'),
                            ('central-ni', 'Central North Island'),
                            ('wellington', 'Wellington'),
                            ('top-of-the-south', 'Nelson/Marlborough'),
                            ('canterbury', 'Canterbury'),
                            ('otago', 'Otago'),
                            ('southland', 'Southland'),
                            ('nationwide', 'Nationwide'),
                            ('online', 'Online'),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    'age_requirement',
                    models.CharField(
                        blank=True,
                        choices=[('all', 'All Ages'), ('13', '13+'), ('16', '16+'), ('18', '18+')],
                        max_length=3,
                    ),
                ),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
        ),
        migrations.CreateModel(
            name='EventSeries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', apps.core.fields.AutoSlugField(populate_from='name', unique=True)),
                ('description', markdownfield.models.MarkdownField(blank=True, rendered_field='description_rendered')),
                ('description_rendered', markdownfield.models.RenderedMarkdownField()),
                (
                    'logo',
                    models.ImageField(
                        blank=True,
                        height_field='logo_height',
                        upload_to='organisations/series',
                        width_field='logo_width',
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('logo_width', models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ('logo_height', models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ('logo_ppoi', models.CharField(default='0.5x0.5', max_length=20)),
                (
                    'organisation',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='series',
                        to='organisations.organisation',
                    ),
                ),
            ],
            options={
                'verbose_name_plural': 'event series',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SocialLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'platform',
                    models.CharField(
                        choices=[
                            ('telegram', 'Telegram'),
                            ('discord', 'Discord'),
                            ('twitter', 'Twitter / X'),
                            ('bluesky', 'Bluesky'),
                            ('instagram', 'Instagram'),
                            ('facebook', 'Facebook'),
                            ('mastodon', 'Mastodon'),
                            ('website', 'Website'),
                        ],
                        max_length=20,
                    ),
                ),
                ('url', models.URLField()),
                ('is_primary', models.BooleanField(default=False)),
                ('click_count', models.PositiveIntegerField(default=0)),
                (
                    'organisation',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='social_links',
                        to='organisations.organisation',
                    ),
                ),
            ],
            options={
                'ordering': ['-is_primary', 'platform'],
            },
        ),
    ]
