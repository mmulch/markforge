"""Secure credential storage using the OS keyring.

Delegates to GNOME Keyring / KWallet on Linux, Keychain on macOS, and
Windows Credential Manager on Windows via the ``keyring`` library.
Falls back to returning empty strings if the keyring is unavailable
(e.g. headless CI environments) so the app still starts without crashing.
"""
from __future__ import annotations

_APP = "MarkForge"

try:
    import keyring
    import keyring.errors
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


def get_secret(key: str) -> str:
    """Return the stored secret for *key*, or '' if unavailable."""
    if not _AVAILABLE:
        return ""
    try:
        return keyring.get_password(_APP, key) or ""
    except Exception:
        return ""


def set_secret(key: str, value: str) -> None:
    """Store *value* for *key* in the OS keyring.

    If *value* is empty the entry is deleted so stale secrets are not left
    behind after the user clears a field.
    """
    if not _AVAILABLE:
        return
    try:
        if value:
            keyring.set_password(_APP, key, value)
        else:
            try:
                keyring.delete_password(_APP, key)
            except keyring.errors.PasswordDeleteError:
                pass
    except Exception:
        pass
