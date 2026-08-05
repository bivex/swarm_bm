#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  SOSTAC® Digital Marketing & Commercial Readiness Auditor                    ║
║                                                                               ║
║  Based on PR Smith's SOSTAC® Planning Model:                                  ║
║  - S: Situation Analysis (Where are we now? Customer/Competitor/SWOT)         ║
║  - O: Objectives (Where do we want to be? 5Ss / SMART KPIs / Targets)         ║
║  - S: Strategy (How do we get there? STP / Positioning / OVP / Value Prop)    ║
║  - T: Tactics (Which marketing mix & tools? SEO / Content / Email / Ads)       ║
║  - A: Actions (Who does what & when? Responsibilities / Timelines / Workflows)║
║  - C: Control (How do we monitor & measure? Analytics / Tracking / ROI)       ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/marketing/sostac_commercial_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

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
class SOSTACCheck:
    clause_id: str          # e.g. "S.1", "O.2"
    stage: str              # SITUATION / OBJECTIVES / STRATEGY / TACTICS / ACTIONS / CONTROL
    title: str
    normative_req: str      # SOSTAC standard requirement
    weight: int
    search_terms: list[str]
    evidence_files: list[str] = field(default_factory=list)
    found: bool = False
    confidence: str = "NONE"


SOSTAC_CHECKS: list[SOSTACCheck] = [

    # ── S: Situation Analysis ────────────────────────────────────────────────
    SOSTACCheck(
        clause_id="S.1", stage="SITUATION",
        title="Target Customer Profile & Personas",
        normative_req="Define target customer demographics, pain points, and buyer personas.",
        weight=4,
        search_terms=["target_audience", "persona", "customer_profile", "user_persona",
                      "pain_points", "target_market", "customer"],
    ),
    SOSTACCheck(
        clause_id="S.2", stage="SITUATION",
        title="Competitor & Market Analysis",
        normative_req="Document market position, direct/indirect competitors, and benchmark analysis.",
        weight=3,
        search_terms=["competitors", "market_analysis", "benchmark", "competitive_landscape",
                      "swot", "market_share"],
    ),
    SOSTACCheck(
        clause_id="S.3", stage="SITUATION",
        title="Current Digital Performance / Audit Baseline",
        normative_req="Audit current digital assets, baseline conversion rates, traffic, and capabilities.",
        weight=3,
        search_terms=["audit", "baseline", "current_performance", "analytics_baseline",
                      "conversion_rate", "traffic"],
    ),

    # ── O: Objectives ────────────────────────────────────────────────────────
    SOSTACCheck(
        clause_id="O.1", stage="OBJECTIVES",
        title="Commercial & Growth Objectives (5Ss: Sell, Serve, Speak, Save, Sizzle)",
        normative_req="Establish clear commercial goals: Sales targets, Customer Service targets, Engagement goals.",
        weight=4,
        search_terms=["objective", "kpi", "sales_target", "growth_goal",
                      "conversion_target", "revenue_goal", "okr"],
    ),
    SOSTACCheck(
        clause_id="O.2", stage="OBJECTIVES",
        title="SMART Marketing Metrics & Milestones",
        normative_req="Ensure objectives are Specific, Measurable, Actionable, Relevant, and Time-bound.",
        weight=3,
        search_terms=["smart_goals", "milestones", "target_metrics", "kpi_target",
                      "timeline_goals", "monthly_target"],
    ),

    # ── S: Strategy ──────────────────────────────────────────────────────────
    SOSTACCheck(
        clause_id="S.TR.1", stage="STRATEGY",
        title="Online Value Proposition (OVP) & Positioning",
        normative_req="Articulate clear Online Value Proposition and positioning statement (Why buy from us?).",
        weight=5,
        search_terms=["value_proposition", "ovp", "positioning", "hero_headline",
                      "unique_selling_proposition", "usp", "tagline"],
    ),
    SOSTACCheck(
        clause_id="S.TR.2", stage="STRATEGY",
        title="Segmentation & Targeting (STP)",
        normative_req="Segment market by user needs/behavior and define explicit target segments.",
        weight=4,
        search_terms=["segmentation", "target_segment", "customer_segment", "niche",
                      "b2b", "b2c", "enterprise_tier"],
    ),

    # ── T: Tactics ───────────────────────────────────────────────────────────
    SOSTACCheck(
        clause_id="T.1", stage="TACTICS",
        title="SEO & Content Marketing Strategy",
        normative_req="Implement search engine optimization (meta tags, semantic HTML, keywords, content plan).",
        weight=4,
        search_terms=["seo", "meta_description", "keywords", "og:image",
                      "content_marketing", "blog", "landing_page", "sitemap"],
    ),
    SOSTACCheck(
        clause_id="T.2", stage="TACTICS",
        title="Lead Generation & Conversion Funnel",
        normative_req="Build structured lead capture forms, call-to-actions (CTAs), and conversion funnels.",
        weight=5,
        search_terms=["lead_capture", "cta", "call_to_action", "signup_form",
                      "checkout", "pricing", "free_trial", "demo_request"],
    ),
    SOSTACCheck(
        clause_id="T.3", stage="TACTICS",
        title="Email & CRM Lifecycle Automation",
        normative_req="Set up automated email onboarding, transactional messages, and CRM nurture flows.",
        weight=3,
        search_terms=["email_template", "newsletter", "onboarding_email", "crm",
                      "mailchimp", "sendgrid", "welcome_email"],
    ),

    # ── A: Actions ───────────────────────────────────────────────────────────
    SOSTACCheck(
        clause_id="A.1", stage="ACTIONS",
        title="Roles, Responsibilities & Execution Workflows",
        normative_req="Document action plans, owner responsibilities, and campaign execution workflows.",
        weight=3,
        search_terms=["action_plan", "workflow", "roadmap", "tasks",
                      "responsibilities", "owner", "campaign_schedule"],
    ),
    SOSTACCheck(
        clause_id="A.2", stage="ACTIONS",
        title="Marketing Assets & Sales Collateral",
        normative_req="Prepare pitch decks, case studies, product sheets, and media assets.",
        weight=3,
        search_terms=["pitch_deck", "case_study", "whitepaper", "brochure",
                      "demo_video", "collateral", "media_kit"],
    ),

    # ── C: Control ───────────────────────────────────────────────────────────
    SOSTACCheck(
        clause_id="C.1", stage="CONTROL",
        title="Web & Product Analytics Tracking",
        normative_req="Integrate analytics tools (Google Analytics, PostHog, Mixpanel) to measure traffic & events.",
        weight=5,
        search_terms=["analytics", "google_analytics", "gtm", "posthog",
                      "mixpanel", "plausible", "tracking_code", "event_tracking"],
    ),
    SOSTACCheck(
        clause_id="C.2", stage="CONTROL",
        title="Conversion & Event Measurement (Pixel / API)",
        normative_req="Track goal completions, funnel drop-offs, and commercial events.",
        weight=4,
        search_terms=["track_event", "conversion_tracking", "goal_completion",
                      "fb_pixel", "event_listener", "telemetry"],
    ),
    SOSTACCheck(
        clause_id="C.3", stage="CONTROL",
        title="Feedback Loops & Continuous Improvement",
        normative_req="Implement user feedback collection (surveys, NPS, reviews) and A/B testing mechanism.",
        weight=3,
        search_terms=["feedback", "nps", "user_survey", "ab_testing",
                      "reviews", "customer_feedback", "hotjar"],
    ),
]


def scan_sostac(root: Path, idx: IndexStoreAdapter) -> list[SOSTACCheck]:
    """Scan codebase for SOSTAC commercial & marketing readiness elements."""
    idx.rebuild(root)
    for check in SOSTAC_CHECKS:
        hits: set[str] = set()
        match_count = 0

        for term in check.search_terms:
            try:
                results = idx.search_code(term, limit=5)
                for r in results:
                    fp = getattr(r, 'path', None)
                    if fp and not any(x in fp for x in ("node_modules", ".git", "vendor", "__pycache__")):
                        hits.add(fp)
                        match_count += 1
            except Exception:
                pass

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

    return SOSTAC_CHECKS


def calculate_score(checks: list[SOSTACCheck]) -> tuple[int, str, str]:
    total_weight = sum(c.weight for c in checks)
    achieved = sum(
        c.weight * (1.0 if c.confidence == "HIGH" else 0.6 if c.confidence == "MEDIUM" else 0.3 if c.confidence == "LOW" else 0)
        for c in checks
    )
    score = int((achieved / total_weight) * 100) if total_weight else 0

    if score >= 75:
        grade, status = "A  (Commercial Ready / Market-Facing)", "🟢 HIGH — SOSTAC marketing & growth engine active"
    elif score >= 50:
        grade, status = "B  (Partial Marketing Engine)", "🟡 PARTIAL — Core value prop present, analytics/lead-gen gaps"
    elif score >= 25:
        grade, status = "C  (Initial Commercial Stage)", "🟠 LOW — Technical product only, lacking marketing strategy"
    else:
        grade, status = "F  (No Commercial Readiness)", "🔴 CRITICAL — Missing value proposition, CTAs and analytics"

    return score, grade, status


def print_report(project: str, root: Path, checks: list[SOSTACCheck],
                 stats: dict, elapsed: float, report_path: Path) -> None:
    score, grade, status = calculate_score(checks)
    conf_icon = {"HIGH": "✅", "MEDIUM": "🟡", "LOW": "⚠️", "NONE": "❌"}
    found_count = sum(1 for c in checks if c.found)

    by_stage: dict[str, list[SOSTACCheck]] = {}
    for c in checks:
        by_stage.setdefault(c.stage, []).append(c)

    stage_titles = {
        "SITUATION": "S — Situation Analysis (Market, Customers, Baseline)",
        "OBJECTIVES": "O — Objectives (SMART Goals & Commercial KPIs)",
        "STRATEGY": "S — Strategy (Value Proposition, STP, Positioning)",
        "TACTICS": "T — Tactics (SEO, Content, Funnel, CRM, Lead-Gen)",
        "ACTIONS": "A — Actions (Workflows, Assets, Execution Plan)",
        "CONTROL": "C — Control (Analytics, Event Tracking, Feedback)",
    }

    lines = [
        f"# 📈 SOSTAC® Digital Marketing & Commercial Readiness Audit — {project}",
        f"> `{root}` · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 Commercial Readiness Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| **SOSTAC Commercial Score** | **{score} / 100** |",
        f"| **Commercial Grade** | **{grade}** |",
        f"| **Status** | **{status}** |",
        f"| Total Files Scanned | {stats.get('total_files', 0):,} |",
        f"| Validated Marketing Elements | {found_count} / {len(checks)} |",
        "",
        "> **Model**: PR Smith's SOSTAC® Planning Model (Situation, Objectives, Strategy, Tactics, Actions, Control).",
        "",
    ]

    for stage, stage_checks in by_stage.items():
        title = stage_titles.get(stage, stage)
        lines += [
            f"## 🔍 {title}",
            "",
            "| ID | Element Title | Confidence | Evidence Files |",
            "|---|---|---|---|",
        ]
        for c in stage_checks:
            icon = conf_icon[c.confidence]
            ev = ", ".join(f"`{e}`" for e in c.evidence_files[:2]) if c.evidence_files else "—"
            lines.append(f"| `{c.clause_id}` | {c.title} | {icon} {c.confidence} | {ev} |")
        lines.append("")

    gaps = [c for c in checks if c.confidence in ("NONE", "LOW")]
    if gaps:
        lines += ["## ⚠️ Commercial & Go-To-Market Gaps", ""]
        for g in gaps:
            lines.append(f"- **{g.clause_id}** {g.title} (weight={g.weight}): {g.normative_req}")
        lines.append("")

    lines += [
        "## 🛠 SOSTAC® Go-To-Market Action Plan",
        "",
        "### 1. Strategy & Value Proposition (S & O)",
        "- Define explicit **Online Value Proposition (OVP)** on landing page / README",
        "- Set clear conversion SMART targets (e.g. 5% sign-up rate, 100 active users)",
        "",
        "### 2. Lead Generation & Tactics (T)",
        "- Build explicit CTA forms (Demo Request, Free Trial, Newsletter)",
        "- Optimize SEO meta tags (`title`, `description`, OpenGraph tags)",
        "",
        "### 3. Control & Analytics (C)",
        "- Add web analytics tracking snippet (PostHog / Google Analytics / Plausible)",
        "- Setup conversion event listeners on key CTAs and forms",
        "",
        "---",
        f"*SOSTAC® Commercial Auditor · PR Smith Planning Framework · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 78
    print(f"\n{SEP}")
    print(f"  SOSTAC® COMMERCIAL READINESS AUDIT: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  SOSTAC Commercial Score     : {score} / 100")
    print(f"  Grade                       : {grade}")
    print(f"  Validated Elements          : {found_count} / {len(checks)}")
    print(f"  Audit Duration              : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 sostac_commercial_audit.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name
    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"sostac_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    checks = scan_sostac(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, checks, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
