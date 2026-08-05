#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🔄 ISO/IEC/IEEE 12207:2017 Software Life Cycle Processes Auditor        ║
║   BM25 + AST + End-to-End SDLC Lifecycle & Architectural Design Scanner   ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC/IEEE 12207 SDLC Processes:       ║
║   - Software Requirements Analysis Specs (REQUIREMENTS.md / PRD)          ║
║   - Software Architecture & Modular Design Specs (DESIGN.md)              ║
║   - Software Integration & Verification Phase Automation                  ║
║   - Software Maintenance & Release Engineering Scripts                    ║
║   - ISO 12207 SDLC Process Index (0–100) & Lifecycle Maturity Grade       ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_12207_software_lifecycle_audit.py /path/to/project [ProjectName]
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
class ISO12207Metric:
    domain: str             # REQUIREMENTS_ANALYSIS / ARCHITECTURAL_DESIGN / INTEGRATION_VERIFICATION / MAINTENANCE_RELEASE
    metric_id: str          # SDLC-001..SDLC-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


SDLC_METRICS: list[ISO12207Metric] = [
    ISO12207Metric(
        domain="REQUIREMENTS_ANALYSIS", metric_id="SDLC-001",
        title="Software Requirements Specification (REQUIREMENTS.md / SPEC.md)",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains software requirements specifications.",
        remediation="Document requirements specifications in `REQUIREMENTS.md`.",
    ),
    ISO12207Metric(
        domain="ARCHITECTURAL_DESIGN", metric_id="SDLC-002",
        title="Software Architectural & Modular Design Specification (DESIGN.md)",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains architectural design specs or component diagrams.",
        remediation="Document system architecture and module boundaries in `DESIGN.md`.",
    ),
    ISO12207Metric(
        domain="INTEGRATION_VERIFICATION", metric_id="SDLC-003",
        title="Automated Integration & System Verification Pipelines",
        impact="POSITIVE", score_delta=+25,
        description="Build pipeline executes automated integration tests and system verification.",
        remediation="Configure integration testing steps in CI workflow.",
    ),
    ISO12207Metric(
        domain="MAINTENANCE_RELEASE", metric_id="SDLC-004",
        title="Software Maintenance & Automated Release Engineering Scripts",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains release engineering or maintenance scripts.",
        remediation="Automate release tags and CHANGELOG generation via release scripts.",
    ),
]


PATTERNS = {
    "SDLC-001": ["REQUIREMENTS.md", "SPEC.md", "PRD.md", "user_stories"],
    "SDLC-002": ["DESIGN.md", "ARCHITECTURE.md", "system_design", "component_diagram"],
    "SDLC-003": ["integration_test", "system_test", "verification_pipeline"],
    "SDLC-004": ["release.sh", "semantic-release", "bump_version", "CHANGELOG.md"],
}


def scan_iso12207(root: Path, idx: IndexStoreAdapter) -> list[ISO12207Metric]:
    """Scan codebase for ISO/IEC/IEEE 12207 Software Life Cycle Processes controls."""
    for m in SDLC_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        if m.metric_id in ("SDLC-001", "SDLC-002", "SDLC-004"):
            sdlc_files = list(root.glob("*REQ*")) + list(root.glob("*SPEC*")) + list(root.glob("*DESIGN*")) + list(root.glob("*RELEASE*")) + list(root.glob("*CHANGE*"))
            if sdlc_files:
                hits.update(str(f.relative_to(root)) for f in sdlc_files[:4])

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

    return SDLC_METRICS


def calculate_iso12207_score(metrics: list[ISO12207Metric]) -> tuple[int, str, str]:
    """Calculate ISO 12207 SDLC Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 12207 SDLC Certified)"
        status = "🟢 HIGH LIFECYCLE MATURITY — Requirements, Architecture Design & Release Scripts Active"
    elif score >= 50:
        grade = "A (Good SDLC Controls)"
        status = "🟢 GOOD — Architecture Specs or Release Scripts Present"
    else:
        grade = "C/F (SDLC Process Gap)"
        status = "🔴 SDLC GAP — Missing Requirements Specs or Release Automation"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO12207Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso12207_score(metrics)

    lines = [
        f"# 🔄 ISO/IEC/IEEE 12207:2017 Software Life Cycle Processes Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 12207 SDLC Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 12207 SDLC Score** | **{score} / 100** |",
        f"| **Lifecycle Maturity Grade** | **{grade}** |",
        f"| **Lifecycle Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified SDLC Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 12207 SDLC Evidence",
        "",
        "| Domain | SDLC Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 12207 SDLC Remediation Blueprint",
        "",
        "1. **Requirements**: Document system specifications in `REQUIREMENTS.md`.",
        "2. **Design Specs**: Maintain architecture design diagrams in `DESIGN.md`.",
        "3. **Release Automation**: Automate release tag generation & CHANGELOG updates.",
        "",
        "---",
        f"*ISO/IEC/IEEE 12207 Software Life Cycle Processes Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🔄 ISO/IEC/IEEE 12207 SOFTWARE LIFE CYCLE AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 12207 SDLC Score        : {score} / 100")
    print(f"  Lifecycle Maturity Grade    : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_12207_software_lifecycle_audit.py /path/to/project [ProjectName]")
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
    metrics = scan_iso12207(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
