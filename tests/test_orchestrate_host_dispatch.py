"""Tester scenarios for `run.worker: host` (SDD 2026-11-20-worker-dispatch-host)."""

from __future__ import annotations

import io
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from forge_context_engine.runtime_ops import run_init
from forge_context_engine.runtime_templates import iter_template_files

ROOT = Path(__file__).resolve().parents[1]
MODE = ".forge/runtime/modes/orchestrate.md"
CONFIG = ".forge/forge.config.yaml"
HOST_COMMENT = (
    "  # forge-orchestrate worker: subagent (host tool subagents), cli (external agent CLI), "
    "or host (dispatch tool provided by a host that runs the orchestrator).\n"
)


def _section(text: str, heading: str) -> str:
    return text.split(f"\n## {heading}\n", 1)[1].split("\n## ", 1)[0]


def _mode_copies() -> dict[str, str]:
    return {
        "orchestrate.md (template)": iter_template_files("base")[MODE],
        "orchestrate.md (runtime/)": (ROOT / "runtime" / MODE).read_text(encoding="utf-8"),
    }


class HostConfigIntegrationTests(unittest.TestCase):
    def _init_config(self, tools: tuple[str, ...]) -> str:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            (target / "README.md").write_text("# Demo\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                status = run_init(target=target, profile="service", selected_tools=tools, dry_run=False, assume_yes=True)
            self.assertEqual(status, 0)
            return (target / CONFIG).read_text(encoding="utf-8")

    def test_ForgeInit_WritesConfigNamingHost_AndDefaultsToSubagent(self) -> None:
        for tools in (("claude",), ("codex",)):
            config = self._init_config(tools)
            self.assertIn(HOST_COMMENT + "  worker: subagent\n", config, tools)

    def test_ForgeInit_ConfigHasExactlyOneWorkerKey(self) -> None:
        config = self._init_config(("claude",))
        self.assertEqual(len(re.findall(r"^  worker:", config, flags=re.MULTILINE)), 1)

    def test_ForgeInitDryRun_WritesNoConfig(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            with redirect_stdout(io.StringIO()):
                run_init(target=target, profile="service", selected_tools=("claude",), dry_run=True, assume_yes=True)
            self.assertFalse((target / CONFIG).exists())

    def test_ConfigTemplate_RuntimeCopy_AndInitBuilder_ShareHostComment(self) -> None:
        template = iter_template_files("base")[CONFIG]
        runtime_copy = (ROOT / "runtime" / CONFIG).read_text(encoding="utf-8")
        self.assertEqual(runtime_copy, template)
        self.assertIn(HOST_COMMENT, template)
        self.assertIn(HOST_COMMENT + "  worker: subagent\n", template)


class HostModeContractTests(unittest.TestCase):
    def test_Inputs_ListHostAsWorkerValue_WithSubagentDefault(self) -> None:
        for name, mode in _mode_copies().items():
            line = next(l for l in _section(mode, "inputs").splitlines() if l.startswith("- `run.worker`:"))
            for token in ("`subagent` (default", "when the key is missing", "`cli`", "`host`"):
                self.assertIn(token, line, name)

    def test_HostDispatch_HandsEveryRoleToHostTool_AndEndsTurn(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            for token in (
                "hand every role to the dispatch tool the host provides",
                "The host defines the tool name and shape",
                "`run.worker_command` is ignored",
                "always new workers with fresh context",
                "counts as `blocked`",
                "After each dispatch, end the turn",
            ):
                self.assertIn(token, dispatch, name)

    def test_HostResume_IsSameSessionOnly_FreshSessionRestartsFromArtifact(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            for token in (
                "the host must resume the same orchestrator session",
                "fix-round count (step 8) stay in that session",
                "plus the worker result the host passes in",
                "A fresh session is not a resume",
                "human re-invocation through `next mode transitions`",
            ):
                self.assertIn(token, dispatch, name)
            # R7: report stays a trace, no new state file.
            self.assertIn("not resumable workflow state", mode, name)
            self.assertIn("except a `host` resume of the same orchestrator session", mode, name)
            self.assertNotRegex(mode.lower(), r"state file|\.forge/state|session\.json", name)

    def test_HostResume_WorkerResultNeverGrantsHumanAnswerApprovalOrOtherVerdict(self) -> None:
        # Negative/permission boundary (fix round 1): a host resume cannot stand in for a human or another role.
        spec = (ROOT / "specs/orchestrate.md").read_text(encoding="utf-8")
        sources = {name: _section(mode, "worker dispatch") for name, mode in _mode_copies().items()}
        sources["specs/orchestrate.md (`host` bullet)"] = next(
            line for line in spec.splitlines() if line.startswith("- `host`:")
        )
        for name, text in sources.items():
            for token in (
                "A resume only completes the pending dispatch",
                "the worker result is data for that one role",
                "never a human answer, Gate 1 approval, or verdict for another role",
                "continue only through `next mode transitions`",
                "needs a human re-invocation",
            ):
                self.assertIn(token, text, name)
        # The boundary adds no stop: stop lines naming a host or a resume are exactly these two.
        for name, mode in _mode_copies().items():
            stops = [
                line
                for line in _section(mode, "stop conditions").splitlines()
                if "host" in line or "resume" in line.lower()
            ]
            self.assertEqual(len(stops), 2, name)
            self.assertTrue(any("no host dispatch tool is available" in line for line in stops), name)
            self.assertTrue(any("resume in place (step 1a) does not apply" in line for line in stops), name)

    def test_HostGuard_IsAdvisory_NotAStopCondition(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            bullet = next(line for line in dispatch.splitlines() if line.startswith("- Git guard under `host`:"))
            for token in (
                "`.forge/runtime/hooks/forge_git_guard.py worker`",
                "`worker git guard not confirmed`",
                "role `orchestrator`",
                "`.forge/runtime/meta/git-guard-rules.json`",
                "`orchestrator git guard not confirmed`",
            ):
                self.assertIn(token, bullet, name)
            stops = _section(mode, "stop conditions")
            for token in ("git guard not confirmed", "forge_git_guard.py worker", "git-guard-rules.json"):
                self.assertNotIn(token, stops, name)

    def test_Preflight_NonClaudeHost_OrchestratorGuardIsAdvisory(self) -> None:
        for name, mode in _mode_copies().items():
            step1 = next(line for line in _section(mode, "behavior").splitlines() if line.startswith("1. Preflight"))
            for token in (
                "when the host is Claude Code",
                "`git guard hook missing`",
                "Otherwise, the host should enforce role `orchestrator`",
                "`.forge/runtime/meta/git-guard-rules.json`",
                "`orchestrator git guard not confirmed`",
            ):
                self.assertIn(token, step1, name)
            stops = _section(mode, "stop conditions")
            self.assertNotIn("orchestrator git guard", stops, name)
            self.assertNotIn("git-guard-rules.json", stops, name)

    def test_StopConditions_HostWithoutDispatchTool_AddsExactlyOneHostStop(self) -> None:
        for name, mode in _mode_copies().items():
            stops = _section(mode, "stop conditions")
            host_stops = [line for line in stops.splitlines() if "`run.worker: host`" in line]
            self.assertEqual(len(host_stops), 1, name)
            self.assertIn("no host dispatch tool is available", host_stops[0], name)

    def test_Regression_CliAndSubagentDispatchAndCliStop_Unchanged(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            for token in (
                "always new subagents, never resumed ones",
                "not defined by Forge and must be verified by the user",
                "while only the executor uses `cli`",
                "reports which worker ran each role",
            ):
                self.assertIn(token, dispatch, name)
            self.assertIn(
                "`run.worker: cli` is set but `run.worker_command` is empty",
                _section(mode, "stop conditions"),
                name,
            )

    def test_Regression_NoNewStatusValue(self) -> None:
        for name, mode in _mode_copies().items():
            self.assertNotIn("host", _section(mode, "status values"), name)


class HostSpecAndValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = (ROOT / "specs/orchestrate.md").read_text(encoding="utf-8")
        self.cases = (ROOT / "validation-cases/orchestrate-gates.md").read_text(encoding="utf-8")

    def test_Spec_StopsHostWithoutDispatchTool(self) -> None:
        stops = _section(self.spec, "6. Stop conditions")
        line = next(line for line in stops.splitlines() if line.startswith("- `run.worker: host`"))
        self.assertIn("no host dispatch tool is available", line)

    def test_Spec_ConfigListsHost_AndHostBulletOwnsNoHostCode(self) -> None:
        self.assertIn("# subagent | cli | host; missing key means subagent", self.spec)
        bullet = next(line for line in self.spec.splitlines() if line.startswith("- `host`:"))
        for token in (
            "Forge ships no host code",
            "resumes the same orchestrator session",
            "a fresh session needs a human re-invocation",
            "`worker git guard not confirmed`",
            "`orchestrator git guard not confirmed`",
            "`blocked_by_environment`",
        ):
            self.assertIn(token, bullet)

    def test_Spec_GitGuard_RulesFileCoversOrchestratorRoleForOtherHosts(self) -> None:
        section = _section(self.spec, "6a. Git guard")
        for token in ("may read the same file", "role `worker` and role `orchestrator`", "`.forge/runtime/meta/git-guard-rules.json`"):
            self.assertIn(token, section)

    def test_Spec_OpenItems_DropsForgeStaysUnchanged(self) -> None:
        self.assertNotIn("Forge stays unchanged", self.spec)
        self.assertIn("instead of overriding the mode's `worker dispatch` section", self.spec)

    def test_ValidationCase18_ExpectsBlockedByEnvironment_AndIsInRegressionList(self) -> None:
        row = next(line for line in self.cases.splitlines() if line.startswith("| 18 |"))
        for token in ("`run.worker: host`", "no host dispatch tool", "`blocked_by_environment`", "nothing committed"):
            self.assertIn(token, row)
        self.assertRegex(self.cases, r"any stop scenario \([^)]*\b18\b")

    def test_ReleaseNotes_ListHostWorker(self) -> None:
        notes = (ROOT / "docs/release-notes.md").read_text(encoding="utf-8")
        self.assertIn("`run.worker` (`subagent` | `cli` | `host`)", notes)


if __name__ == "__main__":
    unittest.main()
