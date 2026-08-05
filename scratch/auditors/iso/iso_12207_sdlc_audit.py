#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ISO/IEC 12207:2008 / IEEE 12207 — Software Life Cycle Processes Auditor      ║
║                                                                               ║
║  Based on normative structure of ISO/IEC 12207:2008 / IEEE Std 12207-2008:    ║
║  Clause 6: System Life Cycle Processes                                       ║
║    6.2 Organizational Project-Enabling Processes (Infrastructure, Quality)  ║
║    6.3 Project Processes (Planning, Risk, Configuration, Measurement)        ║
║    6.4 Technical Processes (Architecture, Implementation, Integration, Ops)  ║
║  Clause 7: Software Specific Processes                                       ║
║    7.1 Software Implementation (Requirements, Architecture, Construction, V&V)║
║    7.2 Software Support (Documentation, SCM, Quality Assurance, Problem Res) ║
║    7.3 Software Reuse Processes (Domain Engineering, Asset Management)       ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_12207_sdlc_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


@dataclass
class SDLC12207Check:
    clause_id: str          # e.g. "6.3.5", "7.1.5"
    clause_ref: str         # Process title
    normative_req: str      # Exact normative requirement from ISO/IEC 12207
    category: str           # PROJECT / TECHNICAL / IMPLEMENTATION / SUPPORT / REUSE
    weight: int             # 1-5 based on critical SDLC impact
    search_terms: list[str] # Terms for evidence search
    evidence_files: list[str] = field(default_factory=list)
    found: bool = False
    confidence: str = "NONE"


SDLC_CHECKS: list[SDLC12207Check] = [

    # ── Clause 6.3: Project Processes ─────────────────────────────────────────
    SDLC12207Check(
        clause_id="6.3.1", clause_ref="Project Planning Process",
        normative_req="The organization SHALL produce project plans defining schedule, milestones, tasks, and resource allocation.",
        category="PROJECT", weight=4,
        search_terms=["roadmap", "milestones", "schedule", "task", "project_plan",
                      "sprint", "kanban", "timeline", "todo"],
    ),
    SDLC12207Check(
        clause_id="6.3.4", clause_ref="Risk Management Process",
        normative_req="The organization SHALL identify, analyze, evaluate, and treat software project risks.",
        category="PROJECT", weight=4,
        search_terms=["risk", "mitigation", "consequence", "likelihood", "security_risk",
                      "threat", "hazard", "risk_register"],
    ),
    SDLC12207Check(
        clause_id="6.3.5", clause_ref="Configuration Management Process (SCM)",
        normative_req="The organization SHALL establish configuration baselines, version control, and change control procedures.",
        category="PROJECT", weight=5,
        search_terms=["git", ".gitignore", "version", "commit", "branch", "tag",
                      "changelog", "release", "semver"],
    ),
    SDLC12207Check(
        clause_id="6.3.7", clause_ref="Measurement Process",
        normative_req="The organization SHALL collect and analyze metrics to monitor software process and product performance.",
        category="PROJECT", weight=3,
        search_terms=["metrics", "coverage", "benchmark", "performance", "telemetry",
                      "stats", "kpi", "prometheus", "grafana"],
    ),

    # ── Clause 6.4: System Technical Processes ───────────────────────────────
    SDLC12207Check(
        clause_id="6.4.1", clause_ref="Stakeholder Requirements Definition",
        normative_req="The organization SHALL define user requirements and stakeholder expectations in documented form.",
        category="TECHNICAL", weight=4,
        search_terms=["readme", "requirements", "user_story", "specification",
                      "feature_request", "use_case", "spec"],
    ),
    SDLC12207Check(
        clause_id="6.4.3", clause_ref="System Architectural Design Process",
        normative_req="The organization SHALL define system architecture, module boundaries, and external interfaces.",
        category="TECHNICAL", weight=5,
        search_terms=["architecture", "design", "component", "diagram", "uml",
                      "interface", "system_design", "module", "layer"],
    ),
    SDLC12207Check(
        clause_id="6.4.5", clause_ref="System Integration Process",
        normative_req="The organization SHALL integrate software components into unified system builds.",
        category="TECHNICAL", weight=4,
        search_terms=["integration", "build", "ci", "github_actions", "jenkins",
                      "docker", "container", "makefile", "pipeline"],
    ),
    SDLC12207Check(
        clause_id="6.4.9", clause_ref="Software Operation Process",
        normative_req="The organization SHALL operate the software product in its intended production environment.",
        category="TECHNICAL", weight=4,
        search_terms=["deploy", "production", "server", "k8s", "kubernetes",
                      "dockerfile", "entrypoint", "env", "service"],
    ),
    SDLC12207Check(
        clause_id="6.4.10", clause_ref="Software Maintenance Process",
        normative_req="The organization SHALL perform ongoing maintenance, patch releases, and bug fixes.",
        category="TECHNICAL", weight=3,
        search_terms=["patch", "fix", "hotfix", "maintenance", "update",
                      "upgrade", "migration", "deprecate"],
    ),

    # ── Clause 7.1: Software Implementation Processes ─────────────────────────
    SDLC12207Check(
        clause_id="7.1.2", clause_ref="Software Requirements Analysis",
        normative_req="The organization SHALL analyze software requirements for accuracy, completeness, and testability.",
        category="IMPLEMENTATION", weight=4,
        search_terms=["functional_requirement", "non_functional", "validation_rules",
                      "input_validation", "schema", "pydantic", "type_check"],
    ),
    SDLC12207Check(
        clause_id="7.1.3", clause_ref="Software Architectural Design",
        normative_req="The organization SHALL transform requirements into a software architecture detailing sub-systems and data structures.",
        category="IMPLEMENTATION", weight=5,
        search_terms=["class", "struct", "interface", "abstract", "pattern",
                      "singleton", "factory", "repository", "controller"],
    ),
    SDLC12207Check(
        clause_id="7.1.5", clause_ref="Software Construction (Coding)",
        normative_req="The organization SHALL construct software units conforming to code standards and requirements.",
        category="IMPLEMENTATION", weight=5,
        search_terms=["def", "function", "method", "class", "impl",
                      "src", "lib", "module", "main"],
    ),
    SDLC12207Check(
        clause_id="7.1.6", clause_ref="Software Integration Process",
        normative_req="The organization SHALL combine software units and verify interoperability.",
        category="IMPLEMENTATION", weight=4,
        search_terms=["import", "require", "include", "dependency", "package",
                      "modules", "plugin", "adapter"],
    ),
    SDLC12207Check(
        clause_id="7.1.7", clause_ref="Software Qualification Testing",
        normative_req="The organization SHALL conduct qualification tests to verify software satisfies specified requirements.",
        category="IMPLEMENTATION", weight=5,
        search_terms=["test", "unittest", "pytest", "spec", "assert",
                      "mock", "fixture", "suite", "e2e"],
    ),

    # ── Clause 7.2: Software Support Processes ────────────────────────────────
    SDLC12207Check(
        clause_id="7.2.1", clause_ref="Software Documentation Management",
        normative_req="The organization SHALL record, produce, and maintain software documentation throughout the lifecycle.",
        category="SUPPORT", weight=4,
        search_terms=["readme", "docs", "documentation", "docstring", "api_docs",
                      "swagger", "openapi", "comments"],
    ),
    SDLC12207Check(
        clause_id="7.2.2", clause_ref="Software Configuration Management",
        normative_req="The organization SHALL manage dependencies, environment configurations, and build artifacts.",
        category="SUPPORT", weight=4,
        search_terms=["requirements.txt", "package.json", "pyproject.toml",
                      "cargo.toml", "go.mod", "pom.xml", "env.example"],
    ),
    SDLC12207Check(
        clause_id="7.2.3", clause_ref="Software Quality Assurance (SQA)",
        normative_req="The organization SHALL execute quality assurance audits, code reviews, and static analysis checks.",
        category="SUPPORT", weight=4,
        search_terms=["lint", "flake8", "eslint", "mypy", "pylint",
                      "sonar", "code_review", "format", "prettier", "black"],
    ),
    SDLC12207Check(
        clause_id="7.2.4", clause_ref="Software Verification Process",
        normative_req="The organization SHALL verify that software products conform to specified design constraints.",
        category="SUPPORT", weight=4,
        search_terms=["type_check", "static_analysis", "verifier", "inspection",
                      "assert", "validator", "conforms"],
    ),
    SDLC12207Check(
        clause_id="7.2.5", clause_ref="Software Validation Process",
        normative_req="The organization SHALL validate that software fulfills intended user needs in operational conditions.",
        category="SUPPORT", weight=4,
        search_terms=["acceptance_test", "user_testing", "validation", "approval",
                      "release_criteria", "staging_test"],
    ),
    SDLC12207Check(
        clause_id="7.2.8", clause_ref="Software Problem Resolution Process",
        normative_req="The organization SHALL establish a mechanism to report, analyze, and resolve defects and issues.",
        category="SUPPORT", weight=4,
        search_terms=["issue", "bug", "error_log", "exception_handling",
                      "sentry", "tracking", "github_issues", "troubleshoot"],
    ),

    # ── Clause 7.3: Software Reuse Processes ─────────────────────────────────
    SDLC12207Check(
        clause_id="7.3.2", clause_ref="Software Reuse Asset Management",
        normative_req="The organization SHALL manage reusable code assets, libraries, and common utilities.",
        category="REUSE", weight=3,
        search_terms=["utils", "helpers", "shared", "common", "library",
                      "base_class", "reusable", "framework"],
    ),
]


def scan_12207(root: Path, idx: IndexStoreAdapter) -> list[SDLC12207Check]:
    """Scan codebase for ISO/IEC 12207 SDLC normative requirements."""
    idx.rebuild(root)
    for check in SDLC_CHECKS:
        hits: set[str] = set()
        match_count = 0

        for term in check.search_terms:
            try:
                results = idx.search_code(term, limit=5)
                for r in results:
                    fp = getattr(r, 'path', None)
                    if fp and not any(x in fp for x in ("node_modules", ".git", "vendor", "__pycache__")):
                        hits.add(fp)
                        match_count += 1
            except Exception:
                pass

        check.evidence_files = sorted(list(hits))[:5]
        check.found = len(check.evidence_files) > 0
        ratio = match_count / max(len(check.search_terms), 1)

        if ratio >= 0.5:
            check.confidence = "HIGH"
        elif match_count >= 2:
            check.confidence = "MEDIUM"
        elif match_count >= 1:
            check.confidence = "LOW"
        else:
            check.confidence = "NONE"

    return SDLC_CHECKS


def calculate_score(checks: list[SDLC12207Check]) -> tuple[int, str, str]:
    total_weight = sum(c.weight for c in checks)
    achieved = sum(
        c.weight * (1.0 if c.confidence == "HIGH" else 0.6 if c.confidence == "MEDIUM" else 0.3 if c.confidence == "LOW" else 0)
        for c in checks
    )
    score = int((achieved / total_weight) * 100) if total_weight else 0

    if score >= 75:
        grade, status = "A  (Mature SDLC Compliance)", "🟢 HIGH — Robust SDLC life cycle processes implemented"
    elif score >= 50:
        grade, status = "B  (Partial SDLC Compliance)", "🟡 PARTIAL — Core construction present, gaps in SQA/testing/ops"
    elif score >= 25:
        grade, status = "C  (Initial/Ad-hoc SDLC)", "🟠 LOW — Minimal SDLC structure, missing quality assurance"
    else:
        grade, status = "F  (Non-Conformant SDLC)", "🔴 CRITICAL — Missing fundamental software engineering processes"

    return score, grade, status


def print_report(project: str, root: Path, checks: list[SDLC12207Check],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    score, grade, status = calculate_score(checks)
    conf_icon = {"HIGH": "✅", "MEDIUM": "🟡", "LOW": "⚠️", "NONE": "❌"}
    found_count = sum(1 for c in checks if c.found)

    by_cat: dict[str, list[SDLC12207Check]] = {}
    for c in checks:
        by_cat.setdefault(c.category, []).append(c)

    cat_titles = {
        "PROJECT": "§6.3 Project Processes (Planning, Risk, SCM, Measurement)",
        "TECHNICAL": "§6.4 System Technical Processes (Requirements, Architecture, Ops, Maintenance)",
        "IMPLEMENTATION": "§7.1 Software Implementation Processes (Analysis, Design, Coding, V&V)",
        "SUPPORT": "§7.2 Software Support Processes (Docs, Config, SQA, Problem Resolution)",
        "REUSE": "§7.3 Software Reuse Processes (Asset Management, Shared Libraries)",
    }

    lines = [
        f"# 💻 ISO/IEC 12207:2008 SDLC Life Cycle Auditor — {project}",
        f"> `{root}` · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 SDLC Compliance Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **ISO 12207 SDLC Score** | **{score} / 100** |",
        f"| **Conformance Grade** | **{grade}** |",
        f"| **Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Validated SDLC Processes | {found_count} / {len(checks)} |",
        "",
        "> **Standard**: ISO/IEC 12207:2008 / IEEE Std 12207-2008 — Systems and software engineering — Software life cycle processes.",
        "",
    ]

    for cat, cat_checks in by_cat.items():
        title = cat_titles.get(cat, cat)
        lines += [
            f"## 🔍 {title}",
            "",
            "| Clause | Process Title | Confidence | Evidence Files |",
            "|---|---|---|---|",
        ]
        for c in cat_checks:
            icon = conf_icon[c.confidence]
            ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2]) if c.evidence_files else "—"
            lines.append(f"| `{c.clause_id}` | {c.clause_ref} | {icon} {c.confidence} | {ev} |")
        lines.append("")

    gaps = [c for c in checks if c.confidence in ("NONE", "LOW")]
    if gaps:
        lines += ["## ⚠️ High-Priority SDLC Gaps", ""]
        for g in gaps:
            lines.append(f"- **{g.clause_id} {g.clause_ref}** (weight={g.weight}): {g.normative_req}")
        lines.append("")

    lines += [
        "## 🛠 ISO/IEC 12207 SDLC Remediation Roadmap",
        "",
        "### Phase 1 — Project & SCM Foundation (§6.3)",
        "- Enforce SCM baseline: `.gitignore`, `CHANGELOG.md`, Semantic Versioning",
        "- Implement risk management register for critical dependencies",
        "",
        "### Phase 2 — Technical & Implementation Quality (§7.1)",
        "- Enforce strict type validation & input schemas (`Pydantic`, `TypeScript`, `type annotations`)",
        "- Build unit and integration test suite with automated test runner (`pytest`, `jest`)",
        "",
        "### Phase 3 — Support & SQA (§7.2)",
        "- Add static analysis and linter configs (`flake8`, `mypy`, `eslint`, `prettier`)",
        "- Automate CI/CD pipeline for integration testing and automated deployment",
        "- Setup automated error tracking and problem resolution (`Sentry`, `logging`)",
        "",
        "---",
        f"*ISO/IEC 12207:2008 Software Life Cycle Processes Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 78
    print(f"\n{SEP}")
    print(f"  ISO/IEC 12207 SDLC PROCESSES AUDIT: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 12207 SDLC Score        : {score} / 100")
    print(f"  Grade                       : {grade}")
    print(f"  Validated SDLC Processes    : {found_count} / {len(checks)}")
    print(f"  Audit Duration              : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 iso_12207_sdlc_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name
    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_12207_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    checks = scan_12207(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, checks, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
