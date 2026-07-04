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
NO_DIRECT_EVIDENCE = "No direct evidence found in bounded init scan."


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
    readme_evidence: tuple[EvidenceFile, ...]
    manifest_evidence: tuple[EvidenceFile, ...]
    structure_evidence: tuple[EvidenceFile, ...]
    package_managers: tuple[str, ...]
    tests_present: bool
    ci_present: bool
    formatter_present: bool
    deployment_present: bool
    docs_present: bool
    api_paths: tuple[str, ...]
    database_paths: tuple[str, ...]
    business_rule_paths: tuple[str, ...]
    integration_paths: tuple[str, ...]
    error_paths: tuple[str, ...]
    observability_paths: tuple[str, ...]
    security_paths: tuple[str, ...]
    release_paths: tuple[str, ...]
    workspace_service_paths: tuple[str, ...]
    unknowns: tuple[str, ...]


def build_repo_context_seed(*, target_root: Path, profile: str) -> RepoContextSeed:
    """Create initial repo-owned context content from bounded repository evidence."""

    facts = _scan_repo(target_root=target_root, profile=profile)
    if profile == "workspace":
        return _build_workspace_context_seed(facts)
    return _build_service_context_seed(facts)


def _build_service_context_seed(facts: RepoFacts) -> RepoContextSeed:
    files = {
        ".forge/context/00-index.md": _render_index(facts),
        ".forge/context/01-service-overview.md": _render_service_overview(facts),
        ".forge/context/02-architecture.md": _render_service_architecture(facts),
        ".forge/context/03-domain-boundaries.md": _render_domain_boundaries(facts),
        ".forge/context/04-interfaces-and-contracts.md": _render_service_interfaces_and_contracts(facts),
        ".forge/context/05-data-and-persistence.md": _render_service_data_and_persistence(facts),
        ".forge/context/06-business-rules-and-flows.md": _render_service_business_rules_and_flows(facts),
        ".forge/context/07-integrations-and-dependencies.md": _render_service_integrations_and_dependencies(facts),
        ".forge/context/08-security-and-access.md": _render_service_security_and_access(facts),
        ".forge/context/09-errors-and-resilience.md": _render_service_errors_and_resilience(facts),
        ".forge/context/10-observability-and-support.md": _render_service_observability_and_support(facts),
        ".forge/context/11-testing-and-quality.md": _render_service_testing_and_quality(facts),
        ".forge/context/12-runtime-deployment-and-config.md": _render_service_runtime_deployment_and_config(facts),
        ".forge/context/13-operations-and-runbook.md": _render_service_operations_and_runbook(facts),
        ".forge/context/14-decisions-assumptions-and-constraints.md": _render_service_decisions_assumptions_and_constraints(facts),
        ".forge/context/98-glossary.md": _render_glossary(facts, profile_scope="service"),
        ".forge/context/99-open-questions.md": _render_open_questions(facts, profile_scope="service"),
    }
    return RepoContextSeed(files=files)


def _build_workspace_context_seed(facts: RepoFacts) -> RepoContextSeed:
    files = {
        ".forge/context/00-index.md": _render_index(facts),
        ".forge/context/01-platform-overview.md": _render_platform_overview(facts),
        ".forge/context/02-system-map.md": _render_workspace_system_map(facts),
        ".forge/context/03-service-catalog.md": _render_workspace_service_catalog(facts),
        ".forge/context/04-domain-boundaries.md": _render_workspace_domain_boundaries(facts),
        ".forge/context/05-cross-service-flows.md": _render_workspace_cross_service_flows(facts),
        ".forge/context/06-interfaces-and-contracts.md": _render_workspace_interfaces_and_contracts(facts),
        ".forge/context/07-data-ownership-and-consistency.md": _render_workspace_data_ownership_and_consistency(facts),
        ".forge/context/08-security-and-access.md": _render_workspace_security_access(facts),
        ".forge/context/09-observability-and-support.md": _render_workspace_observability_and_support(facts),
        ".forge/context/10-testing-and-quality.md": _render_workspace_testing_and_quality(facts),
        ".forge/context/11-runtime-deployment-and-config.md": _render_workspace_runtime_deployment_and_config(facts),
        ".forge/context/12-release-and-feature-flags.md": _render_workspace_release_and_feature_flags(facts),
        ".forge/context/13-operations-and-runbook.md": _render_workspace_operations_and_runbook(facts),
        ".forge/context/14-decisions-assumptions-and-constraints.md": _render_workspace_decisions_assumptions_and_constraints(facts),
        ".forge/context/98-glossary.md": _render_glossary(facts, profile_scope="workspace"),
        ".forge/context/99-open-questions.md": _render_open_questions(facts, profile_scope="workspace"),
    }
    return RepoContextSeed(files=files)


def _scan_repo(*, target_root: Path, profile: str) -> RepoFacts:
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
        path.startswith(("tests/", "test/", "spec/"))
        or path.endswith(("_test.go", ".spec.ts", ".spec.js", "_test.py"))
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

    api_paths = _match_paths(
        files,
        prefixes=("api/", "routes/", "handlers/", "cmd/"),
        suffixes=(".proto", "openapi.yaml", "openapi.yml"),
    )
    database_paths = _match_paths(
        files,
        prefixes=("migrations/", "db/", "database/", "sql/", "prisma/", "alembic/"),
        suffixes=(".sql", "schema.prisma"),
        contains=("migration",),
    )
    business_rule_paths = _match_paths(
        files,
        prefixes=("domain/", "business/", "rules/"),
        contains=("validator", "policy", "rule", "domain"),
    )
    integration_paths = _match_paths(
        files,
        prefixes=("integrations/", "providers/", "clients/", "adapters/", "sdk/"),
        contains=("integration", "provider", "client", "webhook", "external"),
    )
    error_paths = _match_paths(
        files,
        prefixes=("middleware/",),
        contains=("error", "exception", "retry", "circuit"),
    )
    observability_paths = _match_paths(
        files,
        prefixes=("observability/", "telemetry/", "tracing/", "metrics/", "logging/"),
        contains=("prometheus", "grafana", "otel", "opentelemetry", "sentry", "trace", "metric", "log"),
    )
    security_paths = _match_paths(
        files,
        prefixes=("auth/", "security/"),
        contains=("auth", "oauth", "rbac", "permission", "iam"),
    )
    release_paths = _match_paths(
        files,
        contains=("feature_flag", "feature-flag", "featureflag", "launchdarkly", "unleash", "toggle", "release"),
    )
    workspace_service_paths = _derive_workspace_service_paths(files)

    summary = _derive_summary(target_root.name, readme_evidence, manifest_evidence, stack)
    architecture_style = _derive_architecture_style(files, profile)
    unknowns = _derive_unknowns(
        profile=profile,
        readme_evidence=readme_evidence,
        docs_present=docs_present,
        api_paths=api_paths,
        database_paths=database_paths,
        integration_paths=integration_paths,
        deployment_present=deployment_present,
        workspace_service_paths=workspace_service_paths,
        security_paths=security_paths,
        release_paths=release_paths,
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
        readme_evidence=readme_evidence,
        manifest_evidence=manifest_evidence,
        structure_evidence=structure_evidence,
        package_managers=package_managers,
        tests_present=tests_present,
        ci_present=ci_present,
        formatter_present=formatter_present,
        deployment_present=deployment_present,
        docs_present=docs_present,
        api_paths=api_paths,
        database_paths=database_paths,
        business_rule_paths=business_rule_paths,
        integration_paths=integration_paths,
        error_paths=error_paths,
        observability_paths=observability_paths,
        security_paths=security_paths,
        release_paths=release_paths,
        workspace_service_paths=workspace_service_paths,
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


def _match_paths(
    files: list[str],
    *,
    prefixes: tuple[str, ...] = (),
    suffixes: tuple[str, ...] = (),
    contains: tuple[str, ...] = (),
    limit: int = 8,
) -> tuple[str, ...]:
    matched: list[str] = []
    for path in files:
        lower = path.lower()
        if prefixes and any(lower.startswith(prefix) for prefix in prefixes):
            matched.append(path)
        elif suffixes and any(lower.endswith(suffix) for suffix in suffixes):
            matched.append(path)
        elif contains and any(token in lower for token in contains):
            matched.append(path)
        if len(matched) >= limit:
            break
    return tuple(matched)


def _derive_workspace_service_paths(files: list[str]) -> tuple[str, ...]:
    candidates: list[str] = []
    for prefix in ("services/", "packages/", "apps/"):
        seen: set[str] = set()
        for path in files:
            if not path.startswith(prefix):
                continue
            parts = path.split("/")
            if len(parts) < 2:
                continue
            candidate = f"{parts[0]}/{parts[1]}"
            if candidate not in seen:
                seen.add(candidate)
                candidates.append(candidate)
            if len(candidates) >= 8:
                return tuple(candidates)
    return tuple(candidates)


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
    profile: str,
    readme_evidence: tuple[EvidenceFile, ...],
    docs_present: bool,
    api_paths: tuple[str, ...],
    database_paths: tuple[str, ...],
    integration_paths: tuple[str, ...],
    deployment_present: bool,
    workspace_service_paths: tuple[str, ...],
    security_paths: tuple[str, ...],
    release_paths: tuple[str, ...],
) -> tuple[str, ...]:
    unknowns = ["Repository owner and confirmation authority are not discoverable from code alone."]
    if not readme_evidence:
        unknowns.append("No README summary was found, so product intent still needs explicit confirmation.")
    if not docs_present:
        unknowns.append("Architecture and decision documents are sparse or absent, so intent-level reasoning remains inferred.")
    if profile == "service":
        if not api_paths:
            unknowns.append("Service API contracts were not directly evidenced in the bounded init scan.")
        if not database_paths:
            unknowns.append("Data model and database details were not directly evidenced in the bounded init scan.")
        if not integration_paths:
            unknowns.append("Integration dependencies were not directly evidenced in the bounded init scan.")
        if not deployment_present:
            unknowns.append("Runtime and deployment topology are not yet evidenced in the scanned repository surface.")
        return tuple(unknowns)

    if not workspace_service_paths:
        unknowns.append("Candidate service boundaries were not directly evidenced from common workspace directories such as services/, packages/, or apps/.")
    if not api_paths:
        unknowns.append("Cross-service API or event contracts were not directly evidenced in the bounded init scan.")
    if not security_paths:
        unknowns.append("Security and access relationships were not directly evidenced in the bounded init scan.")
    if not release_paths:
        unknowns.append("Release coordination or feature flag details were not directly evidenced in the bounded init scan.")
    if not deployment_present:
        unknowns.append("Deployment topology was not directly evidenced in the bounded init scan.")
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


def _render_index(facts: RepoFacts) -> str:
    if facts.profile == "workspace":
        feature_paths = [
            "- `01-platform-overview.md`",
            "- `03-service-catalog.md`",
            "- `06-interfaces-and-contracts.md`",
            "- `07-data-ownership-and-consistency.md`",
            "- `05-cross-service-flows.md`",
            "- `10-testing-and-quality.md`",
            "- `99-open-questions.md`",
        ]
        api_paths = [
            "- `06-interfaces-and-contracts.md`",
            "- `05-cross-service-flows.md`",
            "- `08-security-and-access.md`",
            "- `09-observability-and-support.md`",
            "- `99-open-questions.md`",
        ]
        incident_paths = [
            "- `05-cross-service-flows.md`",
            "- `09-observability-and-support.md`",
            "- `11-runtime-deployment-and-config.md`",
            "- `13-operations-and-runbook.md`",
            "- `99-open-questions.md`",
        ]
        refactor_paths = [
            "- `02-system-map.md`",
            "- `04-domain-boundaries.md`",
            "- `10-testing-and-quality.md`",
            "- `14-decisions-assumptions-and-constraints.md`",
            "- `99-open-questions.md`",
        ]
        data_paths = [
            "- `07-data-ownership-and-consistency.md`",
            "- `05-cross-service-flows.md`",
            "- `08-security-and-access.md`",
            "- `10-testing-and-quality.md`",
            "- `99-open-questions.md`",
        ]
        security_paths = [
            "- `08-security-and-access.md`",
            "- `06-interfaces-and-contracts.md`",
            "- `07-data-ownership-and-consistency.md`",
            "- `09-observability-and-support.md`",
            "- `99-open-questions.md`",
        ]
    else:
        feature_paths = [
            "- `01-service-overview.md`",
            "- `03-domain-boundaries.md`",
            "- `04-interfaces-and-contracts.md`",
            "- `05-data-and-persistence.md`",
            "- `06-business-rules-and-flows.md`",
            "- `11-testing-and-quality.md`",
            "- `99-open-questions.md`",
        ]
        api_paths = [
            "- `04-interfaces-and-contracts.md`",
            "- `07-integrations-and-dependencies.md`",
            "- `08-security-and-access.md`",
            "- `09-errors-and-resilience.md`",
            "- `99-open-questions.md`",
        ]
        incident_paths = [
            "- `07-integrations-and-dependencies.md`",
            "- `09-errors-and-resilience.md`",
            "- `10-observability-and-support.md`",
            "- `13-operations-and-runbook.md`",
            "- `99-open-questions.md`",
        ]
        refactor_paths = [
            "- `02-architecture.md`",
            "- `03-domain-boundaries.md`",
            "- `11-testing-and-quality.md`",
            "- `14-decisions-assumptions-and-constraints.md`",
            "- `99-open-questions.md`",
        ]
        data_paths = [
            "- `05-data-and-persistence.md`",
            "- `06-business-rules-and-flows.md`",
            "- `08-security-and-access.md`",
            "- `11-testing-and-quality.md`",
            "- `99-open-questions.md`",
        ]
        security_paths = [
            "- `08-security-and-access.md`",
            "- `04-interfaces-and-contracts.md`",
            "- `05-data-and-persistence.md`",
            "- `09-errors-and-resilience.md`",
            "- `99-open-questions.md`",
        ]

    lines = [
        "# Context Index",
        "",
        "## Repository Profile",
        f"- Profile: {facts.profile}",
        "- Context profile version: 2",
        "",
        "## How to Use This Context",
        "- Start here, then read only the files relevant to the task.",
        "- Treat `99-open-questions.md` as the anti-hallucination stop list.",
        "",
        "## Read Paths",
        "",
        "### Feature Implementation",
        "Read:",
        *feature_paths,
        "",
        "### API or Integration Change",
        "Read:",
        *api_paths,
        "",
        "### Production Incident",
        "Read:",
        *incident_paths,
        "",
        "### Refactor",
        "Read:",
        *refactor_paths,
        "",
        "### Data Model Change",
        "Read:",
        *data_paths,
        "",
        "### Security-Sensitive Change",
        "Read:",
        *security_paths,
    ]
    return "\n".join(lines) + "\n"


def _render_service_overview(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Service Overview",
        when_to_read=["- Read before feature work that changes service purpose, scope, or owned capability."],
        do_not_use=[
            "- Detailed module structure: `02-architecture.md`.",
            "- Interface details: `04-interfaces-and-contracts.md`.",
        ],
        source_of_truth="- Service purpose, responsibilities, callers, owned capabilities, and non-goals.",
        current_context=[
            f"- Summary: {facts.summary}",
            f"- Repository: `{facts.repo_name}`",
        ],
        confirmed_facts=[
            _bullet_if(facts.stack != ("unknown",), f"Stack evidence: {', '.join(f'`{item}`' for item in facts.stack)}."),
            _bullet_if(bool(facts.readme_evidence), "README or top-level docs provide at least one purpose summary line."),
        ],
        assumptions=[
            "- Caller expectations and explicit non-goals still need confirmation." if not facts.readme_evidence else None,
        ],
        related_files=["- `02-architecture.md`", "- `03-domain-boundaries.md`", "- `14-decisions-assumptions-and-constraints.md`"],
    )


def _render_service_architecture(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Architecture",
        when_to_read=["- Read before refactors, module moves, or component-level design changes."],
        do_not_use=[
            "- Domain ownership rules: `03-domain-boundaries.md`.",
            "- Deployment details: `12-runtime-deployment-and-config.md`.",
        ],
        source_of_truth="- Architecture style, major components, module boundaries, processing model, and design principles.",
        current_context=[f"- Current structure suggests a **{facts.architecture_style}**."],
        confirmed_facts=[
            _paths_bullet("High-signal paths", facts.key_paths, suffix="/"),
            _bullet_if(bool(facts.package_managers), f"Build/package surface: {', '.join(facts.package_managers)}."),
        ],
        assumptions=["- Component boundaries and design principles need confirmation from maintainers or ADRs."],
        related_files=["- `03-domain-boundaries.md`", "- `12-runtime-deployment-and-config.md`", "- `14-decisions-assumptions-and-constraints.md`"],
    )


def _render_domain_boundaries(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Domain Boundaries",
        when_to_read=["- Read before changes that affect ownership, external contracts, or service scope."],
        do_not_use=[
            "- Business rule flow details: `06-business-rules-and-flows.md`.",
            "- Data store specifics: `05-data-and-persistence.md`.",
        ],
        source_of_truth="- Owned domain, not-owned domain, upstream/downstream boundaries, and data ownership boundary.",
        current_context=["- This repo is currently treated as one primary implementation unit for service-scoped work."],
        confirmed_facts=[
            _bullet_if(facts.docs_present, "Repository docs exist and may define domain ownership more explicitly."),
        ],
        assumptions=["- Explicit owned and not-owned domain boundaries still need confirmation."],
        related_files=["- `01-service-overview.md`", "- `04-interfaces-and-contracts.md`", "- `05-data-and-persistence.md`"],
    )


def _render_service_interfaces_and_contracts(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Interfaces and Contracts",
        when_to_read=["- Read before API, event, request/response, or compatibility changes."],
        do_not_use=[
            "- Dependency inventory: `07-integrations-and-dependencies.md`.",
            "- Auth and access policy: `08-security-and-access.md`.",
        ],
        source_of_truth="- REST, gRPC, events, message contracts, and compatibility rules.",
        current_context=[_paths_bullet("Candidate contract paths", facts.api_paths)],
        confirmed_facts=[_bullet_if(bool(facts.api_paths), "Contract-like files were detected in the bounded scan.")],
        assumptions=["- Confirm authoritative contract definitions before changing public behavior."],
        related_files=["- `03-domain-boundaries.md`", "- `07-integrations-and-dependencies.md`", "- `99-open-questions.md`"],
    )


def _render_service_data_and_persistence(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Data and Persistence",
        when_to_read=["- Read before schema, migration, persistence, or consistency changes."],
        do_not_use=[
            "- Domain flow logic: `06-business-rules-and-flows.md`.",
            "- Runtime configuration: `12-runtime-deployment-and-config.md`.",
        ],
        source_of_truth="- Databases, tables/collections, main fields, data lifecycle, consistency rules, and migrations.",
        current_context=[_paths_bullet("Candidate persistence paths", facts.database_paths)],
        confirmed_facts=[_bullet_if(bool(facts.database_paths), "Schema or migration-related files were detected in the bounded scan.")],
        assumptions=["- Confirm data ownership, retention, and migration policy before mutation work."],
        related_files=["- `03-domain-boundaries.md`", "- `06-business-rules-and-flows.md`", "- `08-security-and-access.md`"],
    )


def _render_service_business_rules_and_flows(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Business Rules and Flows",
        when_to_read=["- Read before changing validation, state transitions, limits, or user-visible flow behavior."],
        do_not_use=[
            "- Interface wire format details: `04-interfaces-and-contracts.md`.",
            "- Incident response steps: `13-operations-and-runbook.md`.",
        ],
        source_of_truth="- Business flows, validation rules, state transitions, limits, exceptions, and edge cases.",
        current_context=[_paths_bullet("Candidate business-rule paths", facts.business_rule_paths)],
        confirmed_facts=[_bullet_if(bool(facts.business_rule_paths), "Domain-rule-like files were detected in the bounded scan.")],
        assumptions=["- Durable business invariants still need confirmation from code owners or tests."],
        related_files=["- `04-interfaces-and-contracts.md`", "- `05-data-and-persistence.md`", "- `11-testing-and-quality.md`"],
    )


def _render_service_integrations_and_dependencies(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Integrations and Dependencies",
        when_to_read=["- Read before external dependency changes, provider swaps, or downstream behavior changes."],
        do_not_use=[
            "- Error handling ownership: `09-errors-and-resilience.md`.",
            "- Security controls: `08-security-and-access.md`.",
        ],
        source_of_truth="- Internal services, external partners, dependency contracts, timeout expectations, retry expectations, and dependency risks.",
        current_context=[_paths_bullet("Candidate integration paths", facts.integration_paths)],
        confirmed_facts=[_bullet_if(bool(facts.integration_paths), "Integration-related files were detected in the bounded scan.")],
        assumptions=["- Timeout, retry, and ownership expectations still need confirmation per dependency."],
        related_files=["- `04-interfaces-and-contracts.md`", "- `08-security-and-access.md`", "- `09-errors-and-resilience.md`"],
    )


def _render_service_security_and_access(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Security and Access",
        when_to_read=["- Read before auth, authorization, secret, token, or sensitive-data changes."],
        do_not_use=[
            "- General dependency inventory: `07-integrations-and-dependencies.md`.",
            "- Incident procedure detail: `13-operations-and-runbook.md`.",
        ],
        source_of_truth="- Auth, authorization, roles, secrets, certificates, sensitive data, and access boundaries.",
        current_context=[_paths_bullet("Candidate security paths", facts.security_paths)],
        confirmed_facts=[_bullet_if(bool(facts.security_paths), "Auth or security-related files were detected in the bounded scan.")],
        assumptions=["- Sensitive data classes, token claims, and permission boundaries still need confirmation."],
        related_files=["- `04-interfaces-and-contracts.md`", "- `05-data-and-persistence.md`", "- `09-errors-and-resilience.md`"],
    )


def _render_service_errors_and_resilience(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Errors and Resilience",
        when_to_read=["- Read before retry, timeout, idempotency, or fallback behavior changes."],
        do_not_use=[
            "- Support dashboards: `10-observability-and-support.md`.",
            "- Dependency list ownership: `07-integrations-and-dependencies.md`.",
        ],
        source_of_truth="- Error code strategy, retries, timeout handling, idempotency, fallback behavior, finality, and recovery rules.",
        current_context=[_paths_bullet("Candidate resilience paths", facts.error_paths)],
        confirmed_facts=[_bullet_if(bool(facts.error_paths), "Retry or error-related files were detected in the bounded scan.")],
        assumptions=["- Error taxonomy and recovery guarantees still need confirmation."],
        related_files=["- `07-integrations-and-dependencies.md`", "- `08-security-and-access.md`", "- `10-observability-and-support.md`"],
    )


def _render_service_observability_and_support(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Observability and Support",
        when_to_read=["- Read before changing logs, metrics, traces, alerts, or support diagnostics."],
        do_not_use=[
            "- Recovery playbooks: `13-operations-and-runbook.md`.",
            "- Runtime topology: `12-runtime-deployment-and-config.md`.",
        ],
        source_of_truth="- Logs, metrics, traces, dashboards, alerts, and support investigation steps.",
        current_context=[_paths_bullet("Candidate observability paths", facts.observability_paths)],
        confirmed_facts=[_bullet_if(bool(facts.observability_paths), "Observability-related files were detected in the bounded scan.")],
        assumptions=["- Dashboard ownership, alert thresholds, and support workflow still need confirmation."],
        related_files=["- `09-errors-and-resilience.md`", "- `12-runtime-deployment-and-config.md`", "- `13-operations-and-runbook.md`"],
    )


def _render_service_testing_and_quality(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Testing and Quality",
        when_to_read=["- Read before changing validation strategy, adding risk, or refactoring behavior."],
        do_not_use=[
            "- Runtime deployment mechanics: `12-runtime-deployment-and-config.md`.",
            "- Business rules authority: `06-business-rules-and-flows.md`.",
        ],
        source_of_truth="- Unit tests, integration tests, contract tests, regression tests, test data, and quality gates.",
        current_context=[
            _bullet_if(facts.tests_present, "Automated test assets are present in the repo.") or f"- {NO_DIRECT_EVIDENCE}",
            _bullet_if(facts.ci_present, "CI workflow files are present."),
            _bullet_if(facts.formatter_present, "Repository-local formatting or editor config is present."),
        ],
        confirmed_facts=[],
        assumptions=["- Quality gates and required regression coverage still need confirmation."],
        related_files=["- `02-architecture.md`", "- `06-business-rules-and-flows.md`", "- `14-decisions-assumptions-and-constraints.md`"],
    )


def _render_service_runtime_deployment_and_config(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Runtime Deployment and Config",
        when_to_read=["- Read before env var, config, runtime, deployment, CI/CD, or rollback changes."],
        do_not_use=[
            "- Operational triage steps: `13-operations-and-runbook.md`.",
            "- Constraint rationale: `14-decisions-assumptions-and-constraints.md`.",
        ],
        source_of_truth="- Runtime, environment variables, config files, deployment topology, CI/CD, and rollback constraints.",
        current_context=[
            _bullet_if(bool(facts.runtimes), f"Runtime evidence: {', '.join(f'`{item}`' for item in facts.runtimes)}.") or "- Runtime version not directly evidenced.",
            _bullet_if(facts.deployment_present, "Deployment-related files are present in the repository surface."),
        ],
        confirmed_facts=[],
        assumptions=["- Environment-specific topology and rollback rules still need confirmation."],
        related_files=["- `02-architecture.md`", "- `10-observability-and-support.md`", "- `13-operations-and-runbook.md`"],
    )


def _render_service_operations_and_runbook(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Operations and Runbook",
        when_to_read=["- Read during incidents, manual recovery, reconciliation, or operational support work."],
        do_not_use=[
            "- Error-handling design authority: `09-errors-and-resilience.md`.",
            "- Deployment topology details: `12-runtime-deployment-and-config.md`.",
        ],
        source_of_truth="- Operational tasks, incident triage, manual checks, reconciliation, recovery, and escalation.",
        current_context=[
            _bullet_if(bool(facts.observability_paths) or facts.deployment_present, "Operational evidence exists but concrete runbooks still need curation."),
        ],
        confirmed_facts=[],
        assumptions=["- Manual recovery and escalation procedures still need confirmation."],
        related_files=["- `09-errors-and-resilience.md`", "- `10-observability-and-support.md`", "- `12-runtime-deployment-and-config.md`"],
    )


def _render_service_decisions_assumptions_and_constraints(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Decisions Assumptions and Constraints",
        when_to_read=["- Read before major design shifts, high-risk changes, or when evidence is weak."],
        do_not_use=[
            "- Unvalidated unknowns: `99-open-questions.md`.",
            "- Term definitions: `98-glossary.md`.",
        ],
        source_of_truth="- Accepted decisions, ADR summaries, assumptions, confirmed facts, inferred knowledge, and technical/business/operational constraints.",
        current_context=[
            "- This file is the canonical home for cross-cutting decisions, assumptions, and constraints that should not be duplicated elsewhere.",
        ],
        confirmed_facts=[
            _bullet_if(facts.docs_present, "Repository docs are present and may contain ADRs or constraint evidence."),
            _bullet_if(facts.deployment_present, "Deployment files imply some runtime constraints."),
        ],
        assumptions=["- Canonical ADR summaries and decision owners still need confirmation."],
        related_files=["- `02-architecture.md`", "- `12-runtime-deployment-and-config.md`", "- `99-open-questions.md`"],
    )


def _render_platform_overview(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Platform Overview",
        when_to_read=["- Read before cross-service planning, coordination, or platform-scope work."],
        do_not_use=[
            "- Service inventory detail: `03-service-catalog.md`.",
            "- Contract detail: `06-interfaces-and-contracts.md`.",
        ],
        source_of_truth="- Platform purpose, major capabilities, scope, and non-goals.",
        current_context=[f"- Summary: {facts.summary}"],
        confirmed_facts=[
            _bullet_if(bool(facts.workspace_service_paths), f"Candidate service roots: {', '.join(f'`{path}/`' for path in facts.workspace_service_paths)}."),
        ],
        assumptions=["- Platform non-goals and explicit service ownership still need confirmation."],
        related_files=["- `02-system-map.md`", "- `03-service-catalog.md`", "- `14-decisions-assumptions-and-constraints.md`"],
    )


def _render_workspace_system_map(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="System Map",
        when_to_read=["- Read before work that spans multiple services or repo areas."],
        do_not_use=[
            "- Detailed service ownership: `03-service-catalog.md`.",
            "- Flow sequencing: `05-cross-service-flows.md`.",
        ],
        source_of_truth="- System landscape, major components, and service relationships.",
        current_context=[f"- Current structure suggests a **{facts.architecture_style}**."],
        confirmed_facts=[_paths_bullet("Candidate workspace roots", facts.workspace_service_paths, suffix="/")],
        assumptions=["- Service-to-service relationship semantics still need confirmation."],
        related_files=["- `03-service-catalog.md`", "- `04-domain-boundaries.md`", "- `05-cross-service-flows.md`"],
    )


def _render_workspace_service_catalog(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Service Catalog",
        when_to_read=["- Read before assigning changes, tracing impact, or coordinating owners across services."],
        do_not_use=[
            "- Cross-service flow sequencing: `05-cross-service-flows.md`.",
            "- Data ownership rules: `07-data-ownership-and-consistency.md`.",
        ],
        source_of_truth="- Services, owners, responsibilities, criticality, and repo paths.",
        current_context=[_paths_bullet("Candidate service paths", facts.workspace_service_paths, suffix="/")],
        confirmed_facts=[_bullet_if(bool(facts.workspace_service_paths), "Common workspace service directories were detected.")],
        assumptions=["- Service ownership, criticality, and support contacts still need confirmation."],
        related_files=["- `02-system-map.md`", "- `04-domain-boundaries.md`", "- `13-operations-and-runbook.md`"],
    )


def _render_workspace_domain_boundaries(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Domain Boundaries",
        when_to_read=["- Read before changing cross-service ownership or shifting bounded responsibilities."],
        do_not_use=[
            "- Per-service internals.",
            "- Contract wire formats: `06-interfaces-and-contracts.md`.",
        ],
        source_of_truth="- Domain ownership across services, not-owned areas, and conflict boundaries.",
        current_context=["- Workspace context should stay at coordination level and avoid service-local implementation detail."],
        confirmed_facts=[_bullet_if(facts.docs_present, "Repository docs exist and may describe ownership boundaries.")],
        assumptions=["- Explicit ownership conflicts and unresolved domains still need confirmation."],
        related_files=["- `02-system-map.md`", "- `03-service-catalog.md`", "- `07-data-ownership-and-consistency.md`"],
    )


def _render_workspace_cross_service_flows(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Cross-Service Flows",
        when_to_read=["- Read before workflow changes that cross service, queue, or orchestration boundaries."],
        do_not_use=[
            "- Service-local business rules.",
            "- Detailed dependency inventory: `06-interfaces-and-contracts.md`.",
        ],
        source_of_truth="- End-to-end flows, orchestration, async/sync boundaries, and transaction boundaries.",
        current_context=[_paths_bullet("Candidate flow or integration paths", facts.integration_paths)],
        confirmed_facts=[_bullet_if(bool(facts.integration_paths), "Integration-like paths were detected in the bounded scan.")],
        assumptions=["- Authoritative end-to-end sequence docs still need confirmation."],
        related_files=["- `02-system-map.md`", "- `06-interfaces-and-contracts.md`", "- `07-data-ownership-and-consistency.md`"],
    )


def _render_workspace_interfaces_and_contracts(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Interfaces and Contracts",
        when_to_read=["- Read before changing cross-service APIs, events, or compatibility rules."],
        do_not_use=[
            "- Data ownership rules: `07-data-ownership-and-consistency.md`.",
            "- Security boundary policy: `08-security-and-access.md`.",
        ],
        source_of_truth="- Cross-service APIs, events, contracts, and compatibility rules.",
        current_context=[_paths_bullet("Candidate contract paths", facts.api_paths)],
        confirmed_facts=[_bullet_if(bool(facts.api_paths), "Contract-like files were detected in the bounded scan.")],
        assumptions=["- Contract owners and compatibility guarantees still need confirmation."],
        related_files=["- `03-service-catalog.md`", "- `05-cross-service-flows.md`", "- `08-security-and-access.md`"],
    )


def _render_workspace_data_ownership_and_consistency(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Data Ownership and Consistency",
        when_to_read=["- Read before changing shared data, replication, consistency, or CDC behavior."],
        do_not_use=[
            "- Runtime topology detail: `11-runtime-deployment-and-config.md`.",
            "- Glossary terms: `98-glossary.md`.",
        ],
        source_of_truth="- Data owners, read/write ownership, replication, consistency, and read-model boundaries.",
        current_context=[_paths_bullet("Candidate data paths", facts.database_paths)],
        confirmed_facts=[_bullet_if(bool(facts.database_paths), "Schema or database-like files were detected in the bounded scan.")],
        assumptions=["- Canonical data owners and consistency guarantees still need confirmation."],
        related_files=["- `04-domain-boundaries.md`", "- `05-cross-service-flows.md`", "- `08-security-and-access.md`"],
    )


def _render_workspace_security_access(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Security and Access",
        when_to_read=["- Read before changing platform auth, permissions, service-to-service trust, or secret handling."],
        do_not_use=[
            "- Detailed incident steps: `13-operations-and-runbook.md`.",
            "- Contract compatibility: `06-interfaces-and-contracts.md`.",
        ],
        source_of_truth="- Platform auth, roles, service-to-service auth, secrets, PII, and permission boundaries.",
        current_context=[_paths_bullet("Candidate security paths", facts.security_paths)],
        confirmed_facts=[_bullet_if(bool(facts.security_paths), "Security-related files were detected in the bounded scan.")],
        assumptions=["- Platform-wide permission boundaries still need confirmation."],
        related_files=["- `06-interfaces-and-contracts.md`", "- `07-data-ownership-and-consistency.md`", "- `13-operations-and-runbook.md`"],
    )


def _render_workspace_observability_and_support(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Observability and Support",
        when_to_read=["- Read before changing shared logging, dashboards, traces, alerts, or support routing."],
        do_not_use=[
            "- Runtime rollout mechanics: `11-runtime-deployment-and-config.md`.",
            "- Release policy: `12-release-and-feature-flags.md`.",
        ],
        source_of_truth="- Platform logs, dashboards, tracing, alerting, and support ownership.",
        current_context=[_paths_bullet("Candidate observability paths", facts.observability_paths)],
        confirmed_facts=[_bullet_if(bool(facts.observability_paths), "Observability-related files were detected in the bounded scan.")],
        assumptions=["- Shared dashboard ownership and support escalation boundaries still need confirmation."],
        related_files=["- `10-testing-and-quality.md`", "- `11-runtime-deployment-and-config.md`", "- `13-operations-and-runbook.md`"],
    )


def _render_workspace_testing_and_quality(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Testing and Quality",
        when_to_read=["- Read before cross-service releases, compatibility changes, or risky refactors."],
        do_not_use=[
            "- Service-local test implementation detail.",
            "- Release policy: `12-release-and-feature-flags.md`.",
        ],
        source_of_truth="- Cross-service testing, contract testing, regression, and release validation.",
        current_context=[
            _bullet_if(facts.tests_present, "Automated test assets are present in the repo.") or f"- {NO_DIRECT_EVIDENCE}",
            _bullet_if(facts.ci_present, "CI workflow files are present."),
        ],
        confirmed_facts=[],
        assumptions=["- Cross-service validation gates and release signoff rules still need confirmation."],
        related_files=["- `06-interfaces-and-contracts.md`", "- `09-observability-and-support.md`", "- `12-release-and-feature-flags.md`"],
    )


def _render_workspace_runtime_deployment_and_config(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Runtime Deployment and Config",
        when_to_read=["- Read before environment, deployment, config, or rollback changes across services."],
        do_not_use=[
            "- Release coordination detail: `12-release-and-feature-flags.md`.",
            "- Manual operational recovery: `13-operations-and-runbook.md`.",
        ],
        source_of_truth="- Environment topology, deployment, config, CI/CD, and rollback boundaries.",
        current_context=[
            _bullet_if(facts.deployment_present, "Deployment-related files are present."),
            _bullet_if(bool(facts.runtimes), f"Runtime evidence: {', '.join(f'`{item}`' for item in facts.runtimes)}."),
        ],
        confirmed_facts=[],
        assumptions=["- Environment topology and rollback ownership still need confirmation."],
        related_files=["- `02-system-map.md`", "- `09-observability-and-support.md`", "- `12-release-and-feature-flags.md`"],
    )


def _render_workspace_release_and_feature_flags(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Release and Feature Flags",
        when_to_read=["- Read before rollout, feature flag, kill switch, or rollback policy changes."],
        do_not_use=[
            "- Runtime topology detail: `11-runtime-deployment-and-config.md`.",
            "- Support triage detail: `13-operations-and-runbook.md`.",
        ],
        source_of_truth="- Release process, rollout, feature flags, kill switch behavior, and rollback expectations.",
        current_context=[_paths_bullet("Candidate release paths", facts.release_paths)],
        confirmed_facts=[_bullet_if(bool(facts.release_paths), "Release or feature-flag related files were detected in the bounded scan.")],
        assumptions=["- Canonical rollout controls and owners still need confirmation."],
        related_files=["- `10-testing-and-quality.md`", "- `11-runtime-deployment-and-config.md`", "- `13-operations-and-runbook.md`"],
    )


def _render_workspace_operations_and_runbook(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Operations and Runbook",
        when_to_read=["- Read during incidents, coordination failures, reconciliation, or manual recovery work."],
        do_not_use=[
            "- Contract authority: `06-interfaces-and-contracts.md`.",
            "- Decision rationale: `14-decisions-assumptions-and-constraints.md`.",
        ],
        source_of_truth="- Operational playbooks, incident response, reconciliation, and escalation.",
        current_context=["- Workspace runbooks should coordinate service owners rather than duplicate service-local runbooks."],
        confirmed_facts=[_bullet_if(facts.ci_present or bool(facts.observability_paths), "Operational signals exist in the repo surface.")],
        assumptions=["- Escalation paths and coordination ownership still need confirmation."],
        related_files=["- `03-service-catalog.md`", "- `09-observability-and-support.md`", "- `12-release-and-feature-flags.md`"],
    )


def _render_workspace_decisions_assumptions_and_constraints(facts: RepoFacts) -> str:
    return _render_active_context_file(
        title="Decisions Assumptions and Constraints",
        when_to_read=["- Read before major platform changes or when cross-service evidence is incomplete."],
        do_not_use=[
            "- Unknown follow-ups: `99-open-questions.md`.",
            "- Term definitions: `98-glossary.md`.",
        ],
        source_of_truth="- Platform decisions, assumptions, confirmed facts, inferred knowledge, and constraints.",
        current_context=["- This file is the canonical home for cross-cutting platform decisions and constraints."],
        confirmed_facts=[_bullet_if(facts.docs_present, "Repository docs may contain platform decisions or ADR-like evidence.")],
        assumptions=["- Accepted platform decisions and durable constraints still need confirmation."],
        related_files=["- `02-system-map.md`", "- `11-runtime-deployment-and-config.md`", "- `99-open-questions.md`"],
    )


def _render_glossary(facts: RepoFacts, *, profile_scope: str) -> str:
    terms = [facts.repo_name]
    terms.extend(facts.stack)
    terms.extend(path.split("/")[0] for path in facts.workspace_service_paths[:3])
    canonical_terms = [term for term in dict.fromkeys(term for term in terms if term and term != "unknown")]
    return _render_active_context_file(
        title="Glossary",
        when_to_read=["- Read when a term, acronym, internal service name, or partner label is unclear."],
        do_not_use=["- Unknown questions: `99-open-questions.md`.", "- Architecture or policy detail."],
        source_of_truth="- Domain terms, acronyms, internal service names, and external partner terms.",
        current_context=[f"- Scope: {profile_scope} glossary for repo-local or platform terms."],
        confirmed_facts=[
            "- Add stable definitions here; do not duplicate explanations in active context files.",
            *[f"- Candidate term: `{term}`." for term in canonical_terms[:6]],
        ],
        assumptions=["- Some domain terms still need confirmation from maintainers."],
        related_files=["- `00-index.md`", "- `14-decisions-assumptions-and-constraints.md`", "- `99-open-questions.md`"],
    )


def _render_open_questions(facts: RepoFacts, *, profile_scope: str) -> str:
    question_lines = [f"- Q-{index:03d}: {item}" for index, item in enumerate(facts.unknowns, start=1)]
    return _render_active_context_file(
        title="Open Questions",
        when_to_read=["- Read whenever task-critical information is missing, weakly evidenced, or risky to infer."],
        do_not_use=["- Confirmed facts.", "- Stable term definitions: `98-glossary.md`."],
        source_of_truth="- Unknowns, risky assumptions, missing documentation, and follow-up items.",
        current_context=["- Unknowns belong here instead of being guessed elsewhere.", *question_lines],
        confirmed_facts=["- Move resolved items into the canonical active file that owns the fact."],
        assumptions=[f"- Open questions below reflect bounded-init uncertainty for the {profile_scope} profile."],
        related_files=["- `00-index.md`", "- `98-glossary.md`", "- `14-decisions-assumptions-and-constraints.md`"],
    )


def _render_active_context_file(
    *,
    title: str,
    when_to_read: list[str],
    do_not_use: list[str],
    source_of_truth: str,
    current_context: list[str | None],
    confirmed_facts: list[str | None],
    assumptions: list[str | None],
    related_files: list[str],
) -> str:
    lines = [f"# {title}"]
    sections = (
        ("When to Read", _clean_lines(when_to_read)),
        ("Do Not Use This For", _clean_lines(do_not_use)),
        ("Source of Truth", _clean_lines([source_of_truth])),
        ("Current Context", _clean_lines(current_context)),
        ("Confirmed Facts", _clean_lines(confirmed_facts)),
        ("Assumptions", _clean_lines(assumptions)),
        ("Related Files", _clean_lines(related_files)),
    )
    for heading, body in sections:
        lines.extend(["", f"## {heading}"])
        lines.extend(body or ["- None yet."])
    return "\n".join(lines) + "\n"


def _clean_lines(lines: list[str | None]) -> list[str]:
    return [line for line in lines if line]


def _paths_bullet(label: str, paths: tuple[str, ...], *, suffix: str = "") -> str:
    if not paths:
        return f"- {NO_DIRECT_EVIDENCE}"
    rendered = ", ".join(f"`{path}{suffix}`" for path in paths[:8])
    return f"- {label}: {rendered}."


def _bullet_if(condition: bool, text: str) -> str | None:
    if not condition:
        return None
    return f"- {text}"


def _base_evidence_paths(facts: RepoFacts) -> list[str]:
    return _compose_paths(
        [item.path for item in facts.readme_evidence],
        [item.path for item in facts.manifest_evidence],
        [item.path for item in facts.structure_evidence],
    )


def _compose_paths(*path_groups: list[str]) -> list[str]:
    combined: list[str] = []
    for group in path_groups:
        for path in group:
            if path not in combined:
                combined.append(path)
    return combined
