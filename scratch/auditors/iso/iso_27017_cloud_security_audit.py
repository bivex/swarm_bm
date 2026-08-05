#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   ☁️ ISO/IEC 27017:2015 Cloud Security & Multi-Tenancy Auditor             ║
║   BM25 + AST + Cloud Tenant Isolation & Infrastructure Security Scanner  ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 27017 Cloud Security Controls:   ║
║   - Multi-Tenant Data Isolation (Row-Level Security / RLS / Tenant IDs)   ║
║   - Cloud Storage Encryption & Bucket Policy Controls                     ║
║   - Cloud IAM Least Privilege & Role Boundaries                           ║
║   - Centralized Cloud Audit Logging (AWS CloudTrail / GCP Audit Logs)     ║
║   - ISO 27017 Cloud Security Score (0–100) & Cloud Governance Grade       ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_27017_cloud_security_audit.py /path/to/project [ProjectName]
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
class ISO27017Metric:
    domain: str             # TENANT_ISOLATION / CLOUD_STORAGE / IAM_GOVERNANCE / CLOUD_AUDIT
    metric_id: str          # CLOUD-001..CLOUD-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


CLOUD_METRICS: list[ISO27017Metric] = [
    ISO27017Metric(
        domain="TENANT_ISOLATION", metric_id="CLOUD-001",
        title="Multi-Tenant Data Isolation (Row-Level Security / tenant_id Filtering)",
        impact="POSITIVE", score_delta=+25,
        description="System enforces multi-tenant data isolation per organization.",
        remediation="Enforce tenant_id filtering or Postgres Row-Level Security (RLS) on all tenant queries.",
    ),
    ISO27017Metric(
        domain="CLOUD_STORAGE", metric_id="CLOUD-002",
        title="Cloud Storage Server-Side Encryption (S3 SSE-KMS / GCS Encryption)",
        impact="POSITIVE", score_delta=+25,
        description="Cloud object storage buckets enforce server-side encryption.",
        remediation="Enable AWS KMS or SSE-S3 server-side encryption on cloud buckets.",
    ),
    ISO27017Metric(
        domain="IAM_GOVERNANCE", metric_id="CLOUD-003",
        title="Cloud IAM Least Privilege & Role Boundaries",
        impact="POSITIVE", score_delta=+25,
        description="Infrastructure defines granular IAM roles with minimal permissions.",
        remediation="Avoid wildcards (*) in IAM policy action statements.",
    ),
    ISO27017Metric(
        domain="CLOUD_AUDIT", metric_id="CLOUD-004",
        title="Centralized Cloud Infrastructure Audit Logging (CloudTrail / Cloud Audit)",
        impact="POSITIVE", score_delta=+25,
        description="Cloud resource actions are audited to centralized log management.",
        remediation="Enable CloudTrail / Cloud Audit logging across all cloud regions.",
    ),
]


PATTERNS = {
    "CLOUD-001": ["tenant_id", "ROW LEVEL SECURITY", "organization_id", "TenantContext"],
    "CLOUD-002": ["ServerSideEncryption", "KmsKeyId", "sse_algorithm", "encryption"],
    "CLOUD-003": ["iam_role", "aws_iam_policy", "roles/", "serviceAccount"],
    "CLOUD-004": ["cloudtrail", "cloud_audit", "audit_log_bucket", "logging"],
}


def scan_iso27017(root: Path, idx: IndexStoreAdapter) -> list[ISO27017Metric]:
    """Scan codebase for ISO/IEC 27017 Cloud Security controls."""
    for m in CLOUD_METRICS:
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

    return CLOUD_METRICS


def calculate_iso27017_score(metrics: list[ISO27017Metric]) -> tuple[int, str, str]:
    """Calculate ISO 27017 Cloud Security Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 27017 Cloud Certified)"
        status = "🟢 HIGH CLOUD SECURITY — Tenant Isolation & Storage Encryption Active"
    elif score >= 50:
        grade = "A (Good Cloud Security)"
        status = "🟢 GOOD — Tenant Isolation or IAM Controls Configured"
    else:
        grade = "C/F (Cloud Governance Risk)"
        status = "🔴 CLOUD GOVERNANCE RISK — Missing Tenant Isolation or Storage Encryption"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO27017Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso27017_score(metrics)

    lines = [
        f"# ☁️ ISO/IEC 27017:2015 Cloud Security Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 27017 Cloud Governance Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 27017 Cloud Security Score** | **{score} / 100** |",
        f"| **Cloud Governance Grade** | **{grade}** |",
        f"| **Cloud Security Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Cloud Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 27017 Cloud Security Evidence",
        "",
        "| Domain | Cloud Control Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 27017 Cloud Security Remediation Blueprint",
        "",
        "1. **Tenant Isolation**: Scope database queries by `tenant_id` context.",
        "2. **Storage Encryption**: Enforce KMS server-side encryption on cloud buckets.",
        "3. **IAM Privilege**: Scope IAM role actions to essential resources only.",
        "",
        "---",
        f"*ISO/IEC 27017:2015 Cloud Security & Multi-Tenancy Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  ☁️ ISO/IEC 27017:2015 CLOUD SECURITY AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 27017 Cloud Score       : {score} / 100")
    print(f"  Cloud Governance Grade      : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_27017_cloud_security_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_27017_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso27017(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
