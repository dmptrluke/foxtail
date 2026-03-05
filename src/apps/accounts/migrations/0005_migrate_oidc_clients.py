"""
Data migration to copy OIDC client records from django-oidc-provider tables
to allauth.idp.oidc tables.

This migration reads from the old oidc_provider_client table using raw SQL
(since the model is being removed) and creates corresponding allauth.idp
Client records.

Client secrets are hashed using Django's make_password since the old fork
stored them in plaintext.
"""

import datetime

from django.contrib.auth.hashers import make_password
from django.db import connection, migrations
from django.utils import timezone


def table_exists(table_name):
    return table_name in connection.introspection.table_names()


def migrate_clients(apps, schema_editor):
    if not table_exists("oidc_provider_client"):
        return

    Client = apps.get_model("allauth_idp_oidc", "Client")

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT client_id, name, client_secret, client_type, "
            "_redirect_uris, _scope, require_consent, "
            "website_url, terms_url, contact_email, logo, date_created "
            "FROM oidc_provider_client"
        )
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    for row in rows:
        redirect_uris = row["_redirect_uris"] or ""
        redirect_uris = redirect_uris.replace("\r\n", "\n").replace("\r", "\n")

        scopes = row["_scope"].strip() if row["_scope"] else ""
        if scopes:
            scopes = "\n".join(scopes.split())
        else:
            scopes = "openid\nemail\nprofile"

        data = {}
        if row.get("website_url"):
            data["website_url"] = row["website_url"]
        if row.get("terms_url"):
            data["terms_url"] = row["terms_url"]
        if row.get("contact_email"):
            data["contact_email"] = row["contact_email"]
        if row.get("logo"):
            data["logo_url"] = f"/media/{row['logo']}"

        Client.objects.create(
            id=row["client_id"],
            name=row["name"],
            secret=make_password(row["client_secret"]),
            type=row["client_type"],
            redirect_uris=redirect_uris,
            scopes=scopes,
            default_scopes="",
            response_types="code",
            grant_types="authorization_code\nrefresh_token",
            skip_consent=not row["require_consent"],
            data=data or None,
            created_at=timezone.make_aware(
                datetime.datetime.combine(row["date_created"], datetime.time.min)
            ) if isinstance(row["date_created"], datetime.date) else row["date_created"],
        )

    if rows:
        print(f"\n  Migrated {len(rows)} OIDC client(s) to allauth.idp.")

    # Print RSA key extraction reminder
    if table_exists("oidc_provider_rsakey"):
        with connection.cursor() as cursor:
            cursor.execute("SELECT key FROM oidc_provider_rsakey LIMIT 1")
            rsa_row = cursor.fetchone()
            if rsa_row:
                print(
                    "\n  !!! RSA PRIVATE KEY found in oidc_provider_rsakey table. !!!"
                    "\n  You must copy this key to the OIDC_RSA_PRIVATE_KEY environment variable."
                    "\n  Run: SELECT key FROM oidc_provider_rsakey;"
                )


def reverse_migration(apps, schema_editor):
    Client = apps.get_model("allauth_idp_oidc", "Client")
    Client.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_migrate_otp_to_allauth_mfa"),
        ("allauth_idp_oidc", "0002_client_default_scopes"),
    ]

    operations = [
        migrations.RunPython(migrate_clients, reverse_migration),
    ]
