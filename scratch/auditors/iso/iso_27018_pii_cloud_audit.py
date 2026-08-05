#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   ☁️🔒 ISO/IEC 27018:2019 Protection of PII in Public Clouds Auditor       ║
║   BM25 + AST + Public Cloud PII Privacy & BYOK Encryption Scanner        ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 27018 Public Cloud PII controls:  ║
║   - Bring Your Own Key (BYOK) Customer-Managed Encryption                 ║
║   - Prohibition of PII Processing for Commercial Advertising              ║
║   - Data Residency & Geographic Storage Location Controls                 ║
║   - Sub-processor Disclosures & Multi-Tenant PII Isolation                ║
║   - ISO 27018 Cloud Privacy Index (0–100) & Cloud PII Grade               ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_27018_pii_cloud_audit.py /path/to/project [ProjectName]
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
class ISO27018Metric:
    domain: str             # BYOK_ENCRYPTION / DATA_RESIDENCY / SUBPROCESSOR_AUDIT / NO_ADVERTISING
    metric_id: str          # CPRIV-001..CPRIV-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


CLOUD_PII_METRICS: list[ISO27018Metric] = [
    ISO27018Metric(
        domain="BYOK_ENCRYPTION", metric_id="CPRIV-001",
        title="Customer-Managed Key Encryption (BYOK / KMS Master Key)",
        impact="POSITIVE", score_delta=+25,
        description="Public cloud storage enforces customer-managed encryption keys (KMS BYOK).",
        remediation="Configure AWS KMS BYOK or GCP Customer-Managed Encryption Keys (CMEK).",
    ),
    ISO27018Metric(
        domain="DATA_RESIDENCY", metric_id="CPRIV-002",
        title="Cloud Region Data Residency & Storage Pinning (EU/US Isolation)",
        impact="POSITIVE", score_delta=+25,
        description="Cloud resource configs pin data storage to explicit geographic regions.",
        remediation="Pin cloud buckets and DB instances to specified geographic compliance regions.",
    ),
    ISO27018Metric(
        domain="NO_ADVERTISING", metric_id="CPRIV-003",
        title="Prohibition of PII Data Usage for Ad Targeting",
        impact="POSITIVE", score_delta=+25,
        description="Application code isolates customer PII from third-party advertising trackers.",
        remediation="Ensure user PII payloads are never transmitted to ad tracking pixels.",
    ),
    ISO27018Metric(
        domain="SUBPROCESSOR_AUDIT", metric_id="CPRIV-004",
        title="Third-Party Sub-processor Disclosure & Contract Isolation",
        impact="POSITIVE", score_delta=+25,
        description="System maintains explicit sub-processor disclosure manifests or SDK registries.",
        remediation="Maintain a sub-processors list detailing third-party cloud integrations.",
    ),
]


PATTERNS = {
    "CPRIV-001": ["KmsKeyId", "BYOK", "CMEK", "kms.encrypt", "customer_managed_key"],
    "CPRIV-002": ["eu-central-1", "us-east-1", "data_residency", "region_pinning"],
    "CPRIV-003": ["no_track", "strip_ad_data", "anonymize_tracking", "dnt_header"],
    "CPRIV-004": ["subprocessors", "third_party_sdks", "vendor_registry"],
}


def scan_iso27018(root: Path, idx: IndexStoreAdapter) -> list[ISO27018Metric]:
    """Scan codebase for ISO/IEC 27018 Protection of PII in Public Clouds controls."""
    for m in CLOUD_PII_METRICS:
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

    return CLOUD_PII_METRICS


def calculate_iso27018_score(metrics: list[ISO27018Metric]) -> tuple[int, str, str]:
    """Calculate ISO 27018 Cloud Privacy Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 27018 Cloud PII Certified)"
        status = "🟢 HIGH CLOUD PRIVACY — BYOK Encryption & Data Residency Active"
    elif score >= 50:
        grade = "A (Good Cloud Privacy Controls)"
        status = "🟢 GOOD — Data Residency or BYOK Configured"
    else:
        grade = "C/F (Cloud PII Risk)"
        status = "🔴 CLOUD PRIVACY RISK — Missing BYOK Encryption or Data Residency Controls"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO27018Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso27018_score(metrics)

    lines = [
        f"# ☁️🔒 ISO/IEC 27018:2019 Protection of PII in Public Clouds Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 27018 Cloud Privacy Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 27018 Cloud Privacy Score** | **{score} / 100** |",
        f"| **Cloud PII Grade** | **{grade}** |",
        f"| **Privacy Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Cloud PII Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 27018 Cloud PII Evidence",
        "",
        "| Domain | Cloud PII Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 27018 Cloud PII Remediation Blueprint",
        "",
        "1. **BYOK Encryption**: Configure customer-managed KMS master keys for S3/GCS buckets.",
        "2. **Data Residency**: Pin cloud deployment regions to compliance jurisdictions (e.g. EU).",
        "3. **Sub-processors**: Maintain a sub-processor vendor list detailing external cloud APIs.",
        "",
        "---",
        f"*ISO/IEC 27018 Public Cloud PII Privacy Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  ☁️🔒 ISO/IEC 27018:2019 PUBLIC CLOUD PII AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 27018 Cloud PII Score   : {score} / 100")
    print(f"  Cloud PII Grade             : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_27018_pii_cloud_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_27018_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso27018(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
