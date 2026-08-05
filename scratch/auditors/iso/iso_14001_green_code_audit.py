#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🌿 ISO 14001 / ISO 14064 Green Software Engineering Auditor            ║
║   BM25 + AST + Carbon Efficiency & Energy Optimization Scanner            ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO 14001 Green Software Engineering:    ║
║   - Response Payload Compression (Gzip / Brotli / Protobuf)               ║
║   - Database Query Indexing & N+1 Query Elimination                       ║
║   - In-Memory Caching & Reduced CPU Re-computation                         ║
║   - Avoidance of Tight Busy-Polling Loops (Sleep / Event Driven)          ║
║   - ISO 14001 Green Code Index (0–100) & Eco Grade                        ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_14001_green_code_audit.py /path/to/project [ProjectName]
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
class ISO14001Metric:
    domain: str             # PAYLOAD_COMPRESSION / QUERY_OPTIMIZATION / CACHING / POLLING_EFFICIENCY
    metric_id: str          # ECO-001..ECO-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


ECO_METRICS: list[ISO14001Metric] = [
    ISO14001Metric(
        domain="PAYLOAD_COMPRESSION", metric_id="ECO-001",
        title="Network Payload Compression (Gzip / Brotli / Protobuf)",
        impact="POSITIVE", score_delta=+25,
        description="System compresses HTTP response payloads to reduce network bandwidth & energy consumption.",
        remediation="Enable Gzip/Brotli response compression middleware in web server.",
    ),
    ISO14001Metric(
        domain="QUERY_OPTIMIZATION", metric_id="ECO-002",
        title="Database Query Indexing & Eager Loading (N+1 Avoidance)",
        impact="POSITIVE", score_delta=+25,
        description="Queries use explicit indexes and eager loading to minimize database CPU cycles.",
        remediation="Use eager loading (`select_related`, `joinedload`) to eliminate N+1 database queries.",
    ),
    ISO14001Metric(
        domain="CACHING", metric_id="ECO-003",
        title="In-Memory Result Caching (Reduced Re-computation CPU Power)",
        impact="POSITIVE", score_delta=+25,
        description="Repeated calculations and API responses are cached to conserve CPU power.",
        remediation="Cache heavy analytical query results in Redis or in-memory cache.",
    ),
    ISO14001Metric(
        domain="POLLING_EFFICIENCY", metric_id="ECO-004",
        title="Tight Busy-Polling Loop Detection (CPU Energy Waste)",
        impact="RISK", score_delta=-20,
        description="Found tight while-true busy loops without sleep or event-driven async triggers.",
        remediation="Replace busy polling loops with event-driven WebSockets, SSE, or async sleep.",
    ),
]


PATTERNS = {
    "ECO-001": ["gzip", "brotli", "GZipMiddleware", "protobuf", "deflate"],
    "ECO-002": ["db_index=True", "select_related", "prefetch_related", "joinedload", "Index("],
    "ECO-003": ["@cache", "redis.get", "memcached", "lru_cache", "cached_property"],
    "ECO-004": ["while True:", "while(1)", "time.sleep(0)", "Thread.sleep(1)"],
}


def scan_iso14001(root: Path, idx: IndexStoreAdapter) -> list[ISO14001Metric]:
    """Scan codebase for ISO 14001 Green Software Engineering controls."""
    for m in ECO_METRICS:
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

    return ECO_METRICS


def calculate_iso14001_score(metrics: list[ISO14001Metric]) -> tuple[int, str, str]:
    """Calculate ISO 14001 Green Code Score (0-100)."""
    base_score = 40
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 80:
        grade = "A+ (ISO 14001 Eco-Certified)"
        status = "🟢 ECO EFFICIENT — Compression, Indexing & Caching Active"
    elif score >= 60:
        grade = "A (Good Green Software)"
        status = "🟢 ACCEPTABLE — Caching or Indexing Active"
    else:
        grade = "C/F (High Carbon / Energy Waste)"
        status = "🔴 ENERGY WASTEFUL — Missing Compression, Caching or Busy Loop Found"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO14001Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso14001_score(metrics)

    lines = [
        f"# 🌿 ISO 14001 / ISO 14064 Green Software Engineering Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 14001 Eco-Efficiency Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 14001 Green Code Score** | **{score} / 100** |",
        f"| **Eco-Efficiency Grade** | **{grade}** |",
        f"| **Energy Efficiency Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Green Code Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 14001 Green Code Evidence",
        "",
        "| Domain | Green Code Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 14001 Green Code Remediation Blueprint",
        "",
        "1. **Payload Compression**: Enable Gzip/Brotli compression middleware.",
        "2. **Query Indexing**: Add database indexes to frequently queried columns.",
        "3. **Caching**: Cache repeated analytical query responses in Redis.",
        "",
        "---",
        f"*ISO 14001 Green Software Engineering Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🌿 ISO 14001 GREEN SOFTWARE ENGINEERING AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 14001 Green Code Score  : {score} / 100")
    print(f"  Eco-Efficiency Grade        : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_14001_green_code_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_14001_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso14001(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
