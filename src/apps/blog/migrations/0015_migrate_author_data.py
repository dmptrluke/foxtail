from django.db import migrations


def migrate_authors(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    Author = apps.get_model('blog', 'Author')

    author_names = Post.objects.exclude(author_legacy='').values_list('author_legacy', flat=True).distinct()
    author_map = {}
    for name in author_names:
        author_map[name], _ = Author.objects.get_or_create(name=name)

    for post in Post.objects.exclude(author_legacy=''):
        post.author = author_map[post.author_legacy]
        post.save(update_fields=['author'])


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0014_author_model'),
    ]

    operations = [
        migrations.RunPython(migrate_authors, migrations.RunPython.noop),
    ]
