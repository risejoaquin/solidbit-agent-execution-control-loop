"""Tests for Gmail API OAuth2 Credential Management."""

from __future__ import annotations

import datetime
from typing import Any, Dict
import pytest

from sacl.transport.exceptions import TransportAuthError
from sacl.transport.oauth import (
    CREDENTIAL_TARGET_NAME,
    InMemoryOAuth2CredentialProvider,
    WindowsCredentialManagerProvider,
)


def test_in_memory_provider_returns_valid_token() -> None:
    provider = InMemoryOAuth2CredentialProvider(
        access_token="valid_access_token_123",
        refresh_token="valid_refresh_token_456",
        client_id="test_client_id",
        client_secret="test_client_secret",
        token_expiry=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
    )
    assert provider.get_access_token() == "valid_access_token_123"
    assert provider.get_auth_headers() == {"Authorization": "Bearer valid_access_token_123"}
    assert not provider.is_token_expired()


def test_in_memory_provider_refreshes_when_expired() -> None:
    refresh_called = False

    def mock_refresh(client_id: str, client_secret: str, refresh_token: str) -> Dict[str, Any]:
        nonlocal refresh_called
        refresh_called = True
        assert client_id == "my_client"
        assert client_secret == "my_secret"
        assert refresh_token == "my_refresh"
        return {
            "access_token": "new_refreshed_access_token_789",
            "expires_in": 3600,
        }

    # Expired 10 seconds ago
    past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=10)
    provider = InMemoryOAuth2CredentialProvider(
        access_token="old_expired_token",
        refresh_token="my_refresh",
        client_id="my_client",
        client_secret="my_secret",
        token_expiry=past_time,
        refresh_callback=mock_refresh,
    )

    assert provider.is_token_expired()
    # Calling get_access_token should auto-refresh
    new_token = provider.get_access_token()
    assert refresh_called is True
    assert new_token == "new_refreshed_access_token_789"
    assert provider.get_access_token() == "new_refreshed_access_token_789"
    assert not provider.is_token_expired()


def test_refresh_fails_without_refresh_token() -> None:
    provider = InMemoryOAuth2CredentialProvider(access_token="only_access_token")
    with pytest.raises(TransportAuthError, match="no refresh_token provided"):
        provider.refresh_access_token()


def test_windows_credential_manager_provider_fallback() -> None:
    fallback = InMemoryOAuth2CredentialProvider(access_token="fallback_token_abc")
    provider = WindowsCredentialManagerProvider(
        target_name=CREDENTIAL_TARGET_NAME, fallback_provider=fallback
    )
    assert provider.get_access_token() == "fallback_token_abc"
    assert provider.get_auth_headers() == {"Authorization": "Bearer fallback_token_abc"}


def test_windows_credential_manager_fails_without_target_or_fallback() -> None:
    provider = WindowsCredentialManagerProvider(target_name="NON_EXISTENT_TARGET")
    with pytest.raises(TransportAuthError, match="not found and no fallback configured"):
        provider.get_access_token()
