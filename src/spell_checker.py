"""Process-wide spell-check singleton wrapping pyspellchecker."""

from __future__ import annotations

try:
    from spellchecker import SpellChecker as _Backend
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


class _SpellCheck:
    available: bool = _AVAILABLE

    def __init__(self) -> None:
        self._enabled  = False
        self._lang     = "en"
        self._backend  = None
        self._cache: dict[str, bool] = {}

    @property
    def enabled(self) -> bool:
        return self._enabled and self._backend is not None

    @property
    def language(self) -> str:
        return self._lang

    def set_enabled(self, on: bool) -> None:
        if self._enabled == on:
            return
        self._enabled = on
        if on and self._backend is None and _AVAILABLE:
            try:
                self._backend = _Backend(language=self._lang)
            except Exception:
                self._enabled = False

    def set_language(self, lang: str) -> None:
        self._lang = lang
        if not _AVAILABLE:
            return
        try:
            self._backend = _Backend(language=lang)
            self._cache.clear()
        except Exception:
            pass

    def is_ok(self, word: str) -> bool:
        """Return True if the word is correctly spelled."""
        if not self.enabled:
            return True
        if word in self._cache:
            return self._cache[word]
        result = len(self._backend.unknown([word])) == 0
        self._cache[word] = result
        return result


_instance = _SpellCheck()


def spell_check() -> _SpellCheck:
    """Return the process-wide SpellCheck singleton."""
    return _instance
