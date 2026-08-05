#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ISO/IEC 42001:2023 — Artificial Intelligence Management System Auditor      ║
║                                                                               ║
║  Based on normative requirements of ISO/IEC 42001:2023 (AIMS):               ║
║  Clause 4: Context of the organization (4.1–4.4)                             ║
║  Clause 5: Leadership (5.1–5.3) — AI Policy, Roles                           ║
║  Clause 6: Planning (6.1–6.3) — Risk Assessment, Impact Assessment,          ║
║            Statement of Applicability, AI Objectives                          ║
║  Clause 7: Support (7.1–7.5) — Resources, Competence, Documented Info        ║
║  Clause 8: Operation (8.1–8.4) — Risk Treatment, Operational Controls        ║
║  Clause 9: Performance Evaluation (9.1–9.3) — Internal Audit, Mgmt Review    ║
║  Clause 10: Improvement (10.1–10.2) — Continual Improvement, NCR             ║
║  Annex A (normative): Controls A.2–A.10 (Table A.1)                          ║
║    A.2 AI Policy · A.3 Internal Org · A.4 Resources · A.5 Impact Assessment  ║
║    A.6 AI System Life Cycle · A.7 Data · A.8 Stakeholder Info                ║
║    A.9 Use of AI · A.10 Third-party Relationships                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/ai/iso_42001_ai_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import json
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
class AIMS42001Check:
    """A normative requirement from ISO/IEC 42001:2023."""
    clause_id: str      # e.g. "4.1", "A.2.2"
    clause_ref: str     # Short title
    normative_req: str  # Exact normative language from the standard (shall/should)
    domain: str         # CONTEXT / LEADERSHIP / PLANNING / SUPPORT / OPERATION / EVALUATION / IMPROVEMENT / ANNEX_A
    weight: int         # Score weight (1–4 based on SHALL vs SHOULD)
    search_terms: list[str]  # Terms from normative text used for BM25 search
    evidence_files: list[str] = field(default_factory=list)
    found: bool = False
    confidence: str = "NONE"  # NONE / LOW / MEDIUM / HIGH


# ─── Normative checks mapped directly to ISO/IEC 42001:2023 clauses ─────────
AIMS_CHECKS: list[AIMS42001Check] = [

    # ── Clause 4: Context ────────────────────────────────────────────────────
    AIMS42001Check(
        clause_id="4.1",
        clause_ref="Understanding organization and context",
        normative_req=(
            "The organization SHALL determine external and internal issues relevant to its purpose "
            "and that affect its ability to achieve the intended result(s) of its AIMS. "
            "SHALL determine its roles w.r.t. AI systems (provider/producer/customer/partner/subject)."
        ),
        domain="CONTEXT", weight=3,
        search_terms=["ai_context", "ai_scope", "aims_scope", "ai_role", "intended_purpose",
                      "ai_system", "context", "scope"],
    ),
    AIMS42001Check(
        clause_id="4.2",
        clause_ref="Needs and expectations of interested parties",
        normative_req=(
            "The organization SHALL determine interested parties relevant to the AIMS, "
            "their relevant requirements, and which requirements will be addressed through the AIMS."
        ),
        domain="CONTEXT", weight=2,
        search_terms=["interested_parties", "stakeholders", "requirements", "regulatory", "legal_requirements"],
    ),
    AIMS42001Check(
        clause_id="4.3",
        clause_ref="Determining scope of AIMS",
        normative_req=(
            "The organization SHALL determine the boundaries and applicability of the AIMS. "
            "The scope SHALL be available as documented information."
        ),
        domain="CONTEXT", weight=3,
        search_terms=["scope", "boundary", "applicability", "aims", "ai_management"],
    ),
    AIMS42001Check(
        clause_id="4.4",
        clause_ref="Establishing the AIMS",
        normative_req=(
            "The organization SHALL establish, implement, maintain, continually improve and document "
            "an AI management system, including the processes needed and their interactions."
        ),
        domain="CONTEXT", weight=4,
        search_terms=["management_system", "process", "ai_policy", "AIMS", "governance"],
    ),

    # ── Clause 5: Leadership ─────────────────────────────────────────────────
    AIMS42001Check(
        clause_id="5.2",
        clause_ref="AI policy",
        normative_req=(
            "Top management SHALL establish an AI policy that: (a) is appropriate to purpose, "
            "(b) provides framework for AI objectives, (c) includes commitment to meet applicable "
            "requirements, (d) includes commitment to continual improvement. "
            "The AI policy SHALL be available as documented information, communicated within the organization."
        ),
        domain="LEADERSHIP", weight=4,
        search_terms=["ai_policy", "policy", "ai_principles", "responsible_ai", "ethics",
                      "AI Policy", "ai_governance_policy"],
    ),
    AIMS42001Check(
        clause_id="5.3",
        clause_ref="Roles, responsibilities and authorities",
        normative_req=(
            "Top management SHALL assign the responsibility and authority for: "
            "(a) ensuring the AIMS conforms to requirements of this document; "
            "(b) reporting on performance of the AIMS to top management. "
            "Control A.3.2: Roles and responsibilities for AI SHALL be defined and allocated."
        ),
        domain="LEADERSHIP", weight=3,
        search_terms=["ai_role", "responsibility", "authority", "accountable", "RACI",
                      "ai_officer", "ai_governance"],
    ),

    # ── Clause 6: Planning ───────────────────────────────────────────────────
    AIMS42001Check(
        clause_id="6.1.1",
        clause_ref="AI risk criteria",
        normative_req=(
            "The organization SHALL establish and maintain AI risk criteria that support: "
            "distinguishing acceptable from non-acceptable risks; performing AI risk assessments; "
            "conducting AI risk treatment; assessing AI risk impacts. "
            "The organization SHALL retain documented information on actions taken to identify risks."
        ),
        domain="PLANNING", weight=4,
        search_terms=["risk_criteria", "risk_assessment", "risk_appetite", "acceptable_risk",
                      "risk_level", "risk", "ai_risk"],
    ),
    AIMS42001Check(
        clause_id="6.1.2",
        clause_ref="AI risk assessment process",
        normative_req=(
            "The organization SHALL define and establish an AI risk assessment process that: "
            "(a) is informed by and aligned with AI policy and AI objectives; "
            "(b) repeated risk assessments produce consistent, valid, comparable results; "
            "(c) identifies risks; (d) analyses the AI risks (consequences, likelihood, levels); "
            "(e) evaluates AI risks (compare with criteria, prioritise for treatment). "
            "SHALL retain documented information about the AI risk assessment process."
        ),
        domain="PLANNING", weight=4,
        search_terms=["risk_assessment", "consequence", "likelihood", "risk_level", "risk_evaluation",
                      "ai_risk_assessment", "risk_analysis"],
    ),
    AIMS42001Check(
        clause_id="6.1.3",
        clause_ref="AI risk treatment + Statement of Applicability",
        normative_req=(
            "The organization SHALL define an AI risk treatment process. "
            "SHALL produce a Statement of Applicability (SoA) containing the necessary controls and "
            "justification for inclusion/exclusion of Annex A controls. "
            "SHALL formulate an AI risk treatment plan. SHALL retain documented information."
        ),
        domain="PLANNING", weight=4,
        search_terms=["risk_treatment", "statement_of_applicability", "soa", "annex_a",
                      "control", "risk_treatment_plan", "residual_risk"],
    ),
    AIMS42001Check(
        clause_id="6.1.4",
        clause_ref="AI system impact assessment (AISIA)",
        normative_req=(
            "The organization SHALL define a process for assessing the potential consequences for "
            "individuals or groups of individuals, or both, and societies that can result from "
            "the development, provision or use of AI systems. "
            "The result of the AI system impact assessment SHALL be documented."
        ),
        domain="PLANNING", weight=4,
        search_terms=["impact_assessment", "ai_impact", "societal_impact", "individual_impact",
                      "impact", "harm", "bias_assessment", "fairness_assessment"],
    ),
    AIMS42001Check(
        clause_id="6.2",
        clause_ref="AI objectives (measurable, monitored, documented)",
        normative_req=(
            "The organization SHALL establish AI objectives at relevant functions and levels. "
            "AI objectives SHALL be: (a) consistent with AI policy; (b) measurable if practicable; "
            "(c) take into account applicable requirements; (d) monitored; (e) communicated; "
            "(f) updated as appropriate; (g) available as documented information."
        ),
        domain="PLANNING", weight=3,
        search_terms=["ai_objective", "kpi", "metric", "target", "measurable",
                      "ai_goals", "objective", "OKR"],
    ),

    # ── Clause 7: Support ────────────────────────────────────────────────────
    AIMS42001Check(
        clause_id="7.2",
        clause_ref="Competence",
        normative_req=(
            "The organization SHALL determine necessary competence of persons doing work affecting "
            "AI performance; ensure they are competent based on appropriate education, training or "
            "experience; where applicable, take actions to acquire competence. "
            "Appropriate documented information SHALL be available as evidence of competence."
        ),
        domain="SUPPORT", weight=2,
        search_terms=["competence", "training", "education", "expertise", "qualification",
                      "ai_training", "certification"],
    ),
    AIMS42001Check(
        clause_id="7.5",
        clause_ref="Documented information (version-controlled)",
        normative_req=(
            "The AIMS SHALL include documented information required by this document. "
            "Documented information shall be controlled to ensure: (a) available and suitable for use; "
            "(b) adequately protected. Control of changes (version control) is required."
        ),
        domain="SUPPORT", weight=3,
        search_terms=["documentation", "version_control", "changelog", "document_control",
                      "README", "CHANGELOG", "docs", "version"],
    ),

    # ── Clause 8: Operation ──────────────────────────────────────────────────
    AIMS42001Check(
        clause_id="8.1",
        clause_ref="Operational planning and control",
        normative_req=(
            "The organization SHALL plan, implement and control the processes needed to meet requirements "
            "and implement actions determined in Clause 6. "
            "SHALL implement controls from 6.1.3 related to the operation of the AIMS "
            "(AI system development and usage life cycle related controls). "
            "The effectiveness of controls SHALL be monitored."
        ),
        domain="OPERATION", weight=4,
        search_terms=["operational_control", "process", "lifecycle", "deployment", "monitoring",
                      "ci_cd", "pipeline", "release"],
    ),
    AIMS42001Check(
        clause_id="8.2",
        clause_ref="AI risk assessment (operational — repeated at planned intervals)",
        normative_req=(
            "The organization SHALL perform AI risk assessments in accordance with 6.1.2 "
            "at planned intervals or when significant changes are proposed or occur. "
            "SHALL retain documented information of the results of all AI risk assessments."
        ),
        domain="OPERATION", weight=3,
        search_terms=["risk_review", "risk_assessment", "security_audit", "vulnerability_scan",
                      "periodic_review", "change_management"],
    ),
    AIMS42001Check(
        clause_id="8.4",
        clause_ref="AI system impact assessment (operational)",
        normative_req=(
            "The organization SHALL perform AI system impact assessments according to 6.1.4 "
            "at planned intervals or when significant changes are proposed to occur. "
            "SHALL retain documented information of the results."
        ),
        domain="OPERATION", weight=3,
        search_terms=["impact_assessment", "bias_evaluation", "fairness_test", "model_card",
                      "system_card", "impact_review"],
    ),

    # ── Clause 9: Performance Evaluation ─────────────────────────────────────
    AIMS42001Check(
        clause_id="9.1",
        clause_ref="Monitoring, measurement, analysis and evaluation",
        normative_req=(
            "The organization SHALL determine what needs to be monitored and measured; "
            "the methods for monitoring and measurement; when monitoring shall be performed; "
            "when results shall be analysed and evaluated. "
            "Documented information SHALL be available as evidence of the results."
        ),
        domain="EVALUATION", weight=3,
        search_terms=["monitoring", "metrics", "evaluation", "measurement", "performance",
                      "logging", "observability", "dashboard"],
    ),
    AIMS42001Check(
        clause_id="9.2",
        clause_ref="Internal audit",
        normative_req=(
            "The organization SHALL conduct internal audits at planned intervals to provide information "
            "on whether the AIMS: (a) conforms to the organization's own requirements and this document; "
            "(b) is effectively implemented and maintained. "
            "Documented information SHALL be available as evidence of the audit programme and results."
        ),
        domain="EVALUATION", weight=3,
        search_terms=["audit", "internal_audit", "compliance_check", "conformity_assessment",
                      "review", "inspection"],
    ),
    AIMS42001Check(
        clause_id="9.3",
        clause_ref="Management review",
        normative_req=(
            "Top management SHALL review the AIMS at planned intervals. "
            "Review inputs SHALL include: status of previous actions; changes in issues/requirements; "
            "performance trends in nonconformities, monitoring results, audit results; "
            "opportunities for continual improvement. "
            "Results SHALL include decisions related to continual improvement."
        ),
        domain="EVALUATION", weight=2,
        search_terms=["management_review", "governance_review", "board_review",
                      "executive_review", "quarterly_review"],
    ),

    # ── Clause 10: Improvement ───────────────────────────────────────────────
    AIMS42001Check(
        clause_id="10.2",
        clause_ref="Nonconformity and corrective action",
        normative_req=(
            "When a nonconformity occurs, the organization SHALL: react to it; evaluate the need for "
            "action to eliminate cause(s) so it does not recur; implement any action needed; "
            "review effectiveness of corrective action taken; make changes to AIMS if necessary. "
            "SHALL retain documented information on the nature of nonconformities and corrective actions."
        ),
        domain="IMPROVEMENT", weight=3,
        search_terms=["nonconformity", "corrective_action", "issue_tracking", "bug", "incident",
                      "JIRA", "GitHub_issues", "defect"],
    ),

    # ── Annex A (Normative) Controls ─────────────────────────────────────────
    AIMS42001Check(
        clause_id="A.2.2",
        clause_ref="AI policy (documented)",
        normative_req=(
            "Control A.2.2: The organization SHALL document a policy for the development or use of AI systems. "
            "The AI policy should include: principles that guide all activities related to AI; "
            "processes for handling deviations and exceptions to policy (B.2.2)."
        ),
        domain="ANNEX_A", weight=4,
        search_terms=["policy", "ai_policy", "principles", "ethics", "responsible_ai",
                      "CODE_OF_CONDUCT", "ai_guidelines"],
    ),
    AIMS42001Check(
        clause_id="A.3.2",
        clause_ref="AI roles and responsibilities (defined and allocated)",
        normative_req=(
            "Control A.3.2: Roles and responsibilities for AI SHALL be defined and allocated "
            "according to the needs of the organization. Areas requiring defined roles include: "
            "risk management, AI system impact assessments, security, safety, privacy, development, "
            "performance, human oversight, supplier relationships, data quality management."
        ),
        domain="ANNEX_A", weight=3,
        search_terms=["owner", "maintainer", "responsible", "CODEOWNERS", "contributor",
                      "ai_owner", "model_owner", "data_owner"],
    ),
    AIMS42001Check(
        clause_id="A.4.2",
        clause_ref="Resource documentation (data, tooling, computing, human)",
        normative_req=(
            "Control A.4.2: The organization SHALL identify and document relevant resources "
            "required for the activities at given AI system life cycle stages. "
            "A.4.3 Data resources SHALL be documented (provenance, categories, quality, bias). "
            "A.4.4 Tooling resources (algorithms, models, tools). "
            "A.4.5 System and computing resources. A.4.6 Human resources and competences."
        ),
        domain="ANNEX_A", weight=3,
        search_terms=["resources", "requirements.txt", "dependencies", "model_card", "dataset",
                      "training_data", "compute", "hardware"],
    ),
    AIMS42001Check(
        clause_id="A.5.2",
        clause_ref="AI system impact assessment process (established)",
        normative_req=(
            "Control A.5.2: The organization SHALL establish a process to assess potential consequences "
            "for individuals or groups of individuals, or both, and societies. "
            "A.5.3: SHALL document the results and retain for a defined period. "
            "A.5.4: SHALL assess impacts on individuals (fairness, accountability, transparency, "
            "security and privacy, safety and health, financial consequences, accessibility, human rights). "
            "A.5.5: SHALL assess societal impacts."
        ),
        domain="ANNEX_A", weight=4,
        search_terms=["impact_assessment", "pia", "dpia", "fairness", "bias", "equity",
                      "explainability", "transparency", "human_rights"],
    ),
    AIMS42001Check(
        clause_id="A.6.2.3",
        clause_ref="AI system design and development documented",
        normative_req=(
            "Control A.6.2.3: The organization SHALL document the AI system design and development "
            "based on organizational objectives, documented requirements and specification criteria. "
            "Documentation should include: ML approach, learning algorithm, model type, training data, "
            "security threats, interface and outputs, interoperability."
        ),
        domain="ANNEX_A", weight=3,
        search_terms=["architecture", "model", "algorithm", "design", "specification",
                      "system_design", "model_architecture", "neural_network", "ml_model"],
    ),
    AIMS42001Check(
        clause_id="A.6.2.4",
        clause_ref="AI system verification and validation",
        normative_req=(
            "Control A.6.2.4: The organization SHALL define and document verification and validation "
            "measures for the AI system and specify criteria for their use. "
            "Should include: testing methodologies, selection of test data, release criteria, "
            "error rates, performance metrics."
        ),
        domain="ANNEX_A", weight=3,
        search_terms=["test", "validation", "verification", "benchmark", "evaluation",
                      "accuracy", "metrics", "test_data"],
    ),
    AIMS42001Check(
        clause_id="A.6.2.5",
        clause_ref="AI system deployment plan",
        normative_req=(
            "Control A.6.2.5: The organization SHALL document a deployment plan and ensure that "
            "appropriate requirements are met prior to deployment. "
            "Deployment plan should include release criteria, verification and validation measures passed, "
            "performance metrics met, management approvals."
        ),
        domain="ANNEX_A", weight=3,
        search_terms=["deployment", "release", "deploy", "docker", "kubernetes", "container",
                      "release_criteria", "production"],
    ),
    AIMS42001Check(
        clause_id="A.6.2.6",
        clause_ref="AI system operation and monitoring (including concept/data drift)",
        normative_req=(
            "Control A.6.2.6: The organization SHALL define and document the necessary elements for "
            "ongoing operation: system and performance monitoring, repairs, updates and support. "
            "B.6.2.6: Should monitor for data drift and concept drift; AI-specific security threats "
            "(data poisoning, model stealing, model inversion attacks) SHALL be identified."
        ),
        domain="ANNEX_A", weight=4,
        search_terms=["monitoring", "drift", "data_drift", "concept_drift", "performance_monitor",
                      "alerting", "observability", "telemetry", "logging"],
    ),
    AIMS42001Check(
        clause_id="A.6.2.7",
        clause_ref="AI system technical documentation",
        normative_req=(
            "Control A.6.2.7: The organization SHALL determine what AI system technical documentation "
            "is needed for each relevant category of interested parties and provide it appropriately. "
            "Documentation should include: general description, intended purpose, usage instructions, "
            "technical assumptions, limitations (error rates, accuracy, reliability, robustness), "
            "monitoring capabilities."
        ),
        domain="ANNEX_A", weight=3,
        search_terms=["README", "documentation", "model_card", "system_card", "intended_use",
                      "limitations", "intended_purpose", "technical_doc"],
    ),
    AIMS42001Check(
        clause_id="A.6.2.8",
        clause_ref="AI system event logging",
        normative_req=(
            "Control A.6.2.8: The organization SHALL determine at which phases of the AI system "
            "life cycle, record keeping of event logs should be enabled, "
            "at minimum when the AI system is in use. "
            "Logs should include: time/date of use, production data on which system operates, "
            "outputs outside intended operating conditions."
        ),
        domain="ANNEX_A", weight=3,
        search_terms=["logging", "log", "audit_log", "event_log", "record",
                      "traceability", "audit_trail", "logger"],
    ),
    AIMS42001Check(
        clause_id="A.7.3",
        clause_ref="Data acquisition (documented: sources, categories, provenance)",
        normative_req=(
            "Control A.7.3: The organization SHALL determine and document details about the "
            "acquisition and selection of data used in AI systems: categories, quantity, sources, "
            "characteristics, subject demographics, prior handling, data rights, metadata, provenance. "
            "A.7.5 Data provenance: SHALL document process for recording provenance of data."
        ),
        domain="ANNEX_A", weight=3,
        search_terms=["dataset", "data_source", "training_data", "provenance", "data_acquisition",
                      "data_catalog", "datasheet", "data_documentation"],
    ),
    AIMS42001Check(
        clause_id="A.7.4",
        clause_ref="Data quality requirements (training, validation, test, production)",
        normative_req=(
            "Control A.7.4: The organization SHALL define and document requirements for data quality "
            "and ensure that data used to develop and operate the AI system meet those requirements. "
            "B.7.4: For ML systems, the quality of training, validation, test and production data "
            "SHALL be defined, measured and improved. SHALL consider impact of bias on system fairness."
        ),
        domain="ANNEX_A", weight=4,
        search_terms=["data_quality", "quality", "validation", "test_data", "training_data",
                      "bias", "fairness", "imbalance", "data_validation"],
    ),
    AIMS42001Check(
        clause_id="A.8.2",
        clause_ref="System documentation and information for users",
        normative_req=(
            "Control A.8.2: The organization SHALL determine and provide the necessary information "
            "to users of the AI system, including: purpose; that the user is interacting with AI; "
            "how to interact and override; technical requirements and limitations; "
            "human oversight needs; information about accuracy and performance."
        ),
        domain="ANNEX_A", weight=3,
        search_terms=["user_documentation", "README", "getting_started", "usage", "limitations",
                      "accuracy", "performance", "user_guide"],
    ),
    AIMS42001Check(
        clause_id="A.9.3",
        clause_ref="Objectives for responsible use (fairness, accountability, transparency…)",
        normative_req=(
            "Control A.9.3: The organization SHALL identify and document objectives to guide "
            "the responsible use of AI systems: fairness, accountability, transparency, explainability, "
            "reliability, safety, robustness and redundancy, privacy and security, accessibility. "
            "B.9.3: SHALL determine at which stages meaningful human oversight objectives are incorporated."
        ),
        domain="ANNEX_A", weight=4,
        search_terms=["fairness", "accountability", "transparency", "explainability",
                      "responsible_ai", "trustworthy", "human_oversight", "safety"],
    ),
    AIMS42001Check(
        clause_id="A.10.2",
        clause_ref="Third-party responsibilities allocated",
        normative_req=(
            "Control A.10.2: The organization SHALL ensure that responsibilities within their "
            "AI system life cycle are allocated between the organization, its partners, suppliers, "
            "customers and third parties. "
            "A.10.3 Suppliers: SHALL establish a process to ensure usage of supplier services aligns "
            "with the organization's responsible AI approach."
        ),
        domain="ANNEX_A", weight=2,
        search_terms=["supplier", "vendor", "third_party", "partner", "contract",
                      "SLA", "procurement", "supply_chain"],
    ),
]


def scan_iso42001(root: Path, idx: IndexStoreAdapter) -> list[AIMS42001Check]:
    """
    Scan codebase for ISO/IEC 42001:2023 AIMS normative requirements.
    Uses BM25 index search per normative clause and assigns confidence levels.
    """
    for check in AIMS_CHECKS:
        hits: set[str] = set()
        match_count = 0

        for term in check.search_terms:
            try:
                results = idx.search_code(term, limit=5)
                for r in results:
                    if r.path and not any(x in r.path for x in
                                          ("node_modules", ".git", "vendor", "__pycache__", ".pyc")):
                        hits.add(r.path)
                        match_count += 1
            except Exception:
                pass

        check.evidence_files = sorted(list(hits))[:5]
        check.found = len(check.evidence_files) > 0

        # Confidence level based on match breadth (how many distinct terms matched)
        if match_count >= len(check.search_terms) * 0.6:
            check.confidence = "HIGH"
        elif match_count >= 2:
            check.confidence = "MEDIUM"
        elif match_count >= 1:
            check.confidence = "LOW"
        else:
            check.confidence = "NONE"

    return AIMS_CHECKS


def calculate_score(checks: list[AIMS42001Check]) -> tuple[int, str, str]:
    """
    Calculate ISO 42001 AIMS compliance score (0–100).
    Weight by clause weight and confidence level.
    """
    total_weight = sum(c.weight for c in checks)
    achieved = 0
    for c in checks:
        if c.confidence == "HIGH":
            achieved += c.weight * 1.0
        elif c.confidence == "MEDIUM":
            achieved += c.weight * 0.6
        elif c.confidence == "LOW":
            achieved += c.weight * 0.3

    score = int((achieved / total_weight) * 100) if total_weight > 0 else 0

    if score >= 75:
        grade = "A  (AIMS Substantially Implemented)"
        status = "🟢 HIGH CONFORMANCE — Most normative clauses evidenced"
    elif score >= 50:
        grade = "B  (Partial AIMS)"
        status = "🟡 PARTIAL — Core controls present, significant gaps remain"
    elif score >= 25:
        grade = "C  (Initial/Ad-hoc)"
        status = "🟠 LOW — AIMS nascent, major structural gaps"
    else:
        grade = "F  (Non-Conformant)"
        status = "🔴 CRITICAL — No systematic evidence of ISO 42001 AIMS controls"

    return score, grade, status


def print_report(project: str, root: Path, checks: list[AIMS42001Check],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    score, grade, status = calculate_score(checks)

    by_domain: dict[str, list[AIMS42001Check]] = {}
    for c in checks:
        by_domain.setdefault(c.domain, []).append(c)

    conf_icon = {"HIGH": "✅", "MEDIUM": "🟡", "LOW": "⚠️", "NONE": "❌"}
    found_count = sum(1 for c in checks if c.found)

    lines = [
        f"# 🤖 ISO/IEC 42001:2023 AIMS Audit — {project}",
        f"> `{root}` · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 AIMS Compliance Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **ISO 42001 AIMS Score** | **{score} / 100** |",
        f"| **Conformance Grade** | **{grade}** |",
        f"| **Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Clauses/Controls with Evidence | {found_count} / {len(checks)} |",
        "",
        "> **Standard**: ISO/IEC 42001:2023 — Information technology — Artificial intelligence —",
        "> Management system for artificial intelligence (AIMS).",
        "> **Scope**: Clauses 4–10 (normative) + Annex A controls (normative Table A.1)",
        "",
    ]

    for domain, domain_checks in by_domain.items():
        lines += [
            f"## 🔍 {domain} — ISO 42001 Clause Checks",
            "",
            "| Clause | Requirement | Confidence | Evidence |",
            "|---|---|---|---|",
        ]
        for c in domain_checks:
            icon = conf_icon[c.confidence]
            ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2]) if c.evidence_files else "—"
            lines.append(
                f"| `{c.clause_id}` {c.clause_ref} | "
                f"{c.normative_req[:80].rstrip()}… | {icon} {c.confidence} | {ev} |"
            )
        lines.append("")

    # Gap analysis
    gaps = [c for c in checks if c.confidence in ("NONE", "LOW")]
    if gaps:
        lines += [
            "## ⚠️ ISO 42001 — High-Priority Gaps",
            "",
            "These normative SHALL requirements have no or very low evidence in the codebase:",
            "",
        ]
        for g in gaps:
            lines.append(
                f"- **{g.clause_id} {g.clause_ref}** (weight={g.weight}): "
                f"{g.normative_req[:120]}…"
            )
        lines.append("")

    lines += [
        "## 🛠 ISO 42001:2023 Remediation Roadmap",
        "",
        "Priority actions to achieve AIMS conformance:",
        "",
        "### Phase 1 — Foundation (Clauses 4–5)",
        "- `4.1–4.4` Define AI system scope, roles (provider/producer/deployer), and context",
        "- `5.2` Establish documented **AI Policy** committing to continual improvement and applicable requirements",
        "- `5.3` / `A.3.2` Assign and document AI roles (data scientist, AI safety officer, human oversight role)",
        "",
        "### Phase 2 — Planning (Clause 6)",
        "- `6.1.2` Implement **AI Risk Assessment** process (consequences, likelihood, risk levels)",
        "- `6.1.3` Produce **Statement of Applicability** (justify inclusion/exclusion of Annex A controls)",
        "- `6.1.4` Implement **AI System Impact Assessment** process (individual and societal impacts)",
        "- `6.2` Set measurable **AI Objectives** (fairness score, error rate bounds, audit frequency)",
        "",
        "### Phase 3 — Operation (Clause 8 + Annex A)",
        "- `A.6.2.4` Document V&V measures: test datasets, evaluation metrics (Precision/Recall/F1), release criteria",
        "- `A.6.2.6` Implement monitoring for **data drift**, **concept drift**, and AI-specific security threats",
        "- `A.6.2.8` Ensure **event logging** is enabled for AI system in production",
        "- `A.7.4` Document **data quality requirements** for training/validation/test/production data",
        "- `A.5.2` Document **impact assessment results** (fairness, bias evaluation, societal impacts)",
        "",
        "### Phase 4 — Evaluation (Clause 9)",
        "- `9.1` Define monitoring metrics and measurement cadence",
        "- `9.2` Schedule internal AIMS audits at planned intervals",
        "- `9.3` Conduct management reviews with documented outcomes",
        "",
        "---",
        f"*ISO/IEC 42001:2023 AIMS Auditor — normative clauses 4–10, Annex A controls · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 78
    print(f"\n{SEP}")
    print(f"  ISO/IEC 42001:2023 AIMS AUDIT: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  AIMS Compliance Score       : {score} / 100")
    print(f"  Conformance Grade           : {grade}")
    print(f"  Clauses with Evidence       : {found_count} / {len(checks)}")
    print(f"  Audit Duration              : {elapsed:.3f}s")
    print(f"  Report                      : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 iso_42001_ai_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_42001_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    checks = scan_iso42001(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, checks, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
