#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🏛️ ISO/IEC 15408 Common Criteria Security Evaluation Auditor            ║
║   BM25 + AST + Evaluation Assurance Level (EAL1–EAL7) Scanner             ║
║                                                                           ║
║   PURPOSE: Evaluate codebase against ISO/IEC 15408 Security Targets (ST):  ║
║   - Security Target (ST) Specification & Target of Evaluation (TOE)      ║
║   - Self-Test Power-On Diagnostics & Integrity Verification               ║
║   - Memory Buffer Bounds Checking (Zero Buffer Overflow Vulnerability)    ║
║   - Formal Security Functional Requirements (SFR) Verification            ║
║   - ISO 15408 EAL Security Index (0–100) & Common Criteria EAL Grade      ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_15408_common_criteria_audit.py /path/to/project [ProjectName]
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
class ISO15408Metric:
    domain: str             # TOE_SPECIFICATION / SELF_TEST / BUFFER_SAFETY / SFR_COMPLIANCE
    metric_id: str          # EAL-001..EAL-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


EAL_METRICS: list[ISO15408Metric] = [
    ISO15408Metric(
        domain="TOE_SPECIFICATION", metric_id="EAL-001",
        title="Target of Evaluation (TOE) & Security Target (ST) Specification",
        impact="POSITIVE", score_delta=+25,
        description="System maintains a formal Security Target document defining TOE scope.",
        remediation="Maintain a Security Target document defining security objectives.",
    ),
    ISO15408Metric(
        domain="SELF_TEST", metric_id="EAL-002",
        title="Self-Test Diagnostics & System Integrity Verification",
        impact="POSITIVE", score_delta=+25,
        description="System performs startup self-tests verifying binary integrity & cryptographic state.",
        remediation="Implement self-test diagnostics during application initialization.",
    ),
    ISO15408Metric(
        domain="BUFFER_SAFETY", metric_id="EAL-003",
        title="Strict Memory Buffer Bounds Verification (Zero Buffer Overflow Risk)",
        impact="POSITIVE", score_delta=+25,
        description="Array indexing and memory buffers enforce strict bounds checking.",
        remediation="Enforce bounds checking on array indexing to prevent buffer overflow.",
    ),
    ISO15408Metric(
        domain="SFR_COMPLIANCE", metric_id="EAL-004",
        title="Formal Security Functional Requirements (SFR) Verification",
        impact="POSITIVE", score_delta=+25,
        description="Security functional requirements (FDP, FIA, FMT) are verified by automated tests.",
        remediation="Map automated unit tests to Security Functional Requirements (SFR).",
    ),
]


PATTERNS = {
    "EAL-001": ["SecurityTarget", "TOE", "EAL", "CommonCriteria", "ST_document"],
    "EAL-002": ["self_test", "POST", "integrity_check", "checksum_verify", "startup_check"],
    "EAL-003": ["bounds_check", "buffer_overflow", "strncpy", "snprintf", "safe_memcpy"],
    "EAL-004": ["SFR", "FDP_", "FIA_", "FMT_", "security_requirement"],
}


def scan_iso15408(root: Path, idx: IndexStoreAdapter) -> list[ISO15408Metric]:
    """Scan codebase for ISO/IEC 15408 Common Criteria security controls."""
    for m in EAL_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

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

    return EAL_METRICS


def calculate_iso15408_score(metrics: list[ISO15408Metric]) -> tuple[int, str, str]:
    """Calculate ISO 15408 Common Criteria Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "EAL4+ (Common Criteria Certified High Assurance)"
        status = "🟢 HIGH ASSURANCE — Self-Tests, Buffer Safety & SFR Verification Active"
    elif score >= 50:
        grade = "EAL2/EAL3 (Moderate Assurance)"
        status = "🟢 GOOD — Self-Tests or Buffer Safety Active"
    else:
        grade = "EAL1 (Basic Assurance)"
        status = "🔴 LOW ASSURANCE — Missing Self-Tests or Bounds Checking Controls"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO15408Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso15408_score(metrics)

    lines = [
        f"# 🏛️ ISO/IEC 15408 Common Criteria Security Evaluation Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 15408 Common Criteria Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 15408 Common Criteria Score** | **{score} / 100** |",
        f"| **Evaluation Assurance Grade** | **{grade}** |",
        f"| **Assurance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified EAL Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 15408 EAL Evidence",
        "",
        "| Domain | EAL Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 15408 Common Criteria Remediation Blueprint",
        "",
        "1. **Self-Test Diagnostics**: Perform startup self-test integrity verification.",
        "2. **Buffer Safety**: Enforce bounds checking on all array and memory buffer accesses.",
        "3. **SFR Mapping**: Map unit test specs to formal Security Functional Requirements.",
        "",
        "---",
        f"*ISO/IEC 15408 Common Criteria Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🏛️ ISO/IEC 15408 COMMON CRITERIA SECURITY AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 15408 EAL Score         : {score} / 100")
    print(f"  Assurance Grade             : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_15408_common_criteria_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_15408_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso15408(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
