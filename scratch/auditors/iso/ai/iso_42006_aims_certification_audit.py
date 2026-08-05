import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from datetime import datetime

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter

@dataclass
class ISO42006Check:
    clause_id: str
    clause_ref: str
    normative_text: str
    category: str
    weight: int
    search_terms: List[str]
    evidence_files: List[str] = field(default_factory=list)
    found: bool = False
    confidence: str = "NONE"

CHECKS = [
    ISO42006Check(
        clause_id="4.1",
        clause_ref="AI-specific competence",
        normative_text="Project maintains evidence of AI competence that auditors can review",
        category="CERT_CONTEXT",
        weight=10,
        search_terms=["AI team competence", "AI training records", "AI skill matrix", "data science qualifications", "ML engineering skills", "AI ethics knowledge", "AI certifications", "AI knowledge sharing", "AI competence assessment", "AI expert profiles"]
    ),
    ISO42006Check(
        clause_id="4.2",
        clause_ref="AI-specific audit methods",
        normative_text="Project accommodates AI-specific audit techniques (e.g., model testing, data sampling)",
        category="CERT_CONTEXT",
        weight=10,
        search_terms=["audit trail AI", "model test results", "data sampling logs", "AI system transparency", "model explainability documentation", "AI testing methodology", "model evaluation framework", "AI reproducibility", "algorithm auditability", "data provenance records"]
    ),
    ISO42006Check(
        clause_id="4.3",
        clause_ref="Understanding of AIMS",
        normative_text="Project demonstrates clear mapping of its processes to ISO 42001 requirements",
        category="CERT_CONTEXT",
        weight=10,
        search_terms=["ISO 42001 mapping", "AIMS conformance", "AI management system documentation", "AIMS gap analysis", "ISO 42001 compliance", "AIMS internal audit", "AIMS implementation plan", "AI process alignment", "AIMS requirement traceability", "AIMS readiness"]
    ),
    ISO42006Check(
        clause_id="5.1",
        clause_ref="Independence and impartiality",
        normative_text="Project has clear separation of duties between AI development and AI assurance/oversight",
        category="CERT_STRUCTURE",
        weight=10,
        search_terms=["separation of duties AI", "independent AI review", "third line of defense AI", "AI model validation independence", "conflict of interest AI", "impartial AI testing", "independent AI ethics board", "AI assurance team", "objective AI assessment", "independent model audit"]
    ),
    ISO42006Check(
        clause_id="5.2",
        clause_ref="Liability provisions",
        normative_text="Project has defined liability and insurance provisions for AI system failures",
        category="CERT_STRUCTURE",
        weight=10,
        search_terms=["AI liability", "AI insurance", "AI failure accountability", "AI indemnification", "AI risk transfer", "AI product liability", "AI financial exposure", "AI loss scenario", "AI legal protection", "AI warranty"]
    ),
    ISO42006Check(
        clause_id="6.1",
        clause_ref="Auditor competence in AI",
        normative_text="Project documents domain, technical, and regulatory context of AI system for external review",
        category="CERT_RESOURCES",
        weight=10,
        search_terms=["AI domain context", "AI regulatory environment", "AI technical specification", "AI system architecture", "AI legal landscape", "AI operational environment", "AI business context", "AI use case description", "AI system boundary", "AI industry standards"]
    ),
    ISO42006Check(
        clause_id="6.2",
        clause_ref="Audit team composition",
        normative_text="Project identifies multidisciplinary stakeholders involved in AI lifecycle",
        category="CERT_RESOURCES",
        weight=10,
        search_terms=["multidisciplinary AI team", "AI stakeholder map", "cross-functional AI review", "AI lifecycle roles", "AI legal compliance technical", "AI team diversity", "AI committee composition", "AI project roles", "AI RACI matrix", "AI cross-domain collaboration"]
    ),
    ISO42006Check(
        clause_id="6.3",
        clause_ref="Technical experts for AI domain",
        normative_text="Project utilizes external or independent AI technical experts when needed",
        category="CERT_RESOURCES",
        weight=10,
        search_terms=["AI external expert", "third-party AI validation", "independent AI consultant", "AI advisory board", "external AI review", "AI subject matter expert", "external model validation", "AI specialized consulting", "independent AI testing", "AI expert network"]
    ),
    ISO42006Check(
        clause_id="7.1",
        clause_ref="AIMS certification process",
        normative_text="Project maintains comprehensive records to support all phases of external certification",
        category="CERT_PROCESS",
        weight=15,
        search_terms=["certification readiness AI", "AIMS evidence repository", "AI compliance artifact", "audit documentation AI", "certification roadmap AI", "AIMS document control", "AI quality records", "external audit preparation AI", "certification body correspondence", "AIMS management review records"]
    ),
    ISO42006Check(
        clause_id="7.2",
        clause_ref="AI-specific audit planning",
        normative_text="Project clearly defines AI system objectives, scope, and boundaries for audit purposes",
        category="CERT_PROCESS",
        weight=15,
        search_terms=["AI system scope", "AI audit boundary", "AI system objectives", "AI operational envelope", "AI intended use", "AI limitations documentation", "AI scope statement", "AI component boundary", "AI system interface", "AI audit criteria"]
    ),
    ISO42006Check(
        clause_id="7.3",
        clause_ref="Audit methodology for AIMS",
        normative_text="Project enables systematic review via documented procedures, interview availability, and system access",
        category="CERT_PROCESS",
        weight=15,
        search_terms=["AI documentation index", "AI system access control", "AI interview plan", "AI demonstration script", "AI system walk-through", "AI codebase review", "AI test environment access", "AI log review capability", "AI audit sampling plan", "AI system visibility"]
    ),
    ISO42006Check(
        clause_id="7.4",
        clause_ref="Audit findings",
        normative_text="Project tracks and remediates AI nonconformities and observations",
        category="CERT_PROCESS",
        weight=15,
        search_terms=["AI nonconformity", "AI corrective action", "AI CAPA", "AI issue tracking", "AI remediation plan", "AI bug report", "AI incident resolution", "AI observation log", "AI continuous improvement", "AI root cause analysis"]
    ),
    ISO42006Check(
        clause_id="8.1",
        clause_ref="Certification body QMS",
        normative_text="Project maintains its own robust quality management practices supporting the AIMS",
        category="CERT_PROCESS",
        weight=10,
        search_terms=["AI quality management", "AIMS quality policy", "AI QMS integration", "AI document control process", "AI record management", "AI internal audit program", "AI management review process", "AI quality objectives", "AI continuous monitoring", "AI quality assurance"]
    ),
]

def calculate_score(match_count: int, total_terms: int, weight: int) -> Tuple[int, str, str]:
    if match_count == 0:
        return 0, "NONE", "No evidence found"
    
    ratio = match_count / total_terms
    if ratio >= 0.5:
        return weight, "HIGH", f"Strong evidence ({match_count}/{total_terms} terms)"
    elif match_count >= 2:
        return int(weight * 0.6), "MEDIUM", f"Partial evidence ({match_count}/{total_terms} terms)"
    else:
        return int(weight * 0.3), "LOW", f"Weak evidence ({match_count}/{total_terms} terms)"

def scan_project(idx: IndexStoreAdapter) -> Tuple[List[ISO42006Check], int, int]:
    total_score = 0
    max_score = sum(c.weight for c in CHECKS)
    
    for check in CHECKS:
        found_terms = 0
        evidence = set()
        
        for term in check.search_terms:
            results = idx.search_code(term, limit=5)
            if results:
                found_terms += 1
                for res in results:
                    evidence.add(getattr(res, 'file_path', 'unknown'))
        
        score, conf, _ = calculate_score(found_terms, len(check.search_terms), check.weight)
        check.confidence = conf
        check.found = found_terms > 0
        check.evidence_files = list(evidence)[:5]
        total_score += score
        
    return CHECKS, total_score, max_score

def print_report(checks: List[ISO42006Check], total: int, max_score: int, proj_name: str, safe_name: str):
    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "c8c09e07-21b1-440f-bf20-c07282cccd62"
    app_data.mkdir(parents=True, exist_ok=True)
    report_path = app_data / f"iso_42006_{safe_name}.md"
    
    with open(report_path, "w") as f:
        f.write(f"# ISO/IEC 42006:2024 AIMS Certification Readiness Audit Report: {proj_name}\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Overall Compliance Score:** {total}/{max_score} ({total/max_score*100:.1f}%)\n\n")
        
        categories = {}
        for c in checks:
            categories.setdefault(c.category, []).append(c)
            
        for cat, cat_checks in categories.items():
            f.write(f"## {cat}\n")
            f.write("| Clause | Requirement | Status | Confidence | Evidence Files |\n")
            f.write("|---|---|---|---|---|\n")
            for c in cat_checks:
                status = "✅" if c.found else "❌"
                ev = "<br>".join(c.evidence_files) if c.evidence_files else "None"
                f.write(f"| {c.clause_id} {c.clause_ref} | {c.normative_text} | {status} | {c.confidence} | {ev} |\n")
            f.write("\n")
            
        f.write("## Gap Analysis & Remediation Roadmap\n")
        f.write("The following areas require attention:\n")
        for c in checks:
            if c.confidence in ["NONE", "LOW"]:
                f.write(f"- **{c.clause_id} {c.clause_ref}**: Missing or weak evidence for '{c.normative_text}'.\n")

    print(f"Report written to {report_path}")
    print(f"Score: {total}/{max_score} ({total/max_score*100:.1f}%)")

def main():
    if len(sys.argv) < 3:
        print("Usage: python iso_42006_aims_certification_audit.py <project_path> <project_name>")
        sys.exit(1)
        
    path = sys.argv[1]
    name = sys.argv[2]
    safe_name = name.lower().replace(" ", "_").replace("/", "_")
    
    idx = IndexStoreAdapter(path)
    
    print(f"Starting ISO/IEC 42006:2024 audit for {name}...")
    checks, total, max_score = scan_project(idx)
    print_report(checks, total, max_score, name, safe_name)

if __name__ == "__main__":
    main()
