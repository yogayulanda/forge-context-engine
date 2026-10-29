from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from forge_context_engine import autopilot
from forge_context_engine.cli import main

FAKE_AGENT = textwrap.dedent(
    """
    import re, sys
    from pathlib import Path

    prompt = Path(sys.argv[1]).read_text()
    stage = re.search(r"stage `([a-z]+)`", prompt).group(1)
    artifact = Path(re.search(r"Write your report to `([^`]+)`", prompt).group(1))
    behavior = (Path(sys.argv[2]).parent.parent / "fake-behavior.txt")
    mode = behavior.read_text().strip() if behavior.exists() else "ok"

    if stage == "execute":
        target = "README.md" if mode == "out-of-scope" else "src/app.py"
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a") as handle:
            handle.write("print('fixed')\\n")
        artifact.write_text("status: success\\n")
    elif stage == "review":
        verdict = "request_changes" if mode == "review-changes" else "accept"
        artifact.write_text(f"verdict: {verdict}\\n")
    elif stage == "security":
        artifact.write_text("verdict: accept\\n")
    elif stage == "test":
        target = "src/app.py" if mode == "tester-prod" else "tests/e2e/test_app.py"
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        Path(target).write_text("def test_app():\\n    assert True\\n")
        artifact.write_text("status: success\\n")
    """
)


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


class AutopilotTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.remote = base / "remote.git"
        _git(base, "init", "-q", "--bare", str(self.remote))
        self.root = base / "repo"
        self.root.mkdir()
        _git(self.root, "init", "-q", "-b", "main")
        _git(self.root, "config", "user.email", "t@example.com")
        _git(self.root, "config", "user.name", "t")
        (self.root / "src").mkdir()
        (self.root / "src/app.py").write_text("print('bug')\n")
        (self.root / "README.md").write_text("demo\n")
        (self.root / ".gitignore").write_text(".forge/runs/\n.forge/generated/reports/\n")
        (self.root / "spec.md").write_text("- [ ] Fix the app\n  repo: demo\n  accept: prints fixed\n")
        agent = base / "fake_agent.py"
        agent.write_text(FAKE_AGENT)
        config = {
            "roles": {"planner": "self", "dev": "fake", "reviewer": "fake", "security": "fake", "tester": "fake"},
            "agents": {"fake": {"command": [sys.executable, str(agent), "{prompt_file}", "{run_dir}/x"]}},
            "worktree_root": str(base / "worktrees"),
            "high_risk_paths": ["src/payments/**"],
            "validation_commands": [f"{sys.executable} -c \"print('ok')\""],
            "e2e": {"command": f"{sys.executable} -c \"print('e2e ok')\"", "test_paths": ["tests/e2e/**"]},
            "vcs": {"provider": "none"},
        }
        (self.root / ".forge").mkdir()
        (self.root / ".forge/autopilot.json").write_text(json.dumps(config))
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "init")
        _git(self.root, "remote", "add", "origin", str(self.remote))
        self.repo = autopilot.Repo(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _submit(self, run_id: str, stage: str, text: str) -> None:
        path = self.root.parent / f"{stage}.md"
        path.write_text(text)
        autopilot.submit(self.repo, run_id, stage, path)

    def _prompt(self) -> Path:
        path = self.root.parent / "prompt.md"
        path.write_text("Do the stage.")
        return path

    def _to_execute(self, ecp_files: str = "- `src/app.py`") -> str:
        state = autopilot.start_run(self.repo, "md:spec.md")
        run_id = state["run_id"]
        self._submit(run_id, "spec", "status: ready\n\n## Decisions taken by autopilot\n\n- keep print API\n")
        self.assertTrue(autopilot.gate(self.repo, run_id, "spec")["passed"])
        self._submit(run_id, "plan", "status: ready_for_implementation\n")
        self.assertTrue(autopilot.gate(self.repo, run_id, "plan")["passed"])
        self._submit(run_id, "ecp", f"status: ecp_ready\n\n## Allowed files\n\n{ecp_files}\n")
        self.assertTrue(autopilot.gate(self.repo, run_id, "ecp")["passed"])
        return run_id

    def _behave(self, mode: str) -> None:
        (self.root / ".forge/runs/fake-behavior.txt").write_text(mode)

    def test_happy_path_reaches_pr_with_report(self) -> None:
        run_id = self._to_execute()
        for stage in ("execute", "review", "test"):
            autopilot.dispatch(self.repo, run_id, stage, self._prompt())
            self.assertTrue(autopilot.gate(self.repo, run_id, stage)["passed"], stage)
        self.assertTrue(autopilot.gate(self.repo, run_id, "validate")["passed"])
        result = autopilot.gate(self.repo, run_id, "pr")
        self.assertEqual(result["status"], "done")

        state = autopilot.load_state(self.repo, run_id)
        self.assertIn("security (skipped: not high-risk)", state["passed"])
        worktree = Path(state["worktree"])
        log = _git(worktree, "log", "--format=%s", "main..HEAD")
        self.assertIn("execute", log)
        self.assertIn("e2e tests", log)
        self.assertTrue(list((worktree / ".forge/generated/plans").glob("*-plan.md")))
        report = (self.root / ".forge/runs" / run_id / "report.md").read_text()
        self.assertIn("keep print API", report)
        self.assertNotIn("not_validated", report)

    def test_out_of_order_stage_is_refused(self) -> None:
        state = autopilot.start_run(self.repo, "md:spec.md")
        with self.assertRaises(autopilot.AutopilotError):
            autopilot.gate(self.repo, state["run_id"], "plan")

    def test_only_one_active_run(self) -> None:
        autopilot.start_run(self.repo, "md:spec.md")
        with self.assertRaises(autopilot.AutopilotError):
            autopilot.start_run(self.repo, "md:spec.md")

    def test_self_role_cannot_be_dispatched(self) -> None:
        state = autopilot.start_run(self.repo, "md:spec.md")
        with self.assertRaises(autopilot.AutopilotError):
            autopilot.dispatch(self.repo, state["run_id"], "spec", self._prompt())

    def test_plan_without_ready_status_does_not_advance(self) -> None:
        state = autopilot.start_run(self.repo, "md:spec.md")
        run_id = state["run_id"]
        self._submit(run_id, "spec", "status: ready\n")
        autopilot.gate(self.repo, run_id, "spec")
        self._submit(run_id, "plan", "status: needs_more_context\n")
        result = autopilot.gate(self.repo, run_id, "plan")
        self.assertFalse(result["passed"])
        self.assertEqual(result["next_stage"], "plan")

    def test_execute_outside_allowed_files_blocks(self) -> None:
        run_id = self._to_execute()
        self._behave("out-of-scope")
        autopilot.dispatch(self.repo, run_id, "execute", self._prompt())
        result = autopilot.gate(self.repo, run_id, "execute")
        self.assertFalse(result["passed"])
        self.assertEqual(result["status"], "blocked")
        self.assertTrue(any("outside allowed files: README.md" in r for r in result["reasons"]))

    def test_ci_path_is_hard_blocked_even_when_allowed(self) -> None:
        run_id = self._to_execute("- `src/app.py`\n- `.github/workflows/**`")
        state = autopilot.load_state(self.repo, run_id)
        workflow = Path(state["worktree"]) / ".github/workflows/ci.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("on: push\n")
        result = autopilot.gate(self.repo, run_id, "execute")
        self.assertTrue(any("hard-blocked path" in r for r in result["reasons"]))

    def test_secret_content_blocks(self) -> None:
        run_id = self._to_execute()
        state = autopilot.load_state(self.repo, run_id)
        (Path(state["worktree"]) / "src/app.py").write_text("password = 'hunter2hunter2'\n")
        result = autopilot.gate(self.repo, run_id, "execute")
        self.assertIn("added content matches a secret pattern", result["reasons"])

    def test_review_request_changes_returns_to_execute_then_blocks(self) -> None:
        run_id = self._to_execute()
        self._behave("review-changes")
        for _ in range(3):
            autopilot.dispatch(self.repo, run_id, "execute", self._prompt())
            autopilot.gate(self.repo, run_id, "execute")
            state = autopilot.load_state(self.repo, run_id)
            if state["status"] != "running":
                break
            autopilot.dispatch(self.repo, run_id, "review", self._prompt())
            result = autopilot.gate(self.repo, run_id, "review")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("review_rounds exhausted", autopilot.load_state(self.repo, run_id)["blocked_reason"])

    def test_high_risk_path_runs_security_stage(self) -> None:
        run_id = self._to_execute("- `src/**`")
        state = autopilot.load_state(self.repo, run_id)
        payments = Path(state["worktree"]) / "src/payments/transfer.py"
        payments.parent.mkdir(parents=True)
        payments.write_text("def transfer():\n    return 1\n")
        autopilot.gate(self.repo, run_id, "execute")
        autopilot.dispatch(self.repo, run_id, "review", self._prompt())
        result = autopilot.gate(self.repo, run_id, "review")
        self.assertEqual(result["next_stage"], "security")
        self.assertTrue(autopilot.load_state(self.repo, run_id)["high_risk"])

    def test_tester_cannot_touch_production_code(self) -> None:
        run_id = self._to_execute()
        autopilot.dispatch(self.repo, run_id, "execute", self._prompt())
        autopilot.gate(self.repo, run_id, "execute")
        autopilot.dispatch(self.repo, run_id, "review", self._prompt())
        autopilot.gate(self.repo, run_id, "review")
        self._behave("tester-prod")
        autopilot.dispatch(self.repo, run_id, "test", self._prompt())
        result = autopilot.gate(self.repo, run_id, "test")
        self.assertFalse(result["passed"])
        self.assertTrue(any("non-test paths" in r for r in result["reasons"]))

    def test_missing_e2e_marks_not_validated(self) -> None:
        config = json.loads((self.root / ".forge/autopilot.json").read_text())
        config["e2e"]["command"] = ""
        (self.root / ".forge/autopilot.json").write_text(json.dumps(config))
        run_id = self._to_execute()
        for stage in ("execute", "review", "test"):
            autopilot.dispatch(self.repo, run_id, stage, self._prompt())
            autopilot.gate(self.repo, run_id, stage)
        autopilot.gate(self.repo, run_id, "validate")
        autopilot.gate(self.repo, run_id, "pr")
        report = (self.root / ".forge/runs" / run_id / "report.md").read_text()
        self.assertIn("not_validated", report)

    def test_kill_switch_refuses_commands(self) -> None:
        state = autopilot.start_run(self.repo, "md:spec.md")
        (self.root / autopilot.STOP_FILE).write_text("")
        with self.assertRaises(autopilot.AutopilotError):
            autopilot.gate(self.repo, state["run_id"], "spec")

    def test_cli_status_json(self) -> None:
        autopilot.start_run(self.repo, "md:spec.md")
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["run", "status", "--json", "--target", str(self.root)])
        self.assertEqual(code, 0)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["stage"], "spec")


if __name__ == "__main__":
    unittest.main()
