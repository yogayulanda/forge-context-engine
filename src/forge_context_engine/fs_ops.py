"""Path helpers for Forge CLI filesystem operations."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


@dataclass(frozen=True)
class ForgeTargetPaths:
    """Resolved target roots for future init/update operations."""

    target_root: Path
    forge_root: Path


def resolve_target_paths(target: Path | None = None) -> ForgeTargetPaths:
    """Resolve the current default target."""

    root = (target or Path.cwd()).resolve()
    return ForgeTargetPaths(
        target_root=root,
        forge_root=root / ".forge",
    )


def to_manifest_path(target_root: Path, path: Path) -> str:
    """Convert a filesystem path into a manifest-friendly relative path."""

    return path.resolve().relative_to(target_root.resolve()).as_posix()


def sha256_text(content: str) -> str:
    """Hash text content for manifest change detection."""

    return sha256(content.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    """Hash a file from disk."""

    return sha256_text(path.read_text(encoding="utf-8"))
