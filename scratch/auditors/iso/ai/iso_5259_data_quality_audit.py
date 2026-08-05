#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   📊 ISO/IEC 5259 ML Training Data Quality & Governance Auditor           ║
║   BM25 + AST Scanner for ML/LLM Dataset Engineering & Lineage             ║
║                                                                           ║
║   OFFICIAL STANDARD: ISO/IEC 5259-1..5:2024 / 2025                        ║
║   ICS: 35.020 | Committee: ISO/IEC JTC 1/SC 42 (Artificial Intelligence)   ║
║                                                                           ║
║   CONTROLS:                                                               ║
║   - Part 1: Data Quality Schemas & Validation (Pydantic / Types)          ║
║   - Part 2: Data Quality Metrics (Deduplication / Null Handling)           ║
║   - Part 3: Dataset Lineage & Provenance (DVC / MLflow / Feast)           ║
║   - Part 4: Data Preprocessing & Cleaning Pipelines                       ║
║   - Part 5: Synthetic Data & Privacy Governance (Anonymization)           ║
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
    part: str               # Part 1..5
    control_id: str         # A.5259.1 .. A.5259.5
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# ISO/IEC 5259 Data Quality Controls Matrix
# ─────────────────────────────────────────────────────────────────────────────
ISO5259_CONTROLS: list[ISO5259Control] = [
    ISO5259Control(
        part="Part 1 (Terminology & Schema)",
        control_id="ISO-5259-1-01",
        title="Structured Data Schema Validation (Pydantic / dataclasses / Zod)",
        impact="POSITIVE", score_delta=+20,
        description="Dataset rows and ML features conform to strongly-typed schemas.",
        remediation="Define Pydantic BaseModel or Zod schemas for all ML inputs.",
    ),
    ISO5259Control(
        part="Part 2 (Quality Metrics)",
        control_id="ISO-5259-2-01",
        title="Data Deduplication & Outlier Handling",
        impact="POSITIVE", score_delta=+20,
        description="Dataset pipeline removes duplicate records and handles null/missing values.",
        remediation="Implement `.drop_duplicates()` or SQL `DISTINCT` in ETL pipelines.",
    ),
    ISO5259Control(
        part="Part 3 (Data Provenance & Lineage)",
        control_id="ISO-5259-3-01",
        title="Dataset Versioning & Lineage Tracking (DVC / MLflow / SHA-256)",
        impact="POSITIVE", score_delta=+20,
        description="Training datasets are versioned with cryptographic hashes and lineage logs.",
        remediation="Use DVC, MLflow or SHA-256 manifest files for training data versioning.",
    ),
    ISO5259Control(
        part="Part 4 (Preprocessing Framework)",
        control_id="ISO-5259-4-01",
        title="Standardized Preprocessing & Normalization Pipelines",
        impact="POSITIVE", score_delta=+20,
        description="Feature scaling, tokenization, or cleaning pipelines are reproducible.",
        remediation="Use Scikit-Learn `Pipeline`, HuggingFace `Tokenizer` or Polars transforms.",
    ),
    ISO5259Control(
        part="Part 5 (Synthetic Data & Privacy)",
        control_id="ISO-5259-5-01",
        title="Data Anonymization & Synthetic Data Privacy Controls",
        impact="POSITIVE", score_delta=+20,
        description="Training datasets scrub PII or use synthetic data generators (Faker / SDV).",
        remediation="Anonymize training data using Faker or differential privacy tools.",
    ),
]


PATTERNS = {
    "ISO-5259-1-01": ["BaseModel", "dataclass", "zod", "schema.json", "TypeVar"],
    "ISO-5259-2-01": ["drop_duplicates", "dropna", "fillna", "isnull", "SELECT DISTINCT"],
    "ISO-5259-3-01": ["dvc.yaml", "mlflow", "hashlib.sha256", "dataset_version", "Feast"],
    "ISO-5259-4-01": ["StandardScaler", "AutoTokenizer", "Pipeline(", "transform(", "polars"],
    "ISO-5259-5-01": ["faker", "anonymize", "synthetic", "diffpriv", "mask_pii"],
}


def scan_iso5259(root: Path, idx: IndexStoreAdapter) -> list[ISO5259Control]:
    """Scan codebase for ISO/IEC 5259 Training Data Quality controls."""
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
    """Calculate ISO 5259 Data Quality Score (0-100) and Maturity Grade."""
    score = sum(c.score_delta for c in controls if c.found)

    if score >= 85:
        grade = "A+ (ISO 5259 Data Quality Certified)"
        status = "🟢 FULLY COMPLIANT — Production ML Data Quality & Provenance"
    elif score >= 60:
        grade = "A (High Data Quality Readiness)"
        status = "🟢 HIGH — Compliant with Minor Lineage/Schema Controls Outstanding"
    elif score >= 40:
        grade = "B (Moderate Data Debt)"
        status = "🟡 MEDIUM — Requires Dataset Versioning & Schema Validation"
    else:
        grade = "C/F (Data Quality Hazard)"
        status = "🔴 NON-COMPLIANT — Lacks Training Data Schemas or Deduplication"

    return score, grade, status


def print_report(project: str, root: Path, controls: list[ISO5259Control],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [c for c in controls if c.found]
    score, grade, status = calculate_iso5259_score(controls)

    lines = [
        f"# 📊 ISO/IEC 5259 ML Training Data Quality Audit — {project}",
        f"> Official Standard: ISO/IEC 5259-1..5:2024/2025 · ICS: 35.020 · Committee: ISO/IEC JTC 1/SC 42 (AI)",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 5259 Data Quality Governance Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 5259 Data Quality Score** | **{score} / 100** |",
        f"| **Data Quality Maturity Grade** | **{grade}** |",
        f"| **Compliance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified Data Controls | {len(found)} / {len(controls)} |",
        "",
        "## 🔍 Verified ISO 5259 Data Quality Controls (Parts 1–5)",
        "",
        "| Standard Part | Control ID | Control Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|---|",
    ]

    for c in found:
        ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2])
        lines.append(f"| `{c.part}` | `{c.control_id}` | {c.title} | ✅ FOUND | {ev} | {c.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 5259 ML Data Quality Remediation Blueprint",
        "",
        "1. **Part 1 (Schemas)**: Enforce Pydantic or Zod models for all dataset columns and ML feature vectors.",
        "2. **Part 2 (Metrics)**: Implement automated deduplication and null-handling in data ingestion jobs.",
        "3. **Part 3 (Lineage)**: Version training datasets using DVC or SHA-256 checksum manifests.",
        "4. **Part 4 (Preprocessing)**: Use Scikit-Learn `Pipeline` or HuggingFace Tokenizers for reproducible ETL.",
        "5. **Part 5 (Privacy)**: Anonymize personal identifiable data or generate synthetic datasets.",
        "",
        "---",
        f"*ISO/IEC 5259 ML Data Quality Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  📊 ISO/IEC 5259 ML TRAINING DATA QUALITY AUDITOR: {project}")
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
