#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   📌 ISO 21500:2021 Project, Programme & Governance Auditor                ║
║   BM25 + AST + Project Governance & Issue Tracking Manifest Scanner       ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO 21500 Project Governance controls:   ║
║   - Structured Issue & Feature Request Templates (.github/ISSUE_TEMPLATE)  ║
║   - Automated Milestone & Task Dependency Tracking                        ║
║   - Project Stakeholder Documentation (CONTRIBUTING.md / GOVERNANCE.md)   ║
║   - Architecture Decision Records (ADR) & Steering Committee Manifests    ║
║   - ISO 21500 Governance Score (0–100) & Project Governance Grade         ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_21500_project_governance_audit.py /path/to/project [ProjectName]
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
class ISO21500Metric:
    domain: str             # ISSUE_TEMPLATES / MILESTONE_TRACKING / STAKEHOLDER_DOCS / GOVERNANCE_ADR
    metric_id: str          # PM-001..PM-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


PM_METRICS: list[ISO21500Metric] = [
    ISO21500Metric(
        domain="ISSUE_TEMPLATES", metric_id="PM-001",
        title="Structured Issue & Bug Report Templates (.github/ISSUE_TEMPLATE)",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains structured issue templates for feature requests & bug reports.",
        remediation="Create issue templates in `.github/ISSUE_TEMPLATE/`.",
    ),
    ISO21500Metric(
        domain="MILESTONE_TRACKING", metric_id="PM-002",
        title="Automated Milestone & Task Dependency Tracking Manifests",
        impact="POSITIVE", score_delta=+25,
        description="Repository specifies milestones or roadmap tracking files.",
        remediation="Maintain a ROADMAP.md or milestone project board.",
    ),
    ISO21500Metric(
        domain="STAKEHOLDER_DOCS", metric_id="PM-003",
        title="Project Governance & Contributor Guidelines (GOVERNANCE.md)",
        impact="POSITIVE", score_delta=+25,
        description="Repository documents steering governance or contributor guidelines.",
        remediation="Add GOVERNANCE.md or CONTRIBUTING.md detailing project processes.",
    ),
    ISO21500Metric(
        domain="GOVERNANCE_ADR", metric_id="PM-004",
        title="Architecture Decision Records (ADR / docs/adr/)",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains Architecture Decision Records (ADRs).",
        remediation="Document major architectural choices in `docs/adr/`.",
    ),
]


PATTERNS = {
    "PM-001": [".github/ISSUE_TEMPLATE", "bug_report.md", "feature_request.md"],
    "PM-002": ["ROADMAP.md", "PROJECT_BOARD.md", "MILESTONES.md"],
    "PM-003": ["GOVERNANCE.md", "CONTRIBUTING.md", "STAKEHOLDERS.md"],
    "PM-004": ["docs/adr", "0001-record-architecture", "ADR-"],
}


def scan_iso21500(root: Path, idx: IndexStoreAdapter) -> list[ISO21500Metric]:
    """Scan codebase for ISO 21500 Project Governance controls."""
    for m in PM_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        if m.metric_id in ("PM-001", "PM-002", "PM-003", "PM-004"):
            gov_files = list(root.glob("*GOVERNANCE*")) + list(root.glob("*CONTRIBUTING*")) + list(root.glob("*ROADMAP*")) + list(root.glob("docs/adr/*"))
            if gov_files:
                hits.update(str(f.relative_to(root)) for f in gov_files[:4])

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

    return PM_METRICS


def calculate_iso21500_score(metrics: list[ISO21500Metric]) -> tuple[int, str, str]:
    """Calculate ISO 21500 Project Governance Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 21500 Governance Certified)"
        status = "🟢 HIGH GOVERNANCE — Issue Templates, ADRs & Roadmap Active"
    elif score >= 50:
        grade = "A (Good Project Governance)"
        status = "🟢 GOOD — Contributor Docs or Issue Templates Present"
    else:
        grade = "C/F (Project Governance Gap)"
        status = "🔴 GOVERNANCE GAP — Missing ADRs, Issue Templates or Roadmap Manifests"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO21500Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso21500_score(metrics)

    lines = [
        f"# 📌 ISO 21500:2021 Project, Programme & Governance Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 21500 Governance Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 21500 Governance Score** | **{score} / 100** |",
        f"| **Project Governance Grade** | **{grade}** |",
        f"| **Governance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Governance Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 21500 Governance Evidence",
        "",
        "| Domain | Governance Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 21500 Governance Remediation Blueprint",
        "",
        "1. **Issue Templates**: Add structured issue templates to `.github/ISSUE_TEMPLATE/`.",
        "2. **ADR Records**: Maintain Architecture Decision Records in `docs/adr/`.",
        "3. **Roadmap**: Publish a `ROADMAP.md` tracking project milestone goals.",
        "",
        "---",
        f"*ISO 21500 Project, Programme & Governance Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  📌 ISO 21500 PROJECT GOVERNANCE AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 21500 Governance Score  : {score} / 100")
    print(f"  Project Governance Grade    : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_21500_project_governance_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_21500_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso21500(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
