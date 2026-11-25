from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "src/forge_context_engine/runtime_templates/base/.forge/runtime/hooks/forge_git_guard.py"
RULES = json.loads((GUARD.parents[1] / "meta/git-guard-rules.json").read_text(encoding="utf-8"))


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
            "git push origin HEAD",  # HEAD resolves to main
            "git push origin :forge/x",  # delete via empty source
            "git --no-pager push origin main",
            "git --git-dir .git push origin main",
            "true & git push origin main",
            "sudo git push origin main",
            "bash -c 'git push origin main'",
            "echo $(git tag v1)",
        ):
            code, err = self.run_guard(command, "orchestrator")
            self.assertEqual(code, 2, command)
            self.assertIn("Forge git guard", err)

    def test_orchestrator_allows_feature_branch_flow(self) -> None:
        _git(self.repo, "checkout", "-q", "-b", "forge/2026-11-10-x")
        for command in (
            "git checkout -b forge/2026-11-10-y",
            "git add -A && git commit -m 'feat: x'",
            "git add -f -- .forge/generated/plans/x.md",
            "git push -u origin forge/2026-11-10-x",
            "git push",  # current branch is the feature branch
            "git push origin HEAD 2>&1",
            "git --no-pager log --oneline -3",
            "glab mr create --draft",
            "git diff --stat",
            "go test ./...",
        ):
            code, _ = self.run_guard(command, "orchestrator")
            self.assertEqual(code, 0, command)

    def test_orchestrator_still_blocks_short_force_push_next_to_force_add(self) -> None:
        _git(self.repo, "checkout", "-q", "-b", "forge/2026-11-10-x")
        for command in (
            "git push -f origin forge/2026-11-10-x",
            "git add -f -- .forge/generated/plans/x.md && git push -f origin forge/2026-11-10-x",
        ):
            code, err = self.run_guard(command, "orchestrator")
            self.assertEqual(code, 2, command)
            self.assertIn("Forge git guard", err)

    def test_force_add_stages_listed_artifacts_but_not_temp_or_cache(self) -> None:
        from forge_context_engine.runtime_ops import FORGE_LOCAL_GITIGNORE

        forge = self.repo / ".forge"
        (forge / "generated/plans").mkdir(parents=True)
        (forge / "temp").mkdir()
        (forge / "cache").mkdir()
        (forge / ".gitignore").write_text(FORGE_LOCAL_GITIGNORE, encoding="utf-8")
        _git(self.repo, "add", ".forge/.gitignore")
        plan = ".forge/generated/plans/x-plan.md"
        (self.repo / plan).write_text("sdd\n", encoding="utf-8")
        (forge / "temp/stray.md").write_text("stray\n", encoding="utf-8")
        (forge / "cache/c.json").write_text("{}\n", encoding="utf-8")

        plain = subprocess.run(["git", "add", "--", plan], cwd=self.repo, capture_output=True, text=True)
        self.assertNotEqual(plain.returncode, 0)  # plain add refuses the gitignored artifact
        _git(self.repo, "add", "-A")
        _git(self.repo, "add", "-f", "--", plan)
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], cwd=self.repo, capture_output=True, text=True, check=True
        ).stdout.split()
        self.assertEqual(sorted(staged), sorted([".forge/.gitignore", plan]))

    def test_worker_blocks_all_git_writes(self) -> None:
        for command in ("git commit -m x", "git push origin forge/x", "git reset --hard", "git checkout main", "FOO=1 git -C . commit -m x",
                        "git --no-pager commit -m x", "git stash", "git clean -fd", "git restore ."):
            code, _ = self.run_guard(command, "worker")
            self.assertEqual(code, 2, command)

    def test_worker_allows_reads_and_tests(self) -> None:
        for command in ("git diff", "git status --porcelain", "git log -5 --oneline", "go test ./... 2>&1", "git --no-pager diff --stat"):
            code, _ = self.run_guard(command, "worker")
            self.assertEqual(code, 0, command)

    def test_decisions_match_rules_file(self) -> None:
        _git(self.repo, "checkout", "-q", "-b", "forge/x")
        pattern_samples = {"gh pr merge 5", "glab mr merge 12"}
        for role, role_rules in RULES["roles"].items():
            for sub in role_rules["blocked_git"]:
                code, err = self.run_guard(f"git {sub} x", role)
                self.assertEqual(code, 2, (role, sub))
                self.assertIn(role_rules["blocked_git"][sub], err)
            for pattern in role_rules["blocked_patterns"]:
                samples = [c for c in pattern_samples if re.search(pattern, c)]
                self.assertTrue(samples, f"no sample command for pattern {pattern}")
                for command in samples:
                    self.assertEqual(self.run_guard(command, role)[0], 2, (role, command))
            if "push" not in role_rules["blocked_git"]:
                for branch in RULES["protected_branches"]:
                    self.assertEqual(self.run_guard(f"git push origin {branch}", role)[0], 2, (role, branch))
                for flag in RULES["forbidden_push_flags"]:
                    self.assertEqual(self.run_guard(f"git push {flag} origin forge/x", role)[0], 2, (role, flag))
                self.assertEqual(self.run_guard("git push origin forge/x", role)[0], 0, role)

    def test_unknown_role_and_missing_rules_fail_closed(self) -> None:
        self.assertEqual(self.run_guard("git status", "intern")[0], 2)
        code, err = self._run_with_rules(None)
        self.assertEqual(code, 2)
        self.assertIn("git-guard-rules.json", err)

    def test_malformed_rules_fail_closed(self) -> None:
        good_role = {"blocked_patterns": {}, "blocked_git": {"commit": "no"}}
        base = {"protected_branches": ["main"], "forbidden_push_flags": ["-f"], "roles": {"worker": good_role}}
        cases = [
            "not json",
            [],
            {},
            {**base, "roles": {}},
            {**base, "roles": {"worker": []}},
            {**base, "roles": {"worker": {**good_role, "blocked_git": ["commit"]}}},
            {**base, "roles": {"worker": {**good_role, "blocked_patterns": {"(": "x"}}}},
            {**base, "roles": {"worker": {"blocked_git": {"commit": "no"}}}},
            {k: v for k, v in base.items() if k != "forbidden_push_flags"},
            {k: v for k, v in base.items() if k != "protected_branches"},
            {**base, "protected_branches": "main"},
            {**base, "roles": {"worker": {**good_role, "blocked_git": {"commit": ""}}}},
            "[" * 100000,
        ]
        self.assertEqual(self._run_with_rules(json.dumps(base))[0], 0)  # control: valid file allows git status
        for rules in cases:
            text = rules if isinstance(rules, str) else json.dumps(rules)
            code, err = self._run_with_rules(text)
            self.assertEqual(code, 2, text)
            self.assertIn("git-guard-rules.json", err, text)

    def _run_with_rules(self, rules_text: str | None) -> tuple[int, str]:
        """Run a copy of the guard whose sibling rules file holds rules_text (None: no file)."""
        root = Path(tempfile.mkdtemp(dir=self._tmp.name)) / ".forge/runtime"
        (root / "hooks").mkdir(parents=True)
        (root / "meta").mkdir()
        (root / "hooks" / GUARD.name).write_text(GUARD.read_text(encoding="utf-8"), encoding="utf-8")
        if rules_text is not None:
            (root / "meta/git-guard-rules.json").write_text(rules_text, encoding="utf-8")
        payload = {"tool_name": "Bash", "tool_input": {"command": "git status"}, "cwd": str(self.repo)}
        result = subprocess.run([sys.executable, "-B", str(root / "hooks" / GUARD.name), "worker"],
                                input=json.dumps(payload), capture_output=True, text=True)
        return result.returncode, result.stderr

    def test_non_bash_tool_is_ignored(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(GUARD), "worker"],
            input=json.dumps({"tool_name": "Edit", "tool_input": {}}), capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
