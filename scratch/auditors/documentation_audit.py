#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  Documentation & Knowledge Management Auditor (ISO/IEC 26514 / ISO 12207 §7.2.1) ║
║                                                                               ║
║  PURPOSE: Evaluates codebase documentation quality, completeness & coverage: ║
║  1. Project-level Docs (README, Architecture, Contributing, Changelog, License)║
║  2. API & Code Documentation (Docstrings coverage, type hints, inline comments)║
║  3. Developer Onboarding & Guides (Setup, Environment, Usage examples)        ║
║  4. API Reference Docs (Swagger/OpenAPI, Sphynx, MkDocs, Markdown docs)       ║
║  5. Maintenance & Currency (Recent doc updates, version alignment)           ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/documentation_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import ast
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
class DocCheck:
    check_id: str           # e.g. "DOC-001"
    category: str           # PROJECT_DOCS / CODE_DOCS / ONBOARDING / API_DOCS / MAINTENANCE
    title: str
    description: str
    weight: int
    search_terms: list[str]
    evidence_files: list[str] = field(default_factory=list)
    found: bool = False
    confidence: str = "NONE"


DOC_CHECKS: list[DocCheck] = [

    # ── 1. Project-Level Documentation ────────────────────────────────────────
    DocCheck(
        check_id="DOC-001", category="PROJECT_DOCS",
        title="Comprehensive README File",
        description="Repository contains a primary README file explaining purpose, installation, and overview.",
        weight=5,
        search_terms=["readme.md", "readme.rst", "readme.txt", "readme"],
    ),
    DocCheck(
        check_id="DOC-002", category="PROJECT_DOCS",
        title="Architecture & System Design Documentation",
        description="Architecture diagrams, system design specs, or ADR (Architecture Decision Records).",
        weight=4,
        search_terms=["architecture", "design", "system_design", "adr", "architecture.md", "docs/architecture"],
    ),
    DocCheck(
        check_id="DOC-003", category="PROJECT_DOCS",
        title="License & Legal Terms",
        description="Legal license file (MIT, Apache, GPL, Proprietary) defining terms of use.",
        weight=4,
        search_terms=["license", "license.md", "license.txt", "copying", "terms"],
    ),
    DocCheck(
        check_id="DOC-004", category="PROJECT_DOCS",
        title="Changelog & Release Notes",
        description="Documented history of changes, version releases, and deprecations.",
        weight=3,
        search_terms=["changelog", "changelog.md", "release_notes", "history.md", "releases"],
    ),
    DocCheck(
        check_id="DOC-005", category="PROJECT_DOCS",
        title="Contribution Guidelines (CONTRIBUTING.md)",
        description="Guidelines for external/internal contributors on code style, PR process, and commit rules.",
        weight=3,
        search_terms=["contributing.md", "contributing", "developer_guide", "code_of_conduct"],
    ),

    # ── 2. Code & API Docstring Coverage ──────────────────────────────────────
    DocCheck(
        check_id="DOC-006", category="CODE_DOCS",
        title="Module & Class Level Docstrings",
        description="Python modules and classes contain explanatory docstrings detailing purpose and usage.",
        weight=4,
        search_terms=["\"\"\"", "'''", "docstring", "__doc__"],
    ),
    DocCheck(
        check_id="DOC-007", category="CODE_DOCS",
        title="Type Annotations & Function Signature Specs",
        description="Functions and methods use Type Hints and parameter/return docstrings.",
        weight=4,
        search_terms=["def ", "->", "typing", "optional", "list[", "dict[", "param", "returns"],
    ),
    DocCheck(
        check_id="DOC-008", category="CODE_DOCS",
        title="Inline Comments & Complex Logic Explanations",
        description="Non-trivial code blocks contain inline comments explaining algorithm rationale.",
        weight=3,
        search_terms=["# ", "// ", "todo", "note:", "fixme", "hack:"],
    ),

    # ── 3. Developer Onboarding & Setup ───────────────────────────────────────
    DocCheck(
        check_id="DOC-009", category="ONBOARDING",
        title="Environment Setup & Quickstart Guide",
        description="Clear instructions for local environment setup, virtual environments, and dependencies.",
        weight=4,
        search_terms=["quickstart", "getting_started", "installation", "pip install", "npm install", "setup"],
    ),
    DocCheck(
        check_id="DOC-010", category="ONBOARDING",
        title="Usage Examples & Sample Code",
        description="Executable code samples, demo scripts, or usage snippets demonstrating features.",
        weight=4,
        search_terms=["examples", "samples", "demo", "tutorial", "usage", "snippet"],
    ),
    DocCheck(
        check_id="DOC-011", category="ONBOARDING",
        title="Environment Variables & Configuration Docs",
        description="Documented configuration parameters, `.env.example`, or config file specs.",
        weight=3,
        search_terms=[".env.example", "config.example", "environment_variables", "settings.md"],
    ),

    # ── 4. API Reference & Technical Docs ─────────────────────────────────────
    DocCheck(
        check_id="DOC-012", category="API_DOCS",
        title="API Reference Specifications (OpenAPI/Swagger/Markdown)",
        description="Formally generated or written API endpoint documentation (OpenAPI, REST, gRPC).",
        weight=4,
        search_terms=["openapi", "swagger", "api.md", "endpoints", "fastapi", "routes", "rest_api"],
    ),
    DocCheck(
        check_id="DOC-013", category="API_DOCS",
        title="Dedicated Documentation Directory (`docs/`)",
        description="Structured documentation folder containing markdown/Sphinx/MkDocs user guides.",
        weight=4,
        search_terms=["docs/", "doc/", "mkdocs.yml", "conf.py", "sphinx"],
    ),

    # ── 5. Maintenance & Governance ──────────────────────────────────────────
    DocCheck(
        check_id="DOC-014", category="MAINTENANCE",
        title="Security & Vulnerability Reporting Policy (SECURITY.md)",
        description="Documented policy for reporting security vulnerabilities responsibly.",
        weight=3,
        search_terms=["security.md", "vulnerability_policy", "security_policy"],
    ),
]


def AST_docstring_audit(root: Path) -> tuple[int, int, float]:
    """
    Perform direct AST analysis on Python files to measure exact Docstring Coverage.
    Returns: (total_functions_classes, documented_functions_classes, coverage_percentage)
    """
    total = 0
    documented = 0

    for py_file in root.rglob("*.py"):
        if any(x in str(py_file) for x in ("node_modules", ".git", "venv", ".venv", "__pycache__", "build", "dist")):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    total += 1
                    if ast.get_docstring(node):
                        documented += 1
        except Exception:
            pass

    pct = (documented / total * 100) if total > 0 else 0.0
    return total, documented, round(pct, 1)


def scan_documentation(root: Path, idx: IndexStoreAdapter) -> list[DocCheck]:
    """Scan codebase for documentation evidence using BM25 and file tree inspection."""
    idx.rebuild(root)
    for check in DOC_CHECKS:
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

    return DOC_CHECKS


def calculate_score(checks: list[DocCheck]) -> tuple[int, str, str]:
    total_weight = sum(c.weight for c in checks)
    achieved = sum(
        c.weight * (1.0 if c.confidence == "HIGH" else 0.6 if c.confidence == "MEDIUM" else 0.3 if c.confidence == "LOW" else 0)
        for c in checks
    )
    score = int((achieved / total_weight) * 100) if total_weight else 0

    if score >= 85:
        grade, status = "A+ (Exemplary Documentation)", "🟢 EXCELLENT — Complete project, API & code-level documentation"
    elif score >= 70:
        grade, status = "A  (Good Documentation)", "🟢 GOOD — Core guides & docstrings present, minor gaps"
    elif score >= 50:
        grade, status = "B  (Partial Documentation)", "🟡 PARTIAL — Basic README present, missing API/architecture docs"
    elif score >= 25:
        grade, status = "C  (Minimal Documentation)", "🟠 LOW — Sparse documentation, missing setup/architecture guides"
    else:
        grade, status = "F  (Undocumented Codebase)", "🔴 CRITICAL — Missing README, docstrings and setup guides"

    return score, grade, status


def print_report(project: str, root: Path, checks: list[DocCheck],
                 ast_stats: tuple[int, int, float], stats: dict,
                 elapsed: float, report_path: Path) -> None:
    score, grade, status = calculate_score(checks)
    total_symbols, doc_symbols, doc_pct = ast_stats
    conf_icon = {"HIGH": "✅", "MEDIUM": "🟡", "LOW": "⚠️", "NONE": "❌"}
    found_count = sum(1 for c in checks if c.found)

    by_cat: dict[str, list[DocCheck]] = {}
    for c in checks:
        by_cat.setdefault(c.category, []).append(c)

    cat_titles = {
        "PROJECT_DOCS": "1. Project-Level Documentation (README, Architecture, License)",
        "CODE_DOCS": "2. Code & API Docstring Coverage (AST Analysis)",
        "ONBOARDING": "3. Developer Onboarding & Quickstart (Setup, Samples, Config)",
        "API_DOCS": "4. Technical & API Specifications (Docs directory, OpenAPI)",
        "MAINTENANCE": "5. Maintenance & Governance (Security policy, Contributing)",
    }

    lines = [
        f"# 📚 Documentation & Knowledge Management Audit — {project}",
        f"> `{root}` · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 Documentation Quality Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **Documentation Score** | **{score} / 100** |",
        f"| **Documentation Grade** | **{grade}** |",
        f"| **Status** | **{status}** |",
        f"| **AST Docstring Coverage** | **{doc_pct}%** ({doc_symbols}/{total_symbols} functions/classes) |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Validated Doc Elements | {found_count} / {len(checks)} |",
        "",
        "> **Standards Basis**: ISO/IEC 26514 (Software User Documentation) & ISO/IEC 12207 §7.2.1 (Software Documentation Management).",
        "",
    ]

    for cat, cat_checks in by_cat.items():
        title = cat_titles.get(cat, cat)
        lines += [
            f"## 🔍 {title}",
            "",
            "| ID | Check Title | Confidence | Evidence Files |",
            "|---|---|---|---|",
        ]
        for c in cat_checks:
            icon = conf_icon[c.confidence]
            ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2]) if c.evidence_files else "—"
            lines.append(f"| `{c.check_id}` | {c.title} | {icon} {c.confidence} | {ev} |")
        lines.append("")

    gaps = [c for c in checks if c.confidence in ("NONE", "LOW")]
    if gaps:
        lines += ["## ⚠️ Documentation Gaps & Recommendations", ""]
        for g in gaps:
            lines.append(f"- **{g.check_id}** {g.title} (weight={g.weight}): {g.description}")
        lines.append("")

    lines += [
        "## 🛠 Documentation Improvement Roadmap",
        "",
        "### 1. Essential Project Docs",
        "- Ensure `README.md` covers project description, features, setup, and usage examples",
        "- Create `LICENSE` file defining open-source / commercial licensing terms",
        "- Add `CHANGELOG.md` to track version history",
        "",
        "### 2. Developer Onboarding & Architecture",
        "- Create `docs/ARCHITECTURE.md` with system design diagrams and module boundaries",
        "- Provide `.env.example` with documented environment configuration keys",
        "- Add executable code samples in `examples/` directory",
        "",
        "### 3. Code-Level Documentation (AST)",
        f"- Target 80%+ docstring coverage (current: {doc_pct}%) for public functions and classes",
        "- Use Type Hints on all function parameters and return values",
        "",
        "---",
        f"*Documentation & Knowledge Management Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 78
    print(f"\n{SEP}")
    print(f"  DOCUMENTATION & KNOWLEDGE AUDIT: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  Documentation Score         : {score} / 100")
    print(f"  Documentation Grade         : {grade}")
    print(f"  AST Docstring Coverage      : {doc_pct}% ({doc_symbols}/{total_symbols} symbols)")
    print(f"  Validated Elements          : {found_count} / {len(checks)}")
    print(f"  Audit Duration              : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 documentation_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name
    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"documentation_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    ast_stats = AST_docstring_audit(project_path)
    checks = scan_documentation(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, checks, ast_stats, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
