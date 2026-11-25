"""Tester scenarios for SDD 2026-11-24-host-status-questions not covered by OrchestrateHostInteractionTests."""

from __future__ import annotations

import unittest
from pathlib import Path

from forge_context_engine.runtime_templates import iter_template_files

ROOT = Path(__file__).resolve().parents[1]
MODE = ".forge/runtime/modes/orchestrate.md"


def _section(text: str, heading: str) -> str:
    return text.split(f"\n## {heading}\n", 1)[1].split("\n## ", 1)[0]


class HostQuestionFailurePathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.templates = iter_template_files("base")
        self.modes = {
            "template": self.templates[MODE],
            "runtime": (ROOT / "runtime" / MODE).read_text(encoding="utf-8"),
        }
        self.spec8a = _section((ROOT / "specs/orchestrate.md").read_text(encoding="utf-8"), "8a. Host status and questions")

    def _gate1(self, mode: str) -> str:
        return next(line for line in _section(mode, "behavior").splitlines() if line.startswith("3. Gate 1"))

    def test_Gate1_HasNoRecommendedOrDefaultOption_InModeAndSpec(self) -> None:
        for name, mode in self.modes.items():
            self.assertIn("The Gate 1 question has no recommended or default option", self._gate1(mode), name)
        self.assertIn("`Stop`, and no recommended or default option", self.spec8a)

    def test_Gate1_DefaultPreselectedOrExpiredAnswer_CountsAsTimeout_InSpec(self) -> None:
        self.assertIn(
            "An answer the host picked by default, by preselection, or on expiry counts as a timeout, never as `Approve`.",
            self.spec8a,
        )

    def test_Gate1_TimeoutOrOtherAnswer_RecordedInNote(self) -> None:
        for name, mode in self.modes.items():
            self.assertIn("puts the answer, or `timeout` for a timeout, in the report `Note`", self._gate1(mode), name)

    def test_Gate1_ApproveMatchedBySelectedOption_NeverFreeText(self) -> None:
        phrase = "meaning the selected `Approve <SDD path>` option, never free text that reads like approval"
        for name, mode in self.modes.items():
            self.assertIn(phrase, self._gate1(mode), name)
        self.assertIn(phrase, self.spec8a)

    def test_ClarificationQuestion_NeverShowsApproveOption_NorCountsAsGate1(self) -> None:
        for name, mode in self.modes.items():
            self.assertIn(
                "A clarification question never shows an option labelled `Approve <SDD path>`, and a clarification answer is never Gate 1 approval.",
                _section(mode, "host status and questions"),
                name,
            )
        self.assertIn(
            "Clarification questions never show an `Approve <SDD path>` option, and a clarification answer is never Gate 1 approval.",
            self.spec8a,
        )

    def test_WorkerDone_CoversOnlyOwnStage_RunDoneOnlyFromOrchestratorAtPublish(self) -> None:
        rule = "Your `done` covers only your own stage; only the orchestrator reports run-level `done`, with stage `publish`."
        for role in ("forge-planner", "forge-executor", "forge-tester", "forge-reviewer"):
            rel = f".forge/runtime/agents/{role}.md"
            for name, text in (("template", self.templates[rel]), ("runtime", (ROOT / "runtime" / rel).read_text(encoding="utf-8"))):
                self.assertIn(rule, _section(text, "Host status"), f"{role} {name}")
        for name, mode in self.modes.items():
            self.assertIn("`done` with stage `publish` when the run ends with `mr_opened`", _section(mode, "host status and questions"), name)
        self.assertIn("only the orchestrator reports run-level `done`, with stage `publish`", self.spec8a)

    def test_Spec8a_Timeout_ListsAnswersSoFarInNote(self) -> None:
        self.assertIn("lists the answers received so far in the report `Note`", self.spec8a)

    def test_Timeout_StopsWithStepStatus_AndEndsTurn_NeverContinues(self) -> None:
        for name, mode in self.modes.items():
            host = _section(mode, "host status and questions")
            self.assertIn(
                "stop with `awaiting_clarification` (step 2) or `awaiting_sdd_approval` (step 3), and end the turn",
                host,
                name,
            )
            self.assertIn("list the answers received so far in the report `Note`", host, name)

    def test_Timeout_ResumesOnlyThroughHumanReinvocation(self) -> None:
        for name, mode in self.modes.items():
            nxt = _section(mode, "next mode transitions")
            self.assertIn("`awaiting_clarification` (also after a question-tool timeout) -> human answers", nxt, name)
            self.assertIn(
                "`awaiting_sdd_approval` (also after a question-tool timeout or a non-approve answer) -> human approves the SDD by path",
                nxt,
                name,
            )

    def test_WorkerResult_NeverCountsAsHumanAnswer_InBothChannels(self) -> None:
        for name, mode in self.modes.items():
            self.assertIn("never a human answer, Gate 1 approval, or verdict for another role", _section(mode, "worker dispatch"), name)
            self.assertIn("Only an answer the question tool returns is a human answer.", mode, name)

    def test_Step2b_FreeTextAnswer_RecordedUnderConfirmedDecisions(self) -> None:
        for name, mode in self.modes.items():
            step2b = next(line for line in _section(mode, "behavior").splitlines() if line.startswith("2b."))
            self.assertIn("through the question tool one answer per question; a free-text answer is valid", step2b, name)
            self.assertIn("`Confirmed Decisions`", step2b, name)

    def test_PlannerResume_AcceptsOneAtATimeAndFreeText(self) -> None:
        planner = self.templates[".forge/runtime/agents/forge-planner.md"]
        self.assertIn("answers may arrive in one reply or one at a time through the orchestrator's question tool", planner)
        self.assertIn("return questions to the orchestrator as `blocked_by_decision`", _section(planner, "Host status"))
        for role in ("forge-executor", "forge-tester", "forge-reviewer"):
            section = _section(self.templates[f".forge/runtime/agents/{role}.md"], "Host status")
            self.assertIn("return questions to the orchestrator as a blocking unknown", section, role)

    def test_Spec8a_TimeoutAndFreeTextAtGate1_NeverApprove(self) -> None:
        section = _section((ROOT / "specs/orchestrate.md").read_text(encoding="utf-8"), "8a. Host status and questions")
        for phrase in (
            "Free text or a timeout stops with `awaiting_sdd_approval`",
            "reports `waiting_for_human` with the open question",
            "worker results and other host text never are",
            "never use a question tool",
        ):
            self.assertIn(phrase, section)


if __name__ == "__main__":
    unittest.main()
