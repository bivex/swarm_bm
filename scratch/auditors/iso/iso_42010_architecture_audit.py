#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ISO/IEC/IEEE 42010:2011 Architecture Description Conformance Auditor        ║
║                                                                               ║
║  Based on normative requirements of ISO/IEC/IEEE 42010:2011:                  ║
║  Clause 4: Conceptual Framework (System, Environment, Stakeholders, Concerns)  ║
║  Clause 5: Architecture Description (AD) Identification & Context             ║
║  Clause 6: Architecture Views, Viewpoints & Model Kinds                       ║
║  Clause 7: Architecture Decisions & Rationale (ADR)                           ║
║  Clause 8: Architecture Relations & Consistency                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_42010_architecture_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import logging
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

# Setup logging configuration conforming to production CLI requirements
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ISO42010Auditor")

# Dynamic root determination for BM25 adapter infrastructure
try:
    root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
    sys.path.insert(0, str(root_dir))
    sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))
    from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
except Exception as e:
    logger.error(f"Failed to load IndexStoreAdapter infrastructure: {e}")
    sys.exit(1)


@dataclass(slots=True)
class ISO42010Check:
    """Dataclass representing an ISO/IEC/IEEE 42010 normative requirement check."""
    clause_id: str
    clause_ref: str
    normative_req: str
    category: str
    weight: int
    search_terms: list[str]
    evidence_files: list[str] = field(default_factory=list)
    found: bool = False
    confidence: str = "NONE"


ARCH_CHECKS: list[ISO42010Check] = [
    # ── Clause 5: Architecture Description Identification & Context ──────────
    ISO42010Check(
        clause_id="5.1",
        clause_ref="Architecture Description Identification & Overview",
        normative_req="An AD SHALL identify the system-of-interest, organization, and provide an overview of the system context.",
        category="CONTEXT",
        weight=4,
        search_terms=["architecture", "system_overview", "readme.md", "architecture.md", "system_design", "scope"],
    ),
    ISO42010Check(
        clause_id="5.2",
        clause_ref="Stakeholders and Concerns Identification",
        normative_req="An AD SHALL identify the architecture stakeholders (users, operators, acquirers) and their key concerns.",
        category="STAKEHOLDERS",
        weight=3,
        search_terms=["stakeholder", "concern", "user_requirements", "business_goals", "actors", "roles"],
    ),

    # ── Clause 6: Architecture Views, Viewpoints & Models ───────────────────
    ISO42010Check(
        clause_id="6.1",
        clause_ref="Architecture Viewpoints Definition",
        normative_req="An AD SHALL frame architectural concerns using defined viewpoints (functional, deployment, data, security).",
        category="VIEWPOINTS",
        weight=5,
        search_terms=["viewpoint", "view", "component_view", "deployment_view", "data_flow", "security_view"],
    ),
    ISO42010Check(
        clause_id="6.2",
        clause_ref="Architecture Views & Diagrams (C4 / UML / Mermaid)",
        normative_req="An AD SHALL include architecture views conforming to their viewpoints, expressing structural models.",
        category="VIEWS",
        weight=5,
        search_terms=["mermaid", "plantuml", "c4", "diagram", "graphviz", "architecture_diagram", "flowchart"],
    ),
    ISO42010Check(
        clause_id="6.3",
        clause_ref="Architecture Model Kinds and Conventions",
        normative_req="An AD SHALL specify the model kinds used (e.g., class diagrams, sequence diagrams, component graphs).",
        category="MODELS",
        weight=3,
        search_terms=["sequence_diagram", "class_diagram", "component_diagram", "data_model", "schema", "er_diagram"],
    ),

    # ── Clause 7: Architecture Decisions & Rationale ─────────
    ISO42010Check(
        clause_id="7.1",
        clause_ref="Architecture Decision Records (ADR)",
        normative_req="An AD SHALL record key architectural decisions (ADRs) that shape the system structure.",
        category="DECISIONS",
        weight=5,
        search_terms=["adr", "docs/adr", "decision_log", "architectural_decision", "decision_record", "rfc"],
    ),
    ISO42010Check(
        clause_id="7.2",
        clause_ref="Architectural Rationale & Alternatives Considered",
        normative_req="An AD SHALL document the rationale for architectural decisions and alternatives rejected.",
        category="DECISIONS",
        weight=4,
        search_terms=["rationale", "alternatives", "trade-offs", "pros_cons", "rejected_options", "justification"],
    ),

    # ── Clause 8: Architecture Consistency & Quality Attributes ────────────
    ISO42010Check(
        clause_id="8.1",
        clause_ref="Architecture Consistency & Cross-View Mapping",
        normative_req="An AD SHALL demonstrate consistency across views and verify no contradictions exist between models.",
        category="CONSISTENCY",
        weight=4,
        search_terms=["interface", "adapter", "boundary", "contract", "api_spec", "data_contract"],
    ),
    ISO42010Check(
        clause_id="8.2",
        clause_ref="Quality Attributes & Non-Functional Requirements (NFR)",
        normative_req="An AD SHALL address non-functional requirements: performance, scalability, security, and reliability.",
        category="QUALITY_ATTRIBUTES",
        weight=4,
        search_terms=["nfr", "scalability", "reliability", "latency", "throughput", "security_architecture", "ha"],
    ),
]


def scan_iso42010(root: Path, idx: IndexStoreAdapter) -> list[ISO42010Check]:
    """Scan codebase for ISO/IEC/IEEE 42010 architecture description evidence using IndexStoreAdapter."""
    try:
        idx.rebuild(root)
    except Exception as e:
        logger.error(f"Error rebuilding index for path {root}: {e}")
        return ARCH_CHECKS

    for check in ARCH_CHECKS:
        hits: set[str] = set()
        match_count = 0

        for term in check.search_terms:
            try:
                results = idx.search_code(term, limit=5)
                for r in results:
                    fp = getattr(r, "path", None)
                    if fp and not any(x in fp for x in ("node_modules", ".git", "vendor", "__pycache__", "venv", ".venv")):
                        hits.add(fp)
                        match_count += 1
            except Exception as e:
                logger.debug(f"Error searching term '{term}': {e}")

        check.evidence_files = sorted(list(hits))[:5]
        check.found = len(check.evidence_files) > 0
        ratio = match_count / max(len(check.search_terms), 1)

        if ratio >= 0.5:
            check.confidence = "HIGH"
        elif match_count >= 2:
            check.confidence = "MEDIUM"
        elif match_count >= 1:
            check.confidence = "LOW"
        else:
            check.confidence = "NONE"

    return ARCH_CHECKS


def calculate_score(checks: list[ISO42010Check]) -> tuple[int, str, str]:
    """Calculate ISO 42010 Architecture Description Conformance score and grade."""
    total_weight = sum(c.weight for c in checks)
    achieved = sum(
        c.weight * (1.0 if c.confidence == "HIGH" else 0.6 if c.confidence == "MEDIUM" else 0.3 if c.confidence == "LOW" else 0.0)
        for c in checks
    )
    score = int((achieved / total_weight) * 100) if total_weight else 0

    if score >= 85:
        grade, status = "A+ (Full ISO 42010 Architecture Conformance)", "🟢 HIGH — Exemplary Architecture Description & ADRs"
    elif score >= 70:
        grade, status = "A  (Good Architectural Governance)", "🟢 GOOD — Structured Views & Design Docs Present"
    elif score >= 50:
        grade, status = "B  (Partial Architecture Docs)", "🟡 PARTIAL — Basic README/Design present, missing ADRs & Views"
    elif score >= 25:
        grade, status = "C  (Initial/Ad-hoc Architecture)", "🟠 LOW — Minimal architectural documentation"
    else:
        grade, status = "F  (Undocumented Architecture)", "🔴 CRITICAL — No architectural documentation or decision records"

    return score, grade, status


def print_report(
    project: str,
    root: Path,
    checks: list[ISO42010Check],
    stats: dict,
    elapsed: float,
    report_path: Path
) -> None:
    """Generate and write markdown report, then print terminal summary."""
    score, grade, status = calculate_score(checks)
    conf_icon = {"HIGH": "✅", "MEDIUM": "🟡", "LOW": "⚠️", "NONE": "❌"}
    found_count = sum(1 for c in checks if c.found)

    by_cat: dict[str, list[ISO42010Check]] = {}
    for c in checks:
        by_cat.setdefault(c.category, []).append(c)

    cat_titles = {
        "CONTEXT": "§5.1 System Identification & Context Scope",
        "STAKEHOLDERS": "§5.2 Stakeholders & Architectural Concerns",
        "VIEWPOINTS": "§6.1 Architecture Viewpoints (Functional, Data, Deployment, Security)",
        "VIEWS": "§6.2 Architecture Views & Diagrams (C4, PlantUML, Mermaid)",
        "MODELS": "§6.3 Model Kinds & Schema Conventions",
        "DECISIONS": "§7 Architecture Decision Records (ADR & Rationale)",
        "CONSISTENCY": "§8.1 Architectural Consistency & Cross-View Contracts",
        "QUALITY_ATTRIBUTES": "§8.2 Quality Attributes & NFR Specification",
    }

    lines = [
        f"# 🏛️ ISO/IEC/IEEE 42010:2011 Architecture Description Audit — {project}",
        f"> `{root}` · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 Architecture Governance Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **ISO 42010 Architecture Score** | **{score} / 100** |",
        f"| **Architecture Grade** | **{grade}** |",
        f"| **Governance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Validated Architecture Checks | {found_count} / {len(checks)} |",
        "",
        "> **Standard**: ISO/IEC/IEEE 42010:2011 — Systems and software engineering — Architecture description.",
        "",
    ]

    for cat, cat_checks in by_cat.items():
        title = cat_titles.get(cat, cat)
        lines += [
            f"## 🔍 {title}",
            "",
            "| Clause | Requirement | Confidence | Evidence Files |",
            "|---|---|---|---|",
        ]
        for c in cat_checks:
            icon = conf_icon[c.confidence]
            ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2]) if c.evidence_files else "—"
            lines.append(f"| `{c.clause_id}` | {c.clause_ref} | {icon} {c.confidence} | {ev} |")
        lines.append("")

    gaps = [c for c in checks if c.confidence in ("NONE", "LOW")]
    if gaps:
        lines += ["## ⚠️ High-Priority Architectural Gaps", ""]
        for g in gaps:
            lines.append(f"- **{g.clause_id} {g.clause_ref}** (weight={g.weight}): {g.normative_req}")
        lines.append("")

    lines += [
        "## 🛠 ISO 42010 Architectural Remediation Roadmap",
        "",
        "### 1. Architectural Decision Records (ADR)",
        "- Create `docs/adr/` directory and record key technical decisions in Markdown (e.g. `0001-record-architecture-decisions.md`).",
        "- Include rationale, alternatives considered, and trade-offs for major framework choices.",
        "",
        "### 2. Architecture Views & Diagrams (C4 / Mermaid)",
        "- Add a C4/Mermaid architecture diagram to `README.md` or `docs/ARCHITECTURE.md` showing system context and container boundaries.",
        "- Define explicit security, data flow, and deployment viewpoints.",
        "",
        "### 3. Consistency & NFRs",
        "- Document Quality Attributes (latency, availability, throughput goals) in `docs/NFR.md`.",
        "",
        "---",
        f"*ISO/IEC/IEEE 42010 Architecture Description Auditor · {date.today()}*",
    ]

    try:
        report_path.write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to write report to {report_path}: {e}")

    SEP = "═" * 78
    print(f"\n{SEP}")
    print(f"  ISO/IEC/IEEE 42010 ARCHITECTURE AUDIT: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 42010 Architecture Score: {score} / 100")
    print(f"  Architecture Grade          : {grade}")
    print(f"  Validated Checks            : {found_count} / {len(checks)}")
    print(f"  Audit Duration              : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 iso_42010_architecture_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        logger.error(f"Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name
    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    
    try:
        app_data.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create app data directory {app_data}: {e}")
        sys.exit(1)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"iso_42010_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    checks = scan_iso42010(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, checks, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
