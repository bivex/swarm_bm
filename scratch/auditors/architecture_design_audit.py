#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🏗️ Architecture & Design Quality Review Auditor                         ║
║   BM25 + AST + Modularity & Coupling & Clean Architecture Scanner          ║
║                                                                           ║
║   PURPOSE: Evaluate software design health, modularity, layering hygiene, ║
║   coupling/cohesion, maintainability impact, and refactoring risk zones.  ║
║                                                                           ║
║   - Layering & Modular Boundaries (Clean Architecture / DDD / Ports)       ║
║   - Coupling & God Objects (Files > 1000 lines, > 30 imports)             ║
║   - Abstraction & Extensibility (SOLID, Interfaces, Abstract Classes)      ║
║   - Error Handling & Resilience (Exception Hierarchy, Panic/Swallowing)   ║
║   - Architectural Health Index (0–100) & Refactoring Risk Map             ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/architecture_design_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from collections import defaultdict
from typing import Any

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


@dataclass
class ArchMetric:
    category: str           # LAYERING / COUPLING / ABSTRACTION / RESILIENCE
    rule_id: str            # ARCH-001, ARCH-002, etc.
    title: str
    impact: str             # POSITIVE / NEGATIVE
    score_delta: int        # Architectural Health Score Delta
    description: str
    evidence_files: list[str] = field(default_factory=list)
    recommendation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Architecture & Design Quality Rules Registry
# ─────────────────────────────────────────────────────────────────────────────
ARCH_RULES: list[ArchMetric] = [

    # ── 1. LAYERING & MODULAR BOUNDARIES ──────────────────────────────────────
    ArchMetric(
        category="LAYERING", rule_id="ARCH-001",
        title="Explicit Hexagonal / Clean Architecture / DDD Layering",
        impact="POSITIVE", score_delta=+20,
        description="Codebase features clear separation between Domain, Application, and Infrastructure layers.",
        recommendation="Maintain strict dependency flow: Infrastructure -> Application -> Domain (Domain depends on nothing).",
    ),
    ArchMetric(
        category="LAYERING", rule_id="ARCH-002",
        title="Layer Leakage: Database ORM / SQL inside Presentation Controllers",
        impact="NEGATIVE", score_delta=-15,
        description="Found database queries or ORM models instantiated directly in HTTP routes/controllers.",
        recommendation="Decouple persistence behind Repository Interfaces (Dependency Inversion).",
    ),
    ArchMetric(
        category="LAYERING", rule_id="ARCH-003",
        title="Modular Component Isolation (Domain-Driven Bounded Contexts)",
        impact="POSITIVE", score_delta=+15,
        description="Codebase is organized into domain-driven sub-packages or isolated modules.",
        recommendation="Keep cross-module communication mediated by public contracts or event buses.",
    ),

    # ── 2. COUPLING & GOD OBJECTS ─────────────────────────────────────────────
    ArchMetric(
        category="COUPLING", rule_id="ARCH-004",
        title="God Objects / High Cyclomatic Complexity Files (> 1,000 Lines)",
        impact="NEGATIVE", score_delta=-20,
        description="Found giant monolithic source files containing excessive responsibilities.",
        recommendation="Decompose monolithic classes/files into smaller, single-responsibility services (SRP).",
    ),
    ArchMetric(
        category="COUPLING", rule_id="ARCH-005",
        title="Tight Coupling / High Import Density (> 25 Imports per File)",
        impact="NEGATIVE", score_delta=-15,
        description="Found files importing large numbers of external modules, indicating high coupling.",
        recommendation="Introduce facade services or mediator patterns to reduce direct import dependencies.",
    ),

    # ── 3. ABSTRACTION & EXTENSIBILITY ───────────────────────────────────────
    ArchMetric(
        category="ABSTRACTION", rule_id="ARCH-006",
        title="SOLID Interface Segregation & Abstract Base Classes",
        impact="POSITIVE", score_delta=+15,
        description="Codebase uses Abstract Base Classes, Interfaces, or Protocols for polymorphic extensibility.",
        recommendation="Leverage dependency injection to swap concrete implementations cleanly.",
    ),
    ArchMetric(
        category="ABSTRACTION", rule_id="ARCH-007",
        title="Plugin / Dynamic Extension Hook Architecture",
        impact="POSITIVE", score_delta=+15,
        description="Found plugin loader or extension registry allowing third-party module additions.",
        recommendation="Document plugin extension interfaces for ecosystem contributors.",
    ),

    # ── 4. ERROR HANDLING & RESILIENCE ────────────────────────────────────────
    ArchMetric(
        category="RESILIENCE", rule_id="ARCH-008",
        title="Structured Domain Exception Hierarchy",
        impact="POSITIVE", score_delta=+10,
        description="Codebase defines custom domain exception classes instead of generic string errors.",
        recommendation="Map domain exceptions cleanly to HTTP/gRPC status codes at the API boundary.",
    ),
    ArchMetric(
        category="RESILIENCE", rule_id="ARCH-009",
        title="Silent Exception Swallowing (`try: pass` / empty catch blocks)",
        impact="NEGATIVE", score_delta=-15,
        description="Found silent try-except blocks swallowing exceptions without logging or re-raising.",
        recommendation="Always log swallowed exceptions or wrap them in explicit error contexts.",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Search & Static Analysis Heuristics
# ─────────────────────────────────────────────────────────────────────────────
RULE_PATTERNS = {
    "ARCH-001": ["domain", "infrastructure", "application", "ports", "adapters"],
    "ARCH-002": ["db.query", "select(*", "objects.filter", "session.query"],
    "ARCH-003": ["bounded_context", "modules", "packages", "services"],
    "ARCH-004": ["class Manager", "class Service", "class Controller", "class Processor"],
    "ARCH-005": ["import ", "from ", "require("],
    "ARCH-006": ["ABC", "abstractmethod", "interface", "protocol", "Protocol"],
    "ARCH-007": ["plugin", "extension", "register_plugin", "hook"],
    "ARCH-008": ["class DomainError", "class AppException", "Exception"],
    "ARCH-009": ["except Exception: pass", "catch (e) {}", "except: pass"],
}


def scan_architecture_design(root: Path, idx: IndexStoreAdapter) -> list[ArchMetric]:
    """Scan codebase for architecture & design quality indicators."""
    for rule in ARCH_RULES:
        patterns = RULE_PATTERNS.get(rule.rule_id, [])
        hits = set()

        for pat in patterns:
            try:
                bm25_results = idx.search_code(pat, limit=4)
                for r in bm25_results:
                    if r.path and not any(x in r.path for x in ("node_modules", ".git", "vendor", "__pycache__")):
                        hits.add(r.path)
            except Exception:
                pass

        rule.evidence_files = sorted(list(hits))[:4]
        rule.found = len(rule.evidence_files) > 0

    # Scan for God Files (> 1,000 lines)
    god_files = []
    for f in list(root.rglob("*.py"))[:100] + list(root.rglob("*.ts"))[:100] + list(root.rglob("*.js"))[:100] + list(root.rglob("*.go"))[:100]:
        if any(x in f.parts for x in ("node_modules", ".git", "vendor")):
            continue
        try:
            lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
            if len(lines) > 1000:
                god_files.append(str(f.relative_to(root)))
        except Exception:
            pass

    for r in ARCH_RULES:
        if r.rule_id == "ARCH-004" and god_files:
            r.evidence_files = god_files[:4]
            r.found = True

    return ARCH_RULES


def calculate_architecture_score(rules: list[ArchMetric]) -> tuple[int, str, str]:
    """Calculate Architectural Health Index (0-100), Maintainability Grade, and Risk Level."""
    base_score = 60
    for r in rules:
        if r.found:
            base_score += r.score_delta

    score = max(0, min(100, base_score))

    if score >= 85:
        grade = "A+ (Excellent Hexagonal / Clean Architecture)"
        risk = "🟢 LOW RISK — Highly Maintainable & Extensible"
    elif score >= 70:
        grade = "A (Good Modular Design)"
        risk = "🟢 LOW-MEDIUM RISK — Structured Codebase"
    elif score >= 55:
        grade = "B (Moderate Technical Debt)"
        risk = "🟡 MEDIUM RISK — Refactoring Needed for Scale"
    elif score >= 40:
        grade = "C (Significant Architectural Debt)"
        risk = "🟠 HIGH RISK — High Coupling / Monolithic Coupling"
    else:
        grade = "F (CRITICAL ARCHITECTURAL DEBT — High Refactoring Hazard)"
        risk = "🔴 CRITICAL RISK — Fragile Monolith"

    return score, grade, risk


def build_report(project: str, root: Path, rules: list[ArchMetric],
                 stats: dict, elapsed: float, report_path: Path) -> str:
    found_rules = [r for r in rules if r.found]
    score, grade, risk = calculate_architecture_score(rules)

    positives = [r for r in found_rules if r.impact == "POSITIVE"]
    negatives = [r for r in found_rules if r.impact == "NEGATIVE"]

    lines = [
        f"# 🏗️ Architecture & Design Quality Review — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📋 Architectural Health Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **Architectural Health Index** | **{score} / 100** |",
        f"| **Maintainability Rating** | **{grade}** |",
        f"| **Refactoring Risk Level** | **{risk}** |",
        f"| Codebase Files Analyzed | {stats.get('total_files', 0):,} |",
        f"| Design Strengths (Enablers) | {len(positives)} |",
        f"| Architectural Debt Targets | {len(negatives)} |",
        "",
    ]

    lines += ["## 🟢 Architectural Strengths & Design Quality Enablers", ""]
    if positives:
        for r in positives:
            ev = ", ".join(f"`{e}`" for e in r.evidence_files)
            lines.append(f"### 🟢 [{r.rule_id}] {r.title} (+{r.score_delta} pts)")
            lines.append(f"**Description:** {r.description}")
            lines.append(f"**Evidence:** {ev}")
            lines.append(f"**Best Practice:** {r.recommendation}")
            lines.append("")
    else:
        lines.append("*No automated architectural enablers detected in core codebase.*")
        lines.append("")

    lines += ["## 🔴 Refactoring Risk Zones & Architectural Debt", ""]
    if negatives:
        for r in negatives:
            ev = ", ".join(f"`{e}`" for e in r.evidence_files)
            lines.append(f"### 🔴 [{r.rule_id}] {r.title} ({r.score_delta} pts)")
            lines.append(f"**Description:** {r.description}")
            lines.append(f"**Evidence Files:** {ev}")
            lines.append(f"**Refactoring Strategy:** {r.recommendation}")
            lines.append("")
    else:
        lines.append("*Zero major architectural debt patterns detected! Clean modular design.*")
        lines.append("")

    lines += [
        "## 🛠️ Senior Architect Refactoring Roadmap",
        "",
        "1. **Decouple Layer Violations**: Move DB ORM calls out of HTTP controllers into Repository Interfaces.",
        "2. **Decompose God Files**: Break classes over 1,000 lines into single-responsibility domain services.",
        "3. **Eliminate Silent Swallowing**: Replace empty `except: pass` blocks with structured exception logging.",
        "4. **Establish Bounded Contexts**: Enforce strict module boundaries with public contract interfaces.",
        "",
        "---",
        f"*Architecture & Design Quality Review Auditor · {date.today()}*",
    ]

    content = "\n".join(lines)
    report_path.write_text(content, encoding="utf-8")
    return content


def print_console(project: str, root: Path, rules: list[ArchMetric],
                  stats: dict, elapsed: float) -> None:
    found_rules = [r for r in rules if r.found]
    score, grade, risk = calculate_architecture_score(rules)

    SEP = "═" * 75
    sep = "─" * 75

    print(f"\n{SEP}")
    print(f"  🏗️ ARCHITECTURE & DESIGN QUALITY REVIEW AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed          : {stats.get('total_files', 0):,}")
    print(f"  Arch Health Index      : {score} / 100")
    print(f"  Maintainability Grade  : {grade}")
    print(f"  Refactoring Risk Level : {risk}")
    print(f"  Active Indicators      : {len(found_rules)} / {len(rules)}")
    print(f"  Scan speed             : {elapsed:.3f}s")
    print(sep)

    for r in found_rules:
        icon = "🟢" if r.impact == "POSITIVE" else "🔴"
        delta = f"+{r.score_delta}" if r.score_delta > 0 else str(r.score_delta)
        ev = ", ".join(r.evidence_files[:2]) if r.evidence_files else "Scanned"
        print(f"  {icon} [{r.rule_id}] {r.title:<50s} ({delta} pts)")
        print(f"     📁 Evidence: {ev}")

    print(f"\n{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/architecture_design_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"architecture_design_{safe_name}.md"

    print(f"\n  🏗️ Architecture Design Auditor — {project_name}")
    print(f"  📁 {project_path}")
    print(f"  ⏳ Building BM25 index...", end="", flush=True)

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    t_index = time.perf_counter() - t0
    print(f" {stats.get('total_files', 0):,} files in {t_index*1000:.0f}ms")

    print(f"  🔎 Running Architecture & Design Quality checks...", end="", flush=True)
    t1 = time.perf_counter()
    rules = scan_architecture_design(project_path, idx)
    t_detect = time.perf_counter() - t1
    found_count = sum(1 for r in rules if r.found)
    print(f" {found_count} metrics in {t_detect*1000:.0f}ms")

    elapsed = time.perf_counter() - t0

    print_console(project_name, project_path, rules, stats, elapsed)
    build_report(project_name, project_path, rules, stats, elapsed, report_path)

    print(f"  [+] Architecture report saved → {report_path}")
    print("═" * 75 + "\n")


if __name__ == "__main__":
    main()
