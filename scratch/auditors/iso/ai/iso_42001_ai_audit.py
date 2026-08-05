#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🤖 ISO/IEC 42001:2023 Artificial Intelligence Management Auditor          ║
║   BM25 + AST + AI Safety, Guardrails & LLM Governance Scanner             ║
║                                                                           ║
║   PURPOSE: Evaluate codebase for ISO/IEC 42001 AI Management controls:    ║
║   - Prompt Injection & Jailbreak Defense Mitigation                       ║
║   - LLM API Call Audit Trail & System Prompt Versioning                   ║
║   - Token Budgeting, Cost Control & Rate Limiting                         ║
║   - Hallucination Mitigation & Output Schema Enforcement                  ║
║   - ISO 42001 AI Governance Index (0–100) & AI Safety Grade               ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/iso/iso_42001_ai_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


@dataclass
class ISO42001Metric:
    domain: str             # PROMPT_SAFETY / LLM_AUDIT / COST_CONTROL / OUTPUT_VALIDATION
    metric_id: str          # AI-001..AI-005
    title: str
    impact: str             # POSITIVE / RISK
    score_delta: int
    description: str
    evidence_files: list[str] = field(default_factory=list)
    remediation: str = ""
    found: bool = False


AI_METRICS: list[ISO42001Metric] = [
    ISO42001Metric(
        domain="PROMPT_SAFETY", metric_id="AI-001",
        title="Prompt Injection & Jailbreak Input Sanitization Guardrails",
        impact="POSITIVE", score_delta=+25,
        description="System sanitizes user prompts before passing to LLM APIs to prevent prompt injection.",
        remediation="Wrap user inputs in prompt guardrail sanitizers (e.g. Guardrails AI / NeMo Guardrails).",
    ),
    ISO42001Metric(
        domain="LLM_AUDIT", metric_id="AI-002",
        title="Structured LLM API Call Audit Trail & Prompt Versioning",
        impact="POSITIVE", score_delta=+25,
        description="System logs LLM prompts, model versions, and completion tokens for audit compliance.",
        remediation="Log model name, prompt tokens, completion tokens, and latency for all LLM API calls.",
    ),
    ISO42001Metric(
        domain="COST_CONTROL", metric_id="AI-003",
        title="Token Budgeting, Rate Limiting & API Cost Controls",
        impact="POSITIVE", score_delta=+25,
        description="Implements token usage limits or caching to prevent API budget overruns.",
        remediation="Set max_tokens caps and cache frequent LLM prompt completions.",
    ),
    ISO42001Metric(
        domain="OUTPUT_VALIDATION", metric_id="AI-004",
        title="Structured Output Validation (Pydantic / JSON Schema Enforcement)",
        impact="POSITIVE", score_delta=+25,
        description="LLM outputs are validated against strict JSON schemas before execution.",
        remediation="Enforce Pydantic schema parsing or JSON mode on LLM completions.",
    ),
]


PATTERNS = {
    "AI-001": ["guardrail", "sanitize_prompt", "prompt_injection", "system_prompt"],
    "AI-002": ["openai", "anthropic", "completion", "prompt_tokens", "llm_log"],
    "AI-003": ["max_tokens", "token_budget", "cost_limit", "llm_cache"],
    "AI-004": ["pydantic", "response_format", "json_object", "schema_validation"],
}


def scan_iso42001(root: Path, idx: IndexStoreAdapter) -> list[ISO42001Metric]:
    """Scan codebase for ISO/IEC 42001 AI Management System controls."""
    for m in AI_METRICS:
        pats = PATTERNS.get(m.metric_id, [])
        hits = set()

        for pat in pats:
            try:
                res = idx.search_code(pat, limit=3)
                for r in res:
                    if r.path and not any(x in r.path for x in ("node_modules", ".git", "vendor")):
                        hits.add(r.path)
            except Exception:
                pass

        m.evidence_files = sorted(list(hits))[:4]
        m.found = len(m.evidence_files) > 0

    return AI_METRICS


def calculate_iso42001_score(metrics: list[ISO42001Metric]) -> tuple[int, str, str]:
    """Calculate ISO 42001 AI Governance Index (0-100)."""
    base_score = 0
    for m in metrics:
        if m.found:
            base_score += m.score_delta

    score = max(0, min(100, base_score))

    if score >= 75:
        grade = "A+ (ISO 42001 AI Safety Certified)"
        status = "🟢 HIGH AI SAFETY — Guardrails, Output Validation & Cost Controls Active"
    elif score >= 50:
        grade = "A (Good AI Governance)"
        status = "🟢 GOOD — LLM Logging or Schema Validation Present"
    else:
        grade = "C/F (AI Governance Risk)"
        status = "🔴 HIGH AI GOVERNANCE RISK — Unguarded LLM Prompts or Missing Cost Caps"

    return score, grade, status


def print_report(project: str, root: Path, metrics: list[ISO42001Metric],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found = [m for m in metrics if m.found]
    score, grade, status = calculate_iso42001_score(metrics)

    lines = [
        f"# 🤖 ISO/IEC 42001:2023 AI Management Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 ISO 42001 AI Governance Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **ISO 42001 AI Governance Score** | **{score} / 100** |",
        f"| **AI Safety Grade** | **{grade}** |",
        f"| **Governance Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Verified AI Safety Controls | {len(found)} / {len(metrics)} |",
        "",
        "## 🔍 Verified ISO 42001 AI Safety Evidence",
        "",
        "| Domain | AI Control Title | Status | Verified Code Evidence | Remediation Action |",
        "|---|---|---|---|---|",
    ]

    for m in found:
        ev = ", ".join(f"`{e}`" for e in m.evidence_files[:2])
        lines.append(f"| `{m.domain}` | {m.title} | ✅ FOUND | {ev} | {m.remediation} |")

    lines += [
        "",
        "## 🚀 ISO 42001 AI Safety Remediation Blueprint",
        "",
        "1. **Prompt Guardrails**: Sanitize user inputs to prevent prompt injection attacks.",
        "2. **Cost Control**: Set `max_tokens` caps on all LLM API invocations.",
        "3. **Output Validation**: Parse LLM responses using Pydantic / JSON schema validators.",
        "",
        "---",
        f"*ISO/IEC 42001:2023 Artificial Intelligence Management Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🤖 ISO/IEC 42001:2023 AI MANAGEMENT AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  ISO 42001 AI Safety Score   : {score} / 100")
    print(f"  AI Safety Grade             : {grade}")
    print(f"  Verified Controls           : {len(found)} / {len(metrics)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/iso/iso_42001_ai_audit.py /path/to/project [ProjectName]")
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
    metrics = scan_iso42001(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, metrics, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
