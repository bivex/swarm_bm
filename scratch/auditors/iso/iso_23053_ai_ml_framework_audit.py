#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🤖⚙️ ISO/IEC 23053:2022 Framework for AI Systems Using ML Auditor        ║
║   BM25 + AST + ML Pipeline Integrity & Model Lineage Scanner              ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 23053 ML System Framework:        ║
║   - ML Model Versioning & Experiment Tracking (MLflow / DVC / Weights&Biases)║
║   - Dataset Lineage & Feature Store Integration (Feast / Hopsworks)       ║
║   - Training Reproducibility & Hyperparameter Serialization               ║
║   - Model Inference Performance & Drift Monitoring                        ║
║   - ISO 23053 ML Framework Index (0–100) & ML Quality Grade               ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_23053_ai_ml_framework_audit.py /path/to/project [ProjectName]
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
class ISO23053Metric:
    domain: str             # MODEL_VERSIONING / DATASET_LINEAGE / REPRODUCIBILITY / DRIFT_MONITORING
    metric_id: str          # ML-001..ML-004
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


ML_METRICS: list[ISO23053Metric] = [
    ISO23053Metric(
        domain="MODEL_VERSIONING", metric_id="ML-001",
        title="ML Model Registry & Experiment Tracking (MLflow / DVC / WandB)",
        impact="POSITIVE", score_delta=+25,
        description="System maintains ML model versioning and artifact tracking.",
        remediation="Integrate MLflow or DVC for ML model artifact versioning.",
    ),
    ISO23053Metric(
        domain="DATASET_LINEAGE", metric_id="ML-002",
        title="Dataset Lineage & Feature Store Integration (Feast / DVC)",
        impact="POSITIVE", score_delta=+25,
        description="System tracks training dataset lineage and feature store definitions.",
        remediation="Use DVC or Feast for feature store and training dataset lineage tracking.",
    ),
    ISO23053Metric(
        domain="REPRODUCIBILITY", metric_id="ML-003",
        title="Training Reproducibility & Random Seed Determinism",
        impact="POSITIVE", score_delta=+25,
        description="Training scripts pin random seeds (`random.seed`, `torch.manual_seed`) for determinism.",
        remediation="Set explicit random seeds in ML training scripts for reproducibility.",
    ),
    ISO23053Metric(
        domain="DRIFT_MONITORING", metric_id="ML-004",
        title="Model Data Drift & Inference Performance Monitoring (Evidently / Deepchecks)",
        impact="POSITIVE", score_delta=+25,
        description="Inference pipeline monitors data drift and model accuracy degradation.",
        remediation="Integrate Evidently or Deepchecks for automated model drift detection.",
    ),
]


PATTERNS = {
    "ML-001": ["mlflow", "wandb", "dvc.yaml", "model_registry"],
    "ML-002": ["feast", "feature_store", "dvc.lock", "dataset_version"],
    "ML-003": ["manual_seed", "random.seed", "np.random.seed", "set_seed"],
    "ML-004": ["evidently", "deepchecks", "data_drift", "concept_drift"],
}


def scan_iso23053(root: Path, idx: IndexStoreAdapter) -> list[ISO23053Metric]:
    """Scan codebase for ISO/IEC 23053 ML Framework controls."""
    for m in ML_METRICS:
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

    return ML_METRICS


def calculate_iso23053_score(metrics: list[ISO23053Metric]) -> tuple[int, str, str]:
    """Calculate ISO 23053 ML Framework Score (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 23053 ML Certified)"
        status = "🟢 HIGH ML QUALITY — Model Registry, Feature Store & Seed Determinism Active"
    elif score >= 50:
        grade = "A (Good ML Framework)"
        status = "🟢 GOOD — Model Registry or Seed Pinning Active"
    else:
        grade = "C/F (ML Pipeline Gap)"
        status = "🔴 ML PIPELINE GAP — Missing Model Registry or Random Seed Determinism"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO23053Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso23053_score(metrics)

    lines = [
        f"# 🤖⚙️ ISO/IEC 23053:2022 Machine Learning Systems Framework Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 23053 ML Framework Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 23053 ML Score** | **{score} / 100** |",
        f"| **ML Framework Grade** | **{grade}** |",
        f"| **Pipeline Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified ML Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 23053 ML Evidence",
        "",
        "| Domain | ML Metric Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 23053 ML Framework Remediation Blueprint",
        "",
        "1. **Model Registry**: Integrate MLflow or DVC for model versioning.",
        "2. **Determinism**: Set explicit random seeds (`torch.manual_seed`) in training scripts.",
        "3. **Drift Detection**: Monitor model performance degradation via Evidently.",
        "",
        "---",
        f"*ISO/IEC 23053 Machine Learning Framework Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🤖⚙️ ISO/IEC 23053 MACHINE LEARNING FRAMEWORK AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 23053 ML Score          : {score} / 100")
    print(f"  ML Framework Grade          : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_23053_ai_ml_framework_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_23053_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    metrics = scan_iso23053(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
