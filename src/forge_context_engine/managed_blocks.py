"""Managed block helpers for safe root-entrypoint updates."""

from __future__ import annotations

from dataclasses import dataclass


START_MARKER = "<!-- BEGIN FORGE MANAGED BLOCK -->"
END_MARKER = "<!-- END FORGE MANAGED BLOCK -->"


@dataclass(frozen=True)
class ManagedBlockTarget:
    """Describes a file that may host a Forge-managed block in Batch B."""

    path: str
    label: str


MANAGED_BLOCK_TARGETS = (
    ManagedBlockTarget(path="AGENTS.md", label="Codex entrypoint"),
    ManagedBlockTarget(path="CLAUDE.md", label="Claude entrypoint"),
    ManagedBlockTarget(
        path=".github/copilot-instructions.md",
        label="GitHub Copilot instructions",
    ),
)


def wrap_managed_block(content: str) -> str:
    """Wrap content in stable Forge managed block markers."""

    body = content.rstrip()
    return f"{START_MARKER}\n{body}\n{END_MARKER}\n"


def has_managed_block(content: str) -> bool:
    """Check whether a file already contains a Forge managed block."""

    return START_MARKER in content and END_MARKER in content


def upsert_managed_block(existing: str, managed_content: str) -> tuple[str, str]:
    """Insert or update a Forge managed block in an existing text file."""

    block = wrap_managed_block(managed_content)
    if has_managed_block(existing):
        start = existing.index(START_MARKER)
        end = existing.index(END_MARKER) + len(END_MARKER)
        suffix = existing[end:]
        if suffix.startswith("\n"):
            suffix = suffix[1:]
        updated = existing[:start] + block + suffix
        return updated, "updated"

    if not existing.strip():
        return block, "created"

    separator = "\n\n" if not existing.endswith("\n\n") else ""
    if existing.endswith("\n"):
        separator = "\n" if not existing.endswith("\n\n") else ""
    updated = existing.rstrip() + separator + block
    return updated, "updated"
