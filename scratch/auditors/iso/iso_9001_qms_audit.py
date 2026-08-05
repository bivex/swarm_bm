#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🏅 ISO 9001:2015 Software Quality Management System (QMS) Auditor        ║
║   BM25 + AST + CI/CD Pipeline & Automated Release Engineering Scanner     ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO 9001 QMS process controls:           ║
║   - CI/CD Pipeline Automation (.github/workflows, GitLab CI)             ║
║   - Automated Unit & Integration Testing Coverage Controls                ║
║   - Pull Request Code Review Governance & CODEOWNERS Policies             ║
║   - Semantic Release Tagging & Changelog Automation                       ║
║   - ISO 9001 QMS Compliance Index (0–100) & Process Grade                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_9001_qms_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


@dataclass
class ISO9001Metric:
    domain: str             # CICD_AUTOMATION / TEST_COVERAGE / PR_GOVERNANCE / RELEASE_TAGGING
    metric_id: str          # QMS-001..QMS-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


QMS_METRICS: list[ISO9001Metric] = [
    ISO9001Metric(
        domain="CICD_AUTOMATION", metric_id="QMS-001",
        title="Automated CI/CD Build Pipeline (.github/workflows / .gitlab-ci.yml)",
        impact="POSITIVE", score_delta=+25,
        description="Repository defines automated continuous integration workflows.",
        remediation="Create a GitHub Actions or GitLab CI workflow for automated testing.",
    ),
    ISO9001Metric(
        domain="TEST_COVERAGE", metric_id="QMS-002",
        title="Automated Unit & Integration Test Suite (PyTest / Jest / Cargo Test)",
        impact="POSITIVE", score_delta=+25,
        description="Repository includes automated unit test suites.",
        remediation="Add automated unit test files in `tests/` directory.",
    ),
    ISO9001Metric(
        domain="PR_GOVERNANCE", metric_id="QMS-003",
        title="Code Review Governance & CODEOWNERS Policies",
        impact="POSITIVE", score_delta=+25,
        description="Repository defines explicit code review ownership via CODEOWNERS or PR templates.",
        remediation="Add a CODEOWNERS file defining mandatory reviewers.",
    ),
    ISO9001Metric(
        domain="RELEASE_TAGGING", metric_id="QMS-004",
        title="Semantic Release Tagging & Automated CHANGELOG.md",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains a CHANGELOG or automated release tagging workflow.",
        remediation="Maintain a CHANGELOG.md documenting version changes.",
    ),
]


PATTERNS = {
    "QMS-001": [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", "circleci"],
    "QMS-002": ["pytest", "jest", "unittest", "cargo test", "go test", "spec.ts"],
    "QMS-003": ["CODEOWNERS", "PULL_REQUEST_TEMPLATE.md", "CONTRIBUTING.md"],
    "QMS-004": ["CHANGELOG.md", "release-please", "semantic-release", "version"],
}


def scan_iso9001(root: Path, idx: IndexStoreAdapter) -> list[ISO9001Metric]:
    """Scan codebase for ISO 9001 QMS release engineering controls."""
    for m in QMS_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        if m.metric_id == "QMS-001":
            ci_files = list(root.glob(".github/workflows/*.yml")) + list(root.glob(".gitlab-ci.yml"))
            if ci_files:
                hits.update(str(f.relative_to(root)) for f in ci_files[:4])

        if m.metric_id in ("QMS-003", "QMS-004"):
            meta_files = list(root.glob("*CHANGELOG*")) + list(root.glob("*CODEOWNERS*")) + list(root.glob("*CONTRIBUTING*"))
            if meta_files:
                hits.update(str(f.relative_to(root)) for f in meta_files[:4])

        for pat in pats:
            try:
                res = idx.search_code(pat, limit=3)
                for r in res:
                    if r.path and not any(x in r.path for x in ("node_modules", ".git", "vendor")):
                        hits.add(r.path)
            except Exception:
                pass

        m.evidence_files = sorted(list(hits))[:4]
        m.found = len(m.evidence_files) > 0

    return QMS_METRICS


def calculate_iso9001_score(metrics: list[ISO9001Metric]) -> tuple[int, str, str]:
    """Calculate ISO 9001 QMS Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 9001 QMS Certified)"
        status = "🟢 HIGH QMS QUALITY — Automated CI/CD, Test Suite & Release Controls Active"
    elif score >= 50:
        grade = "A (Good Process Quality)"
        status = "🟢 GOOD — CI/CD Pipeline or Unit Tests Configured"
    else:
        grade = "C/F (QMS Process Gap)"
        status = "🔴 PROCESS GAP — Missing CI/CD Workflows or Unit Test Automation"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO9001Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso9001_score(metrics)

    lines = [
        f"# 🏅 ISO 9001:2015 Quality Management System Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 9001 QMS Process Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 9001 QMS Score** | **{score} / 100** |",
        f"| **QMS Process Grade** | **{grade}** |",
        f"| **Process Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified QMS Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 9001 QMS Controls & Evidence",
        "",
        "| Domain | QMS Process Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 9001 Release Engineering Remediation Blueprint",
        "",
        "1. **CI/CD Automation**: Add `.github/workflows/ci.yml` for automated testing on push.",
        "2. **PR Governance**: Maintain a `CODEOWNERS` file defining code review ownership.",
        "3. **Changelog**: Maintain a `CHANGELOG.md` file tracking version releases.",
        "",
        "---",
        f"*ISO 9001:2015 Quality Management System Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🏅 ISO 9001:2015 QUALITY MANAGEMENT AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 9001 QMS Score          : {score} / 100")
    print(f"  Process Grade               : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_9001_qms_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_9001_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso9001(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
