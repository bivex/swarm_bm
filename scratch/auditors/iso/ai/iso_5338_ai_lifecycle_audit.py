import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from collections import defaultdict

# Setup path for BM25 IndexStoreAdapter
root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter

@dataclass
class ISO5338Check:
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
    ISO5338Check(
        clause_id="5.1",
        clause_ref="AI system feasibility analysis",
        normative_text="Assess feasibility, stakeholder needs, and system requirements for AI concept processes.",
        category="CONCEPT",
        weight=10,
        search_terms=["feasibility analysis", "stakeholder needs", "system requirements", "concept phase", "ai feasibility", "business case", "technical feasibility", "resource estimation", "roi", "initial assessment", "stakeholder requirements"]
    ),
    ISO5338Check(
        clause_id="5.2",
        clause_ref="Stakeholder needs and requirements definition",
        normative_text="Stakeholder needs and requirements definition.",
        category="CONCEPT",
        weight=10,
        search_terms=["stakeholder needs", "requirements definition", "user requirements", "business requirements", "stakeholder interview", "needs analysis", "requirements gathering", "use case", "persona", "stakeholder requirement"]
    ),
    ISO5338Check(
        clause_id="5.3",
        clause_ref="AI system requirements definition",
        normative_text="AI system requirements definition.",
        category="CONCEPT",
        weight=15,
        search_terms=["ai system requirements", "system requirements specification", "functional requirements", "non-functional requirements", "srs", "ai requirement", "system spec", "requirement tracing", "requirement validation"]
    ),
    ISO5338Check(
        clause_id="6.1",
        clause_ref="AI data management",
        normative_text="Data acquisition, data preparation, data quality verification.",
        category="DEVELOPMENT",
        weight=15,
        search_terms=["data acquisition", "data preparation", "data quality", "data verification", "data cleansing", "data pipeline", "etl", "dataset management", "data governance", "data annotation", "data provenance", "data lineage"]
    ),
    ISO5338Check(
        clause_id="6.2",
        clause_ref="AI model management",
        normative_text="Model development, training, evaluation, model versioning.",
        category="DEVELOPMENT",
        weight=15,
        search_terms=["model development", "model training", "model evaluation", "model versioning", "hyperparameter tuning", "mlflow", "model registry", "model artifact", "training script", "validation set", "test set", "model checkpoint"]
    ),
    ISO5338Check(
        clause_id="6.3",
        clause_ref="AI system design",
        normative_text="Architecture, integration design.",
        category="DEVELOPMENT",
        weight=15,
        search_terms=["architecture design", "integration design", "system architecture", "high level design", "low level design", "design pattern", "api design", "component diagram", "sequence diagram", "design document"]
    ),
    ISO5338Check(
        clause_id="6.4",
        clause_ref="AI system verification",
        normative_text="Unit testing, integration testing, system testing.",
        category="DEVELOPMENT",
        weight=15,
        search_terms=["unit testing", "integration testing", "system testing", "test plan", "test execution", "test report", "verification", "code coverage", "automated testing", "regression testing", "mock"]
    ),
    ISO5338Check(
        clause_id="6.5",
        clause_ref="AI system validation",
        normative_text="Acceptance testing, operational testing.",
        category="DEVELOPMENT",
        weight=15,
        search_terms=["acceptance testing", "operational testing", "validation", "user acceptance test", "uat", "field test", "beta test", "pilot", "validation report", "operational validation"]
    ),
    ISO5338Check(
        clause_id="7.1",
        clause_ref="AI system release management",
        normative_text="AI system release management.",
        category="DEPLOYMENT",
        weight=10,
        search_terms=["release management", "release plan", "release notes", "version control", "deployment package", "release candidate", "go/no-go decision", "release process", "change management", "release cycle"]
    ),
    ISO5338Check(
        clause_id="7.2",
        clause_ref="AI system deployment",
        normative_text="AI system installation, configuration, and release management.",
        category="DEPLOYMENT",
        weight=15,
        search_terms=["system deployment", "installation", "configuration", "deployment pipeline", "ci/cd", "containerization", "kubernetes", "docker", "production rollout", "deployment strategy", "canary release"]
    ),
    ISO5338Check(
        clause_id="7.3",
        clause_ref="AI system operation",
        normative_text="Monitoring, user support.",
        category="DEPLOYMENT",
        weight=15,
        search_terms=["monitoring", "user support", "operations", "system health", "telemetry", "alerting", "log analysis", "helpdesk", "incident management", "performance monitoring", "model monitoring"]
    ),
    ISO5338Check(
        clause_id="8.1",
        clause_ref="AI system decommissioning",
        normative_text="AI system decommissioning.",
        category="RETIREMENT",
        weight=10,
        search_terms=["decommissioning", "end of life", "sunset", "system archiving", "retirement plan", "deactivation", "shutdown", "service termination", "migration plan"]
    ),
    ISO5338Check(
        clause_id="8.2",
        clause_ref="Data disposal and model retirement",
        normative_text="Data disposal and model retirement.",
        category="RETIREMENT",
        weight=10,
        search_terms=["data disposal", "model retirement", "data deletion", "retention policy", "secure disposal", "data purge", "model archiving", "data sanitization", "cryptographic erasure"]
    ),
    ISO5338Check(
        clause_id="9.1",
        clause_ref="AI system risk management",
        normative_text="Risk management throughout the life cycle.",
        category="CROSS_LIFECYCLE",
        weight=10,
        search_terms=["risk management", "risk assessment", "risk mitigation", "hazard analysis", "threat modeling", "vulnerability scan", "risk registry", "risk matrix", "continuous monitoring", "incident response", "contingency plan"]
    ),
    ISO5338Check(
        clause_id="9.2",
        clause_ref="AI system quality management",
        normative_text="Quality management.",
        category="CROSS_LIFECYCLE",
        weight=10,
        search_terms=["quality management", "quality assurance", "qa", "quality control", "quality metric", "process improvement", "audit", "compliance", "standardization", "quality policy"]
    ),
    ISO5338Check(
        clause_id="9.3",
        clause_ref="AI safety assurance",
        normative_text="Safety assurance.",
        category="CROSS_LIFECYCLE",
        weight=10,
        search_terms=["safety assurance", "safety case", "safety critical", "functional safety", "safety integrity", "safety requirement", "hazard log", "safety evidence", "safety assessment report"]
    ),
    ISO5338Check(
        clause_id="9.4",
        clause_ref="AI security management",
        normative_text="Security management.",
        category="CROSS_LIFECYCLE",
        weight=10,
        search_terms=["security management", "information security", "cybersecurity", "security policy", "access control", "encryption", "security audit", "penetration testing", "vulnerability management", "security incident"]
    ),
    ISO5338Check(
        clause_id="9.5",
        clause_ref="AI privacy management",
        normative_text="Privacy management.",
        category="CROSS_LIFECYCLE",
        weight=10,
        search_terms=["privacy management", "data privacy", "gdpr", "pii", "anonymization", "pseudonymization", "privacy policy", "consent management", "privacy impact assessment", "data protection"]
    ),
    ISO5338Check(
        clause_id="9.6",
        clause_ref="AI ethics management",
        normative_text="Ethics management.",
        category="CROSS_LIFECYCLE",
        weight=10,
        search_terms=["ethics management", "ai ethics", "ethical guideline", "bias mitigation", "fairness", "transparency", "accountability", "ethical review", "ethics committee", "value alignment"]
    )
]

def calculate_score(check: ISO5338Check, matches: int) -> Tuple[int, str, str]:
    term_count = len(check.search_terms)
    
    if matches >= term_count * 0.5:
        return int(check.weight * 1.0), "HIGH", f"Strong evidence ({matches}/{term_count} terms)"
    elif matches >= 2:
        return int(check.weight * 0.6), "MEDIUM", f"Partial evidence ({matches}/{term_count} terms)"
    elif matches >= 1:
        return int(check.weight * 0.3), "LOW", f"Weak evidence ({matches}/{term_count} terms)"
    else:
        return 0, "NONE", "No evidence found"

def scan_repository(path: str, checks: List[ISO5338Check]):
    idx = IndexStoreAdapter()
    idx.rebuild(Path(path))
    for check in checks:
        matches_found = 0
        for term in check.search_terms:
            try:
                results = idx.search_code(term, limit=5)
                if results:
                    matches_found += 1
                    for res in results:
                        file_path = res.get('file', '')
                        if file_path and file_path not in check.evidence_files:
                            check.evidence_files.append(file_path)
            except Exception:
                pass
        
        if matches_found > 0:
            check.found = True
        
        score, confidence, _ = calculate_score(check, matches_found)
        check.confidence = confidence

def print_report(checks: List[ISO5338Check], project_name: str):
    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)
    
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', project_name.lower())
    report_file = app_data / f"iso_5338_{safe_name}.md"
    
    total_score = 0
    max_score = sum(c.weight for c in checks)
    
    cat_scores = defaultdict(int)
    cat_max = defaultdict(int)
    
    for c in checks:
        if c.confidence == "HIGH": s = c.weight * 1.0
        elif c.confidence == "MEDIUM": s = c.weight * 0.6
        elif c.confidence == "LOW": s = c.weight * 0.3
        else: s = 0
        
        total_score += s
        cat_scores[c.category] += s
        cat_max[c.category] += c.weight
    
    with open(report_file, "w") as f:
        f.write(f"# ISO/IEC 5338 AI Lifecycle Audit Report: {project_name}\n\n")
        
        f.write("## Executive Summary\n")
        f.write(f"**Total Lifecycle Score:** {int(total_score)} / {max_score}\n\n")
        
        f.write("## Phase Breakdown\n")
        for cat in sorted(cat_max.keys()):
            f.write(f"- **{cat}:** {int(cat_scores[cat])} / {cat_max[cat]}\n")
            
        f.write("\n## Detailed Findings\n")
        for c in checks:
            f.write(f"### {c.clause_id} - {c.clause_ref}\n")
            f.write(f"- **Phase:** {c.category}\n")
            f.write(f"- **Confidence:** {c.confidence}\n")
            f.write(f"- **Requirement:** {c.normative_text}\n")
            if c.evidence_files:
                f.write("- **Evidence Files:**\n")
                for ev in c.evidence_files[:5]:
                    f.write(f"  - `{ev}`\n")
            else:
                f.write("- **Evidence Files:** None found\n")
            f.write("\n")
            
        f.write("## Gap Analysis & Remediation Roadmap\n")
        f.write("1. Review LOW and NONE confidence processes.\n")
        f.write("2. Formalize missing lifecycle phases (e.g., retirement).\n")
        f.write("3. Ensure data and model management practices are thoroughly documented.\n")

    print(f"Report written to {report_file}")
    print(f"ISO 5338 Total Score: {int(total_score)}/{max_score}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python iso_5338_ai_lifecycle_audit.py <repo_path> <project_name>")
        sys.exit(1)
        
    repo_path = sys.argv[1]
    project_name = sys.argv[2]
    
    scan_repository(repo_path, CHECKS)
    print_report(CHECKS, project_name)

if __name__ == "__main__":
    main()
