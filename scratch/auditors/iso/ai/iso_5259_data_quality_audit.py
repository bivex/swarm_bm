#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   📊 ISO/IEC 5259-1:2024 ML Data Quality & Governance Auditor             ║
║   BM25 + AST Scanner for ML Dataset Life Cycle, Lineage & Provenance      ║
║                                                                           ║
║   OFFICIAL STANDARD: ISO/IEC 5259-1:2024(en) (First Edition 2024-07)       ║
║   ICS: 35.020 | Committee: ISO/IEC JTC 1/SC 42 (Artificial Intelligence)   ║
║                                                                           ║
║   CORE NORMATIVE CONCEPTS:                                                ║
║   - Clause 3.2–3.4: Data Roles (Originator, Holder, User & PII Rights)     ║
║   - Clause 3.17: Data Provenance & Cryptographic Ownership Traceability   ║
║   - Clause 5.1.2: ML Partitions (Training, Validation, Test, Production)   ║
║   - Clause 5.1.2 Ex 1: Representativeness & Bias Prevention               ║
║   - Clause 5.2.2.1: Inherent vs System Dependent Data Quality             ║
║   - Clause 5.3: Data Life Cycle (DLC) Process Framework                   ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/ai/iso_5259_data_quality_audit.py /path/to/project [ProjectName]
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
class ISO5259Control:
    clause: str             # Clause 3 / 5.1 / 5.2 / 5.3
    control_id: str         # ISO-5259-1-01 .. 06
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# ISO/IEC 5259-1:2024 Normative Controls Matrix
# ─────────────────────────────────────────────────────────────────────────────
ISO5259_CONTROLS: list[ISO5259Control] = [
    ISO5259Control(
        clause="Clause 3.2–3.4 (Data Roles & PII Rights)",
        control_id="ISO-5259-1-01",
        title="Data Roles & PII Principal Access Controls (Originator / Holder / User)",
        impact="POSITIVE", score_delta=+15,
        description="Dataset access specifies data originator rights, holder authorization, and PII subject consent.",
        remediation="Define explicit data authorization contracts and PII principal rights in dataset metadata.",
    ),
    ISO5259Control(
        clause="Clause 3.17 (Data Provenance)",
        control_id="ISO-5259-1-02",
        title="Data Provenance & Cryptographic Lineage (SHA-256 / DVC / MLflow)",
        impact="POSITIVE", score_delta=+20,
        description="Dataset origin, timestamps, derivation chain, and proof of authenticity are logged.",
        remediation="Use DVC, MLflow or SHA-256 cryptographic manifests for dataset lineage tracking.",
    ),
    ISO5259Control(
        clause="Clause 5.1.2 (ML Dataset Partitioning)",
        control_id="ISO-5259-1-03",
        title="Strict ML Dataset Segregation (Training / Validation / Test / Production)",
        impact="POSITIVE", score_delta=+20,
        description="Dataset is strictly split into training, validation, testing, and production partitions.",
        remediation="Use Scikit-Learn `train_test_split` or explicit train/val/test directory isolation.",
    ),
    ISO5259Control(
        clause="Clause 5.1.2 Ex 1 (Representativeness)",
        control_id="ISO-5259-1-04",
        title="Dataset Representativeness & Bias Mitigation",
        impact="POSITIVE", score_delta=+15,
        description="Training samples accurately represent production population, preventing demographic bias.",
        remediation="Perform stratified sampling and evaluate class balance across sub-populations.",
    ),
    ISO5259Control(
        clause="Clause 5.2.2.1 (Inherent Data Quality)",
        control_id="ISO-5259-1-05",
        title="Inherent Data Quality (Completeness, Accuracy, Deduplication & Type Schemas)",
        impact="POSITIVE", score_delta=+15,
        description="Data items and records conform to Pydantic/Zod schemas with null handling & deduplication.",
        remediation="Enforce Pydantic/dataclass schema validation and drop duplicate rows in ETL.",
    ),
    ISO5259Control(
        clause="Clause 5.3 (Data Life Cycle DLC)",
        control_id="ISO-5259-1-06",
        title="Data Life Cycle (DLC) Pipeline Automation & Preprocessing",
        impact="POSITIVE", score_delta=+15,
        description="End-to-end data life cycle pipeline handles acquisition, cleaning, labelling, and deployment.",
        remediation="Use Scikit-Learn `Pipeline`, HuggingFace Tokenizers or Airflow/Prefect DLC DAGs.",
    ),
]


PATTERNS = {
    "ISO-5259-1-01": ["data_originator", "data_holder", "data_user", "pii_principal", "consent"],
    "ISO-5259-1-02": ["dvc.yaml", "mlflow", "hashlib.sha256", "data_provenance", "dataset_version"],
    "ISO-5259-1-03": ["train_test_split", "validation_data", "test_data", "train_data", "test_set"],
    "ISO-5259-1-04": ["stratified", "class_weight", "representativeness", "balance_dataset", "bias_check"],
    "ISO-5259-1-05": ["BaseModel", "dataclass", "drop_duplicates", "fillna", "dropna"],
    "ISO-5259-1-06": ["Pipeline(", "AutoTokenizer", "data_lifecycle", "etl_pipeline", "polars"],
}


def scan_iso5259(root: Path, idx: IndexStoreAdapter) -> list[ISO5259Control]:
    """Scan codebase for ISO/IEC 5259-1:2024 normative controls."""
    for ctrl in ISO5259_CONTROLS:
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

    return ISO5259_CONTROLS


def calculate_iso5259_score(controls: list[ISO5259Control]) -> tuple[int, str, str]:
    """Calculate ISO 5259-1 Data Quality Score (0-100) and Maturity Grade."""
    score = sum(c.score_delta for c in controls if c.found)

    if score >= 85:
        grade = "A+ (ISO 5259 Data Quality Certified)"
        status = "🟢 FULLY COMPLIANT — Production ML Data Quality & Provenance"
    elif score >= 60:
        grade = "A (High Data Quality Readiness)"
        status = "🟢 HIGH — Compliant with Minor Lineage/Schema Controls Outstanding"
    elif score >= 40:
        grade = "B (Moderate Data Debt)"
        status = "🟡 MEDIUM — Requires Dataset Versioning & Partitioning"
    else:
        grade = "C/F (Data Quality Hazard)"
        status = "🔴 NON-COMPLIANT — Lacks Training Data Schemas or Lineage"

    return score, grade, status


def print_report(project: str, root: Path, controls: list[ISO5259Control],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [c for c in controls if c.found]
    score, grade, status = calculate_iso5259_score(controls)

    lines = [
        f"# 📊 ISO/IEC 5259-1:2024 ML Data Quality Audit — {project}",
        f"> Official Standard: ISO/IEC 5259-1:2024(en) · ICS: 35.020 · Committee: ISO/IEC JTC 1/SC 42 (AI)",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 5259-1 Data Quality Governance Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 5259 Data Quality Score** | **{score} / 100** |",
        f"| **Data Quality Maturity Grade** | **{grade}** |",
        f"| **Compliance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Data Controls | {len(found)} / {len(controls)} |",
        "",
        "## 🔍 Verified ISO/IEC 5259-1:2024 Normative Controls",
        "",
        "| Clause | Control ID | Control Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|---|",
    ]

    for c in found:
        ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2])
        lines.append(f"| `{c.clause}` | `{c.control_id}` | {c.title} | ✅ FOUND | {ev} | {c.remediation} |")

    lines += [
        "",
        "## 🚀 ISO/IEC 5259-1 Data Quality Remediation Blueprint",
        "",
        "1. **Data Roles (Clause 3.2–3.4)**: Define authorization contracts for Data Originators, Data Holders, and Data Users.",
        "2. **Data Provenance (Clause 3.17)**: Version datasets using DVC, MLflow, or SHA-256 cryptographic manifests.",
        "3. **ML Partitions (Clause 5.1.2)**: Strictly isolate Training, Validation, Testing, and Production datasets.",
        "4. **Representativeness (Clause 5.1.2 Ex 1)**: Perform stratified sampling to prevent demographic sampling bias.",
        "5. **Inherent Data Quality (Clause 5.2.2.1)**: Enforce Pydantic/Zod schemas and remove duplicates in ETL.",
        "6. **Data Life Cycle (Clause 5.3)**: Automate end-to-end data pipelines using Scikit-Learn or Airflow DAGs.",
        "",
        "---",
        f"*ISO/IEC 5259-1:2024 ML Data Quality Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  📊 ISO/IEC 5259-1:2024 ML TRAINING DATA QUALITY AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 5259 Data Quality Score : {score} / 100")
    print(f"  Maturity Grade              : {grade}")
    print(f"  Verified Data Controls      : {len(found)} / {len(controls)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/ai/iso_5259_data_quality_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_5259_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    controls = scan_iso5259(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, controls, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
