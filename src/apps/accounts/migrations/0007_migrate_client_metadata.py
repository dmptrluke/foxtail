"""
Data migration to populate ClientMetadata records from old oidc_provider_client
table columns (website_url, terms_url, contact_email, logo).
"""

from django.db import connection, migrations


def table_exists(table_name):
    return table_name in connection.introspection.table_names()


def migrate_metadata(apps, schema_editor):
    if not table_exists("oidc_provider_client"):
        return

    ClientMetadata = apps.get_model("accounts", "ClientMetadata")
    Client = apps.get_model("allauth_idp_oidc", "Client")

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT client_id, website_url, terms_url, contact_email, logo "
            "FROM oidc_provider_client"
        )
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for row in rows:
        has_metadata = any([
            row.get("website_url"),
            row.get("terms_url"),
            row.get("contact_email"),
            row.get("logo"),
        ])
        if not has_metadata:
            continue

        try:
            client = Client.objects.get(id=row["client_id"])
        except Client.DoesNotExist:
            continue

        ClientMetadata.objects.create(
            client=client,
            logo=row.get("logo") or "",
            website_url=row.get("website_url") or "",
            terms_url=row.get("terms_url") or "",
            contact_email=row.get("contact_email") or "",
        )

    count = ClientMetadata.objects.count()
    if count:
        print(f"\n  Created {count} client metadata record(s).")


def reverse_migration(apps, schema_editor):
    ClientMetadata = apps.get_model("accounts", "ClientMetadata")
    ClientMetadata.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_clientmetadata"),
    ]

    operations = [
        migrations.RunPython(migrate_metadata, reverse_migration),
    ]
