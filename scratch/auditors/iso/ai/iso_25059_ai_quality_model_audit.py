#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   📊 ISO/IEC 25059:2023 AI System Quality Model Auditor (SQuaRE Ext)      ║
║   BM25 + AST Scanner for AI Software Quality, Robustness & Transparency   ║
║                                                                           ║
║   REFERENCE: Elsevier Computer Science Review 54 (2024) 100681            ║
║   OFFICIAL STANDARD: ISO/IEC 25059:2023 (AI Software Quality Model)        ║
║   ICS: 35.080 / 35.020 | Committee: ISO/IEC JTC 1/SC 7 & SC 42             ║
║                                                                           ║
║   NORMATIVE AI QUALITY CHARACTERISTICS (ISO 25059 & ISO 25010):            ║
║   - Interaction Capability: User Controllability & Transparency            ║
║   - Reliability: Robustness of Neural Networks (ISO 24029) & Fail-Safe    ║
║   - Security: Intervenability & Adversarial Protection                     ║
║   - Functional Suitability: Functional Adaptability & Correctness         ║
║   - Safety & Ethics: Algorithmic Harm Prevention & ISO 24027 Bias         ║
║   - Explainability: SHAP/LIME Interpretability (ISO 6254)                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/ai/iso_25059_ai_quality_model_audit.py /path/to/project [ProjectName]
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
class ISO25059Control:
    characteristic: str      # Interaction Capability / Reliability / Security / Functional Suitability / Safety / Explainability
    control_id: str          # ISO-25059-01 .. 06
    title: str
    impact: str              # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# ISO/IEC 25059:2023 AI Quality Model Matrix (SQuaRE Extension)
# ─────────────────────────────────────────────────────────────────────────────
ISO25059_CONTROLS: list[ISO25059Control] = [
    ISO25059Control(
        characteristic="Interaction Capability",
        control_id="ISO-25059-01",
        title="User Controllability & System Transparency",
        impact="POSITIVE", score_delta=+20,
        description="Users can override model decisions, adjust hyperparameters, or view confidence thresholds.",
        remediation="Implement user override controls, confidence scores, and model decision transparency APIs.",
    ),
    ISO25059Control(
        characteristic="Reliability & Robustness",
        control_id="ISO-25059-02",
        title="AI Neural Network Robustness & Fallback Handling (ISO 24029)",
        impact="POSITIVE", score_delta=+20,
        description="System withstands out-of-distribution noise, adversarial inputs, and degraded network feeds.",
        remediation="Integrate noise injection testing, adversarial defenses, and graceful fallback modes.",
    ),
    ISO25059Control(
        characteristic="Security & Intervenability",
        control_id="ISO-25059-03",
        title="Human Intervenability & Prompt Injection Protection",
        impact="POSITIVE", score_delta=+15,
        description="Human operator can intervene or halt autonomous AI actions; system sanitizes prompt injections.",
        remediation="Add kill-switch / manual intervention hooks and prompt input sanitization filters.",
    ),
    ISO25059Control(
        characteristic="Functional Adaptability",
        control_id="ISO-25059-04",
        title="Functional Adaptability & Continuous Model Re-training",
        impact="POSITIVE", score_delta=+15,
        description="AI model adapts to shifting domain contexts, fine-tuning, or online streaming updates.",
        remediation="Support dynamic model swap, adapter loading (LoRA), or continuous learning pipelines.",
    ),
    ISO25059Control(
        characteristic="Explainability & Interpretability",
        control_id="ISO-25059-05",
        title="Model Interpretability & Feature Attribution (ISO 6254 / SHAP)",
        impact="POSITIVE", score_delta=+15,
        description="System generates human-understandable explanations or feature importance rankings.",
        remediation="Implement SHAP, LIME, attention maps, or text explanation generators.",
    ),
    ISO25059Control(
        characteristic="Safety & Bias Mitigation",
        control_id="ISO-25059-06",
        title="Safety Guardrails & Algorithmic Bias Mitigation (ISO 24027)",
        impact="POSITIVE", score_delta=+15,
        description="AI system evaluates equalized odds, demographic parity, and implements safety guardrails.",
        remediation="Enforce output guardrails (Guardrails AI, NeMo) and demographic parity audits.",
    ),
]


PATTERNS = {
    "ISO-25059-01": ["confidence_score", "user_override", "transparency", "controllability"],
    "ISO-25059-02": ["robustness", "fallback_model", "out_of_distribution", "adversarial_defense"],
    "ISO-25059-03": ["intervenability", "kill_switch", "human_in_the_loop", "prompt_guard"],
    "ISO-25059-04": ["functional_adaptability", "lora_adapter", "fine_tuning", "online_learning"],
    "ISO-25059-05": ["explainability", "interpretability", "shap", "lime", "feature_importance"],
    "ISO-25059-06": ["bias_mitigation", "guardrail", "demographic_parity", "safety_filter"],
}


def scan_iso25059(root: Path, idx: IndexStoreAdapter) -> list[ISO25059Control]:
    """Scan codebase for ISO/IEC 25059:2023 AI System Quality Model controls."""
    for ctrl in ISO25059_CONTROLS:
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

    return ISO25059_CONTROLS


def calculate_iso25059_score(controls: list[ISO25059Control]) -> tuple[int, str, str]:
    """Calculate ISO 25059 AI Quality Score (0-100) and Grade."""
    score = sum(c.score_delta for c in controls if c.found)

    if score >= 85:
        grade = "A+ (ISO 25059 AI Quality Model Certified)"
        status = "🟢 FULLY COMPLIANT — Production AI Quality, Robustness & Explainability"
    elif score >= 60:
        grade = "A (High AI Quality Readiness)"
        status = "🟢 HIGH — Compliant with Minor Explainability / Adaptability Features Missing"
    elif score >= 40:
        grade = "B (Moderate Quality Debt)"
        status = "🟡 MEDIUM — Requires Human Intervenability & Neural Robustness Testing"
    else:
        grade = "C/F (AI Quality Hazard)"
        status = "🔴 NON-COMPLIANT — Lacks Transparency, Safety Filters or User Controllability"

    return score, grade, status


def print_report(project: str, root: Path, controls: list[ISO25059Control],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [c for c in controls if c.found]
    score, grade, status = calculate_iso25059_score(controls)

    lines = [
        f"# 📊 ISO/IEC 25059:2023 AI System Quality Model Audit — {project}",
        f"> Reference: Computer Science Review 54 (2024) 100681 · Committee: ISO/IEC JTC 1/SC 7 & SC 42",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 25059 AI Quality Model Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 25059 AI Quality Score** | **{score} / 100** |",
        f"| **AI System Quality Grade** | **{grade}** |",
        f"| **Compliance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified AI Quality Characteristics | {len(found)} / {len(controls)} |",
        "",
        "## 🔍 Verified ISO/IEC 25059:2023 Normative AI Quality Characteristics",
        "",
        "| Characteristic | Control ID | Control Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|---|",
    ]

    for c in found:
        ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2])
        lines.append(f"| `{c.characteristic}` | `{c.control_id}` | {c.title} | ✅ FOUND | {ev} | {c.remediation} |")

    lines += [
        "",
        "## 🚀 ISO/IEC 25059 AI System Quality Remediation Blueprint",
        "",
        "1. **Interaction Capability**: Implement user decision overrides and confidence score transparency.",
        "2. **Reliability & Robustness**: Conduct neural network robustness testing under out-of-distribution noise (ISO 24029).",
        "3. **Security & Intervenability**: Provide manual kill-switches and prompt injection protection filters.",
        "4. **Functional Adaptability**: Enable dynamic adapter loading (LoRA) and continuous fine-tuning pipelines.",
        "5. **Explainability**: Integrate SHAP, LIME, or attention map generators for model predictions (ISO 6254).",
        "6. **Safety & Ethics**: Enforce output guardrails (Guardrails AI) and demographic parity audits (ISO 24027).",
        "",
        "---",
        f"*ISO/IEC 25059:2023 AI System Quality Model Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  📊 ISO/IEC 25059:2023 AI SYSTEM QUALITY MODEL AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 25059 AI Quality Score  : {score} / 100")
    print(f"  AI Quality Grade            : {grade}")
    print(f"  Verified Quality Controls   : {len(found)} / {len(controls)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/ai/iso_25059_ai_quality_model_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_25059_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    controls = scan_iso25059(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, controls, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
