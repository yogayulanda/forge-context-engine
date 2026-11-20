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
        "template": iter_template_files("base")[MODE],
        "runtime": (ROOT / "runtime" / MODE).read_text(encoding="utf-8"),
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
            self.assertIn(
                "- `run.worker`: `subagent` (default, also when the key is missing), `cli`, or `host`.",
                _section(mode, "inputs"),
                name,
            )

    def test_HostDispatch_HandsEveryRoleToHostTool_AndEndsTurn(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            for phrase in (
                "hand every role to the dispatch tool the host provides",
                "The host defines the tool name and shape; Forge does not.",
                "`run.worker_command` is ignored.",
                "The tester and reviewer are always new workers with fresh context",
                "a worker that ends without a complete report counts as `blocked`",
                "After each dispatch, end the turn.",
            ):
                self.assertIn(phrase, dispatch, name)

    def test_HostResume_IsSameSessionOnly_FreshSessionRestartsFromArtifact(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            for phrase in (
                "the host must resume the same orchestrator session",
                "fix-round count (step 8) stay in that session",
                "artifacts under `.forge/generated/` plus the worker result the host passes in",
                "A fresh session is not a resume: it needs a human re-invocation through `next mode transitions` from the named SDD or ECP.",
            ):
                self.assertIn(phrase, dispatch, name)
            # R7: report stays a trace, no new state file.
            self.assertIn("not resumable workflow state", mode, name)
            self.assertIn("except a `host` resume of the same orchestrator session", mode, name)
            self.assertNotRegex(mode.lower(), r"state file|\.forge/state|session\.json", name)

    def test_HostResume_WorkerResultNeverGrantsHumanAnswerApprovalOrOtherVerdict(self) -> None:
        # Negative/permission boundary (fix round 1): a host resume cannot stand in for a human or another role.
        boundary = (
            "A resume only completes the pending dispatch: the worker result is data for that one role, "
            "never a human answer, Gate 1 approval, or verdict for another role. "
            "After any stop status, continue only through `next mode transitions`."
        )
        spec = (ROOT / "specs/orchestrate.md").read_text(encoding="utf-8")
        spec_bullet = next(line for line in spec.splitlines() if line.startswith("- `host`:"))
        sources = {name: _section(mode, "worker dispatch") for name, mode in _mode_copies().items()}
        sources["spec"] = spec_bullet
        for name, text in sources.items():
            self.assertIn(boundary, text, name)
            self.assertIn("needs a human re-invocation", text, name)
        # The boundary must not leak into stop conditions as a new stop.
        for name, mode in _mode_copies().items():
            self.assertNotIn("Gate 1 approval", _section(mode, "stop conditions"), name)

    def test_HostGuard_IsAdvisory_NotAStopCondition(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            self.assertIn("run `.forge/runtime/hooks/forge_git_guard.py worker` before worker shell commands", dispatch)
            self.assertIn("continue and put `worker git guard not confirmed` in the report `Note`", dispatch)
            stops = _section(mode, "stop conditions")
            self.assertNotIn("git guard not confirmed", stops, name)
            self.assertNotIn("forge_git_guard.py worker", stops, name)

    def test_StopConditions_HostWithoutDispatchTool_AddsExactlyOneHostStop(self) -> None:
        for name, mode in _mode_copies().items():
            stops = _section(mode, "stop conditions")
            host_stops = [line for line in stops.splitlines() if "`run.worker: host`" in line]
            self.assertEqual(host_stops, ["- `run.worker: host` is set but no host dispatch tool is available."], name)

    def test_Regression_CliAndSubagentDispatchAndCliStop_Unchanged(self) -> None:
        for name, mode in _mode_copies().items():
            dispatch = _section(mode, "worker dispatch")
            self.assertIn("The tester and reviewer are always new subagents, never resumed ones.", dispatch)
            self.assertIn("Flags for any specific CLI are not defined by Forge and must be verified by the user.", dispatch)
            self.assertIn("while only the executor uses `cli`; it reports which worker ran each role.", dispatch)
            self.assertIn(
                "- `run.worker: cli` is set but `run.worker_command` is empty or the command fails to start.",
                _section(mode, "stop conditions"),
            )

    def test_Regression_NoNewStatusValue(self) -> None:
        for name, mode in _mode_copies().items():
            self.assertNotIn("host", _section(mode, "status values"), name)


class HostSpecAndValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = (ROOT / "specs/orchestrate.md").read_text(encoding="utf-8")
        self.cases = (ROOT / "validation-cases/orchestrate-gates.md").read_text(encoding="utf-8")

    def test_Spec_StopsHostWithoutDispatchTool(self) -> None:
        self.assertIn("- `run.worker: host` is set but no host dispatch tool is available;", self.spec)

    def test_Spec_ConfigListsHost_AndHostBulletOwnsNoHostCode(self) -> None:
        self.assertIn("worker: subagent      # subagent | cli | host; missing key means subagent", self.spec)
        bullet = next(line for line in self.spec.splitlines() if line.startswith("- `host`:"))
        for phrase in (
            "Forge ships no host code",
            "resumes the same orchestrator session",
            "a fresh session needs a human re-invocation from the named SDD or ECP",
            "`worker git guard not confirmed`",
            "`blocked_by_environment`",
        ):
            self.assertIn(phrase, bullet)

    def test_Spec_OpenItems_DropsForgeStaysUnchanged(self) -> None:
        self.assertNotIn("Forge stays unchanged", self.spec)
        self.assertIn("set `run.worker: host` instead of overriding the mode's `worker dispatch` section", self.spec)

    def test_ValidationCase18_ExpectsBlockedByEnvironment_AndIsInRegressionList(self) -> None:
        self.assertIn(
            "| 18 | `run.worker: host` and no host dispatch tool available | `blocked_by_environment`; no worker started; nothing committed |",
            self.cases,
        )
        self.assertIn("any stop scenario (2 to 8, 11, 12, 18)", self.cases)

    def test_ReleaseNotes_ListHostWorker(self) -> None:
        notes = (ROOT / "docs/release-notes.md").read_text(encoding="utf-8")
        self.assertIn("`run.worker` (`subagent` | `cli` | `host`)", notes)


if __name__ == "__main__":
    unittest.main()
