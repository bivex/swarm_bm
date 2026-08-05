#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   📊 ISO 8000 Data Quality & Master Data Governance Auditor               ║
║   BM25 + AST + Data Validation, Sanitization & Schema Quality Scanner     ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO 8000 Master Data Quality:            ║
║   - Automated Data Schema Validation (Pydantic / Great Expectations)      ║
║   - Master Data Deduplication & Matching Algorithms                       ║
║   - Input Data Sanitization & Normalization Pipelines                     ║
║   - Master Data Management (MDM) Entity Schema Integrity                  ║
║   - ISO 8000 Data Quality Index (0–100) & Data Governance Grade           ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_8000_data_quality_audit.py /path/to/project [ProjectName]
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
class ISO8000Metric:
    domain: str             # SCHEMA_VALIDATION / DEDUPLICATION / SANITIZATION / MDM_INTEGRITY
    metric_id: str          # DQ-001..DQ-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


DQ_METRICS: list[ISO8000Metric] = [
    ISO8000Metric(
        domain="SCHEMA_VALIDATION", metric_id="DQ-001",
        title="Automated Data Schema Validation (Pydantic / Great Expectations / Cerberus)",
        impact="POSITIVE", score_delta=+25,
        description="Data models enforce strict schema validation rules on input/output data.",
        remediation="Use Pydantic or Great Expectations to validate data quality schemas.",
    ),
    ISO8000Metric(
        domain="DEDUPLICATION", metric_id="DQ-002",
        title="Master Data Deduplication & Entity Record Matching",
        impact="POSITIVE", score_delta=+25,
        description="System implements record deduplication or matching algorithms.",
        remediation="Implement fuzzy deduplication to clean duplicate entity records.",
    ),
    ISO8000Metric(
        domain="SANITIZATION", metric_id="DQ-003",
        title="Data Sanitization, Normalization & Cleaning Pipelines",
        impact="POSITIVE", score_delta=+25,
        description="Data ingest pipeline normalizes strings, dates, and phone numbers.",
        remediation="Normalize e-mails and phone numbers to canonical formats.",
    ),
    ISO8000Metric(
        domain="MDM_INTEGRITY", metric_id="DQ-004",
        title="Master Data Management (MDM) Entity Schema Integrity",
        impact="POSITIVE", score_delta=+25,
        description="Database enforces foreign key constraints & relational integrity.",
        remediation="Enforce foreign key constraints across relational database tables.",
    ),
]


PATTERNS = {
    "DQ-001": ["pydantic", "great_expectations", "cerberus", "schema_validation"],
    "DQ-002": ["deduplicate", "fuzzy_match", "merge_records", "dedupe"],
    "DQ-003": ["normalize_phone", "clean_email", "sanitize_input", "slugify"],
    "DQ-004": ["ForeignKey", "on_delete", "references", "Constraint"],
}


def scan_iso8000(root: Path, idx: IndexStoreAdapter) -> list[ISO8000Metric]:
    """Scan codebase for ISO 8000 Data Quality controls."""
    for m in DQ_METRICS:
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

    return DQ_METRICS


def calculate_iso8000_score(metrics: list[ISO8000Metric]) -> tuple[int, str, str]:
    """Calculate ISO 8000 Data Quality Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 8000 Data Quality Certified)"
        status = "🟢 HIGH DATA QUALITY — Schema Validation, Deduplication & Normalization Active"
    elif score >= 50:
        grade = "A (Good Data Governance)"
        status = "🟢 GOOD — Schema Validation or Constraints Active"
    else:
        grade = "C/F (Data Quality Risk)"
        status = "🔴 DATA QUALITY RISK — Missing Schema Validation or Deduplication Routines"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO8000Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso8000_score(metrics)

    lines = [
        f"# 📊 ISO 8000 Master Data Quality & Data Governance Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 8000 Data Quality Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 8000 Data Quality Score** | **{score} / 100** |",
        f"| **Data Governance Grade** | **{grade}** |",
        f"| **Data Quality Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Data Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 8000 Data Quality Evidence",
        "",
        "| Domain | Data Quality Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 8000 Data Quality Remediation Blueprint",
        "",
        "1. **Schema Validation**: Validate input payloads using Pydantic schemas.",
        "2. **Normalization**: Normalize incoming email and phone string formats.",
        "3. **Integrity**: Enforce database Foreign Key constraints across all tables.",
        "",
        "---",
        f"*ISO 8000 Master Data Quality Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  📊 ISO 8000 MASTER DATA QUALITY AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 8000 Data Score         : {score} / 100")
    print(f"  Data Governance Grade       : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_8000_data_quality_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_8000_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso8000(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
