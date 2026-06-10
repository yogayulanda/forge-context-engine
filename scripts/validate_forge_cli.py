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
sys.dont_write_bytecode = True

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
            run_case("readme release surface", case_readme_release_surface)
            run_case("service init", lambda: case_service_init(scratch / "service"))
            run_case("service init seeds repo context", lambda: case_service_init_seeds_repo_context(scratch / "service-context"))
            run_case("workspace init", lambda: case_workspace_init(scratch / "workspace"))
            run_case("workspace init contract", lambda: case_workspace_init_contract(scratch / "workspace-contract"))
            run_case("tools codex", lambda: case_tools_codex(scratch / "tools-codex"))
            run_case("tools opencode", lambda: case_tools_opencode(scratch / "tools-opencode"))
            run_case("tools codex,claude", lambda: case_tools_codex_claude(scratch / "tools-default"))
            run_case("tools space separated", lambda: case_tools_space_separated(scratch / "tools-space"))
            run_case("tools repeatable flag", lambda: case_tools_repeatable_flag(scratch / "tools-repeat"))
            run_case("tools numeric prompt syntax via flag", lambda: case_tools_numeric_aliases(scratch / "tools-numeric"))
            run_case("tools all", lambda: case_tools_all(scratch / "tools-all"))
            run_case("dry-run no writes", lambda: case_dry_run_init(scratch / "dry-run"))
            run_case("update dry-run no runtime", lambda: case_update_no_runtime(scratch / "no-runtime"))
            run_case("update preserves user-owned", lambda: case_update_preserves_user_owned(scratch / "preserve"))
            run_case("workspace update preserves links", lambda: case_workspace_update_preserves_links(scratch / "workspace-preserve"))
            run_case("update preserves entrypoint user content", lambda: case_update_preserves_entrypoint_user_content(scratch / "preserve-entrypoint"))
            run_case("update conflicts on modified managed", lambda: case_update_conflict(scratch / "conflict"))
            run_case("adoption dry-run", lambda: case_adoption_dry_run(scratch / "adopt-dry"))
            run_case("adoption yes", lambda: case_adoption_yes(scratch / "adopt-yes"))
            run_case("adoption idempotent second dry-run", lambda: case_adoption_idempotent_second_dry_run(scratch / "adopt-idempotent"))
            run_case("legacy config migration backup", lambda: case_legacy_config_migration_backup(scratch / "legacy-config"))
            run_case("wrapper adoption avoids duplicate managed block", lambda: case_wrapper_adoption_avoids_duplicate_managed_block(scratch / "wrapper-adopt"))
            run_case("update tools adds codex to adopted claude repo", lambda: case_update_tools_adds_codex_to_adopted_repo(scratch / "adopt-tools"))
            run_case("update tools all adds copilot", lambda: case_update_tools_all_adds_copilot(scratch / "tools-update-all"))
            run_case("init guidance on initialized repo", lambda: case_init_guidance_on_initialized_repo(scratch / "init-guidance"))
            run_case("update tools dry-run writes nothing", lambda: case_update_tools_dry_run_writes_nothing(scratch / "update-tools-dry"))
            run_case("update summary reporting", lambda: case_update_summary_reporting(scratch / "update-summary"))
            run_case("update checks context contract files", lambda: case_update_checks_context_contract_files(scratch / "context-contract"))
            run_case("entrypoints preserve adapter parity", lambda: case_entrypoints_preserve_adapter_parity(scratch / "adapter-parity"))
            run_case("newline-only managed drift stays unchanged", lambda: case_newline_only_managed_drift_stays_unchanged(scratch / "newline-drift"))
            run_case("ui language id", lambda: case_ui_language_id(scratch / "ui-id"))
            run_case("ui language en default", lambda: case_ui_language_en_default(scratch / "ui-en"))
            run_case("no source copy", lambda: case_no_source_copy(scratch / "no-source"))
            run_case("no engine-only copy", lambda: case_no_engine_only_copy(scratch / "no-engine"))
            run_case("template hygiene", case_template_hygiene)
            run_case("package data includes hidden runtime templates", case_package_data_includes_hidden_runtime_templates)
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
    assert_contains(result.stdout, "forge 1.0.0rc1")


def case_readme_release_surface() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    getting_started = (ROOT / "docs" / "getting-started.md").read_text(encoding="utf-8")
    release_notes = (ROOT / "docs" / "release-notes.md").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    for text in (readme, getting_started):
        assert_contains(text, "uv tool install git+https://github.com/yogayulanda/forge-context-engine.git")
        assert_contains(text, "forge init")
        assert_contains(text, "forge init --workspace")
        assert_contains(text, "forge update")
        assert_contains(text, "forge update --dry-run")

    assert_contains(readme, "## Known Limitations")
    assert_contains(readme, "## Troubleshooting")
    assert_contains(getting_started, "## Troubleshooting And Recovery")
    assert_contains(getting_started, "## Release Checklist")
    assert_contains(readme, "forge update --tools codex,claude")
    assert_contains(readme, "docs/release-notes.md")
    assert_contains(release_notes, "## 1.0.0rc1")
    assert_contains(release_notes, "fresh repo -> `forge init`")
    assert_contains(release_notes, "existing or legacy repo -> `forge update`")

    for entry in ("build/", "dist/", "*.egg-info/", "__pycache__/", "*.pyc", ".venv/", "uv.lock"):
        assert_contains(gitignore, entry)


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
    assert_contains((target / ".forge" / "forge.config.yaml").read_text(encoding="utf-8"), "profile: service")
    for rel in REQUIRED_META_FILES + REQUIRED_MODE_FILES:
        assert_exists(target / rel)


def case_service_init_seeds_repo_context(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    (target / "README.md").write_text("# Billing Service\n\nProcesses invoice events for downstream systems.\n", encoding="utf-8")
    (target / "pyproject.toml").write_text(
        "[project]\nname = \"billing-service\"\nrequires-python = \">=3.11\"\n",
        encoding="utf-8",
    )
    (target / "src").mkdir()
    (target / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")
    (target / "tests").mkdir()
    (target / "tests" / "test_app.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    result = run_cli(["init", "--yes", "--target", str(target)])
    assert_ok(result)

    product = (target / ".forge" / "context" / "01-core" / "product.md").read_text(encoding="utf-8")
    architecture = (target / ".forge" / "context" / "01-core" / "architecture.md").read_text(encoding="utf-8")
    inferred = (target / ".forge" / "context" / "knowledge" / "inferred.md").read_text(encoding="utf-8")
    unknowns = (target / ".forge" / "context" / "knowledge" / "unknowns.md").read_text(encoding="utf-8")
    repo_map = (target / ".forge" / "context" / "repo-map" / "overview.md").read_text(encoding="utf-8")
    system = (target / ".forge" / "context" / "systems" / "service-context" / "system.md").read_text(encoding="utf-8")

    assert_contains(product, "status: inferred")
    assert_contains(product, "Processes invoice events for downstream systems.")
    assert_not_contains(product, "TBD")
    assert_contains(architecture, "single-service application layout")
    assert_contains(inferred, "single-service application layout")
    assert_contains(unknowns, "Repository owner and confirmation authority")
    assert_contains(repo_map, "`src/`")
    assert_contains(system, "system_type: service")

def case_workspace_init(target: Path) -> None:
    result = run_cli(["init", "--workspace", "--yes", "--target", str(target)])
    assert_ok(result)
    workspace = target / ".forge" / "workspace.yaml"
    assert_exists(workspace)
    assert_contains(workspace.read_text(encoding="utf-8"), "linked_services: []")


def case_workspace_init_contract(target: Path) -> None:
    result = run_cli(["init", "--workspace", "--yes", "--target", str(target)])
    assert_ok(result)
    workspace = target / ".forge" / "workspace.yaml"
    manifest = target / ".forge" / "forge-install.yaml"
    config = target / ".forge" / "forge.config.yaml"
    body = workspace.read_text(encoding="utf-8")
    manifest_body = manifest.read_text(encoding="utf-8")
    config_body = config.read_text(encoding="utf-8")
    assert_contains(body, "workspace:")
    assert_contains(body, "default_context_policy: selective")
    assert_contains(body, 'default: "service-first"')
    assert_contains(body, 'cross_repo: "load workspace summary, then only relevant linked service context"')
    assert_contains(body, "Workspace context coordinates services; service context owns repo-specific facts.")
    assert_contains(manifest_body, 'profile: "workspace"')
    assert_contains(manifest_body, "  - .forge/workspace.yaml")
    assert_contains(config_body, "profile: workspace")


def case_tools_codex(target: Path) -> None:
    result = run_cli(["init", "--yes", "--tools", "codex", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_not_exists(target / "CLAUDE.md")
    assert_not_exists(target / ".github")
    assert_not_exists(target / "skills")


def case_tools_opencode(target: Path) -> None:
    result = run_cli(["init", "--yes", "--tools", "opencode", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_exists(target / "skills" / "forge-plan" / "SKILL.md")
    assert_exists(target / "skills" / "forge-review" / "SKILL.md")
    manifest = (target / ".forge" / "forge-install.yaml").read_text(encoding="utf-8")
    assert_contains(manifest, "  - skills/")
    assert_contains(manifest, 'selected_tools:\n  - opencode')
    assert_not_exists(target / "CLAUDE.md")
    assert_not_exists(target / ".github")


def case_tools_codex_claude(target: Path) -> None:
    result = run_cli(["init", "--yes", "--tools", "codex,claude", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_exists(target / "CLAUDE.md")
    assert_exists(target / ".claude" / "commands" / "forge-plan.md")
    assert_not_exists(target / ".github")


def case_tools_space_separated(target: Path) -> None:
    result = run_cli(["init", "--yes", "--tools", "codex", "claude", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_exists(target / "CLAUDE.md")
    assert_exists(target / ".claude" / "commands" / "forge-plan.md")
    assert_not_exists(target / ".github")


def case_tools_repeatable_flag(target: Path) -> None:
    result = run_cli(["init", "--yes", "--tool", "codex", "--tool", "copilot", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_not_exists(target / "CLAUDE.md")
    assert_exists(target / ".github" / "copilot-instructions.md")
    assert_exists(target / ".github" / "prompts" / "forge-plan.prompt.md")


def case_tools_numeric_aliases(target: Path) -> None:
    result = run_cli(["init", "--yes", "--tools", "1+2", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_exists(target / "CLAUDE.md")
    assert_exists(target / ".claude" / "commands" / "forge-plan.md")
    assert_not_exists(target / ".github")


def case_tools_all(target: Path) -> None:
    result = run_cli(["init", "--yes", "--tools", "all", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_exists(target / "CLAUDE.md")
    assert_exists(target / ".claude" / "commands" / "forge-plan.md")
    assert_exists(target / ".github" / "copilot-instructions.md")
    assert_exists(target / ".github" / "prompts" / "forge-plan.prompt.md")
    assert_exists(target / "skills" / "forge-plan" / "SKILL.md")


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


def case_workspace_update_preserves_links(target: Path) -> None:
    run_cli(["init", "--workspace", "--yes", "--target", str(target)])
    workspace = target / ".forge" / "workspace.yaml"
    workspace.write_text(
        workspace.read_text(encoding="utf-8").replace(
            "linked_services: []\n",
            (
                "linked_services:\n"
                "  - name: service-a\n"
                "    path: ../service-a\n"
                "    role: api\n"
                "    context_root: .forge/context\n"
                '    notes: "primary integration path"\n'
            ),
        ),
        encoding="utf-8",
    )
    result = run_cli(["update", "--yes", "--target", str(target)])
    assert_ok(result)
    assert_contains(workspace.read_text(encoding="utf-8"), "name: service-a")


def case_update_preserves_entrypoint_user_content(target: Path) -> None:
    run_cli(["init", "--yes", "--target", str(target)])
    claude = target / "CLAUDE.md"
    claude.write_text("User intro\n\n" + claude.read_text(encoding="utf-8"), encoding="utf-8")
    result = run_cli(["update", "--yes", "--target", str(target)])
    assert_ok(result)
    assert_contains(claude.read_text(encoding="utf-8"), "User intro")


def case_update_conflict(target: Path) -> None:
    run_cli(["init", "--yes", "--target", str(target)])
    managed = target / ".forge" / "context" / "00-meta" / "conventions.md"
    managed.write_text("LOCAL MOD\n", encoding="utf-8")
    result = run_cli(["update", "--yes", "--target", str(target)], check=False)
    assert_nonzero(result)
    assert_contains(result.stdout, "Conflicts: 1")


def case_adoption_dry_run(target: Path) -> None:
    seed_manifestless_runtime(target)
    result = run_cli(["update", "--dry-run", "--target", str(target)])
    assert_ok(result)
    assert_contains(result.stdout, "Mode: adoption")
    assert_not_exists(target / ".forge" / "forge-install.yaml")


def case_adoption_yes(target: Path) -> None:
    seed_manifestless_runtime(target)
    result = run_cli(["update", "--yes", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / ".forge" / "forge-install.yaml")


def case_adoption_idempotent_second_dry_run(target: Path) -> None:
    seed_manifestless_runtime(target)
    run_cli(["update", "--yes", "--target", str(target)])
    manifest_before = (target / ".forge" / "forge-install.yaml").read_text(encoding="utf-8")
    result = run_cli(["update", "--dry-run", "--target", str(target)])
    assert_ok(result)
    assert_contains(result.stdout, "Updated: 0")
    assert_contains(result.stdout, "Conflicts: 0")
    assert_equal((target / ".forge" / "forge-install.yaml").read_text(encoding="utf-8"), manifest_before)


def case_legacy_config_migration_backup(target: Path) -> None:
    seed_manifestless_runtime(target)
    legacy_config = target / ".forge" / "forge.config.yaml"
    legacy_body = (
        'forge_version: "0.2.1"\n'
        "systems:\n"
        "  - name: go-core\n"
        "    type: library\n"
        "loading:\n"
        "  default_mode: implementation\n"
        "runtime:\n"
        "  non_interactive: true\n"
        "size_budget:\n"
        "  core_lines: 200\n"
        "governance:\n"
        "  staleness_days: 90\n"
    )
    legacy_config.write_text(legacy_body, encoding="utf-8")
    dry_run = run_cli(["update", "--dry-run", "--yes", "--target", str(target)])
    assert_ok(dry_run)
    assert_contains(dry_run.stdout, "Legacy config migration:")
    assert_contains(dry_run.stdout, ".forge/forge.config.legacy.yaml")
    assert_contains(dry_run.stdout, ".forge/forge.config.yaml - legacy config migration")

    result = run_cli(["update", "--yes", "--target", str(target)])
    assert_ok(result)
    backup = target / ".forge" / "forge.config.legacy.yaml"
    assert_exists(backup)
    assert_equal(backup.read_text(encoding="utf-8"), legacy_body)
    assert_contains((target / ".forge" / "forge.config.yaml").read_text(encoding="utf-8"), 'forge:\n')
    assert_contains(result.stdout, ".forge/forge.config.yaml - legacy config migration")


def case_wrapper_adoption_avoids_duplicate_managed_block(target: Path) -> None:
    seed_manifestless_runtime(target, tools=("claude",))
    claude = target / "CLAUDE.md"
    claude.write_text(
        "# CLAUDE - Context Adapter\n\n"
        "Thin adapter for AI assistants.\n\n"
        "1. Read `.forge/forge.config.yaml`.\n"
        "2. Read `.forge/context/00-meta/context-manifest.md`.\n"
        "3. Read `.forge/context/00-meta/conventions.md`.\n"
        "4. Follow `.forge/context`.\n",
        encoding="utf-8",
    )
    result = run_cli(["update", "--yes", "--target", str(target)])
    assert_ok(result)
    final = claude.read_text(encoding="utf-8")
    assert_not_contains(final, "<!-- BEGIN FORGE MANAGED BLOCK -->")
    assert_contains(final, ".forge/context/00-meta/context-manifest.md")
    assert_contains(result.stdout, "existing Forge-like wrapper adopted")


def case_update_tools_adds_codex_to_adopted_repo(target: Path) -> None:
    seed_manifestless_runtime(target, tools=("claude",))
    result = run_cli(["update", "--yes", "--tools", "codex,claude", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "AGENTS.md")
    assert_exists(target / "CLAUDE.md")
    manifest = (target / ".forge" / "forge-install.yaml").read_text(encoding="utf-8")
    assert_contains(manifest, "  - codex")
    assert_contains(manifest, "  - claude")


def case_update_tools_all_adds_copilot(target: Path) -> None:
    run_cli(["init", "--yes", "--tools", "claude", "--target", str(target)])
    result = run_cli(["update", "--yes", "--tools", "all", "--target", str(target)])
    assert_ok(result)
    assert_exists(target / "CLAUDE.md")
    assert_exists(target / ".claude" / "commands" / "forge-review.md")
    assert_exists(target / ".github" / "copilot-instructions.md")
    assert_exists(target / ".github" / "prompts" / "forge-review.prompt.md")
    assert_exists(target / "AGENTS.md")
    manifest = (target / ".forge" / "forge-install.yaml").read_text(encoding="utf-8")
    assert_contains(manifest, "  - codex")
    assert_contains(manifest, "  - claude")
    assert_contains(manifest, "  - copilot")


def case_init_guidance_on_initialized_repo(target: Path) -> None:
    run_cli(["init", "--yes", "--target", str(target)])
    result = run_cli(["init", "--tools", "codex", "--target", str(target)], check=False)
    assert_nonzero(result)
    assert_contains(result.stdout, "forge update --tools codex")


def case_update_tools_dry_run_writes_nothing(target: Path) -> None:
    run_cli(["init", "--yes", "--tools", "claude", "--target", str(target)])
    manifest_before = (target / ".forge" / "forge-install.yaml").read_text(encoding="utf-8")
    result = run_cli(["update", "--dry-run", "--tools", "codex,claude", "--target", str(target)])
    assert_ok(result)
    assert_not_exists(target / "AGENTS.md")
    assert_equal((target / ".forge" / "forge-install.yaml").read_text(encoding="utf-8"), manifest_before)


def case_update_summary_reporting(target: Path) -> None:
    run_cli(["init", "--yes", "--target", str(target)])
    result = run_cli(["update", "--dry-run", "--target", str(target)])
    assert_ok(result)
    assert_contains(result.stdout, "Managed files checked:")
    assert_contains(result.stdout, "Unchanged:")
    assert_contains(result.stdout, "Skipped:")
    assert_contains(result.stdout, "Conflicts:")


def case_update_checks_context_contract_files(target: Path) -> None:
    run_cli(["init", "--yes", "--target", str(target)])
    result = run_cli(["update", "--dry-run", "--target", str(target)])
    assert_ok(result)
    assert_contains(result.stdout, ".forge/context/00-meta/conventions.md")
    assert_contains(result.stdout, ".forge/context/modes/ask.md")
    plan = (target / ".forge" / "context" / "modes" / "plan.md").read_text(encoding="utf-8")
    implementation = (target / ".forge" / "context" / "modes" / "implementation.md").read_text(encoding="utf-8")
    review = (target / ".forge" / "context" / "modes" / "review.md").read_text(encoding="utf-8")
    adapter = (target / ".forge" / "adapter.md").read_text(encoding="utf-8")
    planning = (target / ".forge" / "context" / "modes" / "planning.md").read_text(encoding="utf-8")
    testing = (target / ".forge" / "context" / "modes" / "testing.md").read_text(encoding="utf-8")
    assert_contains(plan, "Acceptance Criteria.")
    assert_contains(plan, "Validation Commands.")
    assert_contains(plan, "State assumptions explicitly when the request is ambiguous")
    assert_contains(plan, "`needs_more_context`")
    assert_contains(implementation, "Execution Context Package (ECP) with:")
    assert_contains(implementation, "Exact files likely to change.")
    assert_contains(implementation, "Validation commands.")
    assert_contains(implementation, "Do not edit code, stage, commit, push, merge, deploy, or apply changes.")
    assert_contains(review, "## verdict values")
    assert_contains(review, "Validation Result Assessment.")
    assert_contains(review, "Lifecycle Boundary Assessment.")
    assert_contains(review, "Context Impact.")
    assert_contains(adapter, "Resolve the requested core mode or compatibility/scenario guidance and read only that contract file.")
    assert_contains(adapter, "Do not broad-load `.forge/context`, do not load every mode file by default")
    assert_contains(adapter, "## Adapter parity rules")
    assert_contains(adapter, "Universal Plan, ECP, Execution Report, and Review artifacts stay tool-neutral unless explicitly targeted.")
    assert_contains(adapter, "Target Tool Notes")
    assert_contains(adapter, "## Cross-tool output expectations")
    assert_contains(planning, "compatibility or historical guidance")
    assert_contains(testing, "compatibility, scenario, or historical guidance")


def case_entrypoints_preserve_adapter_parity(target: Path) -> None:
    run_cli(["init", "--yes", "--tools", "all", "--target", str(target)])
    agents = (target / "AGENTS.md").read_text(encoding="utf-8")
    claude = (target / "CLAUDE.md").read_text(encoding="utf-8")
    copilot = (target / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")
    adapter = (target / ".forge" / "adapter.md").read_text(encoding="utf-8")

    for body in (agents, claude, copilot):
        assert_contains(body, "Read `.forge/adapter.md` and follow it.")
        assert_contains(body, ".forge/context")
        assert_not_contains(body, "## Core lifecycle")
        assert_not_contains(body, "## Cross-tool output expectations")
        assert_not_contains(body, "apply_patch")

    assert_contains(agents, "Target Tool Notes")
    assert_contains(claude, "Target Tool Notes")
    assert_contains(copilot, "approved file and scope boundary")
    assert_contains(adapter, "Commit, push, merge, and similar repository publication actions remain human-controlled unless explicitly requested.")


def case_newline_only_managed_drift_stays_unchanged(target: Path) -> None:
    run_cli(["init", "--yes", "--target", str(target)])
    managed = target / ".forge" / "context" / "modes" / "verify-context.md"
    managed.write_text(managed.read_text(encoding="utf-8").rstrip("\n"), encoding="utf-8")
    result = run_cli(["update", "--dry-run", "--target", str(target)])
    assert_ok(result)
    assert_contains(result.stdout, ".forge/context/modes/verify-context.md - already current")
    assert_not_contains(result.stdout, ".forge/context/modes/verify-context.md - managed file modified locally")


def case_ui_language_id(target: Path) -> None:
    run_cli(["init", "--yes", "--target", str(target)])
    config = target / ".forge" / "forge.config.yaml"
    config.write_text(config.read_text(encoding="utf-8").replace("language: en", "language: id"), encoding="utf-8")
    result = run_cli(["update", "--dry-run", "--target", str(target)])
    assert_ok(result)
    assert_contains(result.stdout, "Pemeriksaan file terkelola")
    assert_contains(result.stdout, "Target:")
    assert_contains(result.stdout, ".forge/forge.config.yaml")


def case_ui_language_en_default(target: Path) -> None:
    run_cli(["init", "--yes", "--target", str(target)])
    result = run_cli(["update", "--dry-run", "--target", str(target)])
    assert_ok(result)
    assert_contains(result.stdout, "Managed file checks")
    assert_contains(result.stdout, "Mode: manifest")


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
    manifest = (templates / "base" / ".forge" / "context" / "00-meta" / "context-manifest.md").read_text(encoding="utf-8")
    assert_contains(manifest, "## Daily Default Load")
    assert_contains(manifest, ".forge/adapter.md")
    assert_contains(manifest, "only as a routing index")
    forbidden = []
    for marker in ENGINE_ONLY_MARKERS:
        forbidden.extend(templates.rglob(marker))
    if forbidden:
        raise ValidationError(f"engine-only paths packaged into runtime_templates: {forbidden}")


def case_package_data_includes_hidden_runtime_templates() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    required_entries = (
        'runtime_templates/**/.forge/**/*.md',
        'runtime_templates/**/.forge/**/*.yaml',
        'runtime_templates/**/.forge/**/*.txt',
        'runtime_templates/**/.claude/**/*.md',
        'runtime_templates/**/.github/**/*.md',
    )
    for entry in required_entries:
        assert_contains(pyproject, entry)

def seed_manifestless_runtime(target: Path, tools: tuple[str, ...] = ("codex", "claude")) -> None:
    runtime_root = ROOT / "runtime"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(runtime_root / ".forge", target / ".forge", dirs_exist_ok=True)
    if "codex" in tools:
        shutil.copy2(runtime_root / "AGENTS.md", target / "AGENTS.md")
    if "claude" in tools:
        shutil.copy2(runtime_root / "CLAUDE.md", target / "CLAUDE.md")
        shutil.copytree(runtime_root / "adapters" / "claude" / "commands", target / ".claude" / "commands", dirs_exist_ok=True)
    if "copilot" in tools:
        copilot = target / ".github" / "copilot-instructions.md"
        copilot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(runtime_root / ".github" / "copilot-instructions.md", copilot)
        shutil.copytree(runtime_root / "adapters" / "copilot" / "prompts", target / ".github" / "prompts", dirs_exist_ok=True)
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


def assert_not_contains(text: str, expected: str) -> None:
    if expected in text:
        raise ValidationError(f"did not expect {expected!r} in output:\n{text}")


def assert_equal(left: str, right: str) -> None:
    if left != right:
        raise ValidationError(f"expected values to match\nLEFT:\n{left}\nRIGHT:\n{right}")


class ValidationError(RuntimeError):
    """Validation failure."""


if __name__ == "__main__":
    raise SystemExit(main())
