"""Markdown guideline files and loader for the prompt editor agent."""

from functools import lru_cache
from importlib import resources

_KNOWN = frozenset({"anthropic", "openai", "google", "default"})


def load_provider_guidelines(provider: str | None) -> str:
    """Load provider-specific prompting guidelines as a text block.

    Falls back to ``default.md`` if provider is None or unrecognized.
    """
    key = (provider or "").strip().lower()
    if key not in _KNOWN or key == "default":
        name = "default.md"
    else:
        name = f"{key}.md"
    return _read_guideline_file(name)


@lru_cache(maxsize=8)
def _read_guideline_file(filename: str) -> str:
    """Read a guideline file from this package (cached)."""
    pkg = __package__ or "app.services.prompt_editor.guidelines"
    root = resources.files(pkg)
    return root.joinpath(filename).read_text(encoding="utf-8")
