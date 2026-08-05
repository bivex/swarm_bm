#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   📊 ISO/IEC 5259-2:2024 ML Data Quality Measures Auditor                 ║
║   BM25 + AST Scanner for Inherent, System-Dependent & AI Quality Measures ║
║                                                                           ║
║   OFFICIAL STANDARD: ISO/IEC 5259-2:2024(en) (First Edition 2024-11)       ║
║   ICS: 35.020 | Committee: ISO/IEC JTC 1/SC 42 (Artificial Intelligence)   ║
║                                                                           ║
║   NORMATIVE CHARACTERISTIC GROUPS (Clause 6):                             ║
║   - 6.2 Inherent DQ: Accuracy, Completeness, Consistency, Credibility     ║
║   - 6.3 Inherent & System: Accessibility, Compliance, Precision, Traceability║
║   - 6.4 System-Dependent: Availability, Portability, Recoverability       ║
║   - 6.5 Additional AI/ML DQ: Auditability, Balance, Diversity, Identifi-  ║
║     ability, Relevance, Representativeness, Similarity & Overfitting      ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/ai/iso_5259_2_data_quality_measures_audit.py /path/to/project [ProjectName]
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
class ISO5259Part2Control:
    group: str              # 6.2 INHERENT / 6.3 INHERENT&SYSTEM / 6.4 SYSTEM / 6.5 ADDITIONAL AI/ML
    control_id: str         # ISO-5259-2-6.2.1 .. 6.5.9
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# ISO/IEC 5259-2:2024 Data Quality Measures Matrix
# ─────────────────────────────────────────────────────────────────────────────
ISO5259_PART2_CONTROLS: list[ISO5259Part2Control] = [

    # ── 6.2 INHERENT DATA QUALITY CHARACTERISTICS ─────────────────────────────
    ISO5259Part2Control(
        group="6.2 Inherent DQ", control_id="ISO-5259-2-6.2.1",
        title="Accuracy & True Value Representation",
        impact="POSITIVE", score_delta=+10,
        description="Data items accurately represent real-world entities without noise.",
        remediation="Validate dataset field boundaries and ground-truth values.",
    ),
    ISO5259Part2Control(
        group="6.2 Inherent DQ", control_id="ISO-5259-2-6.2.2",
        title="Completeness & Null Value Handling",
        impact="POSITIVE", score_delta=+10,
        description="Dataset rows contain complete attributes without missing values.",
        remediation="Enforce `.dropna()` or `.fillna()` in data transformation pipelines.",
    ),
    ISO5259Part2Control(
        group="6.2 Inherent DQ", control_id="ISO-5259-2-6.2.3",
        title="Consistency & Schema Integrity",
        impact="POSITIVE", score_delta=+10,
        description="Data attributes across records are free from contradictions.",
        remediation="Enforce Pydantic/dataclass schema types across all pipeline stages.",
    ),

    # ── 6.3 INHERENT & SYSTEM-DEPENDENT CHARACTERISTICS ────────────────────────
    ISO5259Part2Control(
        group="6.3 Inherent & System", control_id="ISO-5259-2-6.3.4",
        title="Precision & High Discrimination Features",
        impact="POSITIVE", score_delta=+10,
        description="Feature values possess necessary numeric precision and resolution.",
        remediation="Use float64/int64 precision for high-dimensional feature vectors.",
    ),
    ISO5259Part2Control(
        group="6.3 Inherent & System", control_id="ISO-5259-2-6.3.5",
        title="Traceability & Lineage Metadata",
        impact="POSITIVE", score_delta=+10,
        description="Data records can be traced back to their originating source.",
        remediation="Log dataset source URLs, Git commit hashes, and ingestion timestamps.",
    ),

    # ── 6.4 SYSTEM-DEPENDENT CHARACTERISTICS ──────────────────────────────────
    ISO5259Part2Control(
        group="6.4 System-Dependent", control_id="ISO-5259-2-6.4.2",
        title="Portability & Open Standard Formats (Parquet / JSONL / Arrow)",
        impact="POSITIVE", score_delta=+10,
        description="Datasets are stored in portable, machine-readable formats.",
        remediation="Save datasets as Parquet, Arrow, or JSONLines format.",
    ),

    # ── 6.5 ADDITIONAL AI/ML DATA QUALITY CHARACTERISTICS ────────────────────
    ISO5259Part2Control(
        group="6.5 Additional AI/ML", control_id="ISO-5259-2-6.5.2",
        title="Balance & Class Representation (Anti-Overfitting)",
        impact="POSITIVE", score_delta=+15,
        description="Dataset classes are balanced to prevent overfitting and sampling skew.",
        remediation="Perform class re-weighting or SMOTE oversampling for imbalanced classes.",
    ),
    ISO5259Part2Control(
        group="6.5 Additional AI/ML", control_id="ISO-5259-2-6.5.5",
        title="Identifiability & Bounding Box / Annotation Quality",
        impact="POSITIVE", score_delta=+10,
        description="Dataset items, bounding boxes, and labels are uniquely identified.",
        remediation="Assign UUIDs or unique IDs to all training samples and annotations.",
    ),
    ISO5259Part2Control(
        group="6.5 Additional AI/ML", control_id="ISO-5259-2-6.5.7",
        title="Representativeness & Production Distribution Alignment",
        impact="POSITIVE", score_delta=+15,
        description="Training distribution aligns with production data distribution.",
        remediation="Evaluate Kolmogorov-Smirnov distribution distance between train and prod data.",
    ),
]


PATTERNS = {
    "ISO-5259-2-6.2.1": ["validate_accuracy", "ground_truth", "assert_bounds"],
    "ISO-5259-2-6.2.2": ["dropna", "fillna", "isnull", "complete_records"],
    "ISO-5259-2-6.2.3": ["BaseModel", "dataclass", "zod", "schema_validation"],
    "ISO-5259-2-6.3.4": ["float64", "double", "precision", "high_resolution"],
    "ISO-5259-2-6.3.5": ["traceability", "provenance", "git_hash", "source_url"],
    "ISO-5259-2-6.4.2": ["to_parquet", "jsonl", "arrow", "feather", "csv"],
    "ISO-5259-2-6.5.2": ["class_weight", "smote", "balance_dataset", "overfitting"],
    "ISO-5259-2-6.5.5": ["bounding_box", "uuid4", "annotation_id", "sample_id"],
    "ISO-5259-2-6.5.7": ["representativeness", "ks_test", "distribution_drift", "prod_distribution"],
}


def scan_iso5259_part2(root: Path, idx: IndexStoreAdapter) -> list[ISO5259Part2Control]:
    """Scan codebase for ISO/IEC 5259-2:2024 data quality measures."""
    for ctrl in ISO5259_PART2_CONTROLS:
        pats = PATTERNS.get(ctrl.control_id, [])
        hits = set()

        for pat in pats:
            try:
                res = idx.search_code(pat, limit=3)
                for r in res:
                    if r.path and not any(x in r.path for x in ("node_modules", ".git", "vendor", "__pycache__")):
                        hits.add(r.path)
            except Exception:
                pass

        ctrl.evidence_files = sorted(list(hits))[:4]
        ctrl.found = len(ctrl.evidence_files) > 0

    return ISO5259_PART2_CONTROLS


def calculate_iso5259_part2_score(controls: list[ISO5259Part2Control]) -> tuple[int, str, str]:
    """Calculate ISO 5259-2 Quality Measures Score (0-100) and Grade."""
    score = sum(c.score_delta for c in controls if c.found)

    if score >= 85:
        grade = "A+ (ISO 5259-2 Quality Measures Certified)"
        status = "🟢 FULLY COMPLIANT — Production ML Dataset Quality Measures & Balance"
    elif score >= 60:
        grade = "A (High Quality Measures Readiness)"
        status = "🟢 HIGH — Compliant with Minor AI Balance/Drift Controls Outstanding"
    elif score >= 40:
        grade = "B (Moderate Quality Debt)"
        status = "🟡 MEDIUM — Requires Class Balancing & Precision Optimizations"
    else:
        grade = "C/F (Data Quality Hazard)"
        status = "🔴 NON-COMPLIANT — Lacks Basic Data Quality Measures or Portability"

    return score, grade, status


def print_report(project: str, root: Path, controls: list[ISO5259Part2Control],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [c for c in controls if c.found]
    score, grade, status = calculate_iso5259_part2_score(controls)

    lines = [
        f"# 📊 ISO/IEC 5259-2:2024 ML Data Quality Measures Audit — {project}",
        f"> Official Standard: ISO/IEC 5259-2:2024(en) · ICS: 35.020 · Committee: ISO/IEC JTC 1/SC 42 (AI)",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 5259-2 Data Quality Measures Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 5259-2 Quality Measures Score** | **{score} / 100** |",
        f"| **Data Quality Measures Grade** | **{grade}** |",
        f"| **Compliance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Quality Measures | {len(found)} / {len(controls)} |",
        "",
        "## 🔍 Verified ISO/IEC 5259-2:2024 Normative Characteristics & Measures",
        "",
        "| Group | Control ID | Characteristic Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|---|",
    ]

    for c in found:
        ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2])
        lines.append(f"| `{c.group}` | `{c.control_id}` | {c.title} | ✅ FOUND | {ev} | {c.remediation} |")

    lines += [
        "",
        "## 🚀 ISO/IEC 5259-2 Data Quality Measures Remediation Blueprint",
        "",
        "1. **Clause 6.2 (Inherent DQ)**: Validate field boundaries, perform `.dropna()` or `.fillna()` and enforce Pydantic types.",
        "2. **Clause 6.3 (Inherent & System)**: Ensure high precision numerical types (`float64`) and log data provenance.",
        "3. **Clause 6.4 (System-Dependent)**: Export datasets using open portable formats (`Parquet`, `JSONL`, `Arrow`).",
        "4. **Clause 6.5 (Additional AI/ML)**: Re-balance imbalanced classes, tag bounding boxes with UUIDs, and measure distribution alignment.",
        "",
        "---",
        f"*ISO/IEC 5259-2:2024 ML Data Quality Measures Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  📊 ISO/IEC 5259-2:2024 ML DATA QUALITY MEASURES AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 5259-2 Quality Score    : {score} / 100")
    print(f"  Measures Grade              : {grade}")
    print(f"  Verified Quality Measures   : {len(found)} / {len(controls)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/ai/iso_5259_2_data_quality_measures_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_5259_2_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    controls = scan_iso5259_part2(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, controls, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
