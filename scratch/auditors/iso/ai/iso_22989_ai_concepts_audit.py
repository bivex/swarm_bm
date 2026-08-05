#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ISO/IEC 22989:2022 — AI Concepts and Terminology Conformance Auditor        ║
║                                                                               ║
║  Based on normative structure of ISO/IEC 22989:2022:                         ║
║  Clause 3: AI ecosystem (AI system, AI application, AI workflow)              ║
║  Clause 4: AI system life cycle                                               ║
║    4.1 AI system life cycle phases                                            ║
║    4.2 AI system roles (provider, producer, customer, partner, subject)       ║
║    4.3 AI workflow (functional layers: hardware, data, model, application)    ║
║  Clause 5: Functional layers of the AI ecosystem                              ║
║    5.2 Hardware layer / 5.3 Data layer / 5.4 Model layer / 5.5 Application   ║
║  Clause 6: AI system engineering                                              ║
║    6.1 AI approach categories (symbolic AI, ML, statistical methods)          ║
║    6.2 Tasks (perception, cognition, communication, actuation)                ║
║    6.3 ML (definition, types: supervised/unsupervised/reinforcement)          ║
║  Clause 7: Trustworthiness characteristics                                    ║
║    7.2 Accuracy / 7.3 Robustness / 7.4 Reliability / 7.5 Resilience          ║
║    7.6 Transparency / 7.7 Accountability / 7.8 Explainability                 ║
║    7.9 Fairness / 7.10 Safety / 7.11 Privacy / 7.12 Security                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/ai/iso_22989_ai_concepts_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


@dataclass
class AI22989Check:
    """A normative element from ISO/IEC 22989:2022."""
    clause_id: str
    clause_ref: str
    normative_text: str
    category: str   # ECOSYSTEM / LIFECYCLE / LAYERS / ENGINEERING / TRUSTWORTHINESS
    weight: int
    search_terms: list[str]
    evidence_files: list[str] = field(default_factory=list)
    found: bool = False
    confidence: str = "NONE"


AI_CHECKS: list[AI22989Check] = [

    # ── Clause 3: AI Ecosystem ────────────────────────────────────────────────
    AI22989Check(
        clause_id="3.1.1",
        clause_ref="AI system definition documented",
        normative_text=(
            "AI system: an engineered system that generates outputs such as content, forecasts, "
            "recommendations or decisions for a given set of human-defined objectives. "
            "An AI system is designed to operate with varying levels of autonomy."
        ),
        category="ECOSYSTEM", weight=4,
        search_terms=["ai_system", "ai", "artificial_intelligence", "model",
                      "inference", "prediction", "recommendation"],
    ),
    AI22989Check(
        clause_id="3.1.3",
        clause_ref="AI workflow (functional layers)",
        normative_text=(
            "AI workflow: sequence of processes applied in the development and use of an AI system. "
            "The AI ecosystem is presented in terms of functional layers: hardware, data, "
            "model/algorithm, application layer."
        ),
        category="ECOSYSTEM", weight=2,
        search_terms=["workflow", "pipeline", "lifecycle", "process", "layers"],
    ),

    # ── Clause 4: AI System Life Cycle ───────────────────────────────────────
    AI22989Check(
        clause_id="4.1",
        clause_ref="AI system life cycle phases (design/dev/deploy/operate/decommission)",
        normative_text=(
            "AI system life cycle phases: design and development, deployment, operation, "
            "and decommissioning. Iterative in nature. Each phase involves specific activities "
            "and produces artifacts used in subsequent phases."
        ),
        category="LIFECYCLE", weight=4,
        search_terms=["lifecycle", "development", "deployment", "operation", "decommission",
                      "release", "versioning"],
    ),
    AI22989Check(
        clause_id="4.2",
        clause_ref="AI system roles (provider/producer/customer/partner/subject)",
        normative_text=(
            "Roles in the AI ecosystem: AI system provider (makes AI system available); "
            "AI system producer (develops); AI system customer (deploys for use); "
            "AI system partner (involved in design/dev/deploy); "
            "AI system subject (affected by AI system output)."
        ),
        category="LIFECYCLE", weight=3,
        search_terms=["provider", "producer", "customer", "partner", "subject",
                      "stakeholder", "user", "contributor", "maintainer"],
    ),

    # ── Clause 5: Functional Layers ───────────────────────────────────────────
    AI22989Check(
        clause_id="5.3",
        clause_ref="Data layer (datasets, data pipeline, preprocessing)",
        normative_text=(
            "Data layer: the functional layer in the AI ecosystem that provides data resources, "
            "data management tools and services. Includes training data, validation data, "
            "test data, and production data."
        ),
        category="LAYERS", weight=3,
        search_terms=["data", "dataset", "training_data", "preprocessing", "data_pipeline",
                      "data_loader", "dataloader"],
    ),
    AI22989Check(
        clause_id="5.4",
        clause_ref="Model layer (ML models, algorithms, model management)",
        normative_text=(
            "Model layer: functional layer providing model resources, model management tools. "
            "ML model: mathematical construct that generates an inference or prediction based on input data. "
            "Model management includes versioning, registry, serving."
        ),
        category="LAYERS", weight=4,
        search_terms=["model", "ml_model", "checkpoint", "model_registry", "model_serving",
                      "inference", "serving", "onnx", "weights"],
    ),
    AI22989Check(
        clause_id="5.5",
        clause_ref="Application layer (AI applications, APIs, user interfaces)",
        normative_text=(
            "Application layer: functional layer in the AI ecosystem that provides AI applications. "
            "AI application: application that uses AI technology to perform one or more tasks. "
            "Applications are built from models and expose APIs or user interfaces."
        ),
        category="LAYERS", weight=3,
        search_terms=["api", "application", "interface", "service", "endpoint",
                      "rest", "grpc", "websocket"],
    ),

    # ── Clause 6: AI System Engineering ──────────────────────────────────────
    AI22989Check(
        clause_id="6.1",
        clause_ref="AI approach category documented (symbolic/ML/statistical)",
        normative_text=(
            "AI approach categories: symbolic AI (knowledge-based, logic-based, expert systems), "
            "machine learning (supervised, unsupervised, reinforcement), "
            "and statistical methods. "
            "The approach category should be documented for AI systems."
        ),
        category="ENGINEERING", weight=3,
        search_terms=["approach", "machine_learning", "deep_learning", "neural_network",
                      "statistical", "knowledge_base", "rule_based"],
    ),
    AI22989Check(
        clause_id="6.2",
        clause_ref="AI task types (perception/cognition/communication/actuation)",
        normative_text=(
            "AI system task types: perception (sensing environment, image/speech/text recognition); "
            "cognition (reasoning, planning, problem solving); "
            "communication (natural language processing, text/speech generation); "
            "actuation (controlling physical or virtual actuators)."
        ),
        category="ENGINEERING", weight=3,
        search_terms=["perception", "cognition", "communication", "actuation",
                      "recognition", "generation", "synthesis", "nlp", "speech",
                      "text_to_speech", "tts"],
    ),
    AI22989Check(
        clause_id="6.3.1",
        clause_ref="ML definition and approach (supervised/unsupervised/reinforcement)",
        normative_text=(
            "Machine learning: process of optimising model parameters through computational techniques, "
            "such that the model's behaviour reflects the data or experience. "
            "ML types: supervised (labelled data), unsupervised (no labels), "
            "reinforcement (reward-based), semi-supervised, transfer learning."
        ),
        category="ENGINEERING", weight=4,
        search_terms=["training", "supervised", "unsupervised", "reinforcement",
                      "optimization", "parameters", "epochs", "learning"],
    ),
    AI22989Check(
        clause_id="6.3.2",
        clause_ref="ML model life cycle (conception/training/evaluation/deployment/monitoring/retirement)",
        normative_text=(
            "ML model life cycle stages: model conception, training, evaluation (performance metrics), "
            "deployment, operation/monitoring, and model retirement/replacement. "
            "Each stage should have defined criteria and documented artifacts."
        ),
        category="ENGINEERING", weight=3,
        search_terms=["train", "evaluate", "deploy", "monitor", "retire",
                      "model_version", "experiment", "mlflow", "wandb"],
    ),

    # ── Clause 7: Trustworthiness ─────────────────────────────────────────────
    AI22989Check(
        clause_id="7.2",
        clause_ref="Accuracy (performance metrics, error rates)",
        normative_text=(
            "Accuracy: ability of an AI system to perform an intended task correctly. "
            "Should be quantified with appropriate metrics for the task type "
            "(e.g. precision/recall/F1 for classification, WER for ASR, MOS for TTS, "
            "BLEU/ROUGE for translation)."
        ),
        category="TRUSTWORTHINESS", weight=4,
        search_terms=["accuracy", "precision", "recall", "f1", "wer", "cer", "mos",
                      "bleu", "rouge", "metric", "performance"],
    ),
    AI22989Check(
        clause_id="7.3",
        clause_ref="Robustness (performance under perturbations)",
        normative_text=(
            "Robustness: ability of an AI system to maintain its level of performance under "
            "a variety of conditions (including unusual or adversarial inputs, noise, "
            "distribution shifts, data quality degradation)."
        ),
        category="TRUSTWORTHINESS", weight=3,
        search_terms=["robustness", "adversarial", "noise", "perturbation",
                      "stress_test", "edge_case", "out_of_distribution"],
    ),
    AI22989Check(
        clause_id="7.4",
        clause_ref="Reliability (consistent performance over time)",
        normative_text=(
            "Reliability: ability of an AI system to perform its required function under stated "
            "conditions for a specified period of time. Relates to failure modes and error handling."
        ),
        category="TRUSTWORTHINESS", weight=3,
        search_terms=["reliability", "availability", "uptime", "error_handling",
                      "exception", "fallback", "retry", "health_check"],
    ),
    AI22989Check(
        clause_id="7.5",
        clause_ref="Resilience (recovery from failures)",
        normative_text=(
            "Resilience: ability of an AI system to recover from an adverse event (failures, "
            "attacks, infrastructure issues) and continue providing its intended service. "
            "Relates to recovery time objectives and graceful degradation."
        ),
        category="TRUSTWORTHINESS", weight=2,
        search_terms=["resilience", "recovery", "fault_tolerance", "graceful_degradation",
                      "redundancy", "backup", "failover"],
    ),
    AI22989Check(
        clause_id="7.6",
        clause_ref="Transparency (process, data, model transparency)",
        normative_text=(
            "Transparency: property of an AI system where information about the AI system "
            "and its outputs is accessible to stakeholders. "
            "Includes: transparency of process (how system was designed/developed), "
            "data transparency (what data was used), model transparency."
        ),
        category="TRUSTWORTHINESS", weight=4,
        search_terms=["transparency", "model_card", "datasheet", "documentation",
                      "README", "explainability", "interpretability"],
    ),
    AI22989Check(
        clause_id="7.7",
        clause_ref="Accountability (responsibility traceable to persons/organisations)",
        normative_text=(
            "Accountability: extent to which actors are responsible for AI systems and their impacts. "
            "Implies that AI decisions and processes are traceable and attributable to "
            "responsible persons or organisations."
        ),
        category="TRUSTWORTHINESS", weight=3,
        search_terms=["accountability", "audit_trail", "logging", "traceability",
                      "responsible", "owner", "CODEOWNERS"],
    ),
    AI22989Check(
        clause_id="7.8",
        clause_ref="Explainability (reasons for outputs provided to stakeholders)",
        normative_text=(
            "Explainability: degree to which information about an AI system and its outputs "
            "is provided to and understood by stakeholders. "
            "Includes functional (what does it do) and operational (why this output) explanations."
        ),
        category="TRUSTWORTHINESS", weight=3,
        search_terms=["explainability", "xai", "shap", "lime", "attribution",
                      "explain", "interpretability", "feature_importance"],
    ),
    AI22989Check(
        clause_id="7.9",
        clause_ref="Fairness (no unjustified discriminatory treatment)",
        normative_text=(
            "Fairness: property of an AI system treating individuals or groups in an equitable way, "
            "without unlawful discrimination based on protected characteristics. "
            "Includes bias detection, demographic parity, equalised odds."
        ),
        category="TRUSTWORTHINESS", weight=4,
        search_terms=["fairness", "bias", "demographic_parity", "equalized_odds",
                      "discrimination", "equity", "balanced", "debiasing"],
    ),
    AI22989Check(
        clause_id="7.10",
        clause_ref="Safety (freedom from unacceptable risk)",
        normative_text=(
            "Safety: condition of an AI system when risk of harm is reduced to an acceptable level. "
            "Safety analysis: identification of potential harms and their causes, "
            "likelihood and severity assessment, and risk mitigation measures."
        ),
        category="TRUSTWORTHINESS", weight=4,
        search_terms=["safety", "harm", "risk", "mitigation", "safe",
                      "guardrail", "safe_output", "content_filter"],
    ),
    AI22989Check(
        clause_id="7.11",
        clause_ref="Privacy (protecting personal data used in AI)",
        normative_text=(
            "Privacy: ability to ensure that personal data used by an AI system is protected "
            "in accordance with applicable requirements. Includes: data minimisation, "
            "purpose limitation, access control, anonymisation/pseudonymisation."
        ),
        category="TRUSTWORTHINESS", weight=3,
        search_terms=["privacy", "pii", "gdpr", "personal_data", "anonymization",
                      "pseudonymization", "data_protection", "access_control"],
    ),
    AI22989Check(
        clause_id="7.12",
        clause_ref="Security (resistance to malicious attacks on AI system)",
        normative_text=(
            "Security: protection of the AI system from malicious attacks. "
            "AI-specific attacks: data poisoning (corrupting training data), adversarial examples "
            "(inputs crafted to fool the model), model stealing, model inversion. "
            "Requires assessment of AI-specific threat landscape."
        ),
        category="TRUSTWORTHINESS", weight=4,
        search_terms=["security", "adversarial", "data_poisoning", "model_stealing",
                      "threat", "vulnerability", "authentication", "encryption"],
    ),
]


def scan_22989(root: Path, idx: IndexStoreAdapter) -> list[AI22989Check]:
    """Scan for ISO/IEC 22989:2022 AI concept implementation evidence."""
    for check in AI_CHECKS:
        hits: set[str] = set()
        match_count = 0

        for term in check.search_terms:
            try:
                results = idx.search_code(term, limit=5)
                for r in results:
                    if r.path and not any(x in r.path for x in
                                          ("node_modules", ".git", "vendor", "__pycache__")):
                        hits.add(r.path)
                        match_count += 1
            except Exception:
                pass

        check.evidence_files = sorted(list(hits))[:5]
        check.found = len(check.evidence_files) > 0

        ratio = match_count / max(len(check.search_terms), 1)
        if ratio >= 0.5:
            check.confidence = "HIGH"
        elif match_count >= 2:
            check.confidence = "MEDIUM"
        elif match_count >= 1:
            check.confidence = "LOW"

    return AI_CHECKS


def calculate_score(checks: list[AI22989Check]) -> tuple[int, str, str]:
    total_weight = sum(c.weight for c in checks)
    achieved = sum(
        c.weight * (1.0 if c.confidence == "HIGH" else 0.6 if c.confidence == "MEDIUM" else 0.3 if c.confidence == "LOW" else 0)
        for c in checks
    )
    score = int((achieved / total_weight) * 100) if total_weight else 0

    if score >= 75:
        grade, status = "A  (Trustworthy AI — Strong ISO 22989 Coverage)", "🟢 HIGH — Trustworthiness properties well-covered"
    elif score >= 50:
        grade, status = "B  (Partial Conformance)", "🟡 PARTIAL — Core AI concepts present, trustworthiness gaps"
    elif score >= 25:
        grade, status = "C  (Initial)", "🟠 LOW — Basic AI implementation, missing trust properties"
    else:
        grade, status = "F  (Non-Conformant)", "🔴 CRITICAL — No evidence of AI trustworthiness properties"
    return score, grade, status


def print_report(project: str, root: Path, checks: list[AI22989Check],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    score, grade, status = calculate_score(checks)
    conf_icon = {"HIGH": "✅", "MEDIUM": "🟡", "LOW": "⚠️", "NONE": "❌"}
    found_count = sum(1 for c in checks if c.found)

    by_cat: dict[str, list[AI22989Check]] = {}
    for c in checks:
        by_cat.setdefault(c.category, []).append(c)

    cat_titles = {
        "ECOSYSTEM": "§3 AI Ecosystem (AI system / AI application / AI workflow)",
        "LIFECYCLE": "§4 AI System Life Cycle (phases / roles)",
        "LAYERS": "§5 Functional Layers (hardware / data / model / application)",
        "ENGINEERING": "§6 AI System Engineering (approach / task types / ML)",
        "TRUSTWORTHINESS": "§7 Trustworthiness (accuracy / robustness / transparency / fairness / safety / security)",
    }

    lines = [
        f"# 🔬 ISO/IEC 22989:2022 AI Concepts Audit — {project}",
        f"> `{root}` · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 Conformance Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **ISO 22989 Score** | **{score} / 100** |",
        f"| **Grade** | **{grade}** |",
        f"| **Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Elements with Evidence | {found_count} / {len(checks)} |",
        "",
        "> **Standard**: ISO/IEC 22989:2022 — Information technology — Artificial intelligence — AI concepts and terminology.",
        "> **Focus**: AI ecosystem (§3), life cycle (§4), functional layers (§5), engineering (§6), trustworthiness properties (§7).",
        "",
    ]

    for cat, cat_checks in by_cat.items():
        title = cat_titles.get(cat, cat)
        lines += [
            f"## 🔍 {title}",
            "",
            "| Clause | Concept | Confidence | Evidence |",
            "|---|---|---|---|",
        ]
        for c in cat_checks:
            icon = conf_icon[c.confidence]
            ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2]) if c.evidence_files else "—"
            lines.append(f"| `{c.clause_id}` | {c.clause_ref} | {icon} {c.confidence} | {ev} |")
        lines.append("")

    gaps = [c for c in checks if c.confidence in ("NONE", "LOW")]
    if gaps:
        lines += ["## ⚠️ Missing or Weak Trustworthiness Evidence", ""]
        for g in gaps:
            lines.append(f"- **{g.clause_id}** {g.clause_ref} — {g.normative_text[:100]}…")
        lines.append("")

    lines += [
        "## 🛠 ISO 22989:2022 Alignment Recommendations",
        "",
        "### §7 Trustworthiness Properties",
        "- **7.2 Accuracy**: Define task-appropriate metrics (WER/CER for ASR, MOS for TTS, F1 for classification)",
        "- **7.6 Transparency**: Publish model card (intended use, training data, known limitations, performance on benchmarks)",
        "- **7.8 Explainability**: Document why outputs are produced (feature attribution, decision criteria)",
        "- **7.9 Fairness**: Audit training data for demographic representation; evaluate bias",
        "- **7.10 Safety**: Identify potential harms (misuse, inappropriate outputs); document mitigations",
        "- **7.12 Security**: Assess AI-specific threats (data poisoning, adversarial inputs, model stealing)",
        "",
        "### §4 Life Cycle",
        "- Document AI system life cycle phases and criteria for each transition",
        "- Define AI system roles (who is the provider, producer, customer, subject)",
        "",
        "---",
        f"*ISO/IEC 22989:2022 AI Concepts Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 78
    print(f"\n{SEP}")
    print(f"  ISO/IEC 22989:2022 AI CONCEPTS AUDIT: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  Conformance Score           : {score} / 100")
    print(f"  Grade                       : {grade}")
    print(f"  Elements with Evidence      : {found_count} / {len(checks)}")
    print(f"  Audit Duration              : {elapsed:.3f}s")
    print(f"  Report                      : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 iso_22989_ai_concepts_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name
    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_22989_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    checks = scan_22989(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, checks, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
