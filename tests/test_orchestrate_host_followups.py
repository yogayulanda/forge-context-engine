"""Tester scenarios for issue #18 (SDD 2026-11-24-orchestrate-host-followups): install level and failure paths."""

from __future__ import annotations

import ast
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import test_orchestrate
import test_orchestrate_host_dispatch as host_dispatch
from forge_context_engine.runtime_ops import run_init
from forge_context_engine.runtime_templates import iter_template_files

ROOT = Path(__file__).resolve().parents[1]
MODE = ".forge/runtime/modes/orchestrate.md"
PLANNER = ".forge/runtime/agents/forge-planner.md"
TESTING = ".forge/runtime/agents/specialties/testing.md"
PLAN_PATH = ".forge/generated/plans/YYYY-MM-DD-<slug>-plan.md"


def _step(text: str, prefix: str) -> str:
    return next(line for line in text.splitlines() if line.startswith(prefix))


def _run(case: unittest.TestCase) -> unittest.TestResult:
    result = unittest.TestResult()
    case.run(result)
    return result


class ForgeInitInstallsFollowupsTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.target = Path(tmp.name)
        (self.target / "README.md").write_text("# Demo\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            status = run_init(target=self.target, profile="service", selected_tools=("codex",), dry_run=False, assume_yes=True)
        self.assertEqual(status, 0)

    def _read(self, rel: str) -> str:
        return (self.target / rel).read_text(encoding="utf-8")

    def test_ForgeInit_InstalledMode_Step1HasNonClaudeOrchestratorGuardNote(self) -> None:
        step1 = _step(self._read(MODE), "1. Preflight")
        for token in ("role `orchestrator`", "git-guard-rules.json", "`orchestrator git guard not confirmed`", "`git guard hook missing`"):
            self.assertIn(token, step1, "installed orchestrate.md")

    def test_ForgeInit_InstalledMode_NamesOnePlanPathAndPlanStatuses(self) -> None:
        mode = self._read(MODE)
        step2 = _step(mode, "2. Clarify")
        for token in (PLAN_PATH, "`ready_for_implementation`", "`blocked_by_decision`", "`needs_more_context`"):
            self.assertIn(token, step2, "installed orchestrate.md step 2")
        self.assertIn("SDD -> .forge/generated/plans/<YYYY-MM-DD>-<slug>-plan.md", mode, "installed orchestrate.md report")

    def test_ForgeInit_InstalledPlannerAndOverlay_CarryNewLines(self) -> None:
        self.assertIn(PLAN_PATH + "` with one `plan` mode status", self._read(PLANNER), "installed forge-planner.md")
        self.assertIn("Assert key tokens, not whole sentences or prose rows.", self._read(TESTING), "installed testing.md")

    def test_ForgeInit_NoInstalledFileNamesSddFileOrDraftStatus(self) -> None:
        for path in (self.target / ".forge").rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for token in ("-sdd.md", "`draft`", "status: draft"):
                self.assertNotIn(token, text, str(path.relative_to(self.target)))


class ShippedRuntimeHasOneSddNameTests(unittest.TestCase):
    def test_NoShippedRuntimeFileNamesSddFileOrDraftStatus(self) -> None:
        sources = {f"{rel} (template)": text for rel, text in iter_template_files("base").items()}
        for path in (ROOT / "runtime").rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".json", ".toml"}:
                sources[f"{path.relative_to(ROOT)}"] = path.read_text(encoding="utf-8")
        sources["specs/orchestrate.md"] = (ROOT / "specs/orchestrate.md").read_text(encoding="utf-8")
        for name, text in sources.items():
            for token in ("-sdd.md", "`draft`", "status: draft"):
                self.assertNotIn(token, text, name)

    def test_RuntimePlannerCopy_NamesPlanPathWithPlanStatus(self) -> None:
        text = (ROOT / "runtime" / PLANNER).read_text(encoding="utf-8")
        self.assertIn(PLAN_PATH + "` with one `plan` mode status", text, "forge-planner.md (runtime/)")


class FailurePathTests(unittest.TestCase):
    """AC4: the shipped checks fail on a broken copy and name it."""

    def _broken_copies(self, runtime_mode: str) -> dict[str, str]:
        return {"orchestrate.md (template)": iter_template_files("base")[MODE], "orchestrate.md (runtime/)": runtime_mode}

    def test_SddNameCheck_Fails_WhenTemplateModeSaysSddFile(self) -> None:
        real = iter_template_files("base")
        broken = dict(real)
        broken[MODE] = real[MODE].replace("-plan.md", "-sdd.md")
        with mock.patch.object(test_orchestrate, "iter_template_files", return_value=broken):
            result = _run(test_orchestrate.OrchestrateContractTests("test_sdd_path_and_status_are_one_set"))
        self.assertEqual(len(result.failures), 1, result.errors)
        self.assertIn("orchestrate.md (template)", result.failures[0][1])

    def test_StopLinesCheck_Fails_WhenAnotherResumeStopIsAdded(self) -> None:
        mode = (ROOT / "runtime" / MODE).read_text(encoding="utf-8")
        broken = mode.replace("\n## stop conditions\n", "\n## stop conditions\n- A host resume arrives without a worker result.\n", 1)
        self.assertNotEqual(broken, mode)
        with mock.patch.object(host_dispatch, "_mode_copies", return_value=self._broken_copies(broken)):
            result = _run(host_dispatch.HostModeContractTests("test_HostResume_WorkerResultNeverGrantsHumanAnswerApprovalOrOtherVerdict"))
        self.assertEqual(len(result.failures), 1, result.errors)
        self.assertIn("orchestrate.md (runtime/)", result.failures[0][1])

    def test_GuardCheck_FailureMessage_NamesRuntimeCopy(self) -> None:
        mode = (ROOT / "runtime" / MODE).read_text(encoding="utf-8")
        broken = mode.replace("`orchestrator git guard not confirmed`", "`guard note`")
        with mock.patch.object(host_dispatch, "_mode_copies", return_value=self._broken_copies(broken)):
            for test in ("test_HostGuard_IsAdvisory_NotAStopCondition", "test_Preflight_NonClaudeHost_OrchestratorGuardIsAdvisory"):
                result = _run(host_dispatch.HostModeContractTests(test))
                self.assertEqual(len(result.failures), 1, test)
                self.assertIn("orchestrate.md (runtime/)", result.failures[0][1], test)


class HostDispatchTestShapeTests(unittest.TestCase):
    """AC5: key-token asserts, no dead assertNotIn, copy-loop asserts carry a message."""

    def setUp(self) -> None:
        self.tree = ast.parse((ROOT / "tests/test_orchestrate_host_dispatch.py").read_text(encoding="utf-8"))

    def _assert_calls(self, node: ast.AST) -> list[ast.Call]:
        return [
            n for n in ast.walk(node)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr.startswith("assert")
        ]

    def test_NoAssertedLiteralSpansTwoSentences_AndNoGate1Phrase(self) -> None:
        for call in self._assert_calls(self.tree):
            for const in (n for n in ast.walk(call) if isinstance(n, ast.Constant) and isinstance(n.value, str)):
                self.assertNotIn(". ", const.value, f"line {call.lineno}")
                self.assertNotEqual(const.value, "Gate 1 approval", f"line {call.lineno}")

    def test_EveryAssertInCopyLoop_PassesCopyName(self) -> None:
        loops = [
            n for n in ast.walk(self.tree)
            if isinstance(n, ast.For) and isinstance(n.iter, ast.Call) and "_mode_copies" in ast.unparse(n.iter)
        ]
        self.assertTrue(loops)
        for loop in loops:
            for call in self._assert_calls(loop):
                self.assertIn("name", [ast.unparse(a) for a in call.args[1:]], f"line {call.lineno}")


if __name__ == "__main__":
    unittest.main()
