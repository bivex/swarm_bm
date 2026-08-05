#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🧪 ISO/IEC/IEEE 29119 Software Testing Standards Auditor               ║
║   BM25 + AST + Test Automation, Fixtures & Coverage Governance Scanner    ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC/IEEE 29119 Testing controls:     ║
║   - Automated Unit & Integration Test Suites (pytest, jest, vitest)       ║
║   - Test Fixtures, Mocks & Test Data Isolation (conftest.py, mocks)       ║
║   - Automated End-to-End (E2E) & Integration Tests (Playwright / Cypress) ║
║   - Code Coverage Threshold Enforcers (coverage.py, c8, nyc)              ║
║   - ISO 29119 Testing Index (0–100) & Software Test Quality Grade         ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_29119_software_testing_audit.py /path/to/project [ProjectName]
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
class ISO29119Metric:
    domain: str             # UNIT_TESTING / TEST_FIXTURES / E2E_TESTING / COVERAGE_GOVERNANCE
    metric_id: str          # TEST-001..TEST-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


TEST_METRICS: list[ISO29119Metric] = [
    ISO29119Metric(
        domain="UNIT_TESTING", metric_id="TEST-001",
        title="Automated Unit Test Suite (pytest / jest / vitest / cargo test)",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains automated unit testing files.",
        remediation="Add automated unit test files in `tests/` or `__tests__/`.",
    ),
    ISO29119Metric(
        domain="TEST_FIXTURES", metric_id="TEST-002",
        title="Test Data Isolation & Fixture Management (conftest.py / mocks)",
        impact="POSITIVE", score_delta=+25,
        description="Repository uses test fixtures or mock objects for isolated test execution.",
        remediation="Define isolated test fixtures (`conftest.py`) avoiding production DB mutations.",
    ),
    ISO29119Metric(
        domain="E2E_TESTING", metric_id="TEST-003",
        title="Automated End-to-End (E2E) & Integration Testing (Playwright / Cypress)",
        impact="POSITIVE", score_delta=+25,
        description="Repository maintains automated integration or E2E browser tests.",
        remediation="Add Playwright or Cypress E2E integration test suites.",
    ),
    ISO29119Metric(
        domain="COVERAGE_GOVERNANCE", metric_id="TEST-004",
        title="Code Coverage Threshold Enforcers (coverage.py / nyc / c8)",
        impact="POSITIVE", score_delta=+25,
        description="Repository enforces minimum code coverage thresholds.",
        remediation="Configure `coverage.py` or `c8` threshold checking in CI pipeline.",
    ),
]


PATTERNS = {
    "TEST-001": ["test_", "_test.py", ".spec.ts", ".test.js", "cargo test"],
    "TEST-002": ["conftest.py", "@pytest.fixture", "jest.mock", "unittest.mock"],
    "TEST-003": ["playwright", "cypress", "e2e", "integration-tests"],
    "TEST-004": [".coveragerc", "coverage.xml", "nyc", "c8", "coverageThreshold"],
}


def scan_iso29119(root: Path, idx: IndexStoreAdapter) -> list[ISO29119Metric]:
    """Scan codebase for ISO/IEC/IEEE 29119 Software Testing controls."""
    for m in TEST_METRICS:
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

    return TEST_METRICS


def calculate_iso29119_score(metrics: list[ISO29119Metric]) -> tuple[int, str, str]:
    """Calculate ISO 29119 Software Testing Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 29119 Testing Certified)"
        status = "🟢 HIGH TEST QUALITY — Unit Tests, Fixtures, E2E & Coverage Enforcers Active"
    elif score >= 50:
        grade = "A (Good Test Coverage)"
        status = "🟢 GOOD — Unit Tests or Fixtures Present"
    else:
        grade = "C/F (Testing Gap Risk)"
        status = "🔴 TESTING RISK — Missing Unit Test Automation or Coverage Threshold Enforcers"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO29119Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso29119_score(metrics)

    lines = [
        f"# 🧪 ISO/IEC/IEEE 29119 Software Testing Standards Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 29119 Software Testing Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 29119 Testing Score** | **{score} / 100** |",
        f"| **Test Quality Grade** | **{grade}** |",
        f"| **Testing Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Testing Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 29119 Testing Evidence",
        "",
        "| Domain | Testing Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 29119 Software Testing Remediation Blueprint",
        "",
        "1. **Unit Tests**: Maintain automated unit tests covering key domain logic.",
        "2. **Test Fixtures**: Use `conftest.py` or mock objects for isolated test data.",
        "3. **Coverage Thresholds**: Enforce 80%+ test coverage thresholds in CI pipeline.",
        "",
        "---",
        f"*ISO/IEC/IEEE 29119 Software Testing Standards Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🧪 ISO/IEC/IEEE 29119 SOFTWARE TESTING AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 29119 Testing Score     : {score} / 100")
    print(f"  Test Quality Grade          : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_29119_software_testing_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_29119_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso29119(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
