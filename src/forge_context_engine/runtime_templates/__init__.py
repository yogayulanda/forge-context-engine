"""Runtime template access helpers."""

from __future__ import annotations

from importlib.resources import files
from typing import Protocol


class Traversable(Protocol):
    def iterdir(self): ...
    def is_dir(self) -> bool: ...
    @property
    def name(self) -> str: ...
    def read_text(self, encoding: str = "utf-8") -> str: ...


def template_root() -> Traversable:
    """Return the packaged runtime template root."""

    return files(__package__)


def iter_template_files(section: str) -> dict[str, str]:
    """Return all text files for a template section, keyed by relative path."""

    root = template_root() / section
    results: dict[str, str] = {}
    _walk(root, prefix="", results=results)
    return results


def read_template(section: str, relative_path: str) -> str:
    """Read one template file from the packaged runtime payload."""

    return (template_root() / section / relative_path).read_text(encoding="utf-8")


def _walk(node: Traversable, *, prefix: str, results: dict[str, str]) -> None:
    """Walk a template tree recursively."""

    for child in node.iterdir():
        rel = f"{prefix}/{child.name}" if prefix else child.name
        if child.is_dir():
            _walk(child, prefix=rel, results=results)
            continue
        results[rel] = child.read_text(encoding="utf-8")
