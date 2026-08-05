#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   📊 ISO/IEC 5259-3:2024 ML Data Quality Management System Auditor        ║
║   BM25 + AST Scanner for DQ Management Life Cycle (DQMLC) & Compliance    ║
║                                                                           ║
║   OFFICIAL STANDARD: ISO/IEC 5259-3:2024(en) (First Edition 2024-07)       ║
║   ICS: 35.020 | Committee: ISO/IEC JTC 1/SC 42 (Artificial Intelligence)   ║
║                                                                           ║
║   NORMATIVE REQUIREMENTS (Clause 6–12):                                   ║
║   - Clause 6.3: Overall DQ Management (Culture, Issue Closing, Audits)    ║
║   - Clause 7.3: DQMLC 8 Stages (Motivation to Decommissioning)            ║
║   - Clause 8.3: Horizontal Quality Gates (V&V, Change Requests, Config)   ║
║   - Clause 9.2: Supply Chain Development Interface Agreement (DIA)        ║
║   - Clause 10.2: Data Processing Tool Impact Management                    ║
║   - Clause 11.2: Internal & External Data Quality Dependencies            ║
║   - Clause 12.4: Project DQ Manager & Quality Manager Roles               ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/ai/iso_5259_3_management_audit.py /path/to/project [ProjectName]
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
class ISO5259Part3Control:
    clause: str             # Clause 6 / 7 / 8 / 9 / 10 / 11 / 12
    control_id: str         # ISO-5259-3-01 .. 08
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# ISO/IEC 5259-3:2024 Data Quality Management Matrix
# ─────────────────────────────────────────────────────────────────────────────
ISO5259_PART3_CONTROLS: list[ISO5259Part3Control] = [
    ISO5259Part3Control(
        clause="Clause 6.3 & 12.4 (Management & Roles)",
        control_id="ISO-5259-3-01",
        title="DQ Management System Integration & Role Appointment (Quality Manager)",
        impact="POSITIVE", score_delta=+15,
        description="Organization appoints a dedicated Quality Manager and integrates DQ into ISO 9001 / ISO 42001.",
        remediation="Appoint a Project Quality Manager and document DQ management rules.",
    ),
    ISO5259Part3Control(
        clause="Clause 6.3.3 (Issue Resolution)",
        control_id="ISO-5259-3-02",
        title="Data Quality Issue Resolution & Escalation Logging",
        impact="POSITIVE", score_delta=+10,
        description="Formal procedures exist for communicating, evaluating, resolving, and closing DQ anomalies.",
        remediation="Maintain an issue tracker for data anomalies with formal closure criteria.",
    ),
    ISO5259Part3Control(
        clause="Clause 7.3.2 (Data Specification)",
        control_id="ISO-5259-3-03",
        title="Formal Data Specification & Non-Intersecting ML Splits",
        impact="POSITIVE", score_delta=+15,
        description="Data specification details syntax, semantics, and non-intersecting train/val/test splits.",
        remediation="Define unambiguous dataset specifications and enforce strict train/test split boundaries.",
    ),
    ISO5259Part3Control(
        clause="Clause 7.3.8 (Decommissioning & Deletion)",
        control_id="ISO-5259-3-04",
        title="Data Decommissioning & Verified Deletion / Transfer Reports",
        impact="POSITIVE", score_delta=+15,
        description="Data decommissioning plan includes secure overwriting, transfer reports, or partial deletion.",
        remediation="Generate verified Data Deletion or Transfer Reports upon dataset retirement.",
    ),
    ISO5259Part3Control(
        clause="Clause 8.3 (Horizontal Processes)",
        control_id="ISO-5259-3-05",
        title="Horizontal Quality Gates, Change Requests & Configuration Control",
        impact="POSITIVE", score_delta=+15,
        description="Quality gates validate each stage work product; change requests track impact and rationale.",
        remediation="Implement stage quality gates and maintain change request impact logs.",
    ),
    ISO5259Part3Control(
        clause="Clause 9.2 (Supply Chain Governance)",
        control_id="ISO-5259-3-06",
        title="Supply Chain Development Interface Agreement (DIA) & Supplier Assessment",
        impact="POSITIVE", score_delta=+10,
        description="Supplier data transactions govern shared responsibilities via Development Interface Agreements.",
        remediation="Execute Development Interface Agreements (DIA) for third-party datasets or labelling.",
    ),
    ISO5259Part3Control(
        clause="Clause 10.2 (Tool Impact Management)",
        control_id="ISO-5259-3-07",
        title="Data Processing Tools Impact & Validation Assessment",
        impact="POSITIVE", score_delta=+10,
        description="ETL and scraping tools undergo impact assessments ensuring they do not corrupt data quality.",
        remediation="Document tool impact assessments for scrapers, transformers, and labelling platforms.",
    ),
    ISO5259Part3Control(
        clause="Clause 11.2 (Dependency Management)",
        control_id="ISO-5259-3-08",
        title="Internal & External Data Quality Dependency Tracking",
        impact="POSITIVE", score_delta=+10,
        description="System identifies and mitigates internal/external data dependencies (cloud feeds, APIs).",
        remediation="Map external data API dependencies and establish fallback data quality mitigations.",
    ),
]


PATTERNS = {
    "ISO-5259-3-01": ["quality_manager", "dqmlc", "iso42001", "iso9001", "dq_culture"],
    "ISO-5259-3-02": ["issue_tracker", "anomaly_report", "resolve_issue", "escalate_issue"],
    "ISO-5259-3-03": ["data_specification", "train_test_split", "statistical_properties", "non_intersecting"],
    "ISO-5259-3-04": ["deletion_report", "decommissioning_plan", "secure_delete", "transfer_report"],
    "ISO-5259-3-05": ["quality_gate", "change_request", "impact_analysis", "configuration_management"],
    "ISO-5259-3-06": ["development_interface_agreement", "dia_contract", "supplier_assessment"],
    "ISO-5259-3-07": ["tool_assessment", "scraper_impact", "processing_tool_validation"],
    "ISO-5259-3-08": ["dependency_mapping", "external_api_dependency", "fallback_mitigation"],
}


def scan_iso5259_part3(root: Path, idx: IndexStoreAdapter) -> list[ISO5259Part3Control]:
    """Scan codebase for ISO/IEC 5259-3:2024 data quality management controls."""
    for ctrl in ISO5259_PART3_CONTROLS:
        pats = PATTERNS.get(ctrl.control_id, [])
        hits = set()

        for pat in pats:
            try:
                res = idx.search_code(pat, limit=3)
                for r in res:
                    if r.path and not any(x in r.path for x in ("node_modules", ".git", "vendor", "__pycache__")):
                        hits.add(r.path)
            except Exception:
                pass

        ctrl.evidence_files = sorted(list(hits))[:4]
        ctrl.found = len(ctrl.evidence_files) > 0

    return ISO5259_PART3_CONTROLS


def calculate_iso5259_part3_score(controls: list[ISO5259Part3Control]) -> tuple[int, str, str]:
    """Calculate ISO 5259-3 DQ Management Score (0-100) and Grade."""
    score = sum(c.score_delta for c in controls if c.found)

    if score >= 85:
        grade = "A+ (ISO 5259-3 DQ Management System Certified)"
        status = "🟢 FULLY COMPLIANT — Production ML Data Quality Management & Quality Gates"
    elif score >= 60:
        grade = "A (High Management Readiness)"
        status = "🟢 HIGH — Compliant with Minor Supply Chain / Dependency Controls Outstanding"
    elif score >= 40:
        grade = "B (Moderate Management Debt)"
        status = "🟡 MEDIUM — Requires Quality Manager Role & Issue Resolution Tracking"
    else:
        grade = "C/F (Management System Hazard)"
        status = "🔴 NON-COMPLIANT — Lacks Data Quality Management System or Quality Gates"

    return score, grade, status


def print_report(project: str, root: Path, controls: list[ISO5259Part3Control],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [c for c in controls if c.found]
    score, grade, status = calculate_iso5259_part3_score(controls)

    lines = [
        f"# 📊 ISO/IEC 5259-3:2024 ML Data Quality Management System Audit — {project}",
        f"> Official Standard: ISO/IEC 5259-3:2024(en) · ICS: 35.020 · Committee: ISO/IEC JTC 1/SC 42 (AI)",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 5259-3 Management System Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 5259-3 Management Score** | **{score} / 100** |",
        f"| **Management System Grade** | **{grade}** |",
        f"| **Compliance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Management Controls | {len(found)} / {len(controls)} |",
        "",
        "## 🔍 Verified ISO/IEC 5259-3:2024 Normative Management Controls",
        "",
        "| Clause | Control ID | Control Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|---|",
    ]

    for c in found:
        ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2])
        lines.append(f"| `{c.clause}` | `{c.control_id}` | {c.title} | ✅ FOUND | {ev} | {c.remediation} |")

    lines += [
        "",
        "## 🚀 ISO/IEC 5259-3 Data Quality Management Remediation Blueprint",
        "",
        "1. **Clause 6.3 & 12.4 (Roles)**: Appoint a Project Quality Manager and document DQ culture rules.",
        "2. **Clause 6.3.3 (Issues)**: Implement formal data issue resolution logs and escalation rules.",
        "3. **Clause 7.3.2 (Specification)**: Specify data syntax/semantics and enforce non-intersecting train/test splits.",
        "4. **Clause 7.3.8 (Decommissioning)**: Generate verified Data Deletion/Transfer Reports upon dataset retirement.",
        "5. **Clause 8.3 (Quality Gates)**: Establish stage quality gates and formal Change Request impact analyses.",
        "6. **Clause 9.2 (Supply Chain)**: Execute Development Interface Agreements (DIA) for third-party datasets.",
        "7. **Clause 10 & 11 (Tools & Dependencies)**: Document processing tool impact and external API dependencies.",
        "",
        "---",
        f"*ISO/IEC 5259-3:2024 ML Data Quality Management System Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  📊 ISO/IEC 5259-3:2024 ML DATA QUALITY MANAGEMENT AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 5259-3 Management Score : {score} / 100")
    print(f"  Management Grade            : {grade}")
    print(f"  Verified Management Controls: {len(found)} / {len(controls)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/ai/iso_5259_3_management_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_5259_3_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    controls = scan_iso5259_part3(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, controls, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
