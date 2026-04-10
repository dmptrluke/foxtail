from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0020_field_cleanup'),
    ]

    operations = [
        # rename model tables (IF EXISTS for fresh databases where tables are already blog_*)
        migrations.RunSQL(
            sql='ALTER TABLE IF EXISTS foxtail_blog_author RENAME TO blog_author;',
            reverse_sql='ALTER TABLE blog_author RENAME TO foxtail_blog_author;',
        ),
        migrations.RunSQL(
            sql='ALTER TABLE IF EXISTS foxtail_blog_post RENAME TO blog_post;',
            reverse_sql='ALTER TABLE blog_post RENAME TO foxtail_blog_post;',
        ),
        migrations.RunSQL(
            sql='ALTER TABLE IF EXISTS foxtail_blog_comment RENAME TO blog_comment;',
            reverse_sql='ALTER TABLE blog_comment RENAME TO foxtail_blog_comment;',
        ),
        # rename M2M tables
        migrations.RunSQL(
            sql='ALTER TABLE IF EXISTS foxtail_blog_post_organisations RENAME TO blog_post_organisations;',
            reverse_sql='ALTER TABLE blog_post_organisations RENAME TO foxtail_blog_post_organisations;',
        ),
        migrations.RunSQL(
            sql='ALTER TABLE IF EXISTS foxtail_blog_post_event_series RENAME TO blog_post_event_series;',
            reverse_sql='ALTER TABLE blog_post_event_series RENAME TO foxtail_blog_post_event_series;',
        ),
        migrations.RunSQL(
            sql='ALTER TABLE IF EXISTS foxtail_blog_post_events RENAME TO blog_post_events;',
            reverse_sql='ALTER TABLE blog_post_events RENAME TO foxtail_blog_post_events;',
        ),
        # update content type registry (idempotent WHERE clauses)
        migrations.RunSQL(
            sql="UPDATE django_content_type SET app_label = 'blog' WHERE app_label = 'foxtail_blog';",
            reverse_sql="UPDATE django_content_type SET app_label = 'foxtail_blog' WHERE app_label = 'blog';",
        ),
        migrations.RunSQL(
            sql="UPDATE django_content_type SET app_label = 'contact' WHERE app_label = 'foxtail_contact';",
            reverse_sql="UPDATE django_content_type SET app_label = 'foxtail_contact' WHERE app_label = 'contact';",
        ),
    ]
