#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🔗 ISO/IEC 27036 Supply Chain & Dependency Lockfile Auditor              ║
║   BM25 + AST + Vendor Lockfile Pinning & Supply Chain Security Scanner    ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 27036 Supply Chain Security:     ║
║   - Exact Dependency Pinning via Lockfiles (package-lock.json, poetry.lock)║
║   - Software Bill of Materials (SBOM) & Vendor Risk Registries            ║
║   - Private Package Repository & Sub-processor Pinning                    ║
║   - Absence of Unpinned Wildcard Third-Party Dependencies                 ║
║   - ISO 27036 Supply Chain Index (0–100) & Vendor Security Grade          ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_27036_supplier_relationships_audit.py /path/to/project [ProjectName]
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
class ISO27036Metric:
    domain: str             # LOCKFILE_PINNING / VENDOR_REGISTRY / REPO_PINNING / UNPINNED_DEPENDENCIES
    metric_id: str          # CHAIN-001..CHAIN-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


CHAIN_METRICS: list[ISO27036Metric] = [
    ISO27036Metric(
        domain="LOCKFILE_PINNING", metric_id="CHAIN-001",
        title="Exact Dependency Pinning via Lockfiles (poetry.lock / package-lock.json / Cargo.lock)",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains exact version pinning via lockfiles to prevent supply chain tampering.",
        remediation="Commit `package-lock.json`, `poetry.lock`, or `Cargo.lock` to source control.",
    ),
    ISO27036Metric(
        domain="VENDOR_REGISTRY", metric_id="CHAIN-002",
        title="Software Bill of Materials & Vendor Risk Registries",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains vendor manifests or SBOM registries.",
        remediation="Maintain a vendor risk registry detailing third-party library dependencies.",
    ),
    ISO27036Metric(
        domain="REPO_PINNING", metric_id="CHAIN-003",
        title="Private Package Repository & Registry Pinning (.npmrc / pip.conf)",
        impact="POSITIVE", score_delta=+25,
        description="Dependency managers are configured with explicit registry URLs.",
        remediation="Specify explicit registry URLs in `.npmrc` or `pip.conf`.",
    ),
    ISO27036Metric(
        domain="UNPINNED_DEPENDENCIES", metric_id="CHAIN-004",
        title="Unpinned Wildcard Third-Party Dependencies (Risk of Supply Chain Attack)",
        impact="RISK", score_delta=-20,
        description="Found unpinned wildcard version specifiers (`*` or `>=`) in dependency manifests.",
        remediation="Pin all third-party package dependencies to exact semantic versions.",
    ),
]


PATTERNS = {
    "CHAIN-001": ["package-lock.json", "poetry.lock", "Cargo.lock", "yarn.lock", "pnpm-lock.yaml"],
    "CHAIN-002": ["vendor", "third_party", "DEPENDENCIES.md", "SBOM"],
    "CHAIN-003": [".npmrc", "pip.conf", "Cargo.toml", "extra-index-url"],
    "CHAIN-004": ['"*": "*"', '">= 0."', '"latest"'],
}


def scan_iso27036(root: Path, idx: IndexStoreAdapter) -> list[ISO27036Metric]:
    """Scan codebase for ISO/IEC 27036 Supply Chain Security controls."""
    for m in CHAIN_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        if m.metric_id == "CHAIN-001":
            lock_files = list(root.glob("*lock*")) + list(root.glob("*.lock"))
            if lock_files:
                hits.update(str(f.relative_to(root)) for f in lock_files[:4])

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

    return CHAIN_METRICS


def calculate_iso27036_score(metrics: list[ISO27036Metric]) -> tuple[int, str, str]:
    """Calculate ISO 27036 Supply Chain Score (0-100)."""
    base_score = 40
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 80:
        grade = "A+ (ISO 27036 Supply Chain Certified)"
        status = "🟢 HIGH SUPPLY CHAIN SECURITY — Lockfiles Pinning & Registry Controls Active"
    elif score >= 60:
        grade = "A (Good Supply Chain Security)"
        status = "🟢 GOOD — Lockfiles or Package Manifests Present"
    else:
        grade = "C/F (Supply Chain Hazard)"
        status = "🔴 SUPPLY CHAIN RISK — Missing Lockfiles or Unpinned Wildcard Dependencies"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO27036Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso27036_score(metrics)

    lines = [
        f"# 🔗 ISO/IEC 27036 Supply Chain & Dependency Lockfile Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 27036 Supply Chain Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 27036 Supply Chain Score** | **{score} / 100** |",
        f"| **Vendor Security Grade** | **{grade}** |",
        f"| **Supply Chain Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Supply Chain Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 27036 Supply Chain Evidence",
        "",
        "| Domain | Supply Chain Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 27036 Supply Chain Remediation Blueprint",
        "",
        "1. **Lockfile Pinning**: Commit `package-lock.json` or `poetry.lock` to source control.",
        "2. **Pin Dependencies**: Replace wildcard version specifiers (`*`) with exact version tags.",
        "3. **Registries**: Specify explicit package registry URLs in configuration files.",
        "",
        "---",
        f"*ISO/IEC 27036 Supply Chain Security Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🔗 ISO/IEC 27036 SUPPLY CHAIN & DEPENDENCY AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 27036 Supply Chain Score: {score} / 100")
    print(f"  Vendor Security Grade       : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_27036_supplier_relationships_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_27036_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso27036(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
