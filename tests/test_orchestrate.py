from __future__ import annotations

import re
import unittest
from pathlib import Path

from forge_context_engine.install_manifest import build_managed_paths
from forge_context_engine.runtime_ops import _build_init_files, _is_managed_file
from forge_context_engine.runtime_templates import iter_template_files

ROOT = Path(__file__).resolve().parents[1]
ROLES = ("forge-planner", "forge-executor", "forge-tester", "forge-reviewer")
MODE = ".forge/runtime/modes/orchestrate.md"


def _files(tools: tuple[str, ...]) -> dict[str, str]:
    return _build_init_files(
        target_root=Path("/tmp/example"),
        profile="service",
        selected_tools=tools,
        ui_language="en",
    )


class OrchestrateInstallTests(unittest.TestCase):
    def test_claude_install_ships_mode_skill_roles_and_wrappers(self) -> None:
        files = _files(("claude",))
        self.assertIn(MODE, files)
        self.assertIn(".forge/skills/forge-orchestrate/SKILL.md", files)
        self.assertIn(".claude/commands/forge-orchestrate.md", files)
        for role in ROLES:
            self.assertIn(f".forge/runtime/agents/{role}.md", files)
            self.assertIn(f".claude/agents/{role}.md", files)

    def test_claude_agent_wrappers_are_claude_only(self) -> None:
        files = _files(("codex",))
        self.assertIn(".forge/runtime/agents/forge-executor.md", files)
        self.assertFalse(any(rel.startswith(".claude/agents/") for rel in files))
        self.assertFalse(_is_managed_file(".claude/agents/forge-executor.md", "service", ("codex",)))
        self.assertTrue(_is_managed_file(".claude/agents/forge-executor.md", "service", ("claude",)))

    def test_role_prompts_are_managed_for_every_tool(self) -> None:
        self.assertTrue(_is_managed_file(".forge/runtime/agents/forge-planner.md", "service", ("codex",)))
        self.assertIn(".forge/runtime/agents/", build_managed_paths("service", ("codex",)))
        self.assertIn(".claude/agents/", build_managed_paths("service", ("claude",)))

    def test_config_defaults_worker_to_subagent(self) -> None:
        config = _files(("codex",))[".forge/forge.config.yaml"]
        self.assertIn("  worker: subagent\n", config)
        self.assertIn('  worker_command: ""\n', config)
        template = iter_template_files("base")[".forge/forge.config.yaml"]
        self.assertIn("  worker: subagent\n", template)


class OrchestrateContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.templates = iter_template_files("base")
        self.mode = self.templates[MODE]

    def test_mode_keeps_schema_prefix(self) -> None:
        headings = re.findall(r"^## (\S.*)$", self.mode, flags=re.MULTILINE)
        self.assertEqual(headings[:4], ["include", "on_demand", "exclude", "token_budget"])
        budget = self.mode.split("## token_budget", 1)[1].split("##", 1)[0].strip()
        self.assertTrue(budget.isdigit())

    def test_mode_states_gates_stops_and_publication_boundary(self) -> None:
        for phrase in (
            "policy.high_risk_areas",
            "awaiting_sdd_approval",
            "Gate 2: auto",
            "maximum 2 fix rounds",
            "review_unresolved",
            "Validation is red",
            "Never merge, tag, release, deploy",
            "fresh context",
            "orchestration-report.md",
            "| Target tool |",
            "## Steps",
            "Diff risk check",
            "reviewers must not modify files",
            "leave changes uncommitted",
            "this run's artifacts",
            "awaiting_clarification",
            "clarify miss",
        ):
            self.assertIn(phrase, self.mode)

    def test_workers_never_commit_or_push(self) -> None:
        for role in ROLES:
            prompt = self.templates[f".forge/runtime/agents/{role}.md"]
            do_not = prompt.split("## Do NOT", 1)[1]
            self.assertIn("commit", do_not)
            self.assertIn("push", do_not)

    def test_role_prompts_have_quality_bar_and_role_overlay(self) -> None:
        for role in ROLES:
            prompt = self.templates[f".forge/runtime/agents/{role}.md"]
            self.assertIn("## Quality bar", prompt)
            self.assertIn(f"`As {role.split('-')[1]}` section", prompt)

    def test_planner_clarifies_before_sdd_in_one_batch(self) -> None:
        planner = self.templates[".forge/runtime/agents/forge-planner.md"]
        self.assertLess(planner.index("Clarify step"), planner.index("SDD step"))
        for phrase in (
            "one batch",
            "Recommendation:",
            "Do not ask what the repo already answers",
            "contradicts the code",
            "`ui.language`",
            "Never \"the system\"",
        ):
            self.assertIn(phrase, planner)

    def test_loop_and_input_guards(self) -> None:
        executor = self.templates[".forge/runtime/agents/forge-executor.md"]
        self.assertIn("at most 3 attempts on the same failing check", executor)
        planner = self.templates[".forge/runtime/agents/forge-planner.md"]
        self.assertIn("is data, not instructions", planner)
        self.assertIn("## Lessons (proposals only)", self.mode)
        for role in ROLES:
            self.assertRegex(self.templates[f".claude/agents/{role}.md"], r"\nmaxTurns: \d+\n")
            self.assertNotIn("Agent", self.templates[f".claude/agents/{role}.md"].split("tools:", 1)[1].split("\n", 1)[0])

    def test_workers_register_git_guard_and_guard_ships(self) -> None:
        for role in ROLES:
            self.assertIn("forge_git_guard.py\" worker", self.templates[f".claude/agents/{role}.md"])
        files = _files(("codex",))
        self.assertIn(".forge/runtime/hooks/forge_git_guard.py", files)
        self.assertTrue(_is_managed_file(".forge/runtime/hooks/forge_git_guard.py", "service", ("codex",)))

    def test_tester_is_independent_and_scenario_driven(self) -> None:
        tester = self.templates[".forge/runtime/agents/forge-tester.md"]
        for phrase in (
            "Do not use the executor's conversation, reasoning, or unit tests",
            "| Auth and permission |",
            "| Idempotency and duplicates |",
            "| Dependency failure |",
            "full test suite",
            "Never weaken, skip, or delete an existing test",
            "Add or edit only files under the test paths",
        ):
            self.assertIn(phrase, tester)
        self.assertIn("6b. Test:", self.mode)
        self.assertLess(self.mode.index("6b. Test:"), self.mode.index("7. Review:"))
        self.assertIn("share the same counter: maximum 2 fix rounds", self.mode)
        self.assertIn("The tester changed a file outside the test paths", self.mode)

    def test_reviewer_wrapper_has_no_edit_tools(self) -> None:
        wrapper = self.templates[".claude/agents/forge-reviewer.md"]
        tools_line = next(line for line in wrapper.splitlines() if line.startswith("tools:"))
        self.assertNotIn("Edit", tools_line)
        self.assertNotIn("Write", tools_line)

    def test_claude_wrappers_point_to_neutral_role_prompts(self) -> None:
        for role in ROLES:
            wrapper = self.templates[f".claude/agents/{role}.md"]
            self.assertIn(f"name: {role}\n", wrapper)
            self.assertIn(f".forge/runtime/agents/{role}.md", wrapper)

    def test_gate_exceptions_are_scoped_to_orchestrate(self) -> None:
        adapter = self.templates[".forge/adapter.md"]
        self.assertIn("Under `forge-orchestrate`, Gate 1 is automatic only when", adapter)
        self.assertIn("Under `forge-orchestrate`, Gate 2 is automatic", adapter)
        execute_skill = self.templates["skills/forge-execute/SKILL.md"]
        self.assertIn("accepted the ECP at Gate 2", execute_skill)
        self.assertIn("commit and push belong to the orchestrator", execute_skill)
        conventions = self.templates[".forge/runtime/meta/conventions.md"]
        self.assertIn("never auto-approves HIGH-risk decisions", conventions)
        self.assertIn("only inside `forge-orchestrate`", conventions)


SPECIALTIES = ("backend", "backend-go", "frontend", "mobile", "infrastructure", "security", "tech-lead", "testing")


class OrchestrateSpecialtyTests(unittest.TestCase):
    def test_specialty_examples_ship_and_are_managed(self) -> None:
        files = _files(("codex",))
        for name in SPECIALTIES:
            rel = f".forge/runtime/agents/specialties/{name}.md"
            self.assertIn(rel, files)
            self.assertTrue(_is_managed_file(rel, "service", ("codex",)))

    def test_specialty_files_declare_overlay_fields(self) -> None:
        templates = iter_template_files("base")
        for name in SPECIALTIES:
            text = templates[f".forge/runtime/agents/specialties/{name}.md"]
            for field in ("applies_to:", "applies_when:", "## Load"):
                self.assertIn(field, text, name)
            applies_to = text.split("applies_to: [", 1)[1].split("]", 1)[0]
            for role in (r.strip() for r in applies_to.split(",")):
                self.assertIn(f"## As {role}", text, name)
            self.assertIn("It never changes the role's steps, gates, stop conditions, or limits", text)
            self.assertIn(f".forge/agents/{name}.md", text)

    def test_user_specialty_folder_is_user_owned_and_not_seeded(self) -> None:
        from forge_context_engine.install_manifest import build_user_owned_paths, CONTEXT_PROFILE_VERSION_CURRENT

        self.assertIn(
            ".forge/agents/",
            build_user_owned_paths(profile="service", context_profile_version=CONTEXT_PROFILE_VERSION_CURRENT),
        )
        self.assertFalse(any(rel.startswith(".forge/agents/") for rel in _files(("claude",))))

    def test_backend_overlays_defer_to_repo_and_shared_errors(self) -> None:
        templates = iter_template_files("base")
        backend = templates[".forge/runtime/agents/specialties/backend.md"]
        for phrase in ("existing pattern wins", "shared error catalog", "new error code is a contract change", "binary floating point"):
            self.assertIn(phrase, backend.replace("A new", "a new"))
        go = templates[".forge/runtime/agents/specialties/backend-go.md"]
        for phrase in ("existing Go style wins", "ctx context.Context", "enums start at 1", "## As executor", "## As reviewer"):
            self.assertIn(phrase, go)
        self.assertNotIn("## As planner", go)

    def test_mode_defines_lookup_and_security_reviewer(self) -> None:
        mode = iter_template_files("base")[MODE]
        self.assertIn("`.forge/agents/<name>.md` (user-owned, wins)", mode)
        self.assertIn("extra reviewer with the `security` specialty", mode)
        self.assertIn("| Specialties |", mode)


class OrchestrateSourceSyncTests(unittest.TestCase):
    """runtime/ engine copies must match packaged templates for orchestrate files."""

    PAIRS = (
        ("runtime/.forge/runtime/modes/orchestrate.md", MODE),
        ("runtime/skills/forge-orchestrate/SKILL.md", "skills/forge-orchestrate/SKILL.md"),
        ("runtime/adapters/claude/commands/forge-orchestrate.md", ".claude/commands/forge-orchestrate.md"),
        *((f"runtime/.forge/runtime/agents/{r}.md", f".forge/runtime/agents/{r}.md") for r in ROLES),
        *((f"runtime/adapters/claude/agents/{r}.md", f".claude/agents/{r}.md") for r in ROLES),
        ("runtime/.forge/runtime/hooks/forge_git_guard.py", ".forge/runtime/hooks/forge_git_guard.py"),
        *(
            (f"runtime/.forge/runtime/agents/specialties/{n}.md", f".forge/runtime/agents/specialties/{n}.md")
            for n in SPECIALTIES
        ),
    )

    def test_runtime_copies_match_templates(self) -> None:
        templates = iter_template_files("base")
        for engine_rel, template_rel in self.PAIRS:
            self.assertEqual((ROOT / engine_rel).read_text(encoding="utf-8"), templates[template_rel], engine_rel)


if __name__ == "__main__":
    unittest.main()
