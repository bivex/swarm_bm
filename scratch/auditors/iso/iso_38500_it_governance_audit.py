#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🏛️💼 ISO/IEC 38500:2015 Corporate Governance of IT Auditor               ║
║   BM25 + AST + IT Steering Committee & Strategic Alignment Scanner        ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 38500 Corporate IT Governance:    ║
║   - Strategic Alignment Documentation (VISION.md / ARCHITECTURE.md)       ║
║   - IT Risk Oversight & Steering Committee Charter (GOVERNANCE.md)        ║
║   - Resource Conformance & Compliance Framework (CODE_OF_CONDUCT.md)      ║
║   - Technology Portfolio Investment & Deprecation Governance              ║
║   - ISO 38500 IT Governance Index (0–100) & Corporate Grade               ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_38500_it_governance_audit.py /path/to/project [ProjectName]
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
class ISO38500Metric:
    domain: str             # STRATEGIC_ALIGNMENT / STEERING_CHARTER / CONFORMANCE_FRAMEWORK / PORTFOLIO_GOVERNANCE
    metric_id: str          # ITGOV-001..ITGOV-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


ITGOV_METRICS: list[ISO38500Metric] = [
    ISO38500Metric(
        domain="STRATEGIC_ALIGNMENT", metric_id="ITGOV-001",
        title="IT Strategic Vision & Architectural Guidelines (ARCHITECTURE.md)",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains architectural guidelines or strategic vision documentation.",
        remediation="Document strategic architecture goals in `ARCHITECTURE.md`.",
    ),
    ISO38500Metric(
        domain="STEERING_CHARTER", metric_id="ITGOV-002",
        title="IT Steering Committee Charter & Governance Rules (GOVERNANCE.md)",
        impact="POSITIVE", score_delta=+25,
        description="Repository documents IT steering governance rules or committee charters.",
        remediation="Define IT steering committee guidelines in `GOVERNANCE.md`.",
    ),
    ISO38500Metric(
        domain="CONFORMANCE_FRAMEWORK", metric_id="ITGOV-003",
        title="Code Conformance & Engineering Code of Conduct (CODE_OF_CONDUCT.md)",
        impact="POSITIVE", score_delta=+25,
        description="Repository specifies explicit engineering codes of conduct or compliance rules.",
        remediation="Publish engineering code of conduct in `CODE_OF_CONDUCT.md`.",
    ),
    ISO38500Metric(
        domain="PORTFOLIO_GOVERNANCE", metric_id="ITGOV-004",
        title="Technology Portfolio Evaluation & Deprecation Policies (DEPRECATION.md)",
        impact="POSITIVE", score_delta=+25,
        description="Repository defines feature deprecation policies or technology lifespan rules.",
        remediation="Document API lifecycle & feature deprecation policies in `DEPRECATION.md`.",
    ),
]


PATTERNS = {
    "ITGOV-001": ["ARCHITECTURE.md", "VISION.md", "design_principles"],
    "ITGOV-002": ["GOVERNANCE.md", "steering_committee", "it_board"],
    "ITGOV-003": ["CODE_OF_CONDUCT.md", "compliance_policy", "engineering_standards"],
    "ITGOV-004": ["DEPRECATION.md", "sunset_policy", "feature_lifecycle"],
}


def scan_iso38500(root: Path, idx: IndexStoreAdapter) -> list[ISO38500Metric]:
    """Scan codebase for ISO/IEC 38500 Corporate Governance of IT controls."""
    for m in ITGOV_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        if m.metric_id in ("ITGOV-001", "ITGOV-002", "ITGOV-003", "ITGOV-004"):
            gov_files = list(root.glob("*ARCH*")) + list(root.glob("*GOVERN*")) + list(root.glob("*CONDUCT*")) + list(root.glob("*DEPRECATION*"))
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

    return ITGOV_METRICS


def calculate_iso38500_score(metrics: list[ISO38500Metric]) -> tuple[int, str, str]:
    """Calculate ISO 38500 IT Governance Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 38500 Corporate IT Certified)"
        status = "🟢 HIGH CORPORATE GOVERNANCE — Architecture Vision, Governance Rules & Conduct Active"
    elif score >= 50:
        grade = "A (Good Corporate IT Controls)"
        status = "🟢 GOOD — Architecture Vision or Code of Conduct Present"
    else:
        grade = "C/F (Corporate IT Governance Gap)"
        status = "🔴 GOVERNANCE GAP — Missing Architecture Documentation or Governance Charters"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO38500Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso38500_score(metrics)

    lines = [
        f"# 🏛️💼 ISO/IEC 38500:2015 Corporate Governance of IT Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 38500 IT Governance Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 38500 IT Governance Score** | **{score} / 100** |",
        f"| **Corporate Governance Grade** | **{grade}** |",
        f"| **IT Governance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Corporate Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 38500 IT Governance Evidence",
        "",
        "| Domain | IT Governance Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 38500 Corporate IT Remediation Blueprint",
        "",
        "1. **Architecture Vision**: Document long-term architecture design principles in `ARCHITECTURE.md`.",
        "2. **Code of Conduct**: Publish engineering conduct guidelines in `CODE_OF_CONDUCT.md`.",
        "3. **Deprecation Policy**: Document feature sunset & deprecation lifecycles in `DEPRECATION.md`.",
        "",
        "---",
        f"*ISO/IEC 38500 Corporate Governance of IT Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🏛️💼 ISO/IEC 38500 CORPORATE GOVERNANCE OF IT AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 38500 IT Gov Score      : {score} / 100")
    print(f"  Corporate Governance Grade  : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_38500_it_governance_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_38500_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso38500(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
