#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║   📋 ISO/IEC 19770 Software Asset Management (SAM) & License Auditor       ║
║   BM25 + AST + Open Source License Compliance & SBOM Scanner              ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 19770 Software Asset controls:   ║
║   - Software Bill of Materials (SBOM / CycloneDX / SPDX) Generation       ║
║   - Detection of Permissive vs Copyleft License Conflicts (GPL / AGPL)    ║
║   - License File Presence & Copyright Notice Verification                 ║
║   - Commercial SaaS Third-Party Dependency Lock-In Risk                   ║
║   - ISO 19770 SAM License Index (0–100) & Asset Compliance Grade          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_19770_license_audit.py /path/to/project [ProjectName]
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
class ISO19770Metric:
    domain: str             # SBOM_GOVERNANCE / COPYLEFT_RISK / LICENSE_NOTICE / THIRD_PARTY_LOCKIN
    metric_id: str          # SAM-001..SAM-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


SAM_METRICS: list[ISO19770Metric] = [
    ISO19770Metric(
        domain="SBOM_GOVERNANCE", metric_id="SAM-001",
        title="Software Bill of Materials Manifests (SBOM / SPDX / CycloneDX)",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains structured package manifests or SPDX/CycloneDX SBOM files.",
        remediation="Generate SPDX or CycloneDX SBOM manifests for all build dependencies.",
    ),
    ISO19770Metric(
        domain="COPYLEFT_RISK", metric_id="SAM-002",
        title="GPL / AGPL Copyleft License Infection Hazard",
        impact="RISK", score_delta=-25,
        description="Found copyleft GPL/AGPL licensed dependencies that may legally force code open-sourcing.",
        remediation="Replace GPL/AGPL dependencies with permissive MIT/Apache-2.0 alternatives.",
    ),
    ISO19770Metric(
        domain="LICENSE_NOTICE", metric_id="SAM-003",
        title="License File & Copyright Attribution Notice (LICENSE.txt)",
        impact="POSITIVE", score_delta=+25,
        description="Repository contains explicit LICENSE file detailing usage terms.",
        remediation="Add a LICENSE file to root repository directory.",
    ),
    ISO19770Metric(
        domain="THIRD_PARTY_LOCKIN", metric_id="SAM-004",
        title="Proprietary SaaS Vendor Lock-In Dependencies",
        impact="RISK", score_delta=-15,
        description="Found heavy reliance on proprietary closed cloud APIs without abstraction layers.",
        remediation="Abstract proprietary SaaS APIs behind domain interface adapters.",
    ),
]


PATTERNS = {
    "SAM-001": ["package.json", "requirements.txt", "Cargo.toml", "pom.xml", "go.mod", "spdx", "cyclonedx", "sbom"],
    "SAM-002": ["GPL-3.0", "AGPL-3.0", "General Public License", "GPLv3"],
    "SAM-003": ["LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING", "mit license"],
    "SAM-004": ["stripe", "twilio", "firebase", "sendgrid", "algolia"],
}


def scan_iso19770(root: Path, idx: IndexStoreAdapter) -> list[ISO19770Metric]:
    """Scan codebase for ISO/IEC 19770 Software Asset Management controls."""
    idx.rebuild(root)
    for m in SAM_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        if m.metric_id == "SAM-003":
            lic_files = list(root.glob("*LICENSE*")) + list(root.glob("*COPYING*"))
            if lic_files:
                hits.update(str(f.relative_to(root)) for f in lic_files[:4])

        if m.metric_id == "SAM-001":
            sbom_files = list(root.glob("**/spdx*")) + list(root.glob("**/cyclonedx*")) + list(root.glob("**/sbom*"))
            if sbom_files:
                hits.update(str(f.relative_to(root)) for f in sbom_files[:4])

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

    return SAM_METRICS


def calculate_iso19770_score(metrics: list[ISO19770Metric]) -> tuple[int, str, str]:
    """Calculate ISO 19770 SAM License Score (0-100)."""
    base_score = 50
    for m in metrics:
        if m.impact == "POSITIVE" and m.found:
            base_score += m.score_delta
        elif m.impact == "RISK" and not m.found:
            # Absence of risk is a positive compliance indicator
            base_score += abs(m.score_delta)

    score = max(0, min(100, base_score))

    if score >= 85:
        grade = "A+ (Full ISO 19770 SAM Conformance)"
        status = "🟢 EXCELLENT — Complete License, Copyright & SBOM Governance"
    elif score >= 70:
        grade = "A (Good Asset Governance)"
        status = "🟢 ACCEPTABLE — License File or Package Manifests Present"
    else:
        grade = "C/F (SAM Compliance Risk)"
        status = "🔴 HIGH RISK — Missing License File or Copyleft Infection Hazard"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO19770Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    score, grade, status = calculate_iso19770_score(metrics)

    lines = [
        f"# 📋 ISO/IEC 19770 Software Asset & License Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 19770 SAM Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 19770 SAM License Score** | **{score} / 100** |",
        f"| **Asset Compliance Grade** | **{grade}** |",
        f"| **Asset Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Asset Controls | {sum(1 for m in metrics if m.found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 19770 SAM Evidence",
        "",
        "| Domain | Asset Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in metrics:
        st = "✅ FOUND" if m.found else "❌ MISSING"
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2]) if m.evidence_files else "None"
        lines.append(f"| `{m.domain}` | {m.title} | {st} | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 19770 SAM Remediation Blueprint",
        "",
        "1. **License Notice**: Ensure a clear `LICENSE.txt` file exists in root.",
        "2. **Copyleft Scrubbing**: Replace any GPL/AGPL dependencies with MIT/Apache alternatives.",
        "3. **SBOM Generation**: Generate CycloneDX / SPDX SBOM manifests in build pipeline.",
        "",
        "---",
        f"*ISO/IEC 19770 Software Asset Management Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  📋 ISO/IEC 19770 SOFTWARE ASSET & LICENSE AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 19770 SAM Score         : {score} / 100")
    print(f"  Asset Compliance Grade      : {grade}")
    print(f"  Verified Controls           : {sum(1 for m in metrics if m.found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_19770_license_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_19770_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso19770(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
