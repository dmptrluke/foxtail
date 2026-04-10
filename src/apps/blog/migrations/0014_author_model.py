import django.db.models.deletion
import imagefield.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_image_remove_null'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='blog_author', to=settings.AUTH_USER_MODEL)),
                ('description', models.TextField(blank=True, help_text='Short bio or tagline.')),
                ('link', models.URLField(blank=True, help_text='Website, social media, etc.')),
                ('avatar', imagefield.fields.ImageField(blank=True, upload_to='blog/authors')),
                ('avatar_ppoi', imagefield.fields.PPOIField(default='0.5x0.5', max_length=20, verbose_name='avatar PPOI')),
                ('avatar_height', models.PositiveIntegerField(blank=True, editable=False, null=True, verbose_name='avatar height')),
                ('avatar_width', models.PositiveIntegerField(blank=True, editable=False, null=True, verbose_name='avatar width')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RenameField(
            model_name='post',
            old_name='author',
            new_name='author_legacy',
        ),
        migrations.AddField(
            model_name='post',
            name='author',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='posts',
                to='blog.author',
            ),
        ),
    ]
