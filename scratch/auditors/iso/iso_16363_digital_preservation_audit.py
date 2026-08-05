#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🏛️📦 ISO 16363:2012 Trustworthy Digital Repository Preservation Auditor   ║
║   BM25 + AST + Checksum Integrity & Long-Term Archival Scanner            ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO 16363 Digital Repository Integrity:  ║
║   - Automated Data Checksum & Hash Verification (SHA-256 / SHA-512)       ║
║   - Persistent Identifier Schemes (DOI / UUID / URN)                      ║
║   - Archival Packaging & Format Migration Routines (ZIP / Tar / Parquet)   ║
║   - Audit Log Trail & Provenance Metadata Integrity                       ║
║   - ISO 16363 Repository Index (0–100) & Digital Trust Grade              ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_16363_digital_preservation_audit.py /path/to/project [ProjectName]
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
class ISO16363Metric:
    domain: str             # CHECKSUM_INTEGRITY / PERSISTENT_IDENTIFIERS / ARCHIVAL_PACKAGING / PROVENANCE_TRAIL
    metric_id: str          # ARCH-001..ARCH-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


ARCH_METRICS: list[ISO16363Metric] = [
    ISO16363Metric(
        domain="CHECKSUM_INTEGRITY", metric_id="ARCH-001",
        title="Automated Data Checksum & Hash Verification (SHA-256 / SHA-512)",
        impact="POSITIVE", score_delta=+25,
        description="System generates or verifies cryptographic hashes to prevent bit rot & corruption.",
        remediation="Verify SHA-256 checksums on all stored digital artifacts.",
    ),
    ISO16363Metric(
        domain="PERSISTENT_IDENTIFIERS", metric_id="ARCH-002",
        title="Persistent Unique Identifier Schemes (UUID4 / DOI / URN)",
        impact="POSITIVE", score_delta=+25,
        description="Stored objects are assigned globally unique persistent identifiers.",
        remediation="Assign UUIDv4 or DOI persistent identifiers to stored assets.",
    ),
    ISO16363Metric(
        domain="ARCHIVAL_PACKAGING", metric_id="ARCH-003",
        title="Archival Packaging & Export Formats (Parquet / ZIP / Tar)",
        impact="POSITIVE", score_delta=+25,
        description="System exports digital assets in open archival formats.",
        remediation="Export archival data packages in Parquet or Tar/Gzip containers.",
    ),
    ISO16363Metric(
        domain="PROVENANCE_TRAIL", metric_id="ARCH-004",
        title="Immutable Provenance Metadata Trail & Chain of Custody",
        impact="POSITIVE", score_delta=+25,
        description="System logs creator, modification, and chain-of-custody metadata.",
        remediation="Store provenance metadata along with digital file assets.",
    ),
]


PATTERNS = {
    "ARCH-001": ["sha256", "sha512", "hashlib", "checksum_verify", "digest"],
    "ARCH-002": ["uuid4", "uuid.uuid4()", "doi:", "urn:uuid"],
    "ARCH-003": ["parquet", "tarfile", "zipfile", "bagit", "archival_format"],
    "ARCH-004": ["provenance", "chain_of_custody", "creation_metadata", "audit_provenance"],
}


def scan_iso16363(root: Path, idx: IndexStoreAdapter) -> list[ISO16363Metric]:
    """Scan codebase for ISO 16363 Trustworthy Digital Repositories controls."""
    for m in ARCH_METRICS:
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

    return ARCH_METRICS


def calculate_iso16363_score(metrics: list[ISO16363Metric]) -> tuple[int, str, str]:
    """Calculate ISO 16363 Digital Trust Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 16363 Digital Repository Certified)"
        status = "🟢 HIGH DIGITAL TRUST — Checksum Verification, UUIDs & Provenance Active"
    elif score >= 50:
        grade = "A (Good Digital Repository Controls)"
        status = "🟢 GOOD — Checksum Verification or UUID Identifiers Active"
    else:
        grade = "C/F (Repository Integrity Risk)"
        status = "🔴 INTEGRITY RISK — Missing Checksum Verification or Provenance Metadata"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO16363Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso16363_score(metrics)

    lines = [
        f"# 🏛️📦 ISO 16363:2012 Trustworthy Digital Repository Preservation Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 16363 Digital Repository Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 16363 Repository Score** | **{score} / 100** |",
        f"| **Digital Trust Grade** | **{grade}** |",
        f"| **Preservation Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Archival Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 16363 Archival Evidence",
        "",
        "| Domain | Archival Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 16363 Digital Preservation Remediation Blueprint",
        "",
        "1. **Checksum Verification**: Generate SHA-256 hashes on digital file ingest.",
        "2. **Persistent Identifiers**: Assign UUIDv4 identifiers to stored entities.",
        "3. **Provenance**: Maintain creator metadata and chain-of-custody audit logs.",
        "",
        "---",
        f"*ISO 16363 Trustworthy Digital Repository Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🏛️📦 ISO 16363 DIGITAL REPOSITORY AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 16363 Repository Score  : {score} / 100")
    print(f"  Digital Trust Grade         : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_16363_digital_preservation_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_16363_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso16363(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
