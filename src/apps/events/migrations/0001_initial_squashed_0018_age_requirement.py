import apps.core.fields
import apps.core.validators
import django.db.models.deletion
import markdownfield.models
import taggit.managers
from django.conf import settings
from django.db import migrations, models


def create_editors_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Event Editors')


def remove_editors_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Event Editors').delete()


class Migration(migrations.Migration):
    replaces = [
        ('events', '0001_initial'),
        ('events', '0002_add_url'),
        ('events', '0003_split_dates'),
        ('events', '0004_rename_fields'),
        ('events', '0005_event_slug'),
        ('events', '0006_event_address'),
        ('events', '0007_swap_autoslugfield'),
        ('events', '0008_event_geocoding'),
        ('events', '0009_switch_to_imagefield'),
        ('events', '0010_image_null_to_empty'),
        ('events', '0011_image_remove_null'),
        ('events', '0012_add_published_model'),
        ('events', '0013_remove_map_image'),
        ('events', '0014_event_editors_group'),
        ('events', '0015_event_organisation_event_series_alter_event_image'),
        ('events', '0016_eventinterest'),
        ('events', '0017_remove_unique_together_use_constraint'),
        ('events', '0018_age_requirement'),
    ]

    initial = True

    dependencies = [
        ('organisations', '0001_initial'),
        ('taggit', '0003_taggeditem_add_unique_index'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='100 characters or fewer.', max_length=100)),
                ('location', models.CharField(max_length=200)),
                ('description', markdownfield.models.MarkdownField(rendered_field='description_rendered')),
                ('description_rendered', markdownfield.models.RenderedMarkdownField()),
                ('start', models.DateField()),
                ('end', models.DateField(blank=True, help_text='End date and time are optional.', null=True)),
                ('start_time', models.TimeField(blank=True, help_text='Time is optional.', null=True)),
                ('end_time', models.TimeField(blank=True, help_text='End date and time are optional.', null=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                (
                    'image',
                    models.ImageField(
                        blank=True,
                        height_field='image_height',
                        upload_to='events',
                        validators=[apps.core.validators.FileSizeValidator()],
                        width_field='image_width',
                    ),
                ),
                ('image_height', models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ('image_width', models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ('image_ppoi', models.CharField(default='0.5x0.5', max_length=20)),
                ('slug', apps.core.fields.AutoSlugField(populate_from='title', unique_for_year='start')),
                ('url', models.URLField(blank=True)),
                ('address', models.TextField(blank=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                (
                    'publish_status',
                    models.SmallIntegerField(
                        choices=[(0, 'Never Available'), (1, 'Available Now'), (2, 'Available after "Publish Date"')],
                        default=1,
                        verbose_name='Publish',
                    ),
                ),
                ('live_as_of', models.DateTimeField(blank=True, null=True, verbose_name='Publish Date')),
                (
                    'age_requirement',
                    models.CharField(
                        blank=True,
                        choices=[('all', 'All Ages'), ('13', '13+'), ('16', '16+'), ('18', '18+')],
                        max_length=3,
                    ),
                ),
                (
                    'tags',
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text='A comma-separated list of tags.',
                        through='taggit.TaggedItem',
                        to='taggit.Tag',
                        verbose_name='Tags',
                    ),
                ),
                (
                    'organisation',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='organisations.organisation',
                    ),
                ),
                (
                    'series',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='organisations.eventseries',
                    ),
                ),
            ],
            options={
                'ordering': ['start'],
            },
        ),
        migrations.RunPython(create_editors_group, remove_editors_group),
        migrations.CreateModel(
            name='EventInterest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'status',
                    models.CharField(
                        choices=[('interested', 'Interested'), ('going', 'Going')], default='interested', max_length=12
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                (
                    'event',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='interests', to='events.event'
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='event_interests',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(fields=('event', 'user'), name='events_eventinterest_event_user_uniq')
                ],
            },
        ),
    ]
