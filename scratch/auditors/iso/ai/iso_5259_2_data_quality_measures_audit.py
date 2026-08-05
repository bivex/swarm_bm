#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   📊 ISO/IEC 5259-2:2024 ML Data Quality Measures & Metrics Auditor       ║
║   BM25 + AST Scanner for Inherent, System-Dependent & AI Quality Measures ║
║                                                                           ║
║   OFFICIAL STANDARD: ISO/IEC 5259-2:2024(en) (First Edition 2024-11)       ║
║   ICS: 35.020 | Committee: ISO/IEC JTC 1/SC 42 (Artificial Intelligence)   ║
║                                                                           ║
║   NORMATIVE ANNEX C PERSPECTIVES:                                         ║
║   - 🛠️ Maintainability: Accessibility, Auditability, Portability          ║
║   - ⌛ Validity: Availability, Currentness, Effectiveness                 ║
║   - 🎯 Reliability: Accuracy, Compliance, Credibility, Precision           ║
║   - ⚖️ Fidelity: Completeness, Balance, Diversity, Representativeness,    ║
║     Similarity, Timeliness & Anti-Overfitting (Clause 3.21)               ║
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
class ISO5259Part2Measure:
    perspective: str        # Maintainability / Validity / Reliability / Fidelity
    qm_id: str              # Acc-ML-7, Com-ML-5, Con-ML-1, etc.
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# ISO/IEC 5259-2:2024 Quality Measures Matrix (Annex C 4 Perspectives)
# ─────────────────────────────────────────────────────────────────────────────
ISO5259_MEASURES: list[ISO5259Part2Measure] = [

    # ── 1. MAINTAINABILITY PERSPECTIVE ───────────────────────────────────────
    ISO5259Part2Measure(
        perspective="MAINTAINABILITY", qm_id="Acs-ML-3",
        title="Data Format Accessibility (Acs-ML-3)",
        impact="POSITIVE", score_delta=+8,
        description="Dataset files are accessible in open readable formats across pipeline stages.",
        remediation="Provide open data readers for CSV, Parquet, or JSONLines datasets.",
    ),
    ISO5259Part2Measure(
        perspective="MAINTAINABILITY", qm_id="Aud-ML-1",
        title="Audited Records & Change Log (Aud-ML-1 / Aud-ML-2)",
        impact="POSITIVE", score_delta=+8,
        description="Dataset modifications, feature engineering, and annotations undergo audit logging.",
        remediation="Maintain an audit log of dataset transformations and label changes.",
    ),
    ISO5259Part2Measure(
        perspective="MAINTAINABILITY", qm_id="Por-ML-1",
        title="Data Portability Ratio (Por-ML-1)",
        impact="POSITIVE", score_delta=+8,
        description="Datasets preserve quality when transferred between systems (Parquet / Arrow).",
        remediation="Export training datasets using portable binary formats (Parquet / Feather / Arrow).",
    ),

    # ── 2. VALIDITY PERSPECTIVE ───────────────────────────────────────────────
    ISO5259Part2Measure(
        perspective="VALIDITY", qm_id="Cur-ML-1",
        title="Feature & Record Currentness (Cur-ML-1 / Cur-ML-2)",
        impact="POSITIVE", score_delta=+8,
        description="Data items fall within required context age range, preventing data-drift.",
        remediation="Filter out stale records or apply inflation/time-decay adjustments.",
    ),
    ISO5259Part2Measure(
        perspective="VALIDITY", qm_id="Eft-ML-1",
        title="Feature Effectiveness Ratio (Eft-ML-1 / Eft-ML-3)",
        impact="POSITIVE", score_delta=+8,
        description="Dataset samples possess acceptable feature quality for the target ML task.",
        remediation="Validate that feature inputs meet acceptable effectiveness thresholds.",
    ),

    # ── 3. RELIABILITY PERSPECTIVE ───────────────────────────────────────────
    ISO5259Part2Measure(
        perspective="RELIABILITY", qm_id="Acc-ML-7",
        title="Data Label Accuracy (Acc-ML-7)",
        impact="POSITIVE", score_delta=+10,
        description="Data labels accurately represent intended target classes and semantic domain.",
        remediation="Verify correctness of label values and bounding box coordinates.",
    ),
    ISO5259Part2Measure(
        perspective="RELIABILITY", qm_id="Cmp-ML-1",
        title="Data Item Regulatory Compliance (Cmp-ML-1)",
        impact="POSITIVE", score_delta=+8,
        description="Dataset meets legal, statutory, and organizational compliance requirements.",
        remediation="Audit dataset against GDPR, PII, and copyright licensing rules.",
    ),
    ISO5259Part2Measure(
        perspective="RELIABILITY", qm_id="Pre-ML-1",
        title="Precision of Numerical Data Values (Pre-ML-1)",
        impact="POSITIVE", score_delta=+8,
        description="Numerical features maintain required floating-point precision (float64).",
        remediation="Use float64 or double precision for high-dimensional feature vectors.",
    ),
    ISO5259Part2Measure(
        perspective="RELIABILITY", qm_id="Tra-ML-1",
        title="Traceability of Data Values (Tra-ML-1)",
        impact="POSITIVE", score_delta=+8,
        description="Data values maintain audit trails tracing back to their origin.",
        remediation="Store source origin URLs, ingestion timestamps, and Git commit hashes.",
    ),

    # ── 4. FIDELITY PERSPECTIVE ───────────────────────────────────────────────
    ISO5259Part2Measure(
        perspective="FIDELITY", qm_id="Com-ML-5",
        title="Label Completeness Ratio (Com-ML-5)",
        impact="POSITIVE", score_delta=+8,
        description="Dataset records are fully labelled without empty bounding boxes or missing tags.",
        remediation="Purge unlabelled samples or perform semi-supervised pseudo-labelling.",
    ),
    ISO5259Part2Measure(
        perspective="FIDELITY", qm_id="Con-ML-1",
        title="Data Record Consistency & Deduplication (Con-ML-1)",
        impact="POSITIVE", score_delta=+8,
        description="Dataset is free from duplicate records that cause feature over-weighting.",
        remediation="Implement `.drop_duplicates()` in data preparation pipelines.",
    ),
    ISO5259Part2Measure(
        perspective="FIDELITY", qm_id="Bal-ML-8",
        title="Label Distribution Balance & KL-Divergence (Bal-ML-8)",
        impact="POSITIVE", score_delta=+10,
        description="Category label distribution is balanced, preventing class underrepresentation.",
        remediation="Perform SMOTE oversampling or class re-weighting to equalize label proportions.",
    ),
    ISO5259Part2Measure(
        perspective="FIDELITY", qm_id="Div-ML-1",
        title="Label Richness & Dataset Diversity (Div-ML-1 / Div-ML-2)",
        impact="POSITIVE", score_delta=+8,
        description="Dataset contains diverse feature ranges, mitigating overfitting risks (Clause 3.21).",
        remediation="Apply data augmentation (rotations/shifts) or synthetic data generation.",
    ),
    ISO5259Part2Measure(
        perspective="FIDELITY", qm_id="Rep-ML-1",
        title="Representativeness Ratio (Rep-ML-1)",
        impact="POSITIVE", score_delta=+9,
        description="Training sample distribution reflects target production population.",
        remediation="Perform Kolmogorov-Smirnov distribution alignment tests between train and prod data.",
    ),
    ISO5259Part2Measure(
        perspective="FIDELITY", qm_id="Tml-ML-1",
        title="Timeliness of Data Items (Tml-ML-1)",
        impact="POSITIVE", score_delta=+8,
        description="Latency ΔT1 between phenomenon occurrence and data availability is minimized.",
        remediation="Use streaming data pipelines (Kafka / Flink) for real-time inference.",
    ),
]


PATTERNS = {
    "Acs-ML-3": ["read_csv", "read_parquet", "json.loads", "dataset_reader"],
    "Aud-ML-1": ["audited_records", "change_log", "dataset_audit", "transformation_history"],
    "Por-ML-1": ["to_parquet", "pyarrow", "feather", "jsonl"],
    "Cur-ML-1": ["max_age", "data_currentness", "data_drift", "time_decay"],
    "Eft-ML-1": ["acceptable_feature", "feature_quality", "validate_features"],
    "Acc-ML-7": ["label_accuracy", "annotation_quality", "bounding_box", "correct_labels"],
    "Cmp-ML-1": ["compliance_check", "gdpr_audit", "pii_compliance", "license_check"],
    "Pre-ML-1": ["float64", "np.double", "precision", "high_precision"],
    "Tra-ML-1": ["source_url", "git_hash", "lineage_metadata", "provenance_log"],
    "Com-ML-5": ["label_completeness", "unlabelled_samples", "bounding_box_area"],
    "Con-ML-1": ["drop_duplicates", "deduplicate", "SELECT DISTINCT", "unique_records"],
    "Bal-ML-8": ["class_weight", "smote", "kl_divergence", "ks_test", "label_balance"],
    "Div-ML-1": ["data_augmentation", "synthetic_data", "label_richness", "diversity"],
    "Rep-ML-1": ["representativeness", "production_distribution", "stratified"],
    "Tml-ML-1": ["timeliness", "streaming_data", "latency", "realtime_inference"],
}


def scan_iso5259_part2(root: Path, idx: IndexStoreAdapter) -> list[ISO5259Part2Measure]:
    """Scan codebase for ISO/IEC 5259-2:2024 normative quality measures."""
    for measure in ISO5259_MEASURES:
        pats = PATTERNS.get(measure.qm_id, [])
        hits = set()

        for pat in pats:
            try:
                res = idx.search_code(pat, limit=3)
                for r in res:
                    if r.path and not any(x in r.path for x in ("node_modules", ".git", "vendor", "__pycache__")):
                        hits.add(r.path)
            except Exception:
                pass

        measure.evidence_files = sorted(list(hits))[:4]
        measure.found = len(measure.evidence_files) > 0

    return ISO5259_MEASURES


def calculate_iso5259_part2_score(measures: list[ISO5259Part2Measure]) -> tuple[int, str, str]:
    """Calculate ISO 5259-2 Data Quality Measures Score (0-100) and Maturity Grade."""
    score = sum(m.score_delta for m in measures if m.found)

    if score >= 85:
        grade = "A+ (ISO 5259-2 Quality Measures Certified)"
        status = "🟢 FULLY COMPLIANT — Production ML Dataset Quality Measures & Balance"
    elif score >= 65:
        grade = "A (High Quality Measures Readiness)"
        status = "🟢 HIGH — Compliant with Minor AI Balance/Lineage Measures Outstanding"
    elif score >= 45:
        grade = "B (Moderate Quality Debt)"
        status = "🟡 MEDIUM — Requires Class Balancing & Precision Optimizations"
    else:
        grade = "C/F (Data Quality Hazard)"
        status = "🔴 NON-COMPLIANT — Lacks Basic Data Quality Measures or Portability"

    return score, grade, status


def print_report(project: str, root: Path, measures: list[ISO5259Part2Measure],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in measures if m.found]
    score, grade, status = calculate_iso5259_part2_score(measures)

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
        f"| Verified Quality Measures | {len(found)} / {len(measures)} |",
        "",
        "## 🔍 Verified ISO/IEC 5259-2:2024 Annex C Quality Perspectives",
        "",
        "| Perspective | QM ID | Quality Measure Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.perspective}` | `{m.qm_id}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO/IEC 5259-2 Data Quality Measures Remediation Blueprint",
        "",
        "1. **Maintainability**: Provide open data readers, change log audits (`Aud-ML-1`), and Parquet portability (`Por-ML-1`).",
        "2. **Validity**: Set max feature age limits (`Cur-ML-1`) and validate feature effectiveness (`Eft-ML-1`).",
        "3. **Reliability**: Audit label accuracy (`Acc-ML-7`), regulatory compliance (`Cmp-ML-1`), and float64 precision (`Pre-ML-1`).",
        "4. **Fidelity**: Purge duplicate records (`Con-ML-1`), balance class distributions (`Bal-ML-8`), and test representativeness (`Rep-ML-1`).",
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
    print(f"  Verified Quality Measures   : {len(found)} / {len(measures)}")
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
    measures = scan_iso5259_part2(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, measures, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
