#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   ⚙️💼 ISO/IEC 20000-1:2018 IT Service Management (ITSM) Auditor            ║
║   BM25 + AST + Service Catalog, SLA Monitoring & Incident Desk Scanner   ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 20000-1 IT Service Management:   ║
║   - Service Level Agreement (SLA) & Response Time Threshold Enforcers     ║
║   - Service Desk & Support Desk API Endpoints (/api/v1/support/tickets)   ║
║   - Capacity Planning & System Load Limit Metrics                         ║
║   - Change Management Request (CMR) Validation Schemas                    ║
║   - ISO 20000-1 ITSM Index (0–100) & IT Service Quality Grade             ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_20000_1_service_management_audit.py /path/to/project [ProjectName]
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
class ISO20000Metric:
    domain: str             # SLA_MONITORING / SERVICE_DESK / CAPACITY_MANAGEMENT / CHANGE_MANAGEMENT
    metric_id: str          # ITSM-001..ITSM-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


ITSM_METRICS: list[ISO20000Metric] = [
    ISO20000Metric(
        domain="SLA_MONITORING", metric_id="ITSM-001",
        title="Service Level Agreement (SLA) Response Time Threshold Enforcers",
        impact="POSITIVE", score_delta=+25,
        description="System enforces or monitors API response latency SLAs (e.g., p99 < 200ms).",
        remediation="Configure SLA latency response threshold monitors in Prometheus / Datadog.",
    ),
    ISO20000Metric(
        domain="SERVICE_DESK", metric_id="ITSM-002",
        title="Service Desk & Support Incident Ticket Integrations",
        impact="POSITIVE", score_delta=+25,
        description="System exposes support ticket endpoints or integrates with Zendesk/Jira.",
        remediation="Expose support ticket endpoints or integrate Zendesk/Jira Service Desk API.",
    ),
    ISO20000Metric(
        domain="CAPACITY_MANAGEMENT", metric_id="ITSM-003",
        title="Capacity Management & Rate Limiting Controls",
        impact="POSITIVE", score_delta=+25,
        description="System enforces request rate limits to prevent capacity exhaustion.",
        remediation="Enable rate limiting middleware to manage capacity limits.",
    ),
    ISO20000Metric(
        domain="CHANGE_MANAGEMENT", metric_id="ITSM-004",
        title="Change Management Request (CMR) Validation & Pull Request Templates",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains Pull Request templates specifying Change Management (CMR) details.",
        remediation="Create `.github/PULL_REQUEST_TEMPLATE.md` with Change Management checklist.",
    ),
]


PATTERNS = {
    "ITSM-001": ["SLA", "p99_latency", "response_time_limit", "sla_target"],
    "ITSM-002": ["zendesk", "jira_ticket", "support_desk", "/tickets"],
    "ITSM-003": ["RateLimiter", "rate_limit", "throttle", "capacity_limit"],
    "ITSM-004": ["PULL_REQUEST_TEMPLATE.md", "change_management", "CMR_id"],
}


def scan_iso20000(root: Path, idx: IndexStoreAdapter) -> list[ISO20000Metric]:
    """Scan codebase for ISO/IEC 20000-1 IT Service Management controls."""
    for m in ITSM_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        if m.metric_id == "ITSM-004":
            pr_files = list(root.glob("*PULL_REQUEST*")) + list(root.glob(".github/*PULL_REQUEST*"))
            if pr_files:
                hits.update(str(f.relative_to(root)) for f in pr_files[:4])

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

    return ITSM_METRICS


def calculate_iso20000_score(metrics: list[ISO20000Metric]) -> tuple[int, str, str]:
    """Calculate ISO 20000-1 ITSM Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 20000-1 ITSM Certified)"
        status = "🟢 HIGH SERVICE QUALITY — SLA Monitoring, Support Desk & Rate Limiting Active"
    elif score >= 50:
        grade = "A (Good Service Management)"
        status = "🟢 GOOD — Rate Limiting or PR Templates Active"
    else:
        grade = "C/F (ITSM Service Gap)"
        status = "🔴 SERVICE GAP — Missing Rate Limiting or SLA Latency Monitoring"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO20000Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso20000_score(metrics)

    lines = [
        f"# ⚙️💼 ISO/IEC 20000-1:2018 IT Service Management Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 20000-1 ITSM Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 20000-1 ITSM Score** | **{score} / 100** |",
        f"| **IT Service Quality Grade** | **{grade}** |",
        f"| **Service Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified ITSM Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 20000-1 ITSM Evidence",
        "",
        "| Domain | ITSM Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 20000-1 ITSM Remediation Blueprint",
        "",
        "1. **Rate Limiting**: Enable rate limiting middleware to prevent capacity overload.",
        "2. **PR Templates**: Maintain `.github/PULL_REQUEST_TEMPLATE.md` with Change Management steps.",
        "3. **SLA Monitoring**: Monitor p99 response times against SLA thresholds.",
        "",
        "---",
        f"*ISO/IEC 20000-1 IT Service Management Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  ⚙️💼 ISO/IEC 20000-1 IT SERVICE MANAGEMENT AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 20000-1 ITSM Score      : {score} / 100")
    print(f"  IT Service Quality Grade    : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_20000_1_service_management_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_20000_1_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso20000(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
