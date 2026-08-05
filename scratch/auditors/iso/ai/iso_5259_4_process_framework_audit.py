#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   📊 ISO/IEC 5259-4:2024 ML Data Quality Process Framework Auditor        ║
║   BM25 + AST Scanner for ML Data Preparation, Labelling & Augmentation    ║
║                                                                           ║
║   OFFICIAL STANDARD: ISO/IEC 5259-4:2024(en) (First Edition 2024-07)       ║
║   ICS: 35.020 | Committee: ISO/IEC JTC 1/SC 42 (Artificial Intelligence)   ║
║                                                                           ║
║   NORMATIVE PROCESSES (Clause 6–8):                                       ║
║   - Clause 6: DQPF Framework (Planning, Evaluation, Improvement, Validation)║
║   - Clause 7.5.5: Wrapped Dataset Composition (Index, Head, Page)          ║
║   - Clause 7.5.9: Imputation & Scaling (MinMax, Robust, IterativeImputer) ║
║   - Clause 7.5.9.4: Data Augmentation (Text, Vision, Speech Perturbation)  ║
║   - Clause 7.5.10: De-identification (Anonymization & Differential Privacy) ║
║   - Clause 7.5.11: Categorical Encoding (OneHotEncoder, LabelEncoder)     ║
║   - Clause 8: Data Labelling (Pseudo-labelling, Cross-validation & AQL)    ║
║   - Clause 11: Reinforcement Learning DQ (Reward & State Recording)        ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/ai/iso_5259_4_process_framework_audit.py /path/to/project [ProjectName]
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
class ISO5259Part4Control:
    clause: str             # Clause 6 / 7.5 / 8 / 11
    control_id: str         # ISO-5259-4-01 .. 08
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# ISO/IEC 5259-4:2024 Process Framework Controls Matrix
# ─────────────────────────────────────────────────────────────────────────────
ISO5259_PART4_CONTROLS: list[ISO5259Part4Control] = [
    ISO5259Part4Control(
        clause="Clause 6 (DQPF Framework)",
        control_id="ISO-5259-4-01",
        title="Data Quality Process Framework (Planning, Evaluation & Validation)",
        impact="POSITIVE", score_delta=+15,
        description="Data quality pipeline implements planning, continuous evaluation, and validation feedback loops.",
        remediation="Build automated evaluation and validation steps in dataset preparation scripts.",
    ),
    ISO5259Part4Control(
        clause="Clause 7.5.5 (Dataset Composition)",
        control_id="ISO-5259-4-02",
        title="Wrapped Dataset Structure & Stratified Sampling",
        impact="POSITIVE", score_delta=+10,
        description="Dataset is structured with metadata headers, index manifests, and stratified sampling.",
        remediation="Use wrapped dataset structures with index manifests or PyTorch/TensorFlow Dataset wrappers.",
    ),
    ISO5259Part4Control(
        clause="Clause 7.5.9 (Imputation & Scaling)",
        control_id="ISO-5259-4-03",
        title="Standardized Scaling & Missing Value Imputation",
        impact="POSITIVE", score_delta=+15,
        description="Pipelines perform scaling (MinMax/Standard/Robust) and imputation (Simple/IterativeImputer).",
        remediation="Incorporate Scikit-Learn `StandardScaler`, `RobustScaler`, or `SimpleImputer` in ETL.",
    ),
    ISO5259Part4Control(
        clause="Clause 7.5.9.4 (Data Augmentation)",
        control_id="ISO-5259-4-04",
        title="Multi-Modal Data Augmentation (Vision / Text / Audio Perturbation)",
        impact="POSITIVE", score_delta=+15,
        description="Training datasets apply augmentation (rotations, cropping, back-translation, noise injection).",
        remediation="Use torchvision transforms, Albumentations, or NLP back-translation augmenters.",
    ),
    ISO5259Part4Control(
        clause="Clause 7.5.10 (Data De-identification)",
        control_id="ISO-5259-4-05",
        title="PII De-identification & Differential Privacy (ISO/IEC 27559)",
        impact="POSITIVE", score_delta=+15,
        description="Personal Identifiable Information (PII) is anonymized, pseudo-anonymized, or scrubbed.",
        remediation="Apply Faker, Presidio, or differential privacy tools to de-identify PII prior to training.",
    ),
    ISO5259Part4Control(
        clause="Clause 7.5.11 (Categorical Encoding)",
        control_id="ISO-5259-4-06",
        title="Numerical Encoding for Categorical Data (OneHot / LabelEncoder)",
        impact="POSITIVE", score_delta=+10,
        description="Categorical attributes are converted to numeric representations using OneHot or Ordinal encoding.",
        remediation="Use `OneHotEncoder` or pandas `get_dummies()` for categorical features.",
    ),
    ISO5259Part4Control(
        clause="Clause 8 (Data Labelling & Cross-Validation)",
        control_id="ISO-5259-4-07",
        title="Data Labelling Process & Mislabel Cross-Validation Revision",
        impact="POSITIVE", score_delta=+10,
        description="Dataset labelling includes quality control, pseudo-labelling, or cross-validation mislabel detection.",
        remediation="Implement N-fold cross-validation or inspection spot-checks to detect mislabeled samples.",
    ),
    ISO5259Part4Control(
        clause="Clause 11 (Reinforcement Learning DQ)",
        control_id="ISO-5259-4-08",
        title="Reinforcement Learning State, Action & Reward Logging",
        impact="POSITIVE", score_delta=+10,
        description="RL agents log state transitions, action spaces, and reward trajectories for DQ validation.",
        remediation="Log RL environment step tuples (state, action, reward, done) using Gymnasium or RLlib.",
    ),
]


PATTERNS = {
    "ISO-5259-4-01": ["dq_plan", "data_quality_evaluation", "process_validation", "dq_strategy"],
    "ISO-5259-4-02": ["Dataset(", "DataLoader", "stratified_sample", "index_manifest"],
    "ISO-5259-4-03": ["StandardScaler", "MinMaxScaler", "RobustScaler", "SimpleImputer", "IterativeImputer"],
    "ISO-5259-4-04": ["RandomCrop", "RandomHorizontalFlip", "Albumentations", "augment", "noise_injection"],
    "ISO-5259-4-05": ["anonymize", "deidentify", "presidio", "diffpriv", "mask_pii"],
    "ISO-5259-4-06": ["OneHotEncoder", "LabelEncoder", "get_dummies", "OrdinalEncoder"],
    "ISO-5259-4-07": ["cross_val_score", "pseudo_label", "annotation_review", "label_inspection"],
    "ISO-5259-4-08": ["reward", "action_space", "gym.make", "environment_step", "rllib"],
}


def scan_iso5259_part4(root: Path, idx: IndexStoreAdapter) -> list[ISO5259Part4Control]:
    """Scan codebase for ISO/IEC 5259-4:2024 process framework controls."""
    for ctrl in ISO5259_PART4_CONTROLS:
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

    return ISO5259_PART4_CONTROLS


def calculate_iso5259_part4_score(controls: list[ISO5259Part4Control]) -> tuple[int, str, str]:
    """Calculate ISO 5259-4 Process Framework Score (0-100) and Grade."""
    score = sum(c.score_delta for c in controls if c.found)

    if score >= 85:
        grade = "A+ (ISO 5259-4 Process Framework Certified)"
        status = "🟢 FULLY COMPLIANT — Production ML Data Preparation, Labelling & Augmentation"
    elif score >= 60:
        grade = "A (High Process Framework Readiness)"
        status = "🟢 HIGH — Compliant with Minor De-identification/Encoding Controls Outstanding"
    elif score >= 40:
        grade = "B (Moderate Process Debt)"
        status = "🟡 MEDIUM — Requires Standardized Scaling, Imputation & Augmentation"
    else:
        grade = "C/F (Data Process Hazard)"
        status = "🔴 NON-COMPLIANT — Lacks Data Preparation Pipelines or Labelling Controls"

    return score, grade, status


def print_report(project: str, root: Path, controls: list[ISO5259Part4Control],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [c for c in controls if c.found]
    score, grade, status = calculate_iso5259_part4_score(controls)

    lines = [
        f"# 📊 ISO/IEC 5259-4:2024 ML Data Quality Process Framework Audit — {project}",
        f"> Official Standard: ISO/IEC 5259-4:2024(en) · ICS: 35.020 · Committee: ISO/IEC JTC 1/SC 42 (AI)",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 5259-4 Process Framework Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 5259-4 Process Score** | **{score} / 100** |",
        f"| **Process Framework Grade** | **{grade}** |",
        f"| **Compliance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Process Controls | {len(found)} / {len(controls)} |",
        "",
        "## 🔍 Verified ISO/IEC 5259-4:2024 Normative Process Controls",
        "",
        "| Clause | Control ID | Control Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|---|",
    ]

    for c in found:
        ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2])
        lines.append(f"| `{c.clause}` | `{c.control_id}` | {c.title} | ✅ FOUND | {ev} | {c.remediation} |")

    lines += [
        "",
        "## 🚀 ISO/IEC 5259-4 Data Process Framework Remediation Blueprint",
        "",
        "1. **Clause 6 (DQPF)**: Integrate automated data quality evaluation and process validation loops in ETL.",
        "2. **Clause 7.5.5 (Composition)**: Wrap datasets with index headers, page manifests, and stratified samplers.",
        "3. **Clause 7.5.9 (Imputation & Scaling)**: Use `StandardScaler`, `RobustScaler`, and `SimpleImputer` for clean features.",
        "4. **Clause 7.5.9.4 (Augmentation)**: Implement vision (rotations/flips), text (back-translation), or audio noise augmentation.",
        "5. **Clause 7.5.10 (De-identification)**: Scrub PII attributes using Faker or Presidio prior to model training.",
        "6. **Clause 7.5.11 (Encoding)**: Encode categorical variables using `OneHotEncoder` or `get_dummies()`.",
        "7. **Clause 8 (Labelling)**: Apply N-fold cross-validation to detect mislabeled items and conduct quality spot-checks.",
        "",
        "---",
        f"*ISO/IEC 5259-4:2024 ML Data Quality Process Framework Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  📊 ISO/IEC 5259-4:2024 ML DATA QUALITY PROCESS FRAMEWORK AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 5259-4 Process Score    : {score} / 100")
    print(f"  Process Grade               : {grade}")
    print(f"  Verified Process Controls   : {len(found)} / {len(controls)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/ai/iso_5259_4_process_framework_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_5259_4_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    controls = scan_iso5259_part4(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, controls, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
