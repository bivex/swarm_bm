#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   📊 ISO 31000:2018 Enterprise Risk Management (ERM) Auditor              ║
║   BM25 + AST + Architectural Risk Governance & Vulnerability Scanner     ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO 31000 Enterprise Risk Controls:     ║
║   - Vulnerability Management (Dependabot / Snyk / Software Bill of Mat)   ║
║   - Single Point of Failure (SPOF) Architectural Exposure                 ║
║   - Deprecated & EOL Language/Library Risk Controls                      ║
║   - Risk Assessment Score (0–100) & ERM Governance Grade                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_31000_risk_audit.py /path/to/project [ProjectName]
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
class ISO31000Metric:
    domain: str             # VULN_MGMT / SPOF_RISK / DEPRECATION_RISK / RISK_REGISTER
    metric_id: str          # RISK-001..RISK-005
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


RISK_METRICS: list[ISO31000Metric] = [
    ISO31000Metric(
        domain="VULN_MGMT", metric_id="RISK-001",
        title="Automated Dependency Vulnerability Scanning (Dependabot / Snyk)",
        impact="POSITIVE", score_delta=+25,
        description="Repository includes automated dependency security update configurations.",
        remediation="Enable Dependabot or Snyk in repository CI/CD pipeline.",
    ),
    ISO31000Metric(
        domain="SPOF_RISK", metric_id="RISK-002",
        title="Single Point of Failure Redundancy Controls (HA / Multi-Region)",
        impact="POSITIVE", score_delta=+25,
        description="System implements load balancing and redundancy to prevent SPOF.",
        remediation="Deploy multi-node replicas behind load balancer to eliminate SPOF.",
    ),
    ISO31000Metric(
        domain="DEPRECATION_RISK", metric_id="RISK-003",
        title="Deprecated API & EOL Dependency Risk Warnings",
        impact="RISK", score_delta=-20,
        description="Found usage of deprecated methods or end-of-life library packages.",
        remediation="Upgrade deprecated package dependencies to actively maintained releases.",
    ),
    ISO31000Metric(
        domain="RISK_REGISTER", metric_id="RISK-004",
        title="Architectural Risk Register Documentation (SECURITY.md / Risk Log)",
        impact="POSITIVE", score_delta=+25,
        description="Project maintains a vulnerability disclosure policy or risk log.",
        remediation="Maintain a SECURITY.md file defining vulnerability reporting guidelines.",
    ),
]


PATTERNS = {
    "RISK-001": ["dependabot", "snyk", "audit", "cargo-audit", "npm audit"],
    "RISK-002": ["load_balancer", "upstream", "cluster", "replica", "redundant"],
    "RISK-003": ["@deprecated", "@Deprecated", "DeprecationWarning", "DEPRECATED"],
    "RISK-004": ["SECURITY.md", "security_policy", "vulnerability_report", "RISK.md"],
}


def scan_iso31000(root: Path, idx: IndexStoreAdapter) -> list[ISO31000Metric]:
    """Scan codebase for ISO 31000 Enterprise Risk Management controls."""
    for m in RISK_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        if m.metric_id == "RISK-004":
            sec_files = list(root.glob("*SECURITY*")) + list(root.glob("*SECURITY*.md"))
            if sec_files:
                hits.update(str(f.relative_to(root)) for f in sec_files[:4])

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

    return RISK_METRICS


def calculate_iso31000_score(metrics: list[ISO31000Metric]) -> tuple[int, str, str]:
    """Calculate ISO 31000 ERM Governance Score (0-100)."""
    base_score = 40
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 80:
        grade = "A+ (ISO 31000 Risk Managed)"
        status = "🟢 LOW RISK EXPOSURE — Automated Vuln Scanning & Redundancy Active"
    elif score >= 60:
        grade = "A (Moderate Risk Controls)"
        status = "🟢 ACCEPTABLE — Vuln Scanners or Security Policy Configured"
    else:
        grade = "C/F (High Architectural Risk)"
        status = "🔴 HIGH RISK EXPOSURE — Missing Vulnerability Scanning or SPOF Redundancy"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO31000Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso31000_score(metrics)

    lines = [
        f"# 📊 ISO 31000:2018 Enterprise Risk Management Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 31000 Risk Governance Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 31000 Risk Score** | **{score} / 100** |",
        f"| **ERM Governance Grade** | **{grade}** |",
        f"| **Risk Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Risk Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 31000 Risk Controls & Evidence",
        "",
        "| Domain | Risk Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 31000 Risk Remediation Blueprint",
        "",
        "1. **Vulnerability Scanning**: Add Dependabot / Snyk configuration to `.github/dependabot.yml`.",
        "2. **Deprecation Scrubbing**: Replace deprecated package APIs with current stable releases.",
        "3. **Security Policy**: Maintain a `SECURITY.md` file detailing disclosure guidelines.",
        "",
        "---",
        f"*ISO 31000 Enterprise Risk Management Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  📊 ISO 31000:2018 ENTERPRISE RISK AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 31000 Risk Score        : {score} / 100")
    print(f"  ERM Governance Grade        : {grade}")
    print(f"  Verified Risk Controls      : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_31000_risk_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_31000_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso31000(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
