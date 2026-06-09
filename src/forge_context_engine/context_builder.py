"""Seed initial Forge context from repository evidence during init."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re


EXCLUDED_DIRS = {
    ".git",
    ".forge",
    ".venv",
    ".idea",
    ".vscode",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "coverage",
    "__pycache__",
}
MAX_FILES_SCANNED = 400
MAX_FILE_BYTES = 32_000


@dataclass(frozen=True)
class RepoContextSeed:
    """Generated user-owned context files for a target repository."""

    files: dict[str, str]


@dataclass(frozen=True)
class EvidenceFile:
    """A small repository file reference used as evidence."""

    path: str
    snippet: str


@dataclass(frozen=True)
class RepoFacts:
    """Bounded facts inferred from a repository scan."""

    repo_name: str
    profile: str
    today: str
    source_commit: str
    summary: str
    architecture_style: str
    stack: tuple[str, ...]
    runtimes: tuple[str, ...]
    key_paths: tuple[str, ...]
    system_name: str
    system_type: str
    readme_evidence: tuple[EvidenceFile, ...]
    manifest_evidence: tuple[EvidenceFile, ...]
    structure_evidence: tuple[EvidenceFile, ...]
    tests_present: bool
    ci_present: bool
    formatter_present: bool
    deployment_present: bool
    docs_present: bool
    api_surface_present: bool
    package_managers: tuple[str, ...]
    unknowns: tuple[str, ...]


def build_repo_context_seed(*, target_root: Path, profile: str) -> RepoContextSeed:
    """Create initial repo-owned context content from bounded repository evidence."""

    facts = _scan_repo(target_root=target_root, profile=profile)
    files = {
        ".forge/context/01-core/product.md": _render_product(facts),
        ".forge/context/01-core/architecture.md": _render_architecture(facts),
        ".forge/context/01-core/principles.md": _render_principles(facts),
        ".forge/context/01-core/constraints.md": _render_constraints(facts),
        ".forge/context/knowledge/inferred.md": _render_inferred(facts),
        ".forge/context/knowledge/unknowns.md": _render_unknowns(facts),
        ".forge/context/repo-map/overview.md": _render_repo_map(facts),
    }
    if profile == "service":
        files[f".forge/context/systems/{facts.system_name}/system.md"] = _render_system(facts)
    return RepoContextSeed(files=files)


def _scan_repo(*, target_root: Path, profile: str) -> RepoFacts:
    repo_name = _slug(target_root.name) or "service"
    today = date.today().isoformat()
    source_commit = _read_git_head(target_root)

    files = _list_repo_files(target_root)
    readme_paths = [path for path in files if path.lower() in {"readme.md", "readme"}]
    manifest_names = (
        "pyproject.toml",
        "package.json",
        "go.mod",
        "Cargo.toml",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "Gemfile",
        "composer.json",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "Makefile",
    )
    manifest_paths = [path for path in files if path in manifest_names]
    key_paths = _select_key_paths(files)

    readme_evidence = _collect_evidence(target_root, readme_paths[:2])
    manifest_evidence = _collect_evidence(target_root, manifest_paths[:6])
    structure_evidence = tuple(EvidenceFile(path=path, snippet="directory present") for path in key_paths[:8])

    package_managers = _detect_package_managers(files)
    stack = _detect_stack(files)
    runtimes = _detect_runtimes(files, target_root)
    tests_present = any(
        path.startswith(("tests/", "test/", "spec/")) or path.endswith(("_test.go", ".spec.ts", ".spec.js", "_test.py"))
        for path in files
    )
    ci_present = any(path.startswith(".github/workflows/") for path in files)
    formatter_present = any(
        path in {".editorconfig", "ruff.toml", ".eslintrc", ".eslintrc.json", ".prettierrc", "biome.json"}
        or path.startswith((".github/", ".vscode/"))
        for path in files
    )
    deployment_present = any(
        path in {"Dockerfile", "docker-compose.yml", "docker-compose.yaml", "Procfile", "helmfile.yaml"}
        or path.startswith(("deploy/", "k8s/", "helm/", ".github/workflows/"))
        for path in files
    )
    docs_present = any(path.startswith(("docs/", "adr/", "decisions/")) for path in files)
    api_surface_present = any(
        path.startswith(("api/", "routes/", "handlers/", "cmd/"))
        or path.endswith((".proto", "openapi.yaml", "openapi.yml"))
        for path in files
    )

    summary = _derive_summary(target_root.name, readme_evidence, manifest_evidence, stack)
    architecture_style = _derive_architecture_style(files, profile)
    unknowns = _derive_unknowns(
        readme_evidence=readme_evidence,
        docs_present=docs_present,
        deployment_present=deployment_present,
        api_surface_present=api_surface_present,
    )

    return RepoFacts(
        repo_name=target_root.name,
        profile=profile,
        today=today,
        source_commit=source_commit,
        summary=summary,
        architecture_style=architecture_style,
        stack=stack,
        runtimes=runtimes,
        key_paths=tuple(key_paths),
        system_name=repo_name,
        system_type="service",
        readme_evidence=readme_evidence,
        manifest_evidence=manifest_evidence,
        structure_evidence=structure_evidence,
        tests_present=tests_present,
        ci_present=ci_present,
        formatter_present=formatter_present,
        deployment_present=deployment_present,
        docs_present=docs_present,
        api_surface_present=api_surface_present,
        package_managers=package_managers,
        unknowns=unknowns,
    )


def _list_repo_files(target_root: Path) -> list[str]:
    files: list[str] = []
    for path in target_root.rglob("*"):
        try:
            rel = path.relative_to(target_root)
        except ValueError:
            continue
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if path.is_dir():
            continue
        files.append(rel.as_posix())
        if len(files) >= MAX_FILES_SCANNED:
            break
    files.sort()
    return files


def _collect_evidence(target_root: Path, rel_paths: list[str]) -> tuple[EvidenceFile, ...]:
    items: list[EvidenceFile] = []
    for rel_path in rel_paths:
        sample = _sample_file(target_root, rel_path)
        if sample is not None:
            items.append(sample)
    return tuple(items)

def _sample_file(target_root: Path, rel_path: str) -> EvidenceFile | None:
    path = target_root / rel_path
    if not path.exists() or not path.is_file():
        return None
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return EvidenceFile(path=rel_path, snippet="file present")
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    snippet = _first_meaningful_line(raw)
    return EvidenceFile(path=rel_path, snippet=snippet or "file present")


def _first_meaningful_line(content: str) -> str:
    heading_fallback = ""
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line in {"{", "}", "[", "]"}:
            continue
        normalized = re.sub(r"\s+", " ", line)[:140]
        if line.startswith("#"):
            if not heading_fallback:
                heading_fallback = normalized.lstrip("# ").strip()
            continue
        return normalized
    return heading_fallback


def _detect_stack(files: list[str]) -> tuple[str, ...]:
    stack: list[str] = []
    if "pyproject.toml" in files or any(path.endswith(".py") for path in files):
        stack.append("python")
    if "package.json" in files or any(path.endswith((".ts", ".tsx", ".js", ".jsx")) for path in files):
        stack.append("node")
    if "go.mod" in files or any(path.endswith(".go") for path in files):
        stack.append("go")
    if "Cargo.toml" in files or any(path.endswith(".rs") for path in files):
        stack.append("rust")
    if "pom.xml" in files or "build.gradle" in files or "build.gradle.kts" in files:
        stack.append("jvm")
    if not stack:
        stack.append("unknown")
    return tuple(stack)


def _detect_runtimes(files: list[str], target_root: Path) -> tuple[str, ...]:
    runtimes: list[str] = []
    pyproject = target_root / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r'requires-python\s*=\s*"([^"]+)"', content)
        if match:
            runtimes.append(f"python {match.group(1)}")
    package_json = target_root / "package.json"
    if package_json.exists():
        content = package_json.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r'"node"\s*:\s*"([^"]+)"', content)
        if match:
            runtimes.append(f"node {match.group(1)}")
    if "go.mod" in files:
        content = (target_root / "go.mod").read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"^go\s+([0-9.]+)$", content, flags=re.MULTILINE)
        if match:
            runtimes.append(f"go {match.group(1)}")
    return tuple(runtimes)


def _detect_package_managers(files: list[str]) -> tuple[str, ...]:
    detected: list[str] = []
    mapping = {
        "pyproject.toml": "python packaging",
        "package.json": "npm-compatible",
        "go.mod": "go modules",
        "Cargo.toml": "cargo",
        "pom.xml": "maven",
        "build.gradle": "gradle",
        "build.gradle.kts": "gradle",
    }
    for name, label in mapping.items():
        if name in files and label not in detected:
            detected.append(label)
    return tuple(detected)


def _select_key_paths(files: list[str]) -> list[str]:
    preferred = [
        "src",
        "app",
        "cmd",
        "internal",
        "pkg",
        "services",
        "packages",
        "api",
        "docs",
        "tests",
        ".github/workflows",
    ]
    dirs = sorted({path.split("/", 1)[0] for path in files if "/" in path})
    selected = [path for path in preferred if path in dirs]
    for path in dirs:
        if path not in selected:
            selected.append(path)
        if len(selected) >= 8:
            break
    return selected


def _derive_summary(
    repo_name: str,
    readme_evidence: tuple[EvidenceFile, ...],
    manifest_evidence: tuple[EvidenceFile, ...],
    stack: tuple[str, ...],
) -> str:
    for evidence in readme_evidence:
        text = evidence.snippet.lstrip("#- ").strip()
        if text and len(text.split()) >= 3:
            return text
    for evidence in manifest_evidence:
        text = evidence.snippet.strip()
        if "description" in text.lower() or "module" in text.lower() or "name" in text.lower():
            return text
    return f"{repo_name} appears to be a {', '.join(stack)} repository based on the current top-level manifests and source layout."


def _derive_architecture_style(files: list[str], profile: str) -> str:
    if profile == "workspace":
        return "workspace coordination repo"
    if any(path.startswith("packages/") for path in files) or any(path.startswith("services/") for path in files):
        return "monorepo or multi-package service layout"
    if any(path.startswith("cmd/") for path in files) and any(path.startswith("internal/") for path in files):
        return "layered service layout"
    if any(path.startswith("src/") for path in files) or any(path.startswith("app/") for path in files):
        return "single-service application layout"
    return "repository structure present, but architecture style still needs confirmation"


def _derive_unknowns(
    *,
    readme_evidence: tuple[EvidenceFile, ...],
    docs_present: bool,
    deployment_present: bool,
    api_surface_present: bool,
) -> tuple[str, ...]:
    unknowns = ["Repository owner and confirmation authority are not discoverable from code alone."]
    if not readme_evidence:
        unknowns.append("No README summary was found, so product intent still needs explicit confirmation.")
    if not docs_present:
        unknowns.append("Architecture and decision documents are sparse or absent, so intent-level reasoning remains inferred.")
    if not deployment_present:
        unknowns.append("Deployment topology is not yet evidenced in the scanned repository surface.")
    if not api_surface_present:
        unknowns.append("Public API or interface boundaries are not obvious from the current top-level structure.")
    return tuple(unknowns)


def _read_git_head(target_root: Path) -> str:
    git_dir = target_root / ".git"
    head_path = git_dir / "HEAD"
    if not head_path.exists():
        return "unknown"
    try:
        head = head_path.read_text(encoding="utf-8", errors="ignore").strip()
    except OSError:
        return "unknown"
    if not head.startswith("ref:"):
        return head[:12] or "unknown"
    ref = head.split(" ", 1)[1].strip()
    ref_path = git_dir / ref
    if ref_path.exists():
        try:
            return ref_path.read_text(encoding="utf-8", errors="ignore").strip()[:12] or "unknown"
        except OSError:
            return "unknown"
    packed_refs = git_dir / "packed-refs"
    if packed_refs.exists():
        try:
            for line in packed_refs.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("#") or line.startswith("^") or not line.strip():
                    continue
                sha, _, name = line.partition(" ")
                if name.strip() == ref:
                    return sha[:12] or "unknown"
        except OSError:
            return "unknown"
    return "unknown"


def _render_product(facts: RepoFacts) -> str:
    evidence_paths = _unique_paths(facts.readme_evidence + facts.manifest_evidence)
    summary_lines = [f"- {facts.summary}"]
    scope_lines = [f"- Primary repository name: `{facts.repo_name}`."]
    if facts.stack and facts.stack != ("unknown",):
        scope_lines.append(f"- Current implementation stack evidence: {', '.join(f'`{item}`' for item in facts.stack)}.")
    unknown_lines = [
        "- Human-confirmed product goals, users, and business priority are still unresolved.",
    ]
    return _render_card(
        card_id="core.product",
        title="Product Context",
        card_type="core",
        status="inferred" if evidence_paths else "unknown",
        confidence="medium" if evidence_paths else "low",
        source="ai" if evidence_paths else "human",
        owner="unresolved",
        updated=facts.today,
        source_paths=evidence_paths or ["README.md"],
        source_commit=facts.source_commit,
        last_verified=facts.today,
        body_sections=[
            ("Summary", summary_lines),
            ("Inferred Scope", scope_lines),
            ("Still Needs Confirmation", unknown_lines),
            ("Evidence", _render_evidence_lines(facts.readme_evidence + facts.manifest_evidence)),
        ],
    )


def _render_architecture(facts: RepoFacts) -> str:
    evidence_paths = _unique_paths(facts.manifest_evidence + facts.structure_evidence + facts.readme_evidence)
    lines = [f"- Current structure suggests a **{facts.architecture_style}**."]
    if facts.key_paths:
        lines.append(f"- High-signal directories: {', '.join(f'`{path}/`' for path in facts.key_paths)}.")
    if facts.package_managers:
        lines.append(f"- Package/build surface: {', '.join(facts.package_managers)}.")
    if facts.api_surface_present:
        lines.append("- Repository surface appears to expose an application or API entrypoint.")
    if facts.deployment_present:
        lines.append("- Deployment or runtime automation files are present in the repository.")
    return _render_card(
        card_id="core.architecture",
        title="Architecture Context",
        card_type="core",
        status="inferred" if evidence_paths else "unknown",
        confidence="medium" if evidence_paths else "low",
        source="ai" if evidence_paths else "human",
        owner="unresolved",
        updated=facts.today,
        source_paths=evidence_paths or [".forge/context/knowledge/unknowns.md"],
        source_commit=facts.source_commit,
        last_verified=facts.today,
        body_sections=[
            ("Current Shape", lines),
            (
                "Open Questions",
                [
                    "- Runtime topology, production dependencies, and ownership still need human confirmation.",
                    "- External contracts should be validated from code paths deeper than this bounded init scan when needed.",
                ],
            ),
            ("Evidence", _render_evidence_lines(facts.manifest_evidence + facts.structure_evidence + facts.readme_evidence)),
        ],
    )


def _render_principles(facts: RepoFacts) -> str:
    evidence = list(facts.structure_evidence)
    lines: list[str] = []
    if facts.tests_present:
        lines.append("- Existing automated tests indicate changes should preserve or extend the current validation surface.")
    if facts.ci_present:
        lines.append("- CI workflow files suggest repository changes should stay compatible with automated checks.")
    if facts.formatter_present:
        lines.append("- Repository-local formatting or editor config should be followed before introducing new style conventions.")
    if not lines:
        lines.append("- Engineering principles are not safely inferable from the bounded init scan and need human confirmation.")
    return _render_card(
        card_id="core.principles",
        title="Engineering Principles",
        card_type="core",
        status="inferred" if facts.tests_present or facts.ci_present or facts.formatter_present else "unknown",
        confidence="medium" if facts.tests_present or facts.ci_present or facts.formatter_present else "low",
        source="ai" if facts.tests_present or facts.ci_present or facts.formatter_present else "human",
        owner="unresolved",
        updated=facts.today,
        source_paths=_unique_paths(evidence) or [".forge/context/knowledge/unknowns.md"],
        source_commit=facts.source_commit,
        last_verified=facts.today,
        body_sections=[
            ("Working Principles", lines),
            ("Evidence", _render_evidence_lines(tuple(evidence))),
        ],
    )


def _render_constraints(facts: RepoFacts) -> str:
    lines: list[str] = []
    if facts.runtimes:
        lines.append(f"- Runtime versions evidenced in manifests: {', '.join(f'`{item}`' for item in facts.runtimes)}.")
    if facts.package_managers:
        lines.append(f"- Repository depends on these build/package surfaces: {', '.join(facts.package_managers)}.")
    if facts.deployment_present:
        lines.append("- Deployment-related files exist, so runtime packaging or delivery conventions should be preserved during changes.")
    if not lines:
        lines.append("- Hard technical constraints are not yet explicit in the scanned repository surface.")
    return _render_card(
        card_id="core.constraints",
        title="Hard Constraints",
        card_type="core",
        status="inferred" if facts.runtimes or facts.package_managers or facts.deployment_present else "unknown",
        confidence="medium" if facts.runtimes or facts.package_managers or facts.deployment_present else "low",
        source="ai" if facts.runtimes or facts.package_managers or facts.deployment_present else "human",
        owner="unresolved",
        updated=facts.today,
        source_paths=_unique_paths(facts.manifest_evidence + facts.structure_evidence) or [".forge/context/knowledge/unknowns.md"],
        source_commit=facts.source_commit,
        last_verified=facts.today,
        body_sections=[
            ("Current Constraints", lines),
            ("Evidence", _render_evidence_lines(facts.manifest_evidence + facts.structure_evidence)),
        ],
    )


def _render_system(facts: RepoFacts) -> str:
    evidence_paths = _unique_paths(facts.structure_evidence + facts.manifest_evidence)
    return _render_card(
        card_id=f"system.{facts.system_name}",
        title=f"System Context: {facts.system_name}",
        card_type="system",
        status="inferred" if evidence_paths else "unknown",
        confidence="medium" if evidence_paths else "low",
        source="ai" if evidence_paths else "human",
        owner="unresolved",
        updated=facts.today,
        source_paths=evidence_paths or [".forge/context/knowledge/unknowns.md"],
        source_commit=facts.source_commit,
        last_verified=facts.today,
        extra_front_matter={"system_type": facts.system_type},
        body_sections=[
            ("Responsibilities", [f"- `{facts.repo_name}` is currently treated as the primary implementation unit for this repository."]),
            ("Relevant Paths", [f"- `{path}/`" for path in facts.key_paths] or ["- No high-signal directories were detected during init."]),
            (
                "Runtime Notes",
                [
                    "- Unit-specific business behavior still needs confirmation from deeper code review and human validation.",
                ],
            ),
            ("Evidence", _render_evidence_lines(facts.structure_evidence + facts.manifest_evidence)),
        ],
    )


def _render_repo_map(facts: RepoFacts) -> str:
    lines = [f"- `{path}/`" for path in facts.key_paths] or ["- No high-signal directories detected in the bounded init scan."]
    manifest_lines = [f"- `{evidence.path}`: {evidence.snippet}" for evidence in facts.manifest_evidence] or ["- No top-level manifests found."]
    return _render_card(
        card_id="repo-map.overview",
        title="Repository Map Overview",
        card_type="map",
        status="inferred",
        confidence="medium",
        source="ai",
        owner="unresolved",
        updated=facts.today,
        source_paths=_unique_paths(facts.manifest_evidence + facts.structure_evidence) or ["README.md"],
        source_commit=facts.source_commit,
        last_verified=facts.today,
        body_sections=[
            ("High-Signal Paths", lines),
            ("Key Top-Level Files", manifest_lines),
        ],
    )


def _render_inferred(facts: RepoFacts) -> str:
    entries = [
        (
            "I-001",
            f"`{facts.repo_name}` currently looks like a {facts.architecture_style}.",
            _join_paths(_unique_paths(facts.structure_evidence + facts.manifest_evidence + facts.readme_evidence)),
        ),
    ]
    if facts.stack and facts.stack != ("unknown",):
        entries.append(
            (
                "I-002",
                f"Primary implementation stack inferred from repository manifests: {', '.join(facts.stack)}.",
                _join_paths(_unique_paths(facts.manifest_evidence + facts.structure_evidence)),
            )
        )
    if facts.tests_present:
        entries.append(("I-003", "Automated test assets are already present in the repository.", _join_paths(_paths_matching(facts, "tests"))))

    table = [
        "| ID | Inference | Evidence | Owner | Created | Status |",
        "|---|---|---|---|---|---|",
    ]
    for entry_id, inference, evidence in entries:
        table.append(f"| {entry_id} | {inference} | {evidence} | unresolved | {facts.today} | inferred |")
    return _render_ledger(
        card_id="knowledge.inferred",
        title="Inferred Knowledge Ledger",
        heading="Inferred",
        intro="AI inference ledger seeded from bounded repository evidence during init. Non-authoritative until confirmed.",
        updated=facts.today,
        table_lines=table,
    )


def _render_unknowns(facts: RepoFacts) -> str:
    table = [
        "| ID | Question / Gap | Priority | Owner | Created | Status | Resolution |",
        "|---|---|---|---|---|---|---|",
    ]
    for index, item in enumerate(facts.unknowns, start=1):
        table.append(f"| U-{index:03d} | {item} | important | unresolved | {facts.today} | open | Pending human confirmation. |")
    return _render_ledger(
        card_id="knowledge.unknowns",
        title="Unknowns Ledger",
        heading="Unknowns",
        intro="Knowledge gaps discovered during bounded init. These are explicit unknowns, not guesses.",
        updated=facts.today,
        table_lines=table,
    )


def _render_card(
    *,
    card_id: str,
    title: str,
    card_type: str,
    status: str,
    confidence: str,
    source: str,
    owner: str,
    updated: str,
    source_paths: list[str],
    source_commit: str,
    last_verified: str,
    body_sections: list[tuple[str, list[str]]],
    extra_front_matter: dict[str, str] | None = None,
) -> str:
    front_matter = [
        "---",
        f"id: {card_id}",
        f'title: "{title}"',
        f"type: {card_type}",
        f"status: {status}",
        f"confidence: {confidence}",
        f"source: {source}",
        f"owner: {owner}",
        f"updated: {updated}",
        "source_paths:",
    ]
    for path in source_paths:
        front_matter.append(f"  - {path}")
    front_matter.extend(
        [
            f"source_commit: {source_commit}",
            f"last_verified: {last_verified}",
        ]
    )
    for key, value in (extra_front_matter or {}).items():
        front_matter.append(f"{key}: {value}")
    front_matter.append("---")

    body = [f"# {title.replace(' Context', '')}"]
    for section, lines in body_sections:
        body.append("")
        body.append(f"## {section}")
        body.extend(lines or ["- None recorded."])
    return "\n".join(front_matter + [""] + body) + "\n"


def _render_ledger(
    *,
    card_id: str,
    title: str,
    heading: str,
    intro: str,
    updated: str,
    table_lines: list[str],
) -> str:
    return (
        "---\n"
        f"id: {card_id}\n"
        f'title: "{title}"\n'
        "type: knowledge\n"
        "status: confirmed\n"
        "confidence: high\n"
        "source: human\n"
        "owner: unresolved\n"
        f"updated: {updated}\n"
        "---\n\n"
        f"# {heading}\n\n"
        f"{intro}\n\n"
        + "\n".join(table_lines)
        + "\n"
    )


def _render_evidence_lines(evidence_items: tuple[EvidenceFile, ...]) -> list[str]:
    if not evidence_items:
        return ["- No direct repository evidence captured in the bounded init scan."]
    return [f"- `{item.path}`: {item.snippet}" for item in evidence_items]


def _unique_paths(evidence_items: tuple[EvidenceFile, ...]) -> list[str]:
    paths: list[str] = []
    for item in evidence_items:
        if item.path not in paths:
            paths.append(item.path)
    return paths


def _paths_matching(facts: RepoFacts, prefix: str) -> list[str]:
    paths = [item.path for item in facts.structure_evidence if item.path.startswith(prefix)]
    return paths or [f"{prefix}/"]


def _join_paths(paths: list[str]) -> str:
    return ", ".join(f"`{path}`" for path in paths) if paths else "`unknown`"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
