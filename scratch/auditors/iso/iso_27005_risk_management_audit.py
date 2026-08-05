#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   📊🔒 ISO/IEC 27005:2022 Information Security Risk Management Auditor     ║
║   BM25 + AST + Security Risk Assessment Register & Treatment Scanner      ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 27005 Security Risk Management:  ║
║   - Information Security Risk Register Documentation (RISK_REGISTER.md)   ║
║   - Automated Vulnerability CVSS Scoring & Threat Impact Matrix           ║
║   - Risk Treatment Plans & Mitigations (RISK_TREATMENT.md)                ║
║   - Residual Security Risk Acceptance Sign-off Logs                       ║
║   - ISO 27005 Risk Index (0–100) & Security Risk Governance Grade         ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_27005_risk_management_audit.py /path/to/project [ProjectName]
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
class ISO27005Metric:
    domain: str             # RISK_REGISTER / CVSS_SCORING / RISK_TREATMENT / RESIDUAL_ACCEPTANCE
    metric_id: str          # ISRM-001..ISRM-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


ISRM_METRICS: list[ISO27005Metric] = [
    ISO27005Metric(
        domain="RISK_REGISTER", metric_id="ISRM-001",
        title="Information Security Risk Register (RISK_REGISTER.md)",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains an information security risk register.",
        remediation="Document security risks in `RISK_REGISTER.md`.",
    ),
    ISO27005Metric(
        domain="CVSS_SCORING", metric_id="ISRM-002",
        title="Automated Vulnerability CVSS Scoring & Severity Classification",
        impact="POSITIVE", score_delta=+25,
        description="Repository categorizes vulnerabilities using CVSS v3/v4 scoring.",
        remediation="Categorize security defects using standard CVSS severity scores.",
    ),
    ISO27005Metric(
        domain="RISK_TREATMENT", metric_id="ISRM-003",
        title="Risk Treatment Plan & Mitigation Strategy Docs (RISK_TREATMENT.md)",
        impact="POSITIVE", score_delta=+25,
        description="Repository documents risk treatment strategies (mitigate, transfer, avoid).",
        remediation="Maintain a risk treatment matrix in `RISK_TREATMENT.md`.",
    ),
    ISO27005Metric(
        domain="RESIDUAL_ACCEPTANCE", metric_id="ISRM-004",
        title="Residual Security Risk Acceptance Sign-off Logs",
        impact="POSITIVE", score_delta=+25,
        description="Project records formal CISO sign-offs for accepted residual risks.",
        remediation="Log accepted residual risks and CISO sign-offs in risk documentation.",
    ),
]


PATTERNS = {
    "ISRM-001": ["RISK_REGISTER.md", "security_risk", "risk_assessment"],
    "ISRM-002": ["CVSS", "cvss_score", "severity_matrix", "vulnerability_score"],
    "ISRM-003": ["RISK_TREATMENT.md", "risk_mitigation", "treatment_plan"],
    "ISRM-004": ["residual_risk", "risk_acceptance", "ciso_signoff"],
}


def scan_iso27005(root: Path, idx: IndexStoreAdapter) -> list[ISO27005Metric]:
    """Scan codebase for ISO/IEC 27005 Information Security Risk Management controls."""
    for m in ISRM_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        if m.metric_id in ("ISRM-001", "ISRM-003"):
            risk_files = list(root.glob("*RISK*")) + list(root.glob("docs/*risk*"))
            if risk_files:
                hits.update(str(f.relative_to(root)) for f in risk_files[:4])

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

    return ISRM_METRICS


def calculate_iso27005_score(metrics: list[ISO27005Metric]) -> tuple[int, str, str]:
    """Calculate ISO 27005 Security Risk Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 27005 ISRM Certified)"
        status = "🟢 HIGH RISK GOVERNANCE — Risk Register, CVSS Scoring & Treatment Active"
    elif score >= 50:
        grade = "A (Good Risk Management)"
        status = "🟢 GOOD — Risk Register or CVSS Scoring Active"
    else:
        grade = "C/F (Security Risk Gap)"
        status = "🔴 RISK GOVERNANCE GAP — Missing Security Risk Register or CVSS Scoring"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO27005Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso27005_score(metrics)

    lines = [
        f"# 📊🔒 ISO/IEC 27005:2022 Information Security Risk Management Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 27005 ISRM Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 27005 Risk Score** | **{score} / 100** |",
        f"| **Risk Governance Grade** | **{grade}** |",
        f"| **Risk Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified ISRM Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 27005 ISRM Evidence",
        "",
        "| Domain | Risk Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 27005 ISRM Remediation Blueprint",
        "",
        "1. **Risk Register**: Maintain an information security risk register in `RISK_REGISTER.md`.",
        "2. **CVSS Scoring**: Classify security vulnerabilities using standard CVSS scores.",
        "3. **Treatment Matrix**: Document risk mitigation strategies in `RISK_TREATMENT.md`.",
        "",
        "---",
        f"*ISO/IEC 27005 Information Security Risk Management Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  📊🔒 ISO/IEC 27005 SECURITY RISK MANAGEMENT AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 27005 Risk Score        : {score} / 100")
    print(f"  Risk Governance Grade       : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_27005_risk_management_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_27005_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso27005(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
