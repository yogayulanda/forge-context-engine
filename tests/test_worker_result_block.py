"""Issue #13: FORGE_RESULT contract checks the executor's tests do not cover.

The block has no parser (SDD non-goal), so `_read_result` below is a test-side reader
built only from the rules the mode states; its allowed values are parsed from the mode.
"""

from __future__ import annotations

import unittest

from forge_context_engine.runtime_templates import iter_template_files

MODE = ".forge/runtime/modes/orchestrate.md"
FIELDS = ("role", "status", "verdict", "artifact", "changed_files", "note")
# SDD A1: allowed status / verdict values per role.
ROLE_VALUES = {
    "planner": ({"done", "blocked", "blocked_by_decision"}, {"n/a"}),
    "executor": ({"done", "blocked", "blocked_by_environment"}, {"n/a"}),
    "tester": ({"done", "blocked", "blocked_by_environment"}, {"pass", "fail", "n/a"}),
    "reviewer": ({"done", "blocked"}, {"accept", "request_changes", "needs_more_validation", "n/a"}),
}


def _section(text: str, heading: str) -> str:
    return text.split(f"\n{heading}\n", 1)[1].split("\n## ", 1)[0]


def _block(text: str) -> dict[str, str]:
    body = text.split("\nFORGE_RESULT\n", 1)[1].split("\nEND_FORGE_RESULT", 1)[0]
    return dict(line.split(": ", 1) for line in body.splitlines())


def _choices(value: str) -> set[str]:
    return set(value.split(" | "))


def _read_result(output: str, allowed: dict[str, set[str]]) -> dict[str, str] | str:
    """Mode rules: last text, at most 1000 chars, six fields in order, listed values; else `blocked`."""
    end = "END_FORGE_RESULT"
    stripped = output.rstrip()
    if not stripped.endswith(end):
        return "blocked"  # missing block, or block not the last text
    start = stripped.rfind("FORGE_RESULT\n", 0, len(stripped) - len(end))
    if start < 0:
        return "blocked"
    block = stripped[start:]
    if len(block) > 1000:
        return "blocked"
    lines = block.splitlines()[1:-1]
    if [line.split(":", 1)[0] for line in lines] != list(FIELDS):
        return "blocked"
    result = dict(line.split(": ", 1) for line in lines)
    for field in ("role", "status", "verdict"):
        if result[field] not in allowed[field]:
            return "blocked"
    if not result["changed_files"].isdigit():
        return "blocked"
    return result


def _output(role: str = "tester", status: str = "done", verdict: str = "pass", note: str = "ok") -> str:
    return (
        "Review or report text.\n\nFORGE_RESULT\n"
        f"role: {role}\nstatus: {status}\nverdict: {verdict}\n"
        "artifact: .forge/generated/reports/x-test-report.md\nchanged_files: 1\n"
        f"note: {note}\nEND_FORGE_RESULT\n"
    )


class WorkerResultRoleValuesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.templates = iter_template_files("base")
        self.mode_block = _block(_section(self.templates[MODE], "## worker handoff"))
        self.allowed = {f: _choices(self.mode_block[f]) for f in ("role", "status", "verdict")}

    def _role_block(self, role: str) -> dict[str, str]:
        prompt = self.templates[f".forge/runtime/agents/forge-{role}.md"]
        return _block(_section(prompt, "## Return to orchestrator"))

    def test_each_role_lists_exactly_its_a1_status_and_verdict_values(self) -> None:
        for role, (statuses, verdicts) in ROLE_VALUES.items():
            block = self._role_block(role)
            self.assertEqual(_choices(block["status"]), statuses, role)
            self.assertEqual(_choices(block["verdict"]), verdicts, role)

    def test_role_values_stay_within_mode_allowed_values(self) -> None:
        self.assertEqual(self.allowed["role"], set(ROLE_VALUES))
        for role in ROLE_VALUES:
            block = self._role_block(role)
            self.assertLessEqual(_choices(block["status"]), self.allowed["status"], role)
            self.assertLessEqual(_choices(block["verdict"]), self.allowed["verdict"], role)

    def test_planner_and_reviewer_report_zero_changed_files(self) -> None:
        for role in ("planner", "reviewer"):
            self.assertEqual(self._role_block(role)["changed_files"], "0", role)

    def test_non_reviewer_artifacts_point_under_forge_generated(self) -> None:
        for role in ("planner", "executor", "tester"):
            self.assertIn(".forge/generated/", self._role_block(role)["artifact"], role)

    def test_fail_closed_mappings_are_stated_per_role(self) -> None:
        phrases = {
            "planner": "`blocked` for `needs_more_context`, `needs_more_evidence`, or `needs_plan_approval`",
            "executor": "`partial_success`, `not_validated`, `blocked`, a blocking unknown, or new scope is `blocked`",
            "tester": "`note` names `e2e blocked_by_environment`",
            "reviewer": "`status: blocked`, `verdict: n/a`",
        }
        for role, phrase in phrases.items():
            prompt = self.templates[f".forge/runtime/agents/forge-{role}.md"]
            self.assertIn(phrase, _section(prompt, "## Return to orchestrator"), role)


class WorkerResultModeRulesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mode = iter_template_files("base")[MODE]
        handoff = _section(self.mode, "## worker handoff")
        block = _block(handoff)
        self.handoff = handoff
        self.allowed = {f: _choices(block[f]) for f in ("role", "status", "verdict")}

    def test_mode_names_missing_block_and_out_of_range_value_as_blocked(self) -> None:
        self.assertIn("A missing block", self.handoff)
        self.assertIn("a value outside the listed ones", self.handoff)

    def test_status_values_and_stop_conditions_are_unchanged(self) -> None:
        statuses = [line for line in _section(self.mode, "## status values").splitlines() if line.startswith("- ")]
        self.assertEqual(
            statuses,
            [
                "- `mr_opened`",
                "- `awaiting_clarification`",
                "- `awaiting_sdd_approval`",
                "- `stopped`",
                "- `review_unresolved`",
                "- `blocked_by_environment`",
            ],
        )
        stops = [line for line in _section(self.mode, "## stop conditions").splitlines() if line.startswith("- ")]
        self.assertEqual(len(stops), 14)

    def test_valid_result_is_read(self) -> None:
        result = _read_result(_output(), self.allowed)
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["verdict"], "pass")

    def test_missing_block_counts_as_blocked(self) -> None:
        self.assertEqual(_read_result("All tests pass, see report.", self.allowed), "blocked")

    def test_block_not_last_text_counts_as_blocked(self) -> None:
        self.assertEqual(_read_result(_output() + "One more thing.\n", self.allowed), "blocked")

    def test_block_over_1000_characters_counts_as_blocked(self) -> None:
        self.assertEqual(_read_result(_output(note="x" * 1000), self.allowed), "blocked")

    def test_unknown_status_counts_as_blocked(self) -> None:
        # Executor's own `success` is not a FORGE_RESULT value: it must be mapped to `done`.
        self.assertEqual(_read_result(_output(status="success"), self.allowed), "blocked")

    def test_unknown_verdict_or_role_counts_as_blocked(self) -> None:
        self.assertEqual(_read_result(_output(verdict="ok"), self.allowed), "blocked")
        self.assertEqual(_read_result(_output(role="orchestrator"), self.allowed), "blocked")

    def test_missing_or_reordered_field_counts_as_blocked(self) -> None:
        self.assertEqual(_read_result(_output().replace("changed_files: 1\n", ""), self.allowed), "blocked")
        swapped = _output().replace("status: done\nverdict: pass", "verdict: pass\nstatus: done")
        self.assertEqual(_read_result(swapped, self.allowed), "blocked")

    def test_non_numeric_changed_files_counts_as_blocked(self) -> None:
        self.assertEqual(_read_result(_output().replace("changed_files: 1", "changed_files: some"), self.allowed), "blocked")

    def test_duplicate_block_reads_only_the_last(self) -> None:
        quoted = _output(status="done", verdict="pass")
        real = _output(status="blocked", verdict="n/a")
        result = _read_result(quoted + "\n" + real, self.allowed)
        self.assertEqual((result["status"], result["verdict"]), ("blocked", "n/a"))

    def test_spoofed_block_before_trailing_text_counts_as_blocked(self) -> None:
        self.assertEqual(_read_result("```\n" + _output() + "```\nDone.", self.allowed), "blocked")


if __name__ == "__main__":
    unittest.main()
