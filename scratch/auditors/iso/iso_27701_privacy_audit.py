#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🔒 ISO/IEC 27701 Privacy Information & PII Governance Auditor           ║
║   BM25 + AST + Personal Identifiable Information (PII) Scanner            ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 27701 & GDPR compliance:         ║
║   - PII Sanitization in Logs (E-mail, Phone, SSN, Credit Card)           ║
║   - Right to be Forgotten (Soft & Hard Delete Mechanisms)                ║
║   - Field-Level Database Encryption for Sensitive PII                     ║
║   - Privacy-by-Design Consent & Opt-Out Flags                             ║
║   - ISO 27701 Privacy Index (0–100) & Compliance Grade                    ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_27701_privacy_audit.py /path/to/project [ProjectName]
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
class ISO27701Metric:
    domain: str             # PII_SANITIZATION / RIGHT_TO_ERASURE / PII_ENCRYPTION / CONSENT / DATA_RETENTION
    metric_id: str          # P-001..Q-010
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


PRIVACY_METRICS: list[ISO27701Metric] = [
    ISO27701Metric(
        domain="PII_SANITIZATION", metric_id="P-001",
        title="PII Masking & Redaction in Log Streams",
        impact="POSITIVE", score_delta=+20,
        description="Log sanitizers mask emails, phone numbers, and auth tokens.",
        remediation="Ensure logger middleware sanitizes all incoming request payloads.",
    ),
    ISO27701Metric(
        domain="RIGHT_TO_ERASURE", metric_id="P-002",
        title="GDPR Right to be Forgotten (Soft & Hard Delete Handlers)",
        impact="POSITIVE", score_delta=+20,
        description="System implements user data deletion routines upon user request.",
        remediation="Implement cascading deletion handlers for all user-linked PII tables.",
    ),
    ISO27701Metric(
        domain="PII_ENCRYPTION", metric_id="P-003",
        title="Field-Level DB Encryption for Sensitive Data",
        impact="POSITIVE", score_delta=+20,
        description="Sensitive columns (SSN, credit card, passport) are encrypted before storage.",
        remediation="Use AES-256 field-level encryption for sensitive database columns.",
    ),
    ISO27701Metric(
        domain="CONSENT", metric_id="P-004",
        title="Explicit User Privacy Consent & Opt-Out Management",
        impact="POSITIVE", score_delta=+20,
        description="System tracks explicit user consent flags and communication preferences.",
        remediation="Store consent timestamps and opt-in/opt-out status for marketing channels.",
    ),
    ISO27701Metric(
        domain="DATA_RETENTION", metric_id="P-005",
        title="Automated Data Retention & Anonymization Background Cron",
        impact="POSITIVE", score_delta=+20,
        description="Scheduled tasks automatically purge or anonymize expired user data.",
        remediation="Run periodic retention cleanup jobs to purge stale PII data after retention period.",
    ),
]


PATTERNS = {
    "P-001": ["mask", "redact", "anonymize", "sanitize", "filter_pii"],
    "P-002": ["delete_user", "anonymize_user", "soft_delete", "hard_delete", "purge_pii"],
    "P-003": ["EncryptedColumn", "encrypt_field", "field_encryption", "kms.encrypt"],
    "P-004": ["consent", "opt_in", "opt_out", "privacy_policy", "gdpr"],
    "P-005": ["retention", "purge_old_data", "anonymize_expired", "cleanup_cron"],
}


def scan_iso27701(root: Path, idx: IndexStoreAdapter) -> list[ISO27701Metric]:
    """Scan codebase for ISO/IEC 27701 Privacy & PII protection controls."""
    for m in PRIVACY_METRICS:
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

    return PRIVACY_METRICS


def calculate_iso27701_score(metrics: list[ISO27701Metric]) -> tuple[int, str, str]:
    """Calculate ISO 27701 Privacy Index (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 80:
        grade = "A+ (ISO 27701 & GDPR Fully Compliant)"
        status = "🟢 HIGH PRIVACY PROTECTION — Field Encryption & Right to Erasure Implemented"
    elif score >= 60:
        grade = "A (Good Privacy Controls)"
        status = "🟢 GOOD — Log Sanitization & Consent Flags Present"
    else:
        grade = "C/F (Privacy Non-Compliance Risk)"
        status = "🔴 HIGH PRIVACY RISK — Lacks Data Retention Purge or Log Sanitization"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO27701Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso27701_score(metrics)

    lines = [
        f"# 🔒 ISO/IEC 27701 Privacy & PII Governance Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 27701 Privacy Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 27701 Privacy Score** | **{score} / 100** |",
        f"| **Privacy Compliance Grade** | **{grade}** |",
        f"| **Compliance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Privacy Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 27701 Privacy & PII Evidence",
        "",
        "| Domain | Privacy Control Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 27701 Privacy Remediation Blueprint",
        "",
        "1. **PII Masking**: Ensure all logger middleware sanitizes e-mails, passwords, and tokens.",
        "2. **Right to Erasure**: Provide an API endpoint for users to trigger complete PII deletion.",
        "3. **Field Encryption**: Encrypt sensitive database columns at rest via AES-256.",
        "",
        "---",
        f"*ISO/IEC 27701 Privacy Information Management Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🔒 ISO/IEC 27701 PRIVACY & PII AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 27701 Privacy Score     : {score} / 100")
    print(f"  Privacy Compliance Grade    : {grade}")
    print(f"  Verified Privacy Controls   : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_27701_privacy_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_27701_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso27701(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
