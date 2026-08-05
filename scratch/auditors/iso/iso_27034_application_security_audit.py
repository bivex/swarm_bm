#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🛡️ ISO/IEC 27034:2011 Application Security (AppSec) Auditor             ║
║   BM25 + AST + Application Security Controls (ASC) Scanner                 ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 27034 Application Security:       ║
║   - Application Security Components (ASC) & Security Functionality        ║
║   - Security Testing Integration in Build Pipelines                       ║
║   - Threat Modeling & Security Requirements Traceability                  ║
║   - Security Defect Tracking & Remediation Workflows                      ║
║   - ISO 27034 AppSec Index (0–100) & Application Security Grade           ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_27034_application_security_audit.py /path/to/project [ProjectName]
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
class ISO27034Metric:
    domain: str             # SECURITY_COMPONENTS / PIPELINE_TESTING / THREAT_MODELING / DEFECT_TRACKING
    metric_id: str          # APPSEC-001..APPSEC-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


APPSEC_METRICS: list[ISO27034Metric] = [
    ISO27034Metric(
        domain="SECURITY_COMPONENTS", metric_id="APPSEC-001",
        title="Application Security Control (ASC) Component Abstractions",
        impact="POSITIVE", score_delta=+25,
        description="Application defines explicit security components (Auth, Crypto, InputSanitizer).",
        remediation="Encapsulate security routines into explicit Application Security Control (ASC) modules.",
    ),
    ISO27034Metric(
        domain="PIPELINE_TESTING", metric_id="APPSEC-002",
        title="Automated SAST / DAST Security Scanning in Build Pipeline",
        impact="POSITIVE", score_delta=+25,
        description="Build pipeline integrates SAST (Bandit / Semgrep / CodeQL) security scanning.",
        remediation="Integrate CodeQL, Semgrep or Bandit SAST tools into CI/CD build pipeline.",
    ),
    ISO27034Metric(
        domain="THREAT_MODELING", metric_id="APPSEC-003",
        title="Threat Modeling Documentation (THREAT_MODEL.md / STRIDE Analysis)",
        impact="POSITIVE", score_delta=+25,
        description="Project maintains threat modeling documentation or STRIDE analysis artifacts.",
        remediation="Document threat model and STRIDE risk boundaries in `THREAT_MODEL.md`.",
    ),
    ISO27034Metric(
        domain="DEFECT_TRACKING", metric_id="APPSEC-004",
        title="Security Defect Severity Labeling & SLA Tracking",
        impact="POSITIVE", score_delta=+25,
        description="Repository specifies security vulnerability labels and SLA remediation targets.",
        remediation="Define security bug severity triage rules in `SECURITY.md`.",
    ),
]


PATTERNS = {
    "APPSEC-001": ["SecurityContext", "InputSanitizer", "CryptoService", "AuthComponent"],
    "APPSEC-002": ["codeql", "semgrep", "bandit", "sast", "sonar-scanner"],
    "APPSEC-003": ["THREAT_MODEL.md", "STRIDE", "threat_model", "attack_surface"],
    "APPSEC-004": ["security_severity", "vulnerability_sla", "cvss"],
}


def scan_iso27034(root: Path, idx: IndexStoreAdapter) -> list[ISO27034Metric]:
    """Scan codebase for ISO/IEC 27034 Application Security controls."""
    for m in APPSEC_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        if m.metric_id == "APPSEC-003":
            tm_files = list(root.glob("*THREAT*")) + list(root.glob("docs/*threat*"))
            if tm_files:
                hits.update(str(f.relative_to(root)) for f in tm_files[:4])

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

    return APPSEC_METRICS


def calculate_iso27034_score(metrics: list[ISO27034Metric]) -> tuple[int, str, str]:
    """Calculate ISO 27034 AppSec Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 27034 AppSec Certified)"
        status = "🟢 HIGH APPSEC QUALITY — Security Components, SAST Pipeline & Threat Models Active"
    elif score >= 50:
        grade = "A (Good Application Security)"
        status = "🟢 GOOD — SAST Scanning or Threat Docs Present"
    else:
        grade = "C/F (AppSec Governance Gap)"
        status = "🔴 APPSEC GAP — Missing SAST Pipeline Scanners or Threat Model Documentation"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO27034Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso27034_score(metrics)

    lines = [
        f"# 🛡️ ISO/IEC 27034:2011 Application Security (AppSec) Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 27034 AppSec Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 27034 AppSec Score** | **{score} / 100** |",
        f"| **AppSec Quality Grade** | **{grade}** |",
        f"| **AppSec Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified AppSec Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 27034 AppSec Evidence",
        "",
        "| Domain | AppSec Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 27034 AppSec Remediation Blueprint",
        "",
        "1. **SAST Integration**: Add CodeQL or Semgrep static security scanning to CI pipeline.",
        "2. **Threat Model**: Maintain `THREAT_MODEL.md` documenting system attack surfaces.",
        "3. **Security Components**: Encapsulate input sanitization in dedicated ASC modules.",
        "",
        "---",
        f"*ISO/IEC 27034 Application Security Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🛡️ ISO/IEC 27034 APPLICATION SECURITY AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 27034 AppSec Score      : {score} / 100")
    print(f"  AppSec Quality Grade        : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_27034_application_security_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_27034_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso27034(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
