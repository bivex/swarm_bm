#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ISO/IEC 23894:2023 — AI Risk Management Guidance Auditor                    ║
║                                                                               ║
║  Based on normative structure of ISO/IEC 23894:2023 (guidance on AI risk):   ║
║  This standard provides guidance on how organizations developing, providing,  ║
║  deploying, or using products, systems and services that use AI can manage    ║
║  risk specifically associated with AI. It is structured on the framework of   ║
║  ISO 31000:2018 risk management.                                              ║
║                                                                               ║
║  Clause 5: Principles (aligned with ISO 31000 §4)                            ║
║    Integrated, structured and comprehensive, customized, inclusive,           ║
║    dynamic, best available information, human and cultural factors,           ║
║    continual improvement                                                      ║
║  Clause 6: Framework (aligned with ISO 31000 §5)                             ║
║    6.2 Leadership and commitment / 6.3 Integration / 6.4 Design              ║
║    6.5 Implementation / 6.6 Evaluation / 6.7 Improvement                     ║
║  Clause 7: Process (aligned with ISO 31000 §6)                               ║
║    7.2 Communication and consultation                                         ║
║    7.3 Scope, context and criteria                                            ║
║    7.4 Risk assessment (identification/analysis/evaluation)                   ║
║    7.5 Risk treatment                                                         ║
║    7.6 Monitoring and review                                                  ║
║    7.7 Recording and reporting                                                ║
║  AI-specific extensions:                                                      ║
║    - AI system risk sources (intended use, misuse, data quality, bias,        ║
║      opacity, security, safety, human-machine interaction)                    ║
║    - Risk treatment options specific to AI (human oversight, explainability,  ║
║      monitoring, deactivation mechanisms)                                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/ai/iso_23894_ai_risk_audit.py /path/to/project [ProjectName]
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
class AIRiskCheck:
    """A normative element from ISO/IEC 23894:2023 AI Risk Management."""
    clause_id: str
    clause_ref: str
    normative_text: str
    category: str   # PRINCIPLES / FRAMEWORK / PROCESS / AI_SPECIFIC_RISK / RISK_TREATMENT
    weight: int
    search_terms: list[str]
    evidence_files: list[str] = field(default_factory=list)
    found: bool = False
    confidence: str = "NONE"


RISK_CHECKS: list[AIRiskCheck] = [

    # ── Clause 5: Principles ─────────────────────────────────────────────────
    AIRiskCheck(
        clause_id="5",
        clause_ref="AI Risk Management Principles (8 principles from ISO 31000)",
        normative_text=(
            "AI risk management SHALL be: integrated (part of all org activities); "
            "structured and comprehensive; customized to AI context; inclusive (stakeholders involved); "
            "dynamic (adapt to changes); based on best available information; "
            "account for human and cultural factors; support continual improvement."
        ),
        category="PRINCIPLES", weight=3,
        search_terms=["risk_management", "risk_policy", "risk_framework",
                      "risk_governance", "risk_principles"],
    ),

    # ── Clause 6: Framework ───────────────────────────────────────────────────
    AIRiskCheck(
        clause_id="6.2",
        clause_ref="Leadership commitment to AI risk management",
        normative_text=(
            "Top management SHALL demonstrate commitment to AI risk management by: "
            "ensuring integration of risk management into all organization activities; "
            "demonstrating leadership and commitment for risk management process; "
            "allocating resources required for risk management."
        ),
        category="FRAMEWORK", weight=3,
        search_terms=["risk_owner", "risk_responsible", "risk_committee",
                      "governance", "executive", "management_commitment"],
    ),
    AIRiskCheck(
        clause_id="6.4",
        clause_ref="AI risk management framework design",
        normative_text=(
            "Risk management framework design SHALL include: understanding organization and context "
            "(both internal/external); articulating risk management commitment (policy); "
            "assigning organizational roles; allocating resources; establishing communication."
        ),
        category="FRAMEWORK", weight=3,
        search_terms=["risk_framework", "risk_policy", "risk_appetite",
                      "risk_criteria", "risk_register", "risk_documentation"],
    ),

    # ── Clause 7.3: Scope, context and criteria ───────────────────────────────
    AIRiskCheck(
        clause_id="7.3",
        clause_ref="AI risk scope, context and criteria defined",
        normative_text=(
            "The organization SHALL define the scope for the AI risk management process. "
            "Context includes: internal context (organizational capabilities, AI use scope); "
            "external context (regulatory environment, societal context, affected parties). "
            "Risk criteria SHALL define: acceptable vs non-acceptable risk levels; "
            "criteria for consequence assessment; criteria for likelihood assessment."
        ),
        category="PROCESS", weight=4,
        search_terms=["risk_criteria", "risk_scope", "risk_context",
                      "acceptable_risk", "risk_appetite", "risk_threshold"],
    ),

    # ── Clause 7.4: Risk Assessment ──────────────────────────────────────────
    AIRiskCheck(
        clause_id="7.4.1",
        clause_ref="AI risk identification (sources of AI risk)",
        normative_text=(
            "AI risk sources SHALL be identified. AI-specific risk sources include: "
            "(a) intended use and foreseeable misuse; (b) performance risks (accuracy, robustness); "
            "(c) data quality and bias risks; (d) opacity/explainability risks; "
            "(e) security threats (data poisoning, model stealing, adversarial attacks); "
            "(f) safety risks; (g) privacy risks; (h) human-machine interaction risks; "
            "(i) societal risks; (j) market concentration risks."
        ),
        category="PROCESS", weight=4,
        search_terms=["risk_identification", "risk_source", "risk_register",
                      "threat", "hazard", "failure_mode", "FMEA"],
    ),
    AIRiskCheck(
        clause_id="7.4.2",
        clause_ref="AI risk analysis (consequence × likelihood = risk level)",
        normative_text=(
            "Risk analysis SHALL determine: consequences of each risk if it were to occur; "
            "likelihood of the risk occurring; the level of risk (combining consequence and likelihood). "
            "For AI systems, analysis should consider: reversibility of harm; "
            "breadth of impact (number of people affected); severity of harm; "
            "vulnerability of affected individuals."
        ),
        category="PROCESS", weight=4,
        search_terms=["risk_analysis", "consequence", "likelihood", "severity",
                      "risk_level", "risk_matrix", "impact", "probability"],
    ),
    AIRiskCheck(
        clause_id="7.4.3",
        clause_ref="AI risk evaluation (compare against criteria, prioritise)",
        normative_text=(
            "Risk evaluation SHALL compare results of risk analysis with risk criteria "
            "to determine whether risk requires treatment and to prioritise risks. "
            "Outputs of evaluation: list of prioritised risks and recommended treatment options."
        ),
        category="PROCESS", weight=3,
        search_terms=["risk_evaluation", "risk_priority", "risk_ranking",
                      "risk_assessment", "treatment_priority"],
    ),

    # ── Clause 7.5: Risk Treatment ────────────────────────────────────────────
    AIRiskCheck(
        clause_id="7.5",
        clause_ref="AI risk treatment plan (select and implement options)",
        normative_text=(
            "Risk treatment options for AI systems: (a) avoid the risk by not pursuing the AI system; "
            "(b) take or increase the risk to pursue an opportunity; (c) remove the risk source; "
            "(d) change the likelihood (data quality improvement, security controls); "
            "(e) change the consequences (human oversight, output filtering, sandboxing); "
            "(f) share the risk (contractual allocation); (g) retain by informed decision."
        ),
        category="PROCESS", weight=4,
        search_terms=["risk_treatment", "mitigation", "control", "safeguard",
                      "risk_response", "risk_mitigation", "countermeasure"],
    ),

    # ── Clause 7.6: Monitoring and Review ────────────────────────────────────
    AIRiskCheck(
        clause_id="7.6",
        clause_ref="AI risk monitoring and review (ongoing, planned intervals)",
        normative_text=(
            "Risk monitoring and review SHALL be planned and conducted on ongoing basis "
            "and at planned intervals. For AI systems, monitoring shall specifically include: "
            "monitoring of AI system performance for degradation (data drift/concept drift); "
            "monitoring for new risks arising from changes in AI system or context; "
            "monitoring effectiveness of implemented risk treatments."
        ),
        category="PROCESS", weight=4,
        search_terms=["monitoring", "drift", "performance_monitoring",
                      "risk_monitoring", "alerting", "review", "audit"],
    ),

    # ── Clause 7.7: Recording and Reporting ──────────────────────────────────
    AIRiskCheck(
        clause_id="7.7",
        clause_ref="AI risk recording and reporting (documented information)",
        normative_text=(
            "Risk process activities and results SHALL be documented and reported at "
            "appropriate levels within the organization. "
            "AI risk documentation should include: risk register; risk assessment results; "
            "risk treatment plan; risk monitoring results; audit results."
        ),
        category="PROCESS", weight=3,
        search_terms=["risk_register", "risk_log", "risk_report", "documentation",
                      "audit_trail", "incident_log", "risk_record"],
    ),

    # ── AI-Specific Risk Sources ──────────────────────────────────────────────
    AIRiskCheck(
        clause_id="ai-risk.data",
        clause_ref="Data quality and bias risks (AI-specific)",
        normative_text=(
            "AI-specific risk: data quality and bias risks. "
            "Training data that is incomplete, unrepresentative, or contains biases "
            "can lead to AI systems that produce unfair, inaccurate, or unsafe outputs. "
            "Risk treatment: data quality assessment, bias testing, diverse data sourcing."
        ),
        category="AI_SPECIFIC_RISK", weight=4,
        search_terms=["data_quality", "bias", "fairness", "training_data",
                      "data_validation", "bias_detection", "imbalance"],
    ),
    AIRiskCheck(
        clause_id="ai-risk.opacity",
        clause_ref="Opacity and explainability risks (AI-specific)",
        normative_text=(
            "AI-specific risk: opacity risks. "
            "AI systems, especially deep learning models, can be opaque (black-box). "
            "Opacity prevents stakeholders from understanding why a decision was made, "
            "hinders error detection, and complicates accountability. "
            "Risk treatment: explainability methods (SHAP, LIME), model cards."
        ),
        category="AI_SPECIFIC_RISK", weight=3,
        search_terms=["explainability", "interpretability", "xai", "shap", "lime",
                      "black_box", "transparency", "explain"],
    ),
    AIRiskCheck(
        clause_id="ai-risk.security",
        clause_ref="AI security threats (data poisoning, adversarial, model stealing)",
        normative_text=(
            "AI-specific security risks: data poisoning (attacker corrupts training data); "
            "adversarial examples (inputs crafted to fool AI system); "
            "model stealing (attacker recreates proprietary model by querying it); "
            "model inversion (attacker extracts training data from model). "
            "Risk treatment: input validation, adversarial training, API rate limiting."
        ),
        category="AI_SPECIFIC_RISK", weight=4,
        search_terms=["security", "adversarial", "data_poisoning", "model_stealing",
                      "input_validation", "rate_limit", "authentication"],
    ),
    AIRiskCheck(
        clause_id="ai-risk.misuse",
        clause_ref="Intended use and foreseeable misuse risks",
        normative_text=(
            "AI systems carry risks from both intended use and foreseeable misuse. "
            "Organizations shall identify foreseeable misuse scenarios and assess their risks. "
            "Risk treatment: use restrictions, output filtering, user authentication, "
            "human oversight for high-risk decisions."
        ),
        category="AI_SPECIFIC_RISK", weight=3,
        search_terms=["intended_use", "misuse", "use_case", "prohibited_use",
                      "content_filter", "human_oversight", "terms_of_use"],
    ),
    AIRiskCheck(
        clause_id="ai-risk.performance",
        clause_ref="AI performance degradation risks (drift, distribution shift)",
        normative_text=(
            "AI systems can experience performance degradation over time due to: "
            "data drift (production data distribution diverges from training data); "
            "concept drift (relationship between inputs and outputs changes); "
            "infrastructure changes affecting inference performance. "
            "Risk treatment: continuous monitoring, retraining pipelines, performance alerting."
        ),
        category="AI_SPECIFIC_RISK", weight=4,
        search_terms=["drift", "data_drift", "concept_drift", "performance_degradation",
                      "monitoring", "retraining", "alerting", "benchmark"],
    ),

    # ── Risk Treatment Measures for AI ───────────────────────────────────────
    AIRiskCheck(
        clause_id="rt.oversight",
        clause_ref="Human oversight mechanisms (risk treatment)",
        normative_text=(
            "Human oversight is a key risk treatment for AI systems, especially for high-risk decisions. "
            "Should include: mechanisms to flag uncertain AI outputs for human review; "
            "ability to override AI decisions; logging of AI-assisted decisions; "
            "clear communication to users when AI is involved in a decision."
        ),
        category="RISK_TREATMENT", weight=4,
        search_terms=["human_oversight", "human_review", "override", "fallback",
                      "escalation", "human_in_loop", "confidence_threshold"],
    ),
    AIRiskCheck(
        clause_id="rt.monitoring",
        clause_ref="Ongoing monitoring (risk treatment — detect new/changed risks)",
        normative_text=(
            "Ongoing monitoring is a fundamental risk treatment for AI systems. "
            "Should monitor: AI system performance metrics; error rates and failure modes; "
            "data drift indicators; security events; user feedback and complaints; "
            "regulatory and legal changes affecting the AI system."
        ),
        category="RISK_TREATMENT", weight=4,
        search_terms=["monitoring", "logging", "alerting", "metrics", "dashboard",
                      "error_rate", "performance", "telemetry", "observability"],
    ),
    AIRiskCheck(
        clause_id="rt.deactivation",
        clause_ref="Deactivation mechanism (kill switch / graceful shutdown)",
        normative_text=(
            "AI systems should have the ability to be deactivated or shut down gracefully "
            "when unacceptable risks are detected. This includes: mechanisms to pause or stop "
            "AI system operations; ability to roll back to a previous model version; "
            "incident response procedures for AI system failures."
        ),
        category="RISK_TREATMENT", weight=3,
        search_terms=["shutdown", "rollback", "kill_switch", "feature_flag",
                      "incident_response", "circuit_breaker", "failover"],
    ),
]


def scan_23894(root: Path, idx: IndexStoreAdapter) -> list[AIRiskCheck]:
    """Scan for ISO/IEC 23894:2023 AI risk management evidence."""
    for check in RISK_CHECKS:
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

    return RISK_CHECKS


def calculate_score(checks: list[AIRiskCheck]) -> tuple[int, str, str]:
    total_weight = sum(c.weight for c in checks)
    achieved = sum(
        c.weight * (1.0 if c.confidence == "HIGH" else 0.6 if c.confidence == "MEDIUM" else 0.3 if c.confidence == "LOW" else 0)
        for c in checks
    )
    score = int((achieved / total_weight) * 100) if total_weight else 0

    if score >= 75:
        grade, status = "A  (Systematic AI Risk Management)", "🟢 HIGH — AI risk management practices well-evidenced"
    elif score >= 50:
        grade, status = "B  (Partial Risk Management)", "🟡 PARTIAL — Some risk controls present, gaps in process"
    elif score >= 25:
        grade, status = "C  (Ad-hoc Risk Awareness)", "🟠 LOW — Informal risk management, no systematic process"
    else:
        grade, status = "F  (No AI Risk Management)", "🔴 CRITICAL — No evidence of AI risk management process"
    return score, grade, status


def print_report(project: str, root: Path, checks: list[AIRiskCheck],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    score, grade, status = calculate_score(checks)
    conf_icon = {"HIGH": "✅", "MEDIUM": "🟡", "LOW": "⚠️", "NONE": "❌"}
    found_count = sum(1 for c in checks if c.found)

    by_cat: dict[str, list[AIRiskCheck]] = {}
    for c in checks:
        by_cat.setdefault(c.category, []).append(c)

    cat_titles = {
        "PRINCIPLES": "§5 Risk Management Principles (ISO 31000 alignment)",
        "FRAMEWORK": "§6 Risk Management Framework (leadership / design / implementation)",
        "PROCESS": "§7 Risk Management Process (scope → identify → analyse → evaluate → treat → monitor → record)",
        "AI_SPECIFIC_RISK": "AI-Specific Risk Sources (data quality, opacity, security, misuse, drift)",
        "RISK_TREATMENT": "Risk Treatment Measures (human oversight / monitoring / deactivation)",
    }

    lines = [
        f"# ⚠️ ISO/IEC 23894:2023 AI Risk Management Audit — {project}",
        f"> `{root}` · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 AI Risk Management Conformance Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **ISO 23894 Risk Score** | **{score} / 100** |",
        f"| **Grade** | **{grade}** |",
        f"| **Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Risk Checks with Evidence | {found_count} / {len(checks)} |",
        "",
        "> **Standard**: ISO/IEC 23894:2023 — Information technology — Artificial intelligence — Guidance on risk management.",
        "> **Framework basis**: ISO 31000:2018 risk management principles and process, extended for AI-specific risks.",
        "",
    ]

    for cat, cat_checks in by_cat.items():
        title = cat_titles.get(cat, cat)
        lines += [
            f"## 🔍 {title}",
            "",
            "| Clause | Risk Element | Confidence | Evidence |",
            "|---|---|---|---|",
        ]
        for c in cat_checks:
            icon = conf_icon[c.confidence]
            ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2]) if c.evidence_files else "—"
            lines.append(f"| `{c.clause_id}` | {c.clause_ref} | {icon} {c.confidence} | {ev} |")
        lines.append("")

    gaps = [c for c in checks if c.confidence in ("NONE", "LOW")]
    if gaps:
        lines += ["## ⚠️ High-Priority Risk Management Gaps", ""]
        for g in gaps:
            lines.append(f"- **{g.clause_id}** {g.clause_ref} (weight={g.weight})")
        lines.append("")

    lines += [
        "## 🛠 AI Risk Management Roadmap (ISO 23894:2023)",
        "",
        "### Phase 1 — Foundation (§6 Framework)",
        "- Establish AI risk policy and risk criteria (acceptable vs non-acceptable risk levels)",
        "- Assign AI risk owner role; integrate risk management into SDLC",
        "",
        "### Phase 2 — Risk Assessment (§7.3–7.4)",
        "- Define risk scope and context for each AI system",
        "- Identify AI-specific risk sources: data quality, bias, opacity, security threats, drift",
        "- Perform risk analysis: consequence × likelihood matrix",
        "- Produce risk register with prioritised risks",
        "",
        "### Phase 3 — Risk Treatment (§7.5)",
        "- **Data quality**: implement data validation and bias testing pipelines",
        "- **Security**: address data poisoning, adversarial examples, model stealing",
        "- **Human oversight**: implement confidence thresholds and escalation mechanisms",
        "- **Deactivation**: create rollback procedures and circuit breakers",
        "",
        "### Phase 4 — Monitoring (§7.6)",
        "- Implement continuous monitoring for performance degradation, data drift, errors",
        "- Set up alerting for risk indicators",
        "- Conduct periodic risk reviews and update risk register",
        "",
        "---",
        f"*ISO/IEC 23894:2023 AI Risk Management Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 78
    print(f"\n{SEP}")
    print(f"  ISO/IEC 23894:2023 AI RISK MANAGEMENT AUDIT: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  Risk Conformance Score      : {score} / 100")
    print(f"  Grade                       : {grade}")
    print(f"  Risk Checks with Evidence   : {found_count} / {len(checks)}")
    print(f"  Audit Duration              : {elapsed:.3f}s")
    print(f"  Report                      : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 iso_23894_ai_risk_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name
    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_23894_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    checks = scan_23894(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, checks, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
