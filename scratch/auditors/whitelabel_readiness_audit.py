#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🏷️ Rebrand & White-Label Readiness Auditor (OEM / Reseller Edition)     ║
║   BM25 + AST + Hardcoded Branding & Multi-Tenancy & Custom Domain Scanner ║
║                                                                           ║
║   PURPOSE: Evaluate feasibility of taking open-source software,           ║
║   rebranding it, adding multi-tenancy, and selling as a White-Label SaaS.  ║
║                                                                           ║
║   - Hardcoded Vendor Branding & String Leaks (Logos, Links, Copyrights)   ║
║   - Themeability & Dynamic UI Customization (CSS Tokens, Tailwind, Themes) ║
║   - Multi-Tenancy Architecture (Tenant ID, Workspace, RLS, Schema-per-tenant)║
║   - Custom Domain & Subdomain Routing Readiness                           ║
║   - Rebrand Effort Score (0–100) & White-Label Grade (A+ to F)            ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/whitelabel_readiness_audit.py /path/to/project [ProjectName]
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
class WhiteLabelMetric:
    category: str           # BRANDING / THEMING / MULTITENANCY / DOMAINS
    metric_id: str          # WL-001, WL-002, etc.
    title: str
    impact: str             # POSITIVE / NEGATIVE
    score_delta: int        # Delta for White-Label Score
    description: str
    evidence_files: list[str] = field(default_factory=list)
    recommendation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# White-Label Rules Registry
# ─────────────────────────────────────────────────────────────────────────────
WHITELABEL_RULES: list[WhiteLabelMetric] = [

    # ── 1. HARDCODED BRANDING & LEAKS ─────────────────────────────────────────
    WhiteLabelMetric(
        category="BRANDING", metric_id="WL-001",
        title="Hardcoded Vendor Logos & Assets (favicon.ico, logo.svg/png)",
        impact="NEGATIVE", score_delta=-15,
        description="Found vendor logo images or favicons hardcoded in static asset folders.",
        recommendation="Replace hardcoded logo assets with dynamic `/api/v1/theme/logo` endpoints or environment variables.",
        found=False
    ),
    WhiteLabelMetric(
        category="BRANDING", metric_id="WL-002",
        title="Hardcoded Vendor Footers & Copyright Strings ('Powered by...')",
        impact="NEGATIVE", score_delta=-15,
        description="Found 'Powered by', vendor copyright notices, or hardcoded vendor names in UI components.",
        recommendation="Abstract brand strings into customizable config files or database tenant settings.",
        found=False
    ),
    WhiteLabelMetric(
        category="BRANDING", metric_id="WL-003",
        title="Hardcoded External Vendor Links (Discord, Docs, Github, Support)",
        impact="NEGATIVE", score_delta=-10,
        description="Found hardcoded URLs pointing to vendor documentation, Discord server, or GitHub repos.",
        recommendation="Pass help/docs URLs from tenant configuration dynamically.",
        found=False
    ),

    # ── 2. THEMEABILITY & DYNAMIC UI ──────────────────────────────────────────
    WhiteLabelMetric(
        category="THEMING", metric_id="WL-004",
        title="CSS Variables / Design Tokens (`--primary-color`, `:root`)",
        impact="POSITIVE", score_delta=+20,
        description="Codebase uses CSS variables or design tokens, enabling instant White-Label theme customization.",
        recommendation="Inject tenant primary/secondary colors into `:root` CSS variables dynamically.",
        found=False
    ),
    WhiteLabelMetric(
        category="THEMING", metric_id="WL-005",
        title="Tailwind CSS / Dynamic Theme Switcher Support",
        impact="POSITIVE", score_delta=+15,
        description="Found Tailwind config or dark/light theme switching infrastructure.",
        recommendation="Leverage Tailwind theme extension for tenant-specific color schemes.",
        found=False
    ),
    WhiteLabelMetric(
        category="THEMING", metric_id="WL-006",
        title="Dynamic Logo & Favicon Configuration API",
        impact="POSITIVE", score_delta=+15,
        description="Found existing endpoints or hooks for runtime logo/favicon upload and replacement.",
        recommendation="Store tenant logos in S3/MinIO and serve dynamically per tenant subdomain.",
        found=False
    ),

    # ── 3. MULTI-TENANCY ARCHITECTURE ─────────────────────────────────────────
    WhiteLabelMetric(
        category="MULTITENANCY", metric_id="WL-007",
        title="Native Multi-Tenancy Data Model (`tenant_id`, `org_id`, `workspace_id`)",
        impact="POSITIVE", score_delta=+25,
        description="Database models already feature tenant/organization isolation fields.",
        recommendation="Enforce automatic tenant_id filtering across all DB queries via middleware or RLS.",
        found=False
    ),
    WhiteLabelMetric(
        category="MULTITENANCY", metric_id="WL-008",
        title="Database Row-Level Security (RLS) or Schema-per-Tenant",
        impact="POSITIVE", score_delta=+20,
        description="Found PostgreSQL RLS policies or isolated schema/database connection routing.",
        recommendation="Ideal enterprise multi-tenant isolation — ready for B2B SaaS deployment.",
        found=False
    ),
    WhiteLabelMetric(
        category="MULTITENANCY", metric_id="WL-009",
        title="Single-Tenant Single-User Legacy Architecture",
        impact="NEGATIVE", score_delta=-20,
        description="Codebase lacks tenant isolation; designed for single-user or single-instance deployment.",
        recommendation="Wrap application in Docker container-per-tenant orchestrator or refactor DB models.",
        found=False
    ),

    # ── 4. CUSTOM DOMAIN & SUBDOMAIN ROUTING ──────────────────────────────────
    WhiteLabelMetric(
        category="DOMAINS", metric_id="WL-010",
        title="Subdomain Host Routing Infrastructure (`{tenant}.domain.com`)",
        impact="POSITIVE", score_delta=+15,
        description="Found middleware or router handling wildcard subdomains for tenant identification.",
        recommendation="Connect tenant lookup directly to Host header parsing middleware.",
        found=False
    ),
    WhiteLabelMetric(
        category="DOMAINS", metric_id="WL-011",
        title="Custom Domain Mapping & SSL Provisioning Support (CNAME)",
        impact="POSITIVE", score_delta=+15,
        description="Found support for custom domain CNAME routing or SSL cert auto-provisioning.",
        recommendation="Integrate Caddy / Cloudflare for automated custom domain SSL certificates.",
        found=False
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Search Patterns
# ─────────────────────────────────────────────────────────────────────────────
RULE_PATTERNS = {
    "WL-001": ["logo.svg", "logo.png", "favicon.ico", "brand-logo"],
    "WL-002": ["powered by", "copyright", "all rights reserved", "built with"],
    "WL-003": ["discord.gg", "github.com", "docs.", "support."],
    "WL-004": ["--primary", "--color-primary", ":root", "var("],
    "WL-005": ["tailwind.config", "theme:", "darkMode"],
    "WL-006": ["logo_url", "favicon_url", "upload_logo"],
    "WL-007": ["tenant_id", "org_id", "organization_id", "workspace_id"],
    "WL-008": ["ENABLE ROW LEVEL SECURITY", "schema_per_tenant", "tenant_db"],
    "WL-009": ["single_user", "admin_user", "default_user"],
    "WL-010": ["subdomain", "host.split", "req.headers.host"],
    "WL-011": ["custom_domain", "cname", "ssl_cert"],
}


def scan_whitelabel_readiness(root: Path, idx: IndexStoreAdapter) -> list[WhiteLabelMetric]:
    """Scan codebase for white-label readiness and rebrand metrics."""
    for rule in WHITELABEL_RULES:
        patterns = RULE_PATTERNS.get(rule.metric_id, [])
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

    return WHITELABEL_RULES


def calculate_whitelabel_score(rules: list[WhiteLabelMetric]) -> tuple[int, str, str]:
    """Calculate White-Label Score (0-100), Grade, and Rebrand Effort Hours."""
    base_score = 50
    for r in rules:
        if r.found:
            base_score += r.score_delta

    score = max(0, min(100, base_score))

    if score >= 85:
        grade = "A+ (Turnkey White-Label SaaS Ready)"
        effort = "5–15 hours (Trivial — CSS & Logo swap only)"
    elif score >= 70:
        grade = "A (High White-Label Potential)"
        effort = "20–40 hours (Easy — minor UI & brand string refactoring)"
    elif score >= 55:
        grade = "B (Moderate Effort Required)"
        effort = "40–80 hours (Medium — add multi-tenant DB fields)"
    elif score >= 40:
        grade = "C (Significant Refactoring Needed)"
        effort = "80–160 hours (High — refactor for tenant isolation)"
    else:
        grade = "F (Hardcoded Single-Tenant Monolith)"
        effort = "200+ hours (Container-per-tenant strategy recommended)"

    return score, grade, effort


def build_report(project: str, root: Path, rules: list[WhiteLabelMetric],
                 stats: dict, elapsed: float, report_path: Path) -> str:
    found_rules = [r for r in rules if r.found]
    score, grade, effort = calculate_whitelabel_score(rules)

    positives = [r for r in found_rules if r.impact == "POSITIVE"]
    negatives = [r for r in found_rules if r.impact == "NEGATIVE"]

    lines = [
        f"# 🏷️ Rebrand & White-Label Readiness Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📋 White-Label Opportunity Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **White-Label Readiness Score** | **{score} / 100** |",
        f"| **OEM / Reseller Rating** | **{grade}** |",
        f"| **Estimated Rebrand Effort** | **{effort}** |",
        f"| Codebase Files Scanned | {stats.get('total_files', 0):,} |",
        f"| White-Label Enablers (Found) | {len(positives)} |",
        f"| Hardcoded Leaks & Obstacles | {len(negatives)} |",
        "",
    ]

    lines += ["## 🚀 White-Label Enablers & Strengths", ""]
    if positives:
        for r in positives:
            ev = ", ".join(f"`{e}`" for e in r.evidence_files)
            lines.append(f"### 🟢 [{r.metric_id}] {r.title} (+{r.score_delta} pts)")
            lines.append(f"**Description:** {r.description}")
            lines.append(f"**Evidence:** {ev}")
            lines.append(f"**Action:** {r.recommendation}")
            lines.append("")
    else:
        lines.append("*No automated White-Label enablers detected in core codebase.*")
        lines.append("")

    lines += ["## ⚠️ Hardcoded Leaks & Rebrand Obstacles", ""]
    if negatives:
        for r in negatives:
            ev = ", ".join(f"`{e}`" for e in r.evidence_files)
            lines.append(f"### 🔴 [{r.metric_id}] {r.title} ({r.score_delta} pts)")
            lines.append(f"**Description:** {r.description}")
            lines.append(f"**Evidence:** {ev}")
            lines.append(f"**Fix:** {r.recommendation}")
            lines.append("")
    else:
        lines.append("*Zero hardcoded branding leaks detected! Perfect clean slate for rebranding.*")
        lines.append("")

    lines += [
        "## 💡 4-Step White-Label SaaS Commercial Blueprint",
        "",
        "1. **Asset & String Abstraction**: Move all logos, favicons, and company names into `/config/branding.json`.",
        "2. **Dynamic CSS Variables**: Map primary and secondary UI colors to tenant database settings.",
        "3. **Subdomain Router**: Use host header middleware to resolve `tenant.your-saas.com` to tenant ID.",
        "4. **Custom Domain SSL**: Add Caddy / Cloudflare API for 1-click customer CNAME custom domains.",
        "",
        "---",
        f"*Rebrand & White-Label Readiness Auditor · OEM Edition · {date.today()}*",
    ]

    content = "\n".join(lines)
    report_path.write_text(content, encoding="utf-8")
    return content


def print_console(project: str, root: Path, rules: list[WhiteLabelMetric],
                  stats: dict, elapsed: float) -> None:
    found_rules = [r for r in rules if r.found]
    score, grade, effort = calculate_whitelabel_score(rules)

    SEP = "═" * 75
    sep = "─" * 75

    print(f"\n{SEP}")
    print(f"  🏷️ WHITE-LABEL & REBRAND READINESS AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed          : {stats.get('total_files', 0):,}")
    print(f"  White-Label Score      : {score} / 100")
    print(f"  Reseller Grade         : {grade}")
    print(f"  Rebrand Effort Est.    : {effort}")
    print(f"  Active Indicators      : {len(found_rules)} / {len(rules)}")
    print(f"  Scan speed             : {elapsed:.3f}s")
    print(sep)

    for r in found_rules:
        icon = "🟢" if r.impact == "POSITIVE" else "🔴"
        delta = f"+{r.score_delta}" if r.score_delta > 0 else str(r.score_delta)
        ev = ", ".join(r.evidence_files[:2]) if r.evidence_files else "Scanned"
        print(f"  {icon} [{r.metric_id}] {r.title:<50s} ({delta} pts)")
        print(f"     📁 Evidence: {ev}")

    print(f"\n{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/whitelabel_readiness_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"whitelabel_readiness_{safe_name}.md"

    print(f"\n  🏷️ White-Label Readiness Auditor — {project_name}")
    print(f"  📁 {project_path}")
    print(f"  ⏳ Building BM25 index...", end="", flush=True)

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    t_index = time.perf_counter() - t0
    print(f" {stats.get('total_files', 0):,} files in {t_index*1000:.0f}ms")

    print(f"  🔎 Running White-Label & Rebrand checks...", end="", flush=True)
    t1 = time.perf_counter()
    rules = scan_whitelabel_readiness(project_path, idx)
    t_detect = time.perf_counter() - t1
    found_count = sum(1 for r in rules if r.found)
    print(f" {found_count} metrics in {t_detect*1000:.0f}ms")

    elapsed = time.perf_counter() - t0

    print_console(project_name, project_path, rules, stats, elapsed)
    build_report(project_name, project_path, rules, stats, elapsed, report_path)

    print(f"  [+] White-Label report saved → {report_path}")
    print("═" * 75 + "\n")


if __name__ == "__main__":
    main()
