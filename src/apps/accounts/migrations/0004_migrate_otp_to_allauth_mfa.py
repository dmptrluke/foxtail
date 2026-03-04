"""
Data migration: Migrate django-otp TOTP devices and static tokens
to allauth's built-in MFA (mfa_authenticator table).

Reads directly from the old django-otp tables via raw SQL so the
django-otp package does not need to be installed.
"""

import base64
import json

from django.db import connection, migrations


def table_exists(table_name):
    return table_name in connection.introspection.table_names()


def migrate_otp_to_allauth_mfa(apps, schema_editor):
    if not table_exists("otp_totp_totpdevice"):
        return

    Authenticator = apps.get_model("mfa", "Authenticator")

    with connection.cursor() as cursor:
        # Migrate confirmed TOTP devices
        cursor.execute(
            "SELECT user_id, key, created_at, last_used_at "
            "FROM otp_totp_totpdevice "
            "WHERE confirmed = true"
        )
        totp_rows = cursor.fetchall()

    for user_id, hex_key, created_at, last_used_at in totp_rows:
        # django-otp stores keys as hex, allauth expects base32
        secret = base64.b32encode(bytes.fromhex(hex_key)).decode("ascii")

        if not Authenticator.objects.filter(user_id=user_id, type="totp").exists():
            Authenticator.objects.create(
                user_id=user_id,
                type="totp",
                data={"secret": secret},
                created_at=created_at,
                last_used_at=last_used_at,
            )

    # Migrate recovery codes (static tokens)
    if not table_exists("otp_static_staticdevice"):
        return

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT sd.user_id, array_agg(st.token) "
            "FROM otp_static_staticdevice sd "
            "JOIN otp_static_statictoken st ON st.device_id = sd.id "
            "WHERE sd.confirmed = true "
            "GROUP BY sd.user_id"
        )
        static_rows = cursor.fetchall()

    for user_id, tokens in static_rows:
        if not tokens:
            continue
        if not Authenticator.objects.filter(
            user_id=user_id, type="recovery_codes"
        ).exists():
            # allauth supports a "migrated_codes" format for imported codes
            Authenticator.objects.create(
                user_id=user_id,
                type="recovery_codes",
                data={"migrated_codes": list(tokens)},
            )


def reverse_migration(apps, schema_editor):
    # We don't reverse this - the old tables remain untouched
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_alter_user_first_name"),
        ("mfa", "0003_authenticator_type_uniq"),
    ]

    operations = [
        migrations.RunPython(migrate_otp_to_allauth_mfa, reverse_migration),
    ]
