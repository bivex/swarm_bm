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
class ISO25059Check:
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
    ISO25059Check(
        clause_id="4.1",
        clause_ref="Functional suitability",
        normative_text="Assess functional correctness, completeness, appropriateness, and AI task performance.",
        category="ISO25010_BASE",
        weight=10,
        search_terms=["functional correctness", "task performance", "completeness", "appropriateness", "functional testing", "test case", "accuracy", "precision", "recall", "f1 score", "functional suitability", "system test"]
    ),
    ISO25059Check(
        clause_id="4.2",
        clause_ref="Performance efficiency",
        normative_text="Assess time behaviour, resource utilization, capacity, and inference latency.",
        category="ISO25010_BASE",
        weight=10,
        search_terms=["time behaviour", "resource utilization", "capacity", "inference latency", "response time", "throughput", "benchmark", "performance test", "profiling", "latency evaluation", "memory usage", "cpu usage"]
    ),
    ISO25059Check(
        clause_id="4.3",
        clause_ref="Compatibility",
        normative_text="Co-existence, interoperability with other AI/non-AI systems.",
        category="ISO25010_BASE",
        weight=10,
        search_terms=["compatibility", "co-existence", "interoperability", "api integration", "data format", "system integration", "protocol", "interface testing", "backward compatibility", "cross-platform", "integration test"]
    ),
    ISO25059Check(
        clause_id="4.4",
        clause_ref="Usability",
        normative_text="Appropriateness recognizability, learnability, operability, user error protection, accessibility.",
        category="ISO25010_BASE",
        weight=10,
        search_terms=["usability", "recognizability", "learnability", "operability", "user error protection", "accessibility", "user experience", "ux design", "ui testing", "user feedback", "intuitive", "user guide"]
    ),
    ISO25059Check(
        clause_id="4.5",
        clause_ref="Reliability",
        normative_text="Maturity, availability, fault tolerance, recoverability, and consistency under different inputs.",
        category="ISO25010_BASE",
        weight=15,
        search_terms=["maturity", "availability", "fault tolerance", "recoverability", "consistency", "reliability testing", "uptime", "failover", "error handling", "recovery time", "system stability"]
    ),
    ISO25059Check(
        clause_id="4.6",
        clause_ref="Security",
        normative_text="Confidentiality, integrity, non-repudiation, accountability, authenticity, resistance to adversarial attacks.",
        category="ISO25010_BASE",
        weight=15,
        search_terms=["confidentiality", "integrity", "non-repudiation", "accountability", "authenticity", "adversarial attack", "security test", "vulnerability", "encryption", "access control", "authentication", "threat model"]
    ),
    ISO25059Check(
        clause_id="4.7",
        clause_ref="Maintainability",
        normative_text="Modularity, reusability, analysability, modifiability, testability, retrain-ability, model updating.",
        category="ISO25010_BASE",
        weight=10,
        search_terms=["modularity", "reusability", "analysability", "modifiability", "testability", "retrain-ability", "model updating", "code refactoring", "technical debt", "maintainability index", "continuous training", "pipeline update"]
    ),
    ISO25059Check(
        clause_id="4.8",
        clause_ref="Portability",
        normative_text="Adaptability, installability, replaceability.",
        category="ISO25010_BASE",
        weight=10,
        search_terms=["adaptability", "installability", "replaceability", "portability", "platform independence", "environment setup", "container", "docker", "kubernetes", "migration", "cross-platform support"]
    ),
    ISO25059Check(
        clause_id="4.9.1",
        clause_ref="Fairness",
        normative_text="Group fairness, individual fairness, counterfactual fairness.",
        category="FAIRNESS",
        weight=15,
        search_terms=["group fairness", "individual fairness", "counterfactual fairness", "bias mitigation", "demographic parity", "equalized odds", "disparate impact", "fairness metric", "bias detection", "fairness assessment", "unbiased"]
    ),
    ISO25059Check(
        clause_id="4.9.2",
        clause_ref="Explainability",
        normative_text="Local and global explainability, completeness.",
        category="EXPLAINABILITY",
        weight=15,
        search_terms=["local explainability", "global explainability", "completeness", "shap", "lime", "feature importance", "interpretability", "explanation generation", "explainable ai", "xai", "model transparency"]
    ),
    ISO25059Check(
        clause_id="4.9.3",
        clause_ref="Robustness",
        normative_text="Distribution shift, adversarial robustness.",
        category="ROBUSTNESS",
        weight=15,
        search_terms=["distribution shift", "adversarial robustness", "concept drift", "data shift", "adversarial attack", "robustness testing", "out of distribution", "ood detection", "perturbation", "noise tolerance", "resilience"]
    ),
    ISO25059Check(
        clause_id="4.9.4",
        clause_ref="Transparency",
        normative_text="Transparency of training data, algorithm, model structure.",
        category="AI_QUALITY",
        weight=15,
        search_terms=["transparency", "training data", "algorithm", "model structure", "data provenance", "model documentation", "model card", "data sheet", "open source", "traceability", "audit log"]
    ),
    ISO25059Check(
        clause_id="4.9.5",
        clause_ref="Safety",
        normative_text="Safety impact assessment, hazard identification.",
        category="SAFETY",
        weight=15,
        search_terms=["safety impact", "hazard identification", "safety assessment", "risk evaluation", "functional safety", "fail-safe", "emergency stop", "human safety", "hazard analysis", "safety critical", "safe operation"]
    ),
    ISO25059Check(
        clause_id="4.9.6",
        clause_ref="Autonomy level",
        normative_text="Degree of human oversight required.",
        category="AI_QUALITY",
        weight=10,
        search_terms=["autonomy level", "human oversight", "human in the loop", "hitl", "human on the loop", "automation degree", "manual override", "supervisor control", "autonomous operation", "decision boundary"]
    )
]

def calculate_score(check: ISO25059Check, matches: int) -> Tuple[int, str, str]:
    term_count = len(check.search_terms)
    
    if matches >= term_count * 0.5:
        return int(check.weight * 1.0), "HIGH", f"Strong evidence ({matches}/{term_count} terms)"
    elif matches >= 2:
        return int(check.weight * 0.6), "MEDIUM", f"Partial evidence ({matches}/{term_count} terms)"
    elif matches >= 1:
        return int(check.weight * 0.3), "LOW", f"Weak evidence ({matches}/{term_count} terms)"
    else:
        return 0, "NONE", "No evidence found"

def scan_repository(path: str, checks: List[ISO25059Check]):
    idx = IndexStoreAdapter()
    idx.rebuild(Path(path))
    for check in checks:
        matches_found = 0
        for term in check.search_terms:
            try:
                results = idx.search_code(term, limit=5)
                if results:
                    matches_found += 1
                    for r in results:
                        fp = getattr(r, 'path', None)
                        if fp and not any(x in fp for x in ('.git', '__pycache__', 'node_modules')):
                            if fp not in check.evidence_files:
                                check.evidence_files.append(fp)
            except Exception:
                pass

        check.found = len(check.evidence_files) > 0
        score, confidence, _ = calculate_score(check, matches_found)
        check.confidence = confidence

def print_report(checks: List[ISO25059Check], project_name: str):
    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)
    
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', project_name.lower())
    report_file = app_data / f"iso_25059_{safe_name}.md"
    
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
        f.write(f"# ISO/IEC 25059 AI Quality Model Audit Report: {project_name}\n\n")
        
        f.write("## Executive Summary\n")
        f.write(f"**Total Quality Score:** {int(total_score)} / {max_score}\n\n")
        
        f.write("## Category Breakdown\n")
        for cat in sorted(cat_max.keys()):
            f.write(f"- **{cat}:** {int(cat_scores[cat])} / {cat_max[cat]}\n")
            
        f.write("\n## Detailed Findings\n")
        for c in checks:
            f.write(f"### {c.clause_id} - {c.clause_ref}\n")
            f.write(f"- **Category:** {c.category}\n")
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
        f.write("1. Review LOW and NONE confidence areas.\n")
        f.write("2. Implement missing quality characteristics.\n")
        f.write("3. Add documentation and automated tests for AI-specific quality attributes.\n")

    SEP = "═" * 78
    score_pct = int((total_score / max_score) * 100) if max_score else 0
    if score_pct >= 75: grade = "A  (High AI Quality)"
    elif score_pct >= 50: grade = "B  (Partial Quality)"
    elif score_pct >= 25: grade = "C  (Basic Quality)"
    else: grade = "F  (Non-Conformant)"
    print(f"\n{SEP}")
    print(f"  ISO/IEC 25059:2023 AI QUALITY MODEL AUDIT: {project_name}")
    print(SEP)
    print(f"  ISO 25059 Quality Score       : {int(total_score)} / {max_score} ({score_pct}%)")
    print(f"  Conformance Grade             : {grade}")
    print(f"  Report                        : {report_file}")
    print(f"{SEP}\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python iso_25059_ai_quality_model_audit.py <repo_path> <project_name>")
        sys.exit(1)
        
    repo_path = sys.argv[1]
    project_name = sys.argv[2]
    
    scan_repository(repo_path, CHECKS)
    print_report(CHECKS, project_name)

if __name__ == "__main__":
    main()
