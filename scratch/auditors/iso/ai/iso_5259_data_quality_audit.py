import os
import sys
import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter

@dataclass
class ISO5259Check:
    clause_id: str
    clause_ref: str
    normative_text: str
    category: str
    weight: int
    search_terms: List[str]
    evidence_files: List[str] = field(default_factory=list)
    found: bool = False
    confidence: str = "NONE"

def calculate_score(check: ISO5259Check, match_count: int) -> Tuple[int, str, str]:
    if match_count == 0:
        return 0, "NONE", f"0/{len(check.search_terms)} terms found"
    
    match_ratio = match_count / len(check.search_terms)
    if match_ratio >= 0.5:
        return int(check.weight * 1.0), "HIGH", f"{match_count}/{len(check.search_terms)} terms found"
    elif match_count >= 2:
        return int(check.weight * 0.6), "MEDIUM", f"{match_count}/{len(check.search_terms)} terms found"
    else:
        return int(check.weight * 0.3), "LOW", f"{match_count}/{len(check.search_terms)} terms found"

def scan_project(path: str, project_name: str) -> List[ISO5259Check]:
    checks = [
        ISO5259Check(
            clause_id="4.1",
            clause_ref="Data Quality Concept",
            normative_text="Data quality for AI/ML defined as fitness of data for intended purpose.",
            category="DQ_DIMENSIONS",
            weight=10,
            search_terms=["fitness", "intended purpose", "data quality", "analytics", "machine learning"]
        ),
        ISO5259Check(
            clause_id="4.2",
            clause_ref="Data Quality Dimensions",
            normative_text="Define data quality dimensions: accuracy, completeness, consistency, currentness, accessibility, etc.",
            category="DQ_DIMENSIONS",
            weight=10,
            search_terms=["accuracy", "completeness", "consistency", "timeliness", "accessibility", "compliance", "credibility", "traceability", "understandability", "portability"]
        ),
        ISO5259Check(
            clause_id="5.1",
            clause_ref="Data Quality Process",
            normative_text="Data quality requirements definition and process overview.",
            category="DQ_PROCESS",
            weight=10,
            search_terms=["requirements definition", "quality measurement", "assessment", "improvement", "control"]
        )
    ]

    try:
        idx = IndexStoreAdapter(path)
        for check in checks:
            match_count = 0
            for term in check.search_terms:
                results = idx.search_code(term, limit=5)
                if results and len(results) > 0:
                    match_count += 1
                    for r in results:
                        path = getattr(r, 'path', r.get('path') if isinstance(r, dict) else None)
                        if path and path not in check.evidence_files:
                            check.evidence_files.append(path)
                            
            score, conf, reason = calculate_score(check, match_count)
            check.confidence = conf
            check.found = match_count > 0
            
    except Exception as e:
        print(f"Error scanning: {e}")
        
    return checks

def print_report(checks: List[ISO5259Check], project_name: str):
    safe_name = "".join([c if c.isalnum() else "_" for c in project_name]).lower()
    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)
    report_file = app_data / f"iso_5259_{safe_name}.md"
    
    with open(report_file, "w") as f:
        f.write(f"# ISO/IEC 5259-1 Data Quality Audit Report: {project_name}\n\n")
        
        categories = {}
        for c in checks:
            categories.setdefault(c.category, []).append(c)
            
        for cat, cat_checks in categories.items():
            f.write(f"## {cat}\n\n")
            f.write("| Clause | Ref | Status | Confidence | Evidence |\n")
            f.write("|---|---|---|---|---|\n")
            for c in cat_checks:
                status = "✅" if c.found else "❌"
                evidence = f"[{len(c.evidence_files)} files]" if c.evidence_files else "None"
                f.write(f"| {c.clause_id} | {c.clause_ref} | {status} | {c.confidence} | {evidence} |\n")
            f.write("\n")
            
        f.write("## Gap Analysis & Remediation Roadmap\n\n")
        gaps = [c for c in checks if c.confidence in ("NONE", "LOW")]
        for c in gaps:
            f.write(f"- **{c.clause_id} {c.clause_ref}**: Missing or weak evidence for '{c.normative_text}'\n")

    print(f"Report written to {report_file}")
    for c in checks:
        print(f"{c.clause_id} {c.clause_ref}: {c.confidence} ({len(c.evidence_files)} files)")

def main():
    if len(sys.argv) < 3:
        print("Usage: python iso_5259_data_quality_audit.py <path> <project_name>")
        sys.exit(1)
        
    path = sys.argv[1]
    project_name = sys.argv[2]
    
    checks = scan_project(path, project_name)
    print_report(checks, project_name)

if __name__ == "__main__":
    main()
