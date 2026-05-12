import logging

from django.test import override_settings

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_rsa_key() -> str:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


@pytest.fixture
def primary_key():
    return generate_rsa_key()


@pytest.fixture
def fallback_key():
    return generate_rsa_key()


def get_jwks(client, path='/.well-known/jwks.json'):
    response = client.get(path)
    assert response.status_code == 200
    return response, response.json()


class TestOIDCJwksView:
    def test_discovery_jwks_exposes_primary_and_fallback_keys(self, client, primary_key, fallback_key):
        """Discovery JWKS includes the active key and rotation fallback keys."""
        with override_settings(
            IDP_OIDC_PRIVATE_KEY=primary_key,
            IDP_OIDC_PRIVATE_KEY_FALLBACKS=[fallback_key],
        ):
            response, data = get_jwks(client)

        assert response['Access-Control-Allow-Origin'] == '*'
        assert response['Cache-Control'] == 'public, max-age=3600'
        assert len(data['keys']) == 2
        assert {key['kty'] for key in data['keys']} == {'RSA'}
        assert len({key['kid'] for key in data['keys']}) == 2

    def test_legacy_jwks_alias_uses_same_key_set(self, client, primary_key, fallback_key):
        """Legacy /openid/jwks clients get the same rotation keys as discovery clients."""
        with override_settings(
            IDP_OIDC_PRIVATE_KEY=primary_key,
            IDP_OIDC_PRIVATE_KEY_FALLBACKS=[fallback_key],
        ):
            _, discovery_data = get_jwks(client)
            _, legacy_data = get_jwks(client, '/openid/jwks')

        assert legacy_data == discovery_data

    def test_duplicate_and_empty_fallback_keys_are_ignored(self, client, primary_key):
        """Duplicate and empty fallback settings do not add extra JWKS entries."""
        with override_settings(
            IDP_OIDC_PRIVATE_KEY=primary_key,
            IDP_OIDC_PRIVATE_KEY_FALLBACKS=['', None, primary_key],
        ):
            _, data = get_jwks(client)

        assert len(data['keys']) == 1

    def test_literal_newline_escaped_keys_are_supported(self, client, primary_key):
        """PEM keys loaded from escaped environment values still produce a JWK."""
        escaped_key = primary_key.replace('\n', '\\n')

        with override_settings(IDP_OIDC_PRIVATE_KEY=escaped_key, IDP_OIDC_PRIVATE_KEY_FALLBACKS=[]):
            _, data = get_jwks(client)

        assert len(data['keys']) == 1
        assert data['keys'][0]['kty'] == 'RSA'

    def test_invalid_fallback_key_is_logged_and_skipped(self, client, caplog, primary_key):
        """Invalid fallback keys are logged and do not break the JWKS response."""
        with (
            override_settings(
                IDP_OIDC_PRIVATE_KEY=primary_key,
                IDP_OIDC_PRIVATE_KEY_FALLBACKS=['not a pem key'],
            ),
            caplog.at_level(logging.ERROR, logger='apps.accounts.views'),
        ):
            _, data = get_jwks(client)

        assert len(data['keys']) == 1
        assert 'Failed to load OIDC fallback 1 signing key for JWKS.' in caplog.text
