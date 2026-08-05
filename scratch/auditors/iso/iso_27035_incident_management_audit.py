#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🚨 ISO/IEC 27035:2023 Security Incident Management Auditor               ║
║   BM25 + AST + Incident Response Playbooks & Alerting Scanner             ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 27035 Incident Management:       ║
║   - Incident Response Playbooks (INCIDENT_RESPONSE.md / RUNBOOK.md)        ║
║   - Automated Security Alerting & PagerDuty / Sentry Integration          ║
║   - Incident Escalation Handlers & Post-Mortem Templates                  ║
║   - Centralized SIEM / Log Aggregation (Datadog / Splunk / ELK)           ║
║   - ISO 27035 Incident Readiness Index (0–100) & Response Grade           ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_27035_incident_management_audit.py /path/to/project [ProjectName]
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
class ISO27035Metric:
    domain: str             # RESPONSE_PLAYBOOK / ALERTING_INTEGRATION / INCIDENT_ESCALATION / SIEM_LOGGING
    metric_id: str          # INC-001..INC-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


INCIDENT_METRICS: list[ISO27035Metric] = [
    ISO27035Metric(
        domain="RESPONSE_PLAYBOOK", metric_id="INC-001",
        title="Incident Response Playbook & Runbooks (INCIDENT_RESPONSE.md)",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains documented incident response playbooks or runbooks.",
        remediation="Document security incident triage steps in `INCIDENT_RESPONSE.md`.",
    ),
    ISO27035Metric(
        domain="ALERTING_INTEGRATION", metric_id="INC-002",
        title="Automated Security Alerting (Sentry / PagerDuty / Opsgenie)",
        impact="POSITIVE", score_delta=+25,
        description="Application integrates automated error tracking or incident alerting SDKs.",
        remediation="Integrate Sentry or PagerDuty SDK for instant error & breach notifications.",
    ),
    ISO27035Metric(
        domain="INCIDENT_ESCALATION", metric_id="INC-003",
        title="Incident Escalation Handlers & Post-Mortem Templates",
        impact="POSITIVE", score_delta=+25,
        description="Project defines post-mortem templates or incident escalation chains.",
        remediation="Maintain a post-mortem template in `docs/post_mortem_template.md`.",
    ),
    ISO27035Metric(
        domain="SIEM_LOGGING", metric_id="INC-004",
        title="Centralized SIEM & Log Aggregation (Datadog / Splunk / ELK)",
        impact="POSITIVE", score_delta=+25,
        description="Logs are formatted for ingestion into SIEM security monitoring platforms.",
        remediation="Format log outputs as structured JSON for Datadog or Splunk SIEM ingestion.",
    ),
]


PATTERNS = {
    "INC-001": ["INCIDENT_RESPONSE.md", "RUNBOOK.md", "incident_playbook", "SEV-1"],
    "INC-002": ["sentry_sdk", "pagerduty", "opsgenie", "capture_exception"],
    "INC-003": ["post_mortem", "escalation_policy", "on_call", "incident_lead"],
    "INC-004": ["datadog", "splunk", "elastic", "fluentd", "json_formatter"],
}


def scan_iso27035(root: Path, idx: IndexStoreAdapter) -> list[ISO27035Metric]:
    """Scan codebase for ISO/IEC 27035 Security Incident Management controls."""
    for m in INCIDENT_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        if m.metric_id in ("INC-001", "INC-003"):
            doc_files = list(root.glob("*INCIDENT*")) + list(root.glob("*RUNBOOK*"))
            if doc_files:
                hits.update(str(f.relative_to(root)) for f in doc_files[:4])

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

    return INCIDENT_METRICS


def calculate_iso27035_score(metrics: list[ISO27035Metric]) -> tuple[int, str, str]:
    """Calculate ISO 27035 Incident Readiness Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 27035 Incident Ready Certified)"
        status = "🟢 HIGH INCIDENT READINESS — Alerting SDKs, SIEM & Incident Playbooks Active"
    elif score >= 50:
        grade = "A (Good Incident Controls)"
        status = "🟢 GOOD — Alerting SDKs or Log Aggregation Active"
    else:
        grade = "C/F (Incident Response Gap)"
        status = "🔴 INCIDENT RESPONSE GAP — Missing Incident Alerting or SIEM Logging"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO27035Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso27035_score(metrics)

    lines = [
        f"# 🚨 ISO/IEC 27035:2023 Security Incident Management Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 27035 Incident Readiness Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 27035 Incident Readiness Score** | **{score} / 100** |",
        f"| **Response Quality Grade** | **{grade}** |",
        f"| **Incident Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Incident Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 27035 Incident Evidence",
        "",
        "| Domain | Incident Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 27035 Incident Readiness Remediation Blueprint",
        "",
        "1. **Alerting**: Integrate Sentry / PagerDuty SDK for instant breach notifications.",
        "2. **Playbooks**: Document security incident response steps in `INCIDENT_RESPONSE.md`.",
        "3. **SIEM**: Format logger outputs as JSON for Datadog or Splunk SIEM ingestion.",
        "",
        "---",
        f"*ISO/IEC 27035 Security Incident Management Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🚨 ISO/IEC 27035 SECURITY INCIDENT MANAGEMENT AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 27035 Incident Score    : {score} / 100")
    print(f"  Response Quality Grade      : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_27035_incident_management_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_27035_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso27035(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
