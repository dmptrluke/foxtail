import django.db.models.deletion
from django.db import migrations, models

import imagefield.fields


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_migrate_oidc_clients"),
        ("allauth_idp_oidc", "0002_client_default_scopes"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClientMetadata",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "logo",
                    imagefield.fields.ImageField(
                        blank=True, upload_to="oidc/clients/"
                    ),
                ),
                ("website_url", models.URLField(blank=True)),
                ("terms_url", models.URLField(blank=True)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                (
                    "client",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="metadata",
                        to="allauth_idp_oidc.client",
                    ),
                ),
            ],
            options={
                "verbose_name": "client metadata",
                "verbose_name_plural": "client metadata",
            },
        ),
    ]
