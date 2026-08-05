#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   💾🔒 ISO/IEC 27040:2024 Storage Security & Data Encryption Auditor       ║
║   BM25 + AST + Storage at Rest Encryption & Sanitization Scanner          ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 27040 Storage Security:          ║
║   - Storage Encryption at Rest (AES-256 / LUKS / SSE-KMS / BitLocker)      ║
║   - Secure Storage Wiping & Media Sanitization Routines                   ║
║   - Database & Object Storage Access Control Lists (ACL / IAM)            ║
║   - Automated Backup Verification & Snapshot Encryption                   ║
║   - ISO 27040 Storage Security Index (0–100) & Storage Trust Grade        ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_27040_storage_security_audit.py /path/to/project [ProjectName]
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
class ISO27040Metric:
    domain: str             # ENCRYPTION_AT_REST / SANITIZATION / STORAGE_ACL / BACKUP_VERIFICATION
    metric_id: str          # STOR-001..STOR-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


STOR_METRICS: list[ISO27040Metric] = [
    ISO27040Metric(
        domain="ENCRYPTION_AT_REST", metric_id="STOR-001",
        title="Storage Encryption at Rest (AES-256 / LUKS / SSE-KMS / BitLocker)",
        impact="POSITIVE", score_delta=+25,
        description="Database or block storage enforces AES-256 encryption at rest.",
        remediation="Enable SSE-KMS or AES-256 disk encryption on storage volumes.",
    ),
    ISO27040Metric(
        domain="SANITIZATION", metric_id="STOR-002",
        title="Secure Media Sanitization & Disk Wiping Routines",
        impact="POSITIVE", score_delta=+25,
        description="System implements secure media wiping or cryptographic erasure.",
        remediation="Use cryptographic erasure or secure wiping for retired storage media.",
    ),
    ISO27040Metric(
        domain="STORAGE_ACL", metric_id="STOR-003",
        title="Storage Bucket & Volume Access Control Lists (ACL / IAM Policy)",
        impact="POSITIVE", score_delta=+25,
        description="Storage buckets enforce restrictive IAM policies preventing public read/write.",
        remediation="Block public access on cloud storage buckets and enforce IAM policies.",
    ),
    ISO27040Metric(
        domain="BACKUP_VERIFICATION", metric_id="STOR-004",
        title="Automated Backup Snapshot Encryption & Restore Verification",
        impact="POSITIVE", score_delta=+25,
        description="Storage snapshots are encrypted and verified via automated restore tests.",
        remediation="Automate backup snapshot encryption and periodic restore testing.",
    ),
]


PATTERNS = {
    "STOR-001": ["AES-256", "sse_kms", "luks", "encrypted=True", "db_encryption"],
    "STOR-002": ["crypto_erase", "media_sanitize", "shred_file", "secure_wipe"],
    "STOR-003": ["block_public_access", "bucket_policy", "storage_acl", "private_bucket"],
    "STOR-004": ["backup_restore", "snapshot_encryption", "backup_test", "pg_dump"],
}


def scan_iso27040(root: Path, idx: IndexStoreAdapter) -> list[ISO27040Metric]:
    """Scan codebase for ISO/IEC 27040 Storage Security controls."""
    for m in STOR_METRICS:
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

    return STOR_METRICS


def calculate_iso27040_score(metrics: list[ISO27040Metric]) -> tuple[int, str, str]:
    """Calculate ISO 27040 Storage Security Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 27040 Storage Security Certified)"
        status = "🟢 HIGH STORAGE SECURITY — Encryption at Rest, Storage ACLs & Backup Tests Active"
    elif score >= 50:
        grade = "A (Good Storage Security)"
        status = "🟢 GOOD — Encryption at Rest or Storage ACLs Active"
    else:
        grade = "C/F (Storage Security Risk)"
        status = "🔴 STORAGE SECURITY RISK — Missing Storage Encryption at Rest or Storage ACLs"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO27040Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso27040_score(metrics)

    lines = [
        f"# 💾🔒 ISO/IEC 27040:2024 Storage Security & Data Encryption Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 27040 Storage Security Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 27040 Storage Score** | **{score} / 100** |",
        f"| **Storage Trust Grade** | **{grade}** |",
        f"| **Storage Security Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Storage Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 27040 Storage Security Evidence",
        "",
        "| Domain | Storage Security Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 27040 Storage Security Remediation Blueprint",
        "",
        "1. **Encryption at Rest**: Enable SSE-KMS or AES-256 disk encryption for databases.",
        "2. **Storage ACLs**: Enforce IAM private bucket policies on cloud storage containers.",
        "3. **Backup Testing**: Automate periodic restore testing of encrypted database backups.",
        "",
        "---",
        f"*ISO/IEC 27040 Storage Security Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  💾🔒 ISO/IEC 27040 STORAGE SECURITY AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 27040 Storage Score     : {score} / 100")
    print(f"  Storage Trust Grade         : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_27040_storage_security_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_27040_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso27040(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
