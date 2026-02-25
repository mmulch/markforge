"""Process-wide spell-check singleton supporting pyspellchecker and enchant."""

from __future__ import annotations

try:
    from spellchecker import SpellChecker as _PyspellChecker
    _PYSPELL_AVAILABLE = True
except ImportError:
    _PYSPELL_AVAILABLE = False

try:
    import enchant as _enchant
    _ENCHANT_AVAILABLE = True
except ImportError:
    _ENCHANT_AVAILABLE = False

# Languages with a pyspellchecker built-in frequency dictionary
_PYSPELL_LANGS: frozenset[str] = frozenset(
    {"en", "de", "es", "fr", "it", "nl", "pt", "ar", "fa"}
)

# Enchant locale codes for languages that need system Hunspell dictionaries
_ENCHANT_CODES: dict[str, str] = {
    "vi": "vi_VN",
    "sv": "sv_SE",
    "uk": "uk_UA",
    "kn": "kn_IN",
    "hi": "hi_IN",
}


class _SpellCheck:
    available: bool = _PYSPELL_AVAILABLE or _ENCHANT_AVAILABLE

    def __init__(self) -> None:
        self._enabled  = False
        self._lang     = "en"
        self._backend  = None   # pyspellchecker SpellChecker or enchant Dict
        self._cache: dict[str, bool] = {}

    @property
    def enabled(self) -> bool:
        return self._enabled and self._backend is not None

    @property
    def language(self) -> str:
        return self._lang

    def _init_backend(self) -> None:
        """Choose and initialise the appropriate backend for the current language."""
        self._backend = None
        if self._lang in _PYSPELL_LANGS and _PYSPELL_AVAILABLE:
            try:
                self._backend = _PyspellChecker(language=self._lang)
            except Exception:
                pass
        elif self._lang in _ENCHANT_CODES and _ENCHANT_AVAILABLE:
            try:
                self._backend = _enchant.Dict(_ENCHANT_CODES[self._lang])
            except Exception:
                pass

    def set_enabled(self, on: bool) -> None:
        if self._enabled == on:
            return
        self._enabled = on
        if on and self._backend is None:
            self._init_backend()

    def set_language(self, lang: str) -> None:
        self._lang = lang
        self._backend = None
        self._cache.clear()
        if self._enabled:
            self._init_backend()

    def is_ok(self, word: str) -> bool:
        """Return True if the word is correctly spelled."""
        if not self.enabled:
            return True
        if word in self._cache:
            return self._cache[word]
        try:
            if _PYSPELL_AVAILABLE and hasattr(self._backend, "unknown"):
                result = len(self._backend.unknown([word])) == 0
            else:
                result = self._backend.check(word)   # enchant Dict interface
        except Exception:
            result = True
        self._cache[word] = result
        return result


_instance = _SpellCheck()


def spell_check() -> _SpellCheck:
    """Return the process-wide SpellCheck singleton."""
    return _instance
