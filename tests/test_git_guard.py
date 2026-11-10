from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "src/forge_context_engine/runtime_templates/base/.forge/runtime/hooks/forge_git_guard.py"


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class GitGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _git(self.repo, "init", "-q", "-b", "main")
        _git(self.repo, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_guard(self, command: str, role: str) -> tuple[int, str]:
        payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(self.repo)}
        result = subprocess.run(
            [sys.executable, "-B", str(GUARD), role],
            input=json.dumps(payload), capture_output=True, text=True, cwd=self.repo,
        )
        return result.returncode, result.stderr

    def test_orchestrator_blocks_protected_and_dangerous_pushes(self) -> None:
        for command in (
            "git push origin main",
            "git push origin HEAD:master",
            "git push --force origin forge/2026-11-10-x",
            "git push origin +forge/x",
            "git push --tags",
            "git push origin --delete forge/x",
            "git tag v1.0.0",
            "git merge forge/x",
            "glab mr merge 12",
            "gh pr merge 5 --squash",
            "go test ./... && git push origin main",
            "git push",  # current branch is main
        ):
            code, err = self.run_guard(command, "orchestrator")
            self.assertEqual(code, 2, command)
            self.assertIn("Forge git guard", err)

    def test_orchestrator_allows_feature_branch_flow(self) -> None:
        _git(self.repo, "checkout", "-q", "-b", "forge/2026-11-10-x")
        for command in (
            "git checkout -b forge/2026-11-10-y",
            "git add -A && git commit -m 'feat: x'",
            "git push -u origin forge/2026-11-10-x",
            "git push",  # current branch is the feature branch
            "glab mr create --draft",
            "git diff --stat",
            "go test ./...",
        ):
            code, _ = self.run_guard(command, "orchestrator")
            self.assertEqual(code, 0, command)

    def test_worker_blocks_all_git_writes(self) -> None:
        for command in ("git commit -m x", "git push origin forge/x", "git reset --hard", "git checkout main", "FOO=1 git -C . commit -m x"):
            code, _ = self.run_guard(command, "worker")
            self.assertEqual(code, 2, command)

    def test_worker_allows_reads_and_tests(self) -> None:
        for command in ("git diff", "git status --porcelain", "git log -5 --oneline", "go test ./..."):
            code, _ = self.run_guard(command, "worker")
            self.assertEqual(code, 0, command)

    def test_non_bash_tool_is_ignored(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(GUARD), "worker"],
            input=json.dumps({"tool_name": "Edit", "tool_input": {}}), capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
