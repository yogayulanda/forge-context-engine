"""Autopilot control plane for `forge run` (specs/autopilot.md).

Forge owns run state, deterministic gates, role-agent dispatch, validation, and the PR.
The orchestrator (any LLM tool) decides what to dispatch and writes stage prompts.
"""

from __future__ import annotations

import fnmatch
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONFIG_PATH = ".forge/autopilot.json"
RUNS_DIR = ".forge/runs"
STOP_FILE = ".forge/runs/STOP"

STAGES = ("spec", "plan", "ecp", "execute", "review", "security", "test", "validate", "pr")
AGENT_STAGES = ("spec", "plan", "ecp", "execute", "review", "security", "test")
STAGE_ROLE = {
    "spec": "planner",
    "plan": "planner",
    "ecp": "planner",
    "execute": "dev",
    "review": "reviewer",
    "security": "security",
    "test": "tester",
}
STAGE_MODE = {
    "spec": "plan",
    "plan": "plan",
    "ecp": "implementation",
    "execute": "execute",
    "review": "review",
    "security": "review",
    "test": "execute",
}
EDITING_STAGES = ("execute", "test")
TERMINAL = ("done", "blocked", "failed", "cancelled")

DEFAULT_CONFIG: dict[str, Any] = {
    "roles": {
        "planner": "self",
        "dev": "claude",
        "reviewer": "codex",
        "security": "claude",
        "tester": "claude",
    },
    # Placeholders: verify each CLI's headless flags before relying on them.
    "agents": {
        "claude": {"command": ["claude", "-p", "@{prompt_file}"]},
        "codex": {"command": ["codex", "exec", "--cd", "{workdir}", "@{prompt_file}"]},
        "copilot": {"command": ["copilot", "-p", "@{prompt_file}"]},
        "hermes": {"command": ["hermes", "-z", "@{prompt_file}"]},
    },
    "limits": {
        "plan_rounds": 2,
        "review_rounds": 2,
        "test_rounds": 2,
        "stage_timeout_minutes": 30,
        "max_changed_files": 30,
        "max_changed_lines": 1500,
    },
    "hard_block_paths": [],
    "high_risk_paths": [],
    "validation_commands": [],
    "security": {"always": False},
    "e2e": {"command": "", "setup": "", "test_paths": ["test/e2e/**", "tests/e2e/**", "e2e/**"]},
    "worktree_root": "",
    "vcs": {
        "provider": "github",
        "remote": "origin",
        "base": "main",
        "branch_prefix": "forge/auto/",
        "draft": True,
        "high_risk_labels": ["high-risk"],
        "not_validated_labels": ["not-validated"],
    },
}

CI_PATHS = (
    ".github/workflows/**",
    ".gitlab-ci.yml",
    ".gitlab/**",
    "Jenkinsfile",
    ".circleci/**",
    "azure-pipelines.yml",
    "bitbucket-pipelines.yml",
)
SECRET_PATHS = (".env", ".env.*", "**/.env", "**/.env.*", "*.pem", "**/*.pem", "*.key", "**/*.key")
SECRET_CONTENT = re.compile(
    r"(-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|"
    r"(?i:(password|passwd|secret|api_key|apikey|token)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]))"
)
TEST_PATH_HINTS = ("test", "tests", "spec", "__tests__", "e2e")

STATUS_VALUES = {
    "spec": ("ready", "blocked"),
    "plan": ("ready_for_implementation", "blocked_by_decision", "needs_more_context"),
    "ecp": ("ecp_ready", "blocked_by_decision", "needs_more_evidence", "needs_plan_approval"),
    "review": ("accept", "request_changes", "needs_more_validation", "blocked"),
    "security": ("accept", "request_changes", "needs_more_validation", "blocked"),
}


class AutopilotError(Exception):
    """A refused `forge run` command; the message is shown to the orchestrator."""


@dataclass
class Repo:
    root: Path

    @property
    def runs_dir(self) -> Path:
        return self.root / RUNS_DIR


# ---------------------------------------------------------------------------
# config and state


def load_config(root: Path) -> dict[str, Any]:
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    path = root / CONFIG_PATH
    if path.exists():
        try:
            user = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AutopilotError(f"{CONFIG_PATH} is not valid JSON: {exc}") from exc
        _deep_merge(config, user)
    return config


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:40].strip("-") or "run"


def _run_dir(repo: Repo, run_id: str) -> Path:
    path = repo.runs_dir / run_id
    if not (path / "state.json").exists():
        raise AutopilotError(f"unknown run: {run_id}")
    return path


def load_state(repo: Repo, run_id: str) -> dict[str, Any]:
    return json.loads((_run_dir(repo, run_id) / "state.json").read_text(encoding="utf-8"))


def save_state(repo: Repo, state: dict[str, Any]) -> None:
    state["updated"] = _now()
    path = repo.runs_dir / state["run_id"] / "state.json"
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def list_runs(repo: Repo) -> list[dict[str, Any]]:
    if not repo.runs_dir.exists():
        return []
    runs = []
    for state_path in sorted(repo.runs_dir.glob("*/state.json")):
        runs.append(json.loads(state_path.read_text(encoding="utf-8")))
    return runs


def _active_run(repo: Repo) -> dict[str, Any] | None:
    for state in list_runs(repo):
        if state["status"] not in TERMINAL:
            return state
    return None


def _check_stop(repo: Repo) -> None:
    if (repo.root / STOP_FILE).exists():
        raise AutopilotError(f"kill switch present: remove {STOP_FILE} to continue")


# ---------------------------------------------------------------------------
# git helpers


def _git(cwd: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise AutopilotError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def _changed_files(worktree: Path, since: str) -> list[tuple[str, str]]:
    """Return (status, path) for committed and uncommitted changes since `since`."""

    _git(worktree, "add", "-A")
    out = _git(worktree, "diff", "--cached", "--name-status", "--no-renames", since)
    changes = []
    for line in out.splitlines():
        if not line.strip():
            continue
        status, path = line.split("\t", 1)
        changes.append((status[0], path))
    return changes


def _changed_lines(worktree: Path, since: str) -> int:
    out = _git(worktree, "diff", "--cached", "--numstat", since)
    total = 0
    for line in out.splitlines():
        added, removed, _ = line.split("\t", 2)
        if added != "-":
            total += int(added) + int(removed)
    return total


def _added_content(worktree: Path, since: str) -> str:
    out = _git(worktree, "diff", "--cached", "-U0", since)
    return "\n".join(
        line[1:] for line in out.splitlines() if line.startswith("+") and not line.startswith("+++")
    )


def _commit(worktree: Path, message: str) -> str:
    _git(worktree, "add", "-A")
    if not _git(worktree, "diff", "--cached", "--name-only").strip():
        return _git(worktree, "rev-parse", "HEAD").strip()
    _git(
        worktree,
        "-c", "user.name=forge-autopilot",
        "-c", "user.email=forge-autopilot@localhost",
        "commit", "-q", "-m", message,
    )
    return _git(worktree, "rev-parse", "HEAD").strip()


def _matches(path: str, patterns: list[str] | tuple[str, ...]) -> bool:
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
        if pattern.endswith("/**") and (path == pattern[:-3] or path.startswith(pattern[:-2])):
            return True
    return False


# ---------------------------------------------------------------------------
# commands


def start_run(repo: Repo, source: str, title: str | None = None) -> dict[str, Any]:
    _check_stop(repo)
    active = _active_run(repo)
    if active:
        raise AutopilotError(f"run {active['run_id']} is still active; stop or finish it first")

    kind, _, raw_path = source.partition(":")
    if kind not in ("md", "text") or not raw_path:
        raise AutopilotError("source must be md:<path> or text:<path> in v0.1")
    spec_path = (repo.root / raw_path).resolve()
    if not spec_path.is_file():
        raise AutopilotError(f"spec not found: {raw_path}")
    spec_text = spec_path.read_text(encoding="utf-8")

    config = load_config(repo.root)
    vcs = config["vcs"]
    first = next((line for line in spec_text.splitlines() if line.strip()), "")
    heading = re.sub(r"^\s*(#+|[-*])?\s*(\[[ xX]\])?\s*", "", first)
    slug = _slugify(title or heading or spec_path.stem)
    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{slug}"
    run_dir = repo.runs_dir / run_id
    run_dir.mkdir(parents=True)
    ignore = repo.runs_dir / ".gitignore"
    if not ignore.exists():
        ignore.write_text("*\n", encoding="utf-8")
    (run_dir / "request.md").write_text(spec_text, encoding="utf-8")

    base_commit = _git(repo.root, "rev-parse", vcs["base"]).strip()
    branch = f"{vcs['branch_prefix']}{run_id}"
    worktree_root = Path(config["worktree_root"]) if config["worktree_root"] else (
        repo.root.parent / ".forge-worktrees" / repo.root.name
    )
    worktree = (worktree_root / run_id).resolve()
    worktree.parent.mkdir(parents=True, exist_ok=True)
    _git(repo.root, "worktree", "add", "-q", "-b", branch, str(worktree), base_commit)

    state = {
        "run_id": run_id,
        "slug": slug,
        "source": source,
        "status": "running",
        "stage": "spec",
        "passed": [],
        "rounds": {"plan": 0, "review": 0, "test": 0, "e2e_retry": 0},
        "branch": branch,
        "worktree": str(worktree),
        "base_commit": base_commit,
        "stage_commit": base_commit,
        "allowed_files": [],
        "high_risk": False,
        "risk_reasons": [],
        "decisions": [],
        "gates": [],
        "invocations": [],
        "validation": [],
        "blocked_reason": "",
        "pr_url": "",
        "created": _now(),
    }
    save_state(repo, state)
    return state


def _require_stage(state: dict[str, Any], stage: str) -> None:
    if stage not in STAGES:
        raise AutopilotError(f"unknown stage: {stage}")
    if state["status"] != "running":
        raise AutopilotError(f"run is {state['status']}: {state['blocked_reason'] or 'no further stages'}")
    if state["stage"] != stage:
        raise AutopilotError(f"out of order: current stage is {state['stage']}, not {stage}")


def _artifact_path(repo: Repo, state: dict[str, Any], stage: str) -> Path:
    return repo.runs_dir / state["run_id"] / f"{stage}.md"


def _stage_prompt(state: dict[str, Any], stage: str, orchestrator_prompt: str, artifact: Path) -> str:
    mode = STAGE_MODE[stage]
    lines = [
        f"Forge autopilot run {state['run_id']}, stage `{stage}`.",
        f"Work in Forge `{mode}` mode: read `.forge/forge.config.yaml` and `.forge/runtime/modes/{mode}.md` first.",
        "Mode approvals for this stage are granted by the autopilot gates (specs/autopilot.md).",
        "Do not commit, push, merge, or open pull requests. Forge does that after its gates.",
    ]
    if stage == "execute":
        lines.append("Edit only these files: " + ", ".join(state["allowed_files"]))
    if stage == "test":
        lines.append("Write or update e2e tests only. Do not edit production code.")
    if stage == "ecp":
        lines.append("Include a `## Allowed files` section listing each path or glob as a bullet in backticks.")
    if stage in ("review", "security"):
        lines.append("Start your report with `verdict: <accept|request_changes|needs_more_validation|blocked>`.")
    else:
        lines.append("Start your report with `status: <value>` using this mode's status values.")
    lines.append(f"Write your report to `{artifact}`.")
    lines.extend(["", "## Orchestrator instructions", "", orchestrator_prompt])
    return "\n".join(lines) + "\n"


def dispatch(repo: Repo, run_id: str, stage: str, prompt_file: Path) -> dict[str, Any]:
    _check_stop(repo)
    state = load_state(repo, run_id)
    _require_stage(state, stage)
    if stage not in AGENT_STAGES:
        raise AutopilotError(f"stage {stage} is run by Forge: use `forge run gate {run_id} --stage {stage}`")
    config = load_config(repo.root)
    agent = config["roles"].get(STAGE_ROLE[stage], "self")
    if agent == "self":
        raise AutopilotError(f"role {STAGE_ROLE[stage]} is `self`: write the artifact and use `forge run submit`")
    template = config["agents"].get(agent, {}).get("command")
    if not template:
        raise AutopilotError(f"no command configured for agent `{agent}`")

    run_dir = repo.runs_dir / run_id
    artifact = _artifact_path(repo, state, stage)
    prompt = _stage_prompt(state, stage, Path(prompt_file).read_text(encoding="utf-8"), artifact)
    prompt_path = run_dir / f"{stage}.prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    values = {"prompt_file": str(prompt_path), "workdir": state["worktree"], "run_dir": str(run_dir)}
    command = []
    for part in template:
        if part.startswith("@{prompt_file}"):
            command.append(prompt)
        else:
            command.append(part.format(**values))
    timeout = int(config["limits"]["stage_timeout_minutes"]) * 60
    started = _now()
    try:
        result = subprocess.run(command, cwd=state["worktree"], capture_output=True, text=True, timeout=timeout)
        exit_code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        exit_code, stdout, stderr = 127, "", f"command not found: {command[0]}"
    except subprocess.TimeoutExpired as exc:
        exit_code, stdout, stderr = 124, exc.stdout or "", f"timed out after {timeout}s"
    (run_dir / f"{stage}.stdout.txt").write_text(stdout or "", encoding="utf-8")
    (run_dir / f"{stage}.stderr.txt").write_text(stderr or "", encoding="utf-8")
    if not artifact.exists() and stdout:
        artifact.write_text(stdout, encoding="utf-8")

    state["invocations"].append(
        {"stage": stage, "agent": agent, "exit_code": exit_code, "started": started, "finished": _now()}
    )
    save_state(repo, state)
    return {"run_id": run_id, "stage": stage, "agent": agent, "exit_code": exit_code,
            "artifact": str(artifact) if artifact.exists() else "", "stderr_tail": (stderr or "")[-500:]}


def submit(repo: Repo, run_id: str, stage: str, file: Path) -> dict[str, Any]:
    _check_stop(repo)
    state = load_state(repo, run_id)
    _require_stage(state, stage)
    if stage in EDITING_STAGES:
        raise AutopilotError(f"stage {stage} edits code: dispatch it to its role agent")
    shutil.copyfile(file, _artifact_path(repo, state, stage))
    state["invocations"].append({"stage": stage, "agent": "self", "exit_code": 0, "started": _now(), "finished": _now()})
    save_state(repo, state)
    return {"run_id": run_id, "stage": stage, "artifact": str(_artifact_path(repo, state, stage))}


def _extract(text: str, key: str, allowed: tuple[str, ...]) -> str:
    pattern = re.compile(rf"\b{key}\b\W{{0,6}}({'|'.join(allowed)})\b", re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1).lower() if match else ""


def _allowed_files(text: str) -> list[str]:
    match = re.search(r"^#+\s*Allowed files\s*$(.*?)(?=^#+\s|\Z)", text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if not match:
        return []
    return re.findall(r"^\s*[-*]\s*`([^`]+)`", match.group(1), re.MULTILINE)


def _decisions(text: str) -> list[str]:
    match = re.search(r"^#+\s*Decisions taken by autopilot\s*$(.*?)(?=^#+\s|\Z)", text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if not match:
        return []
    return [line.strip()[2:].strip() for line in match.group(1).splitlines() if line.strip().startswith(("- ", "* "))]


def _record(state: dict[str, Any], stage: str, passed: bool, reasons: list[str]) -> None:
    state["gates"].append({"stage": stage, "passed": passed, "reasons": reasons, "at": _now()})


def _advance(state: dict[str, Any], stage: str, config: dict[str, Any]) -> None:
    state["passed"].append(stage)
    order = list(STAGES)
    nxt = order[order.index(stage) + 1]
    if nxt == "security" and not (state["high_risk"] or config["security"].get("always")):
        state["passed"].append("security (skipped: not high-risk)")
        nxt = "test"
    state["stage"] = nxt


def _block(state: dict[str, Any], reason: str) -> None:
    state["status"] = "blocked"
    state["blocked_reason"] = reason


def _back_to_execute(state: dict[str, Any], config: dict[str, Any], counter: str, limit_key: str, reason: str) -> None:
    state["rounds"][counter] += 1
    if state["rounds"][counter] > int(config["limits"][limit_key]):
        _block(state, f"{reason}; {limit_key} exhausted")
    else:
        state["stage"] = "execute"


def gate(repo: Repo, run_id: str, stage: str) -> dict[str, Any]:
    _check_stop(repo)
    state = load_state(repo, run_id)
    _require_stage(state, stage)
    config = load_config(repo.root)
    worktree = Path(state["worktree"])
    artifact = _artifact_path(repo, state, stage)
    text = artifact.read_text(encoding="utf-8") if artifact.exists() else ""
    reasons: list[str] = []

    if stage in ("spec", "plan", "ecp"):
        if not text.strip():
            reasons.append(f"no {stage} artifact")
        status = _extract(text, "status", STATUS_VALUES[stage])
        ok_status = {"spec": "ready", "plan": "ready_for_implementation", "ecp": "ecp_ready"}[stage]
        if text.strip() and status != ok_status:
            reasons.append(f"status is `{status or 'missing'}`, need `{ok_status}`")
        if stage == "spec":
            state["decisions"] = _decisions(text)
        if stage == "ecp":
            allowed = _allowed_files(text)
            if not allowed:
                reasons.append("ECP has no `## Allowed files` section with backticked paths")
            state["allowed_files"] = allowed
        if stage == "plan" and not reasons:
            dated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            plan_rel = f".forge/generated/plans/{dated}-{state['slug']}-plan.md"
            (worktree / plan_rel).parent.mkdir(parents=True, exist_ok=True)
            spec_text = _artifact_path(repo, state, "spec").read_text(encoding="utf-8")
            (worktree / plan_rel).write_text(spec_text.rstrip() + "\n\n---\n\n" + text, encoding="utf-8")
            state["stage_commit"] = _commit(worktree, f"forge(autopilot): add plan for {state['slug']}")
        passed = not reasons
        _record(state, stage, passed, reasons)
        if passed:
            _advance(state, stage, config)
        elif status in ("blocked", "blocked_by_decision"):
            _block(state, f"{stage}: {status}")
        elif stage in ("plan", "ecp", "spec"):
            state["rounds"]["plan"] += 1
            if state["rounds"]["plan"] > int(config["limits"]["plan_rounds"]):
                _block(state, f"{stage}: " + "; ".join(reasons))

    elif stage == "execute":
        reasons = _scope_check(state, config, worktree)
        _update_risk(repo, state, config, worktree)
        passed = not reasons
        _record(state, stage, passed, reasons)
        if passed:
            state["stage_commit"] = _commit(worktree, f"forge(autopilot): execute {state['slug']}")
            _advance(state, stage, config)
        else:
            _block(state, "scope: " + "; ".join(reasons))

    elif stage in ("review", "security"):
        verdict = _extract(text, "verdict", STATUS_VALUES[stage])
        if verdict in ("accept", "needs_more_validation"):
            _record(state, stage, True, [])
            _advance(state, stage, config)
        elif verdict == "request_changes":
            reasons = [f"{stage} requested changes"]
            _record(state, stage, False, reasons)
            _back_to_execute(state, config, "review", "review_rounds", reasons[0])
        else:
            reasons = [f"{stage} verdict is `{verdict or 'missing'}`"]
            _record(state, stage, False, reasons)
            _block(state, reasons[0])

    elif stage == "test":
        changes = _changed_files(worktree, state["stage_commit"])
        test_paths = config["e2e"]["test_paths"]
        outside = [path for _, path in changes if not _matches(path, test_paths)]
        if outside:
            reasons.append("tester changed non-test paths: " + ", ".join(outside))
        if not changes and "test" not in state["passed"]:
            reasons.append("tester added no e2e tests")
        passed = not reasons
        _record(state, stage, passed, reasons)
        if passed:
            state["stage_commit"] = _commit(worktree, f"forge(autopilot): e2e tests for {state['slug']}")
            _advance(state, stage, config)
        else:
            _git(worktree, "reset", "-q", "--hard", state["stage_commit"])
            state["rounds"]["test"] += 1
            if state["rounds"]["test"] > int(config["limits"]["test_rounds"]):
                _block(state, "test: " + "; ".join(reasons))

    elif stage == "validate":
        results = _run_validation(config, worktree)
        state["validation"] = results
        e2e_failed = any(r["kind"] == "e2e" and r["result"] == "failed" for r in results)
        if e2e_failed and state["rounds"]["e2e_retry"] == 0:
            state["rounds"]["e2e_retry"] = 1
            reasons = ["e2e failed; back to execute once"]
            _record(state, stage, False, reasons)
            state["stage"] = "execute"
        else:
            _record(state, stage, True, [])
            _advance(state, stage, config)

    elif stage == "pr":
        reasons = []
        state["pr_url"] = _open_pr(repo, state, config)
        state["status"] = "done"
        state["passed"].append("pr")
        _record(state, stage, True, [])

    save_state(repo, state)
    return {"run_id": run_id, "stage": stage, "passed": not reasons, "reasons": reasons,
            "next_stage": state["stage"], "status": state["status"]}


def _scope_check(state: dict[str, Any], config: dict[str, Any], worktree: Path) -> list[str]:
    since = state["stage_commit"]
    changes = _changed_files(worktree, since)
    reasons = []
    if not changes:
        reasons.append("no changes")
    allowed = state["allowed_files"]
    hard = list(CI_PATHS) + list(config["hard_block_paths"])
    for status, path in changes:
        if _matches(path, hard):
            reasons.append(f"hard-blocked path: {path}")
        elif _matches(path, SECRET_PATHS):
            reasons.append(f"secret-like file: {path}")
        elif not _matches(path, allowed):
            reasons.append(f"outside allowed files: {path}")
        if status == "D" and any(part in TEST_PATH_HINTS for part in Path(path).parts) and not _matches(path, allowed):
            reasons.append(f"test deleted: {path}")
    if SECRET_CONTENT.search(_added_content(worktree, since)):
        reasons.append("added content matches a secret pattern")
    if len(changes) > int(config["limits"]["max_changed_files"]):
        reasons.append(f"{len(changes)} files changed, limit {config['limits']['max_changed_files']}")
    lines = _changed_lines(worktree, since)
    if lines > int(config["limits"]["max_changed_lines"]):
        reasons.append(f"{lines} lines changed, limit {config['limits']['max_changed_lines']}")
    return reasons


def _update_risk(repo: Repo, state: dict[str, Any], config: dict[str, Any], worktree: Path) -> None:
    for _, path in _changed_files(worktree, state["base_commit"]):
        if _matches(path, config["high_risk_paths"]):
            reason = f"high-risk path: {path}"
            if reason not in state["risk_reasons"]:
                state["risk_reasons"].append(reason)
    for stage in ("spec", "plan", "ecp"):
        artifact = _artifact_path(repo, state, stage)
        if artifact.exists() and _extract(artifact.read_text(encoding="utf-8"), "risk", ("high",)) == "high":
            reason = f"{stage} declares risk: high"
            if reason not in state["risk_reasons"]:
                state["risk_reasons"].append(reason)
    state["high_risk"] = bool(state["risk_reasons"])


def _run_validation(config: dict[str, Any], worktree: Path) -> list[dict[str, Any]]:
    results = []
    timeout = int(config["limits"]["stage_timeout_minutes"]) * 60

    def run(kind: str, command: str) -> dict[str, Any]:
        try:
            proc = subprocess.run(command, shell=True, cwd=worktree, capture_output=True, text=True, timeout=timeout)
            result = "passed" if proc.returncode == 0 else "failed"
            detail = (proc.stdout + proc.stderr)[-1500:]
        except subprocess.TimeoutExpired:
            result, detail = "not_run", f"timed out after {timeout}s"
        return {"kind": kind, "command": command, "result": result, "detail": detail}

    for command in config["validation_commands"]:
        results.append(run("validation", command))
    e2e = config["e2e"]
    if not e2e.get("command"):
        results.append({"kind": "e2e", "command": "", "result": "not_run", "detail": "e2e.command not configured"})
    else:
        setup_ok = True
        if e2e.get("setup"):
            setup = run("e2e-setup", e2e["setup"])
            results.append(setup)
            setup_ok = setup["result"] == "passed"
        if setup_ok:
            results.append(run("e2e", e2e["command"]))
        else:
            results.append({"kind": "e2e", "command": e2e["command"], "result": "not_run", "detail": "environment setup failed"})
    return results


def _not_validated(state: dict[str, Any]) -> bool:
    return any(r["result"] != "passed" for r in state["validation"]) or not state["validation"]


def _open_pr(repo: Repo, state: dict[str, Any], config: dict[str, Any]) -> str:
    vcs = config["vcs"]
    worktree = Path(state["worktree"])
    report_path = write_report(repo, state)
    if vcs["provider"] == "none":
        return ""
    _git(worktree, "push", "-q", "-u", vcs["remote"], state["branch"])
    labels = []
    if state["high_risk"]:
        labels += vcs["high_risk_labels"]
    if _not_validated(state):
        labels += vcs["not_validated_labels"]
    title = f"forge(autopilot): {state['slug']}"
    if vcs["provider"] == "github":
        command = ["gh", "pr", "create", "--base", vcs["base"], "--head", state["branch"],
                   "--title", title, "--body-file", str(report_path)]
        if vcs["draft"]:
            command.append("--draft")
        for label in labels:
            command += ["--label", label]
    elif vcs["provider"] == "gitlab":
        command = ["glab", "mr", "create", "--target-branch", vcs["base"], "--source-branch", state["branch"],
                   "--title", title, "--description", report_path.read_text(encoding="utf-8"), "--yes"]
        if vcs["draft"]:
            command.append("--draft")
        if labels:
            command += ["--label", ",".join(labels)]
    else:
        raise AutopilotError(f"unknown vcs.provider: {vcs['provider']}")
    result = subprocess.run(command, cwd=worktree, capture_output=True, text=True)
    if result.returncode != 0:
        raise AutopilotError(f"{command[0]} failed: {result.stderr.strip()}")
    urls = re.findall(r"https?://\S+", result.stdout)
    return urls[-1] if urls else result.stdout.strip()


# ---------------------------------------------------------------------------
# presentation


def render_report(state: dict[str, Any]) -> str:
    lines = [f"# Autopilot report: {state['slug']}", ""]
    lines.append(f"Run `{state['run_id']}` from `{state['source']}`, branch `{state['branch']}`.")
    lines.append("")
    lines.append("## Decisions taken by autopilot")
    lines.append("")
    lines.extend([f"- {d}" for d in state["decisions"]] or ["- none recorded"])
    lines += ["", "## Risk", ""]
    lines.append("High-risk: " + ("yes" if state["high_risk"] else "no"))
    lines.extend(f"- {r}" for r in state["risk_reasons"])
    lines += ["", "## Gates", "", "| Stage | Result | Reasons |", "|---|---|---|"]
    for g in state["gates"]:
        lines.append(f"| {g['stage']} | {'pass' if g['passed'] else 'fail'} | {'; '.join(g['reasons'])} |")
    lines += ["", "## Validation", "", "| Kind | Command | Result |", "|---|---|---|"]
    for r in state["validation"]:
        lines.append(f"| {r['kind']} | `{r['command']}` | {r['result']} |")
    if _not_validated(state):
        lines += ["", "Status: `not_validated`. At least one check failed or did not run."]
    lines += ["", "## Agents", ""]
    lines.extend(f"- {i['stage']}: {i['agent']} (exit {i['exit_code']})" for i in state["invocations"])
    lines += ["", "Merge is a human decision. Forge never merges."]
    return "\n".join(lines) + "\n"


def write_report(repo: Repo, state: dict[str, Any]) -> Path:
    report = render_report(state)
    path = repo.runs_dir / state["run_id"] / "report.md"
    path.write_text(report, encoding="utf-8")
    dated = state["created"][:10]
    generated = repo.root / ".forge/generated/reports" / f"{dated}-{state['slug']}-autopilot-report.md"
    generated.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text(report, encoding="utf-8")
    return path


def render_status(state: dict[str, Any]) -> str:
    lines = [f"{state['run_id']}  [{state['status']}]"]
    for stage in STAGES:
        skipped = next((p for p in state["passed"] if p.startswith(stage + " (skipped")), None)
        if skipped:
            mark = "[-]"
        elif stage in state["passed"]:
            mark = "[x]"
        elif stage == state["stage"] and state["status"] == "running":
            mark = "[>]"
        else:
            mark = "[ ]"
        lines.append(f"  {mark} {stage}")
    if state["blocked_reason"]:
        lines.append(f"  blocked: {state['blocked_reason']}")
    if state["decisions"]:
        lines.append(f"  decisions: {len(state['decisions'])}")
    if state["high_risk"]:
        lines.append("  high-risk: " + "; ".join(state["risk_reasons"]))
    if state["pr_url"]:
        lines.append(f"  PR: {state['pr_url']}")
    return "\n".join(lines)


def stop_run(repo: Repo, run_id: str) -> dict[str, Any]:
    state = load_state(repo, run_id)
    state["status"] = "cancelled"
    save_state(repo, state)
    return state


def resume_run(repo: Repo, run_id: str) -> dict[str, Any]:
    _check_stop(repo)
    state = load_state(repo, run_id)
    if state["status"] != "blocked":
        raise AutopilotError(f"run is {state['status']}, only blocked runs resume")
    state["status"] = "running"
    state["blocked_reason"] = ""
    save_state(repo, state)
    return state

