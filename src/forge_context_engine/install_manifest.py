"""Install manifest schema definitions for Forge init/update flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

from .version import __version__

MANIFEST_VERSION = "1"
PROFILE_SERVICE = "service"
PROFILE_WORKSPACE = "workspace"
INSTALLED_FROM = "git+https://github.com/yogayulanda/forge-context-engine.git"

DEFAULT_SELECTED_TOOLS = ("codex", "claude")
ALL_SUPPORTED_TOOLS = ("codex", "claude", "copilot", "opencode")

MANAGED_PATHS_BASELINE = (
    ".forge/.gitignore",
    ".forge/adapter.md",
    ".forge/forge.config.yaml",
    ".forge/forge-install.yaml",
    ".forge/context/modes/",
    ".forge/context/00-meta/ai-readiness-factors.md",
    ".forge/context/00-meta/conventions-evidence.md",
    ".forge/context/00-meta/conventions-language.md",
    ".forge/context/00-meta/conventions-risk.md",
    ".forge/context/00-meta/conventions-validation.md",
    ".forge/context/00-meta/conventions.md",
)

USER_OWNED_PATHS_BASELINE = (
    ".forge/context/00-meta/context-manifest.md",
    ".forge/context/00-meta/glossary.md",
    ".forge/context/01-core/",
    ".forge/context/layers/",
    ".forge/context/repo-map/",
    ".forge/context/systems/",
    ".forge/context/knowledge/",
    ".forge/context/decisions/",
    ".forge/context/unknowns/",
    ".forge/context-patches/",
    ".forge/generated/",
)

LOCAL_ONLY_PATHS_BASELINE = (
    ".forge/temp/",
    ".forge/cache/",
)


@dataclass(frozen=True)
class ForgeInstallManifest:
    """Schema model for `.forge/forge-install.yaml`."""

    manifest_version: str = MANIFEST_VERSION
    forge_version: str = __version__
    profile: str = PROFILE_SERVICE
    selected_tools: tuple[str, ...] = field(default_factory=lambda: DEFAULT_SELECTED_TOOLS)
    installed_from: str = INSTALLED_FROM
    installed_at: str = ""
    template_revision: str = __version__
    source_revision: str = __version__
    managed_paths: tuple[str, ...] = field(default_factory=lambda: MANAGED_PATHS_BASELINE)
    user_owned_paths: tuple[str, ...] = field(default_factory=lambda: USER_OWNED_PATHS_BASELINE)
    local_only_paths: tuple[str, ...] = field(default_factory=lambda: LOCAL_ONLY_PATHS_BASELINE)
    managed_file_hashes: dict[str, str] = field(default_factory=dict)


TOOL_ALIASES = {
    "0": "all",
    "1": "codex",
    "2": "claude",
    "3": "copilot",
    "4": "opencode",
    "all": "all",
    "default": "default",
    "codex": "codex",
    "code": "codex",
    "claude": "claude",
    "claude-code": "claude",
    "claude_code": "claude",
    "copilot": "copilot",
    "github-copilot": "copilot",
    "github_copilot": "copilot",
    "gh-copilot": "copilot",
    "opencode": "opencode",
    "open-code": "opencode",
    "open_code": "opencode",
}


def normalize_tools(tools: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """Normalize tool names into canonical order."""

    seen: set[str] = set()
    unknown: list[str] = []
    for tool in tools:
        token = tool.strip().lower()
        if not token:
            continue
        canonical = TOOL_ALIASES.get(token)
        if canonical is None:
            unknown.append(tool.strip())
            continue
        if canonical == "default":
            seen.update(DEFAULT_SELECTED_TOOLS)
            continue
        if canonical == "all":
            return ALL_SUPPORTED_TOOLS
        seen.add(canonical)

    if unknown:
        joined = ", ".join(sorted(set(unknown)))
        raise ValueError(
            "Unsupported tool selection: "
            f"{joined}. Use codex, claude, copilot, opencode, all, or numeric picks 1/2/3/4."
        )

    normalized = tuple(tool for tool in ALL_SUPPORTED_TOOLS if tool in seen)
    if not normalized:
        raise ValueError("At least one tool must be selected.")
    return normalized


def parse_tools_args(raw: str | list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    """Parse friendly tool input into a canonical tool tuple."""

    if raw is None:
        return DEFAULT_SELECTED_TOOLS
    values = [raw] if isinstance(raw, str) else list(raw)
    tokens: list[str] = []
    for value in values:
        for token in re.split(r"[\s,;+|/]+", value.strip()):
            cleaned = token.strip()
            if cleaned:
                tokens.append(cleaned)
    return normalize_tools(tokens)


def parse_tools_arg(raw: str | None) -> tuple[str, ...]:
    """Parse `--tools` into a canonical tool tuple."""

    return parse_tools_args(raw)

def build_managed_paths(profile: str, selected_tools: tuple[str, ...]) -> tuple[str, ...]:
    """Build manifest managed paths for the selected profile/tools."""

    paths = list(MANAGED_PATHS_BASELINE)
    if "codex" in selected_tools or "opencode" in selected_tools:
        paths.append("AGENTS.md")
    if "opencode" in selected_tools:
        paths.append("skills/")
    if "claude" in selected_tools:
        paths.extend(("CLAUDE.md", ".claude/commands/"))
    if "copilot" in selected_tools:
        paths.extend((".github/copilot-instructions.md", ".github/prompts/"))
    if profile == PROFILE_WORKSPACE:
        paths.append(".forge/workspace.yaml")
    return tuple(paths)


def build_manifest(
    *,
    profile: str,
    selected_tools: tuple[str, ...],
    managed_file_hashes: dict[str, str],
    installed_at: str | None = None,
) -> ForgeInstallManifest:
    """Create a manifest with current defaults."""

    return ForgeInstallManifest(
        profile=profile,
        selected_tools=selected_tools,
        installed_at=installed_at or utc_now_iso(),
        managed_paths=build_managed_paths(profile, selected_tools),
        managed_file_hashes=dict(sorted(managed_file_hashes.items())),
    )


def utc_now_iso() -> str:
    """Return a stable UTC timestamp for manifest writing."""

    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def manifest_to_document(manifest: ForgeInstallManifest) -> dict[str, Any]:
    """Convert a manifest dataclass into a deterministic document."""

    return {
        "manifest_version": manifest.manifest_version,
        "forge_version": manifest.forge_version,
        "profile": manifest.profile,
        "selected_tools": list(manifest.selected_tools),
        "installed_from": manifest.installed_from,
        "installed_at": manifest.installed_at,
        "template_revision": manifest.template_revision,
        "source_revision": manifest.source_revision,
        "managed_paths": list(manifest.managed_paths),
        "user_owned_paths": list(manifest.user_owned_paths),
        "local_only_paths": list(manifest.local_only_paths),
        "managed_file_hashes": dict(sorted(manifest.managed_file_hashes.items())),
    }


def dump_manifest(manifest: ForgeInstallManifest) -> str:
    """Serialize a manifest to deterministic YAML."""

    document = manifest_to_document(manifest)
    lines: list[str] = []
    ordered_keys = (
        "manifest_version",
        "forge_version",
        "profile",
        "selected_tools",
        "installed_from",
        "installed_at",
        "template_revision",
        "source_revision",
        "managed_paths",
        "user_owned_paths",
        "local_only_paths",
        "managed_file_hashes",
    )

    for key in ordered_keys:
        value = document[key]
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for subkey, subvalue in value.items():
                lines.append(f"  {subkey}: {subvalue}")
        else:
            lines.append(f'{key}: "{value}"')

    return "\n".join(lines) + "\n"


def load_manifest_text(text: str) -> ForgeInstallManifest:
    """Parse manifest YAML written by `dump_manifest`."""

    parsed = _parse_simple_yaml(text)
    return ForgeInstallManifest(
        manifest_version=str(parsed.get("manifest_version", MANIFEST_VERSION)),
        forge_version=str(parsed.get("forge_version", __version__)),
        profile=str(parsed.get("profile", PROFILE_SERVICE)),
        selected_tools=tuple(parsed.get("selected_tools", list(DEFAULT_SELECTED_TOOLS))),
        installed_from=str(parsed.get("installed_from", INSTALLED_FROM)),
        installed_at=str(parsed.get("installed_at", "")),
        template_revision=str(parsed.get("template_revision", __version__)),
        source_revision=str(parsed.get("source_revision", __version__)),
        managed_paths=tuple(parsed.get("managed_paths", list(MANAGED_PATHS_BASELINE))),
        user_owned_paths=tuple(parsed.get("user_owned_paths", list(USER_OWNED_PATHS_BASELINE))),
        local_only_paths=tuple(parsed.get("local_only_paths", list(LOCAL_ONLY_PATHS_BASELINE))),
        managed_file_hashes=dict(parsed.get("managed_file_hashes", {})),
    )


def load_manifest(path: Path) -> ForgeInstallManifest:
    """Read and parse a manifest from disk."""

    return load_manifest_text(path.read_text(encoding="utf-8"))


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse the limited YAML shape used by the install manifest."""

    result: dict[str, Any] = {}
    lines = text.splitlines()
    index = 0

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        if raw.startswith(" "):
            raise ValueError(f"Unexpected indentation in manifest: {raw}")
        if ":" not in raw:
            raise ValueError(f"Invalid manifest line: {raw}")

        key, remainder = raw.split(":", 1)
        key = key.strip()
        value = remainder.strip()
        if value:
            result[key] = _strip_yaml_scalar(value)
            index += 1
            continue

        index += 1
        block: list[str] = []
        while index < len(lines):
            child = lines[index]
            if not child.strip():
                index += 1
                continue
            if not child.startswith("  "):
                break
            block.append(child[2:])
            index += 1

        if not block:
            result[key] = []
        elif all(item.startswith("- ") for item in block):
            result[key] = [_strip_yaml_scalar(item[2:].strip()) for item in block]
        else:
            mapping: dict[str, str] = {}
            for item in block:
                if ":" not in item:
                    raise ValueError(f"Invalid manifest mapping line: {item}")
                subkey, subvalue = item.split(":", 1)
                mapping[subkey.strip()] = _strip_yaml_scalar(subvalue.strip())
            result[key] = mapping

    return result


def _strip_yaml_scalar(value: str) -> str:
    """Strip the simple quoted scalars emitted by `dump_manifest`."""

    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value
