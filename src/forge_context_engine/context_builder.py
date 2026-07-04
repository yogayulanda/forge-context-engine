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
        ".forge/context/02-service-architecture.md": _render_service_architecture(facts),
        ".forge/context/03-domain-boundary.md": _render_domain_boundary(facts),
        ".forge/context/04-api-contracts.md": _render_service_api_contracts(facts),
        ".forge/context/05-data-model-and-database.md": _render_service_data_model(facts),
        ".forge/context/06-business-rules.md": _render_service_business_rules(facts),
        ".forge/context/07-integration-dependencies.md": _render_service_integrations(facts),
        ".forge/context/08-error-handling.md": _render_service_error_handling(facts),
        ".forge/context/09-observability.md": _render_service_observability(facts),
        ".forge/context/10-testing-strategy.md": _render_service_testing(facts),
        ".forge/context/11-runtime-and-deployment.md": _render_service_runtime_deployment(facts),
        ".forge/context/99-open-questions.md": _render_open_questions(facts, profile_scope="service"),
    }
    return RepoContextSeed(files=files)


def _build_workspace_context_seed(facts: RepoFacts) -> RepoContextSeed:
    files = {
        ".forge/context/00-workspace-index.md": _render_workspace_index(facts),
        ".forge/context/01-platform-overview.md": _render_platform_overview(facts),
        ".forge/context/02-system-map.md": _render_workspace_system_map(facts),
        ".forge/context/03-service-catalog.md": _render_workspace_service_catalog(facts),
        ".forge/context/04-domain-boundaries.md": _render_workspace_domain_boundaries(facts),
        ".forge/context/05-cross-service-flows.md": _render_workspace_cross_service_flows(facts),
        ".forge/context/06-api-and-event-contracts.md": _render_workspace_api_event_contracts(facts),
        ".forge/context/07-data-ownership.md": _render_workspace_data_ownership(facts),
        ".forge/context/08-security-and-access.md": _render_workspace_security_access(facts),
        ".forge/context/09-observability-and-operations.md": _render_workspace_observability_operations(facts),
        ".forge/context/10-deployment-topology.md": _render_workspace_deployment_topology(facts),
        ".forge/context/11-release-and-feature-flags.md": _render_workspace_release_feature_flags(facts),
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
    return _render_profile_card(
        facts,
        card_id="service.index",
        title="Service Context Index",
        file_type="core",
        profile_scope="service",
        evidence_paths=_base_evidence_paths(facts),
        body_sections=[
            ("Purpose", ["- Use this profile to ground implementation, testing, refactoring, review, and bug-fix work for one service or application."]),
            ("Current Summary", [f"- {facts.summary}", f"- Current structure suggests a **{facts.architecture_style}**."]),
            (
                "File Guide",
                [
                    "- `01-service-overview.md` for product and repository scope.",
                    "- `02-service-architecture.md` for structure and runtime shape.",
                    "- `04-api-contracts.md`, `05-data-model-and-database.md`, and `07-integration-dependencies.md` for boundary evidence.",
                    "- `99-open-questions.md` for unresolved or weakly evidenced details.",
                ],
            ),
        ],
    )


def _render_workspace_index(facts: RepoFacts) -> str:
    return _render_profile_card(
        facts,
        card_id="workspace.index",
        title="Workspace Context Index",
        file_type="core",
        profile_scope="workspace",
        evidence_paths=_base_evidence_paths(facts),
        body_sections=[
            ("Purpose", ["- Use this profile for cross-service planning, impact analysis, and platform-level coordination reasoning."]),
            ("Current Summary", [f"- {facts.summary}", "- Workspace context stays lightweight and does not replace service-local context."]),
            (
                "File Guide",
                [
                    "- `02-system-map.md` and `03-service-catalog.md` capture directly evidenced workspace structure.",
                    "- `05-cross-service-flows.md` and `06-api-and-event-contracts.md` should only contain direct cross-service evidence.",
                    "- `99-open-questions.md` holds missing ownership, contract, data, and rollout details.",
                ],
            ),
        ],
    )


def _render_service_overview(facts: RepoFacts) -> str:
    lines = [f"- {facts.summary}", f"- Repository name: `{facts.repo_name}`."]
    if facts.stack and facts.stack != ("unknown",):
        lines.append(f"- Implementation stack evidence: {', '.join(f'`{item}`' for item in facts.stack)}.")
    if facts.readme_evidence:
        lines.append("- README or manifest text provides the current best available product/service summary.")
    return _render_profile_card(
        facts,
        card_id="service.overview",
        title="Service Overview",
        file_type="core",
        profile_scope="service",
        evidence_paths=_base_evidence_paths(facts),
        body_sections=[("Observed Scope", lines)],
    )


def _render_service_architecture(facts: RepoFacts) -> str:
    lines = [f"- Current structure suggests a **{facts.architecture_style}**."]
    if facts.key_paths:
        lines.append(f"- High-signal paths: {', '.join(f'`{path}/`' for path in facts.key_paths)}.")
    if facts.package_managers:
        lines.append(f"- Package/build surface: {', '.join(facts.package_managers)}.")
    return _render_profile_card(
        facts,
        card_id="service.architecture",
        title="Service Architecture",
        file_type="core",
        profile_scope="service",
        evidence_paths=_base_evidence_paths(facts),
        body_sections=[("Observed Architecture", lines or [f"- {NO_DIRECT_EVIDENCE}"])],
    )


def _render_domain_boundary(facts: RepoFacts) -> str:
    lines = ["- This repository is currently treated as one primary implementation unit for service-scoped work."]
    if facts.docs_present:
        lines.append("- Repository docs are present and may contain stronger domain boundary definitions than this bounded init scan could confirm.")
    else:
        lines.append(f"- {NO_DIRECT_EVIDENCE} for explicit domain ownership or excluded scope.")
    return _render_profile_card(
        facts,
        card_id="service.domain-boundary",
        title="Domain Boundary",
        file_type="core",
        profile_scope="service",
        evidence_paths=_base_evidence_paths(facts),
        body_sections=[("Boundary Notes", lines)],
    )


def _render_service_api_contracts(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="service.api-contracts",
        title="API Contracts",
        profile_scope="service",
        paths=facts.api_paths,
        present_intro="- Candidate API or contract files were detected in the bounded init scan.",
        missing_question="Confirm whether this service exposes HTTP, RPC, CLI, or event contracts and where their authoritative definitions live.",
    )


def _render_service_data_model(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="service.data-model",
        title="Data Model and Database",
        profile_scope="service",
        paths=facts.database_paths,
        present_intro="- Candidate database or schema assets were detected in the bounded init scan.",
        missing_question="Confirm whether this service owns persistent data, migrations, or schema contracts and where they are defined.",
    )


def _render_service_business_rules(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="service.business-rules",
        title="Business Rules",
        profile_scope="service",
        paths=facts.business_rule_paths,
        present_intro="- Candidate business-rule or domain-policy files were detected in the bounded init scan.",
        missing_question="Confirm the service's durable business rules, validation rules, and domain invariants.",
    )


def _render_service_integrations(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="service.integration-dependencies",
        title="Integration Dependencies",
        profile_scope="service",
        paths=facts.integration_paths,
        present_intro="- Candidate integration-related paths were detected in the bounded init scan.",
        missing_question="Confirm external providers, internal dependencies, and the contracts this service relies on.",
    )


def _render_service_error_handling(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="service.error-handling",
        title="Error Handling",
        profile_scope="service",
        paths=facts.error_paths,
        present_intro="- Candidate retry, middleware, or error-related paths were detected in the bounded init scan.",
        missing_question="Confirm service-level error handling, retries, timeout policy, and failure classification.",
    )


def _render_service_observability(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="service.observability",
        title="Observability",
        profile_scope="service",
        paths=facts.observability_paths,
        present_intro="- Candidate observability-related paths were detected in the bounded init scan.",
        missing_question="Confirm logs, metrics, traces, alerts, and operational dashboards for this service.",
    )


def _render_service_testing(facts: RepoFacts) -> str:
    lines: list[str] = []
    if facts.tests_present:
        lines.append("- Automated test assets are present in the repository.")
    else:
        lines.append(f"- {NO_DIRECT_EVIDENCE} for automated test assets.")
    if facts.ci_present:
        lines.append("- CI workflow files are present and likely define at least part of the validation surface.")
    if facts.formatter_present:
        lines.append("- Repository-local formatting or editor configuration is present and should be preserved during changes.")
    return _render_profile_card(
        facts,
        card_id="service.testing-strategy",
        title="Testing Strategy",
        file_type="core",
        profile_scope="service",
        evidence_paths=_compose_paths(list(facts.key_paths), _base_evidence_paths(facts)),
        body_sections=[("Observed Validation Surface", lines)],
    )


def _render_service_runtime_deployment(facts: RepoFacts) -> str:
    lines: list[str] = []
    if facts.runtimes:
        lines.append(f"- Runtime versions evidenced in manifests: {', '.join(f'`{item}`' for item in facts.runtimes)}.")
    if facts.deployment_present:
        lines.append("- Deployment-related files are present in the repository surface.")
    else:
        lines.append(f"- {NO_DIRECT_EVIDENCE} for deployment topology or runtime packaging details.")
    return _render_profile_card(
        facts,
        card_id="service.runtime-deployment",
        title="Runtime and Deployment",
        file_type="core",
        profile_scope="service",
        evidence_paths=_base_evidence_paths(facts),
        body_sections=[("Observed Runtime Surface", lines or [f"- {NO_DIRECT_EVIDENCE}"])],
    )


def _render_platform_overview(facts: RepoFacts) -> str:
    lines = [f"- {facts.summary}", "- Current workspace profile is intended for coordination context, not deep service internals."]
    if facts.stack and facts.stack != ("unknown",):
        lines.append(f"- Mixed implementation stack evidence in this repo currently includes: {', '.join(f'`{item}`' for item in facts.stack)}.")
    return _render_profile_card(
        facts,
        card_id="workspace.platform-overview",
        title="Platform Overview",
        file_type="core",
        profile_scope="workspace",
        evidence_paths=_base_evidence_paths(facts),
        body_sections=[("Observed Scope", lines)],
    )


def _render_workspace_system_map(facts: RepoFacts) -> str:
    lines = [f"- Current structure suggests a **{facts.architecture_style}**."]
    if facts.workspace_service_paths:
        lines.append("- Candidate service or package roots detected:")
        lines.extend(f"- `{path}/`" for path in facts.workspace_service_paths)
    elif facts.key_paths:
        lines.append(f"- High-signal top-level paths: {', '.join(f'`{path}/`' for path in facts.key_paths)}.")
    else:
        lines.append(f"- {NO_DIRECT_EVIDENCE} for workspace service layout.")
    return _render_profile_card(
        facts,
        card_id="workspace.system-map",
        title="System Map",
        file_type="core",
        profile_scope="workspace",
        evidence_paths=_compose_paths(list(facts.workspace_service_paths), _base_evidence_paths(facts)),
        body_sections=[("Observed Layout", lines)],
    )


def _render_workspace_service_catalog(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="workspace.service-catalog",
        title="Service Catalog",
        profile_scope="workspace",
        paths=facts.workspace_service_paths,
        present_intro="- Candidate service or package roots were detected in common workspace directories.",
        missing_question="Confirm which directories represent independently owned services, applications, or platform components.",
    )


def _render_workspace_domain_boundaries(facts: RepoFacts) -> str:
    lines = ["- Workspace boundary definitions should stay at coordination level and defer deep implementation facts to each service repository."]
    if facts.docs_present:
        lines.append("- Repository docs are present and may define domain ownership more clearly than the bounded init scan could confirm.")
    else:
        lines.append(f"- {NO_DIRECT_EVIDENCE} for explicit cross-service domain ownership.")
    return _render_profile_card(
        facts,
        card_id="workspace.domain-boundaries",
        title="Domain Boundaries",
        file_type="core",
        profile_scope="workspace",
        evidence_paths=_base_evidence_paths(facts),
        body_sections=[("Boundary Notes", lines)],
    )


def _render_workspace_cross_service_flows(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="workspace.cross-service-flows",
        title="Cross-Service Flows",
        profile_scope="workspace",
        paths=facts.integration_paths,
        present_intro="- Candidate integration-related paths were detected, but they still require service-level confirmation before treating them as authoritative cross-service flows.",
        missing_question="Confirm which workflows actually cross service boundaries and where the authoritative sequence or ownership docs live.",
    )


def _render_workspace_api_event_contracts(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="workspace.api-event-contracts",
        title="API and Event Contracts",
        profile_scope="workspace",
        paths=facts.api_paths,
        present_intro="- Candidate contract-related files were detected in the bounded init scan.",
        missing_question="Confirm which APIs or events are shared across services and which repo owns each contract.",
    )


def _render_workspace_data_ownership(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="workspace.data-ownership",
        title="Data Ownership",
        profile_scope="workspace",
        paths=facts.database_paths,
        present_intro="- Candidate database or schema assets were detected, but ownership boundaries still require human confirmation.",
        missing_question="Confirm which service owns each persistent dataset, schema, and migration stream.",
    )


def _render_workspace_security_access(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="workspace.security-access",
        title="Security and Access",
        profile_scope="workspace",
        paths=facts.security_paths,
        present_intro="- Candidate auth or security-related files were detected in the bounded init scan.",
        missing_question="Confirm cross-service authentication, authorization, and access-control boundaries.",
    )


def _render_workspace_observability_operations(facts: RepoFacts) -> str:
    lines: list[str] = []
    if facts.observability_paths:
        lines.append("- Candidate observability-related paths were detected in the bounded init scan.")
        lines.extend(f"- `{path}`" for path in facts.observability_paths)
    else:
        lines.append(f"- {NO_DIRECT_EVIDENCE} for shared observability or operational coordination assets.")
    if facts.ci_present:
        lines.append("- CI workflow files are present and may carry operational clues, but they do not by themselves define runtime ownership.")
    return _render_profile_card(
        facts,
        card_id="workspace.observability-operations",
        title="Observability and Operations",
        file_type="core",
        profile_scope="workspace",
        evidence_paths=_compose_paths(list(facts.observability_paths), _base_evidence_paths(facts)),
        body_sections=[("Observed Operational Surface", lines)],
    )


def _render_workspace_deployment_topology(facts: RepoFacts) -> str:
    lines: list[str] = []
    if facts.deployment_present:
        lines.append("- Deployment-related files are present in the repository surface.")
    else:
        lines.append(f"- {NO_DIRECT_EVIDENCE} for deployment topology.")
    if facts.runtimes:
        lines.append(f"- Runtime version evidence present: {', '.join(f'`{item}`' for item in facts.runtimes)}.")
    return _render_profile_card(
        facts,
        card_id="workspace.deployment-topology",
        title="Deployment Topology",
        file_type="core",
        profile_scope="workspace",
        evidence_paths=_base_evidence_paths(facts),
        body_sections=[("Observed Deployment Surface", lines)],
    )


def _render_workspace_release_feature_flags(facts: RepoFacts) -> str:
    return _render_path_scoped_card(
        facts,
        card_id="workspace.release-feature-flags",
        title="Release and Feature Flags",
        profile_scope="workspace",
        paths=facts.release_paths,
        present_intro="- Candidate release or feature-flag related files were detected in the bounded init scan.",
        missing_question="Confirm release coordination, feature flag ownership, and rollout control points across services.",
    )


def _render_open_questions(facts: RepoFacts, *, profile_scope: str) -> str:
    table = [
        "| ID | Open Question | Priority | Status |",
        "|---|---|---|---|",
    ]
    for index, item in enumerate(facts.unknowns, start=1):
        table.append(f"| Q-{index:03d} | {item} | important | open |")
    return _render_profile_card(
        facts,
        card_id=f"{profile_scope}.open-questions",
        title="Open Questions",
        file_type="knowledge",
        profile_scope=profile_scope,
        evidence_paths=_base_evidence_paths(facts),
        body_sections=[
            ("Unresolved Items", ["- Missing or weakly evidenced details are tracked here instead of being guessed in profile files."]),
            ("Question Ledger", table),
        ],
    )


def _render_path_scoped_card(
    facts: RepoFacts,
    *,
    card_id: str,
    title: str,
    profile_scope: str,
    paths: tuple[str, ...],
    present_intro: str,
    missing_question: str,
) -> str:
    if paths:
        body_lines = [present_intro]
        body_lines.extend(f"- `{path}`" for path in paths)
    else:
        body_lines = [f"- {NO_DIRECT_EVIDENCE}"]
    body_lines.append("- If this area matters for active work, verify it against source paths or record clarification in `99-open-questions.md`.")
    return _render_profile_card(
        facts,
        card_id=card_id,
        title=title,
        file_type="core",
        profile_scope=profile_scope,
        evidence_paths=list(paths),
        body_sections=[("Observed Evidence", body_lines), ("Follow-Up", [f"- {missing_question}"])],
    )


def _render_profile_card(
    facts: RepoFacts,
    *,
    card_id: str,
    title: str,
    file_type: str,
    profile_scope: str,
    evidence_paths: list[str],
    body_sections: list[tuple[str, list[str]]],
) -> str:
    status = "inferred" if evidence_paths else "unknown"
    confidence = "medium" if evidence_paths else "low"
    front_matter = [
        "---",
        f"id: {card_id}",
        f'title: "{title}"',
        f"type: {file_type}",
        f"status: {status}",
        f"confidence: {confidence}",
        "source: ai",
        "owner: unresolved",
        f"updated: {facts.today}",
    ]
    if evidence_paths:
        front_matter.append("source_paths:")
        for path in evidence_paths:
            front_matter.append(f"  - {path}")
    else:
        front_matter.append("source_paths: []")
    front_matter.extend(
        [
            f"source_commit: {facts.source_commit}",
            f"last_verified: {facts.today}",
            f"profile_scope: {profile_scope}",
            "generated_from: forge-init",
            "---",
        ]
    )

    body = [f"# {title}"]
    for section, lines in body_sections:
        body.append("")
        body.append(f"## {section}")
        body.extend(lines or [f"- {NO_DIRECT_EVIDENCE}"])
    return "\n".join(front_matter + [""] + body) + "\n"


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
