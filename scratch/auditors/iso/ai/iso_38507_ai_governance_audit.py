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
class ISO38507Check:
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
    ISO38507Check(
        clause_id="4.1",
        clause_ref="Governing principles - Responsibility",
        normative_text="Individuals and groups take responsibility for supply and demand of AI",
        category="PRINCIPLES",
        weight=10,
        search_terms=["AI responsibility", "AI accountability", "AI owner", "governance roles", "AI stakeholder", "model owner", "AI committee", "approval matrix", "sign-off process", "responsibility assignment"]
    ),
    ISO38507Check(
        clause_id="4.2",
        clause_ref="Governing principles - Strategy",
        normative_text="Governing body considers AI in organizational strategy",
        category="PRINCIPLES",
        weight=10,
        search_terms=["AI strategy", "AI roadmap", "strategic alignment", "AI business case", "organizational goals AI", "AI value proposition", "AI adoption plan", "strategic objectives AI", "AI capability building", "governing body AI"]
    ),
    ISO38507Check(
        clause_id="4.3",
        clause_ref="Governing principles - Acquisition",
        normative_text="AI acquisitions made for valid reasons, appropriate authority and controls",
        category="PRINCIPLES",
        weight=10,
        search_terms=["AI procurement", "AI vendor assessment", "buy vs build AI", "AI acquisition policy", "AI vendor risk", "third-party AI", "AI software evaluation", "vendor due diligence", "AI sourcing", "AI supply chain"]
    ),
    ISO38507Check(
        clause_id="4.4",
        clause_ref="Governing principles - Performance",
        normative_text="AI performs well (meets business needs), with appropriate oversight",
        category="PRINCIPLES",
        weight=10,
        search_terms=["AI performance metrics", "model evaluation", "AI business value", "ROI of AI", "AI operational metrics", "model oversight", "AI health check", "model drift monitoring", "AI success criteria", "AI continuous monitoring"]
    ),
    ISO38507Check(
        clause_id="4.5",
        clause_ref="Governing principles - Conformance",
        normative_text="AI complies with mandatory legislation and regulations; policies followed",
        category="PRINCIPLES",
        weight=10,
        search_terms=["AI compliance", "AI regulatory requirements", "AI legal review", "AI policy enforcement", "mandatory AI rules", "AI audit logs", "AI regulatory compliance", "AI legal framework", "AI compliance checklist", "internal policy adherence"]
    ),
    ISO38507Check(
        clause_id="4.6",
        clause_ref="Governing principles - Human behaviour",
        normative_text="AI respects human rights, dignity; employees trained on AI use",
        category="PRINCIPLES",
        weight=10,
        search_terms=["AI human rights", "AI ethics training", "AI workforce impact", "AI user training", "AI dignity", "human-centric AI", "AI literacy", "AI awareness program", "AI acceptable use", "AI employee guidelines"]
    ),
    ISO38507Check(
        clause_id="5.1",
        clause_ref="Governance model - Evaluate",
        normative_text="Governing body evaluates current and future use of AI (benefits, risks, opportunities)",
        category="GOVERNANCE_MODEL",
        weight=15,
        search_terms=["evaluate AI risks", "evaluate AI benefits", "AI opportunity assessment", "AI risk-benefit analysis", "AI portfolio review", "AI impact evaluation", "future AI capabilities", "AI feasibility study", "board AI review", "executive AI evaluation"]
    ),
    ISO38507Check(
        clause_id="5.2",
        clause_ref="Governance model - Direct",
        normative_text="Governing body directs preparation and implementation of AI policies and plans",
        category="GOVERNANCE_MODEL",
        weight=15,
        search_terms=["direct AI implementation", "AI policy creation", "AI mandate", "AI steering committee", "AI leadership direction", "AI plan execution", "executive sponsorship AI", "AI governance directive", "AI policy rollout", "AI program management"]
    ),
    ISO38507Check(
        clause_id="5.3",
        clause_ref="Governance model - Monitor",
        normative_text="Governing body monitors implementation of policies, plans, AI performance",
        category="GOVERNANCE_MODEL",
        weight=15,
        search_terms=["monitor AI performance", "AI compliance monitoring", "AI dashboard", "AI governance reporting", "executive AI metrics", "AI progress tracking", "AI incident reporting", "AI status update", "board AI reporting", "AI audit monitoring"]
    ),
    ISO38507Check(
        clause_id="6.1",
        clause_ref="Governance responsibilities - AI Strategy",
        normative_text="Strategy for AI use is developed and communicated",
        category="GOVERNANCE_RESPONSIBILITIES",
        weight=10,
        search_terms=["AI strategy document", "communicate AI vision", "AI strategic plan", "AI communication plan", "AI roadmap presentation", "AI strategy execution", "enterprise AI strategy", "AI organizational change", "AI leadership communication", "strategic AI alignment"]
    ),
    ISO38507Check(
        clause_id="6.2",
        clause_ref="Governance responsibilities - AI Policies",
        normative_text="Policies for responsible AI use are established",
        category="GOVERNANCE_RESPONSIBILITIES",
        weight=10,
        search_terms=["responsible AI policy", "trustworthy AI guidelines", "AI ethics policy", "AI acceptable use policy", "AI governance framework", "AI development standards", "AI deployment policy", "AI data policy", "AI security policy", "AI policy approval"]
    ),
    ISO38507Check(
        clause_id="6.3",
        clause_ref="Governance responsibilities - AI Risk management",
        normative_text="Risk management for AI is integrated into organizational ERM",
        category="GOVERNANCE_RESPONSIBILITIES",
        weight=10,
        search_terms=["ERM AI integration", "enterprise risk management AI", "AI risk register", "AI risk assessment", "corporate risk AI", "AI threat modeling", "AI risk mitigation", "AI vulnerability management", "strategic AI risks", "AI compliance risk"]
    ),
    ISO38507Check(
        clause_id="6.4",
        clause_ref="Governance responsibilities - AI Performance management",
        normative_text="KPIs for AI defined, measured, reported to governing body",
        category="GOVERNANCE_RESPONSIBILITIES",
        weight=10,
        search_terms=["AI KPIs", "AI key performance indicators", "AI business metrics", "AI performance dashboard", "AI reporting to board", "AI success measurement", "AI OKRs", "AI financial impact", "AI operational efficiency", "executive AI metrics"]
    ),
    ISO38507Check(
        clause_id="6.5",
        clause_ref="Governance responsibilities - Human factors",
        normative_text="Impact on employees and stakeholders considered (reskilling, job displacement)",
        category="GOVERNANCE_RESPONSIBILITIES",
        weight=10,
        search_terms=["AI job impact", "AI reskilling program", "AI workforce transition", "employee AI enablement", "AI change management", "stakeholder AI impact", "AI human resources", "AI skill gaps", "AI talent strategy", "AI organizational design"]
    ),
    ISO38507Check(
        clause_id="6.6",
        clause_ref="Governance responsibilities - Legal and regulatory",
        normative_text="Legal and regulatory compliance for AI",
        category="GOVERNANCE_RESPONSIBILITIES",
        weight=10,
        search_terms=["AI legal counsel", "AI regulatory tracking", "AI legislation monitoring", "AI compliance officer", "AI legal review process", "AI regulatory alignment", "AI data privacy law", "AI IP protection", "AI liability assessment", "AI legal framework"]
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

def scan_project(idx: IndexStoreAdapter) -> Tuple[List[ISO38507Check], int, int]:
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

def print_report(checks: List[ISO38507Check], total: int, max_score: int, proj_name: str, safe_name: str):
    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "c8c09e07-21b1-440f-bf20-c07282cccd62"
    app_data.mkdir(parents=True, exist_ok=True)
    report_path = app_data / f"iso_38507_{safe_name}.md"
    
    with open(report_path, "w") as f:
        f.write(f"# ISO/IEC 38507:2022 AI Governance Audit Report: {proj_name}\n\n")
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
        print("Usage: python iso_38507_ai_governance_audit.py <project_path> <project_name>")
        sys.exit(1)
        
    path = sys.argv[1]
    name = sys.argv[2]
    safe_name = name.lower().replace(" ", "_").replace("/", "_")
    
    idx = IndexStoreAdapter(path)
    
    print(f"Starting ISO/IEC 38507:2022 audit for {name}...")
    checks, total, max_score = scan_project(idx)
    print_report(checks, total, max_score, name, safe_name)

if __name__ == "__main__":
    main()
