#!/usr/bin/env python3
"""Lightweight validation harness for Forge CLI init/update behavior."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import os
from pathlib import Path

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

ROOT = Path(__file__).resolve().parents[1]
CLI = [sys.executable, "-B", "-m", "forge_context_engine.cli"]
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
ENGINE_ONLY_MARKERS = (
    "docs",
    "specs",
    "validation-cases",
    "runtime/adapters",
    "runtime/skills",
)
REQUIRED_META_FILES = (
    ".forge/context/00-meta/context-manifest.md",
    ".forge/context/00-meta/conventions.md",
)
REQUIRED_MODE_FILES = (
    ".forge/context/modes/ask.md",
    ".forge/context/modes/plan.md",
    ".forge/context/modes/execute.md",
    ".forge/context/modes/review.md",
    ".forge/context/modes/verify-context.md",
)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="forge-cli-validate-") as tmp:
        scratch = Path(tmp)
        try:
            run_case("version", lambda: case_version())
            run_case("init help", lambda: case_help("init"))
            run_case("update help", lambda: case_help("update"))
            run_case("service init", lambda: case_service_init(scratch / "service"))
            run_case("workspace init", lambda: case_workspace_init(scratch / "workspace"))
            run_case("tools codex", lambda: case_tools_codex(scratch / "tools-codex"))
            run_case("tools codex,claude", lambda: case_tools_codex_claude(scratch / "tools-default"))
            run_case("tools all", lambda: case_tools_all(scratch / "tools-all"))
            run_case("dry-run no writes", lambda: case_dry_run_init(scratch / "dry-run"))
            run_case("update dry-run no runtime", lambda: case_update_no_runtime(scratch / "no-runtime"))
            run_case("update preserves user-owned", lambda: case_update_preserves_user_owned(scratch / "preserve"))
            run_case("update conflicts on modified managed", lambda: case_update_conflict(scratch / "conflict"))
            run_case("adoption dry-run", lambda: case_adoption_dry_run(scratch / "adopt-dry"))
            run_case("adoption yes", lambda: case_adoption_yes(scratch / "adopt-yes"))
            run_case("no source copy", lambda: case_no_source_copy(scratch / "no-source"))
            run_case("no engine-only copy", lambda: case_no_engine_only_copy(scratch / "no-engine"))
            run_case("template hygiene", case_template_hygiene)
        except ValidationError as exc:
            print(f"FAIL: {exc}")
            return 1

    print("PASS: validate_forge_cli")
    return 0


def run_case(name: str, fn) -> None:
    fn()
    print(f"OK: {name}")


def case_version() -> None:
    result = run_cli(["--version"])
    assert_ok(result)
    assert_contains(result.stdout, "forge 0.4.0a0")


def case_help(command: str) -> None:
    result = run_cli([command, "--help"])
    assert_ok(result)
    assert_contains(result.stdout, "usage:")


def case_service_init(target: Path) -> None:
    result = run_cli(["init", "--yes", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_exists(target / "CLAUDE.md")
    assert_exists(target / ".forge" / "forge-install.yaml")
    for rel in REQUIRED_META_FILES + REQUIRED_MODE_FILES:
        assert_exists(target / rel)


def case_workspace_init(target: Path) -> None:
    result = run_cli(["init", "--workspace", "--yes", "--target", str(target)])
    assert_ok(result)
    workspace = target / ".forge" / "workspace.yaml"
    assert_exists(workspace)
    assert_contains(workspace.read_text(encoding="utf-8"), "linked_services: []")


def case_tools_codex(target: Path) -> None:
    result = run_cli(["init", "--yes", "--tools", "codex", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_not_exists(target / "CLAUDE.md")
    assert_not_exists(target / ".github")


def case_tools_codex_claude(target: Path) -> None:
    result = run_cli(["init", "--yes", "--tools", "codex,claude", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_exists(target / "CLAUDE.md")
    assert_not_exists(target / ".github")


def case_tools_all(target: Path) -> None:
    result = run_cli(["init", "--yes", "--tools", "all", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_exists(target / "CLAUDE.md")
    assert_exists(target / ".github" / "copilot-instructions.md")


def case_dry_run_init(target: Path) -> None:
    result = run_cli(["init", "--yes", "--dry-run", "--target", str(target)])
    assert_ok(result)
    assert_not_exists(target / ".forge")


def case_update_no_runtime(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    result = run_cli(["update", "--dry-run", "--target", str(target)], check=False)
    assert_nonzero(result)
    assert_contains(result.stdout, "No Forge runtime detected")


def case_update_preserves_user_owned(target: Path) -> None:
    run_cli(["init", "--yes", "--target", str(target)])
    product = target / ".forge" / "context" / "01-core" / "product.md"
    product.write_text(product.read_text(encoding="utf-8") + "\nuser-owned context\n", encoding="utf-8")
    result = run_cli(["update", "--yes", "--target", str(target)])
    assert_ok(result)
    assert_contains(product.read_text(encoding="utf-8"), "user-owned context")


def case_update_conflict(target: Path) -> None:
    run_cli(["init", "--yes", "--target", str(target)])
    managed = target / ".forge" / "context" / "00-meta" / "conventions.md"
    managed.write_text("LOCAL MOD\n", encoding="utf-8")
    result = run_cli(["update", "--yes", "--target", str(target)], check=False)
    assert_nonzero(result)
    assert_contains(result.stdout, "CONFLICT")


def case_adoption_dry_run(target: Path) -> None:
    seed_manifestless_runtime(target)
    result = run_cli(["update", "--dry-run", "--target", str(target)])
    assert_ok(result)
    assert_contains(result.stdout, "Adoption preview:")
    assert_not_exists(target / ".forge" / "forge-install.yaml")


def case_adoption_yes(target: Path) -> None:
    seed_manifestless_runtime(target)
    result = run_cli(["update", "--yes", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / ".forge" / "forge-install.yaml")


def case_no_source_copy(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    source = target / "app.py"
    source.write_text("print('hello')\n", encoding="utf-8")
    run_cli(["init", "--yes", "--target", str(target)])
    found = list((target / ".forge").rglob("app.py"))
    if found:
        raise ValidationError(f"source file copied into .forge: {found}")


def case_no_engine_only_copy(target: Path) -> None:
    run_cli(["init", "--yes", "--tools", "all", "--target", str(target)])
    for marker in ENGINE_ONLY_MARKERS:
        if list(target.rglob(marker)):
            raise ValidationError(f"engine-only marker copied into target repo: {marker}")


def case_template_hygiene() -> None:
    templates = ROOT / "src" / "forge_context_engine" / "runtime_templates"
    pycache = list(templates.rglob("__pycache__"))
    pyc = list(templates.rglob("*.pyc"))
    if pycache or pyc:
        raise ValidationError(f"template payload contains Python cache artifacts: {pycache or pyc}")
    for rel in REQUIRED_META_FILES + REQUIRED_MODE_FILES:
        assert_exists(templates / "base" / rel)
    forbidden = []
    for marker in ENGINE_ONLY_MARKERS:
        forbidden.extend(templates.rglob(marker))
    if forbidden:
        raise ValidationError(f"engine-only paths packaged into runtime_templates: {forbidden}")


def seed_manifestless_runtime(target: Path) -> None:
    runtime_root = ROOT / "runtime"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(runtime_root / ".forge", target / ".forge", dirs_exist_ok=True)
    shutil.copy2(runtime_root / "AGENTS.md", target / "AGENTS.md")
    shutil.copy2(runtime_root / "CLAUDE.md", target / "CLAUDE.md")
    manifest = target / ".forge" / "forge-install.yaml"
    if manifest.exists():
        manifest.unlink()


def run_cli(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = CLI + args
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=ENV,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise ValidationError(
            f"command failed ({result.returncode}): {' '.join(command)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def assert_ok(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode != 0:
        raise ValidationError(f"expected success, got {result.returncode}\n{result.stdout}\n{result.stderr}")


def assert_nonzero(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode == 0:
        raise ValidationError(f"expected non-zero exit\n{result.stdout}\n{result.stderr}")


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise ValidationError(f"expected path to exist: {path}")


def assert_not_exists(path: Path) -> None:
    if path.exists():
        raise ValidationError(f"expected path not to exist: {path}")


def assert_contains(text: str, expected: str) -> None:
    if expected not in text:
        raise ValidationError(f"expected {expected!r} in output:\n{text}")


class ValidationError(RuntimeError):
    """Validation failure."""


if __name__ == "__main__":
    raise SystemExit(main())
