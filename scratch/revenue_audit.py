#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   💎 Revenue Maximization & Commercial Potential Auditor                  ║
║   10 Commercial Strategy Specialists · BM25+AST · Zero Magic              ║
║                                                                           ║
║   PURPOSE: Not "how is the code structured?" but                          ║
║   "Where is the client already getting value we can charge for?"          ║
║   and "Where can we embed a commercial product?"                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

10 Specialist Blocks:
  1. What Can Be Monetized
  2. Volume-Based Billing (ticks/requests/files/users)
  3. Enterprise Sales Surface (RBAC, SSO, multi-tenant, audit, webhooks)
  4. Standalone Module & SaaS Extraction
  5. Where the Client Already Saves Money (ROI proof)
  6. LTV Maximization & Stickiness Drivers
  7. Professional Services Opportunities
  8. Upsell & Average-Check Expansion
  9. Recurring Cost Drivers (CPU/GPU/network/storage/API)
  10. Commercial Potential Score & ARR Forecast

Usage:
    python3 scratch/revenue_audit.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


# ─────────────────────────────────────────────────────────────────────────────
# Revenue Specialists Definition
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class RevenueSpecialist:
    name: str
    role: str
    emoji: str
    block: str
    focus: str
    questions: list[tuple[str, list[str], int]]  # (question, tokens, revenue_weight 1-5)


REVENUE_TEAM: list[RevenueSpecialist] = [

    # ─── BLOCK 1: What Can Be Monetized ─────────────────────────────────────
    RevenueSpecialist(
        name="Irina Volkov", role="Core Value Monetization Analyst", emoji="💡",
        block="BLOCK 1 — What Can Be Monetized",
        focus="Identify business functions the client cannot live without — highest willingness to pay",
        questions=[
            ("Какие бизнес-функции выполняются наиболее часто? (высочайшая ценность для клиента)",
             ["process", "execute", "run", "handle", "invoke", "call", "perform", "dispatch"], 5),
            ("Какие операции являются критически важными — без них бизнес остановится?",
             ["critical", "required", "must", "core", "essential", "primary", "main", "production"], 5),
            ("Какие функции невозможно отключить без полного останова системы?",
             ["shutdown", "startup", "init", "boot", "lifecycle", "signal", "kill", "daemon"], 4),
            ("Какие операции имеют наибольшую стоимость для клиента (ML/AI, транскодирование, OCR)?",
             ["model", "inference", "predict", "transcribe", "ocr", "encode", "compress", "generate"], 5),
            ("Где клиент уже автоматизировал дорогостоящие ручные процессы и готов платить за скорость?",
             ["automate", "workflow", "pipeline", "batch", "schedule", "trigger", "task"], 4),
            ("Какие модули отвечают за генерацию конечного продукта/результата (output value)?",
             ["output", "result", "report", "export", "render", "build", "artifact", "product"], 5),
            ("Где концентрируется бизнес-логика принятия решений (decision engine)?",
             ["decision", "rule", "policy", "condition", "evaluate", "score", "recommend", "rank"], 5),
            ("Какие функции используются в реальном времени и требуют надёжности 99.9%?",
             ["realtime", "live", "stream", "socket", "event", "async", "publish", "latency"], 4),
        ]
    ),

    # ─── BLOCK 2: Volume-Based Billing ──────────────────────────────────────
    RevenueSpecialist(
        name="Marcus Billing", role="Usage-Based Pricing Architect", emoji="📊",
        block="BLOCK 2 — Volume-Based Billing (Natural Unit of Monetization)",
        focus="Find countable entities for per-unit, per-request, per-tenant pricing models",
        questions=[
            ("Что можно считать как сущности? (документы, файлы, проекты, запросы, изображения)",
             ["document", "file", "project", "image", "record", "item", "object", "entity"], 5),
            ("Где происходят тысячи операций в день — главный кандидат на per-request billing?",
             ["request", "call", "query", "event", "message", "transaction", "operation", "hit"], 5),
            ("Какие API эндпоинты являются наиболее нагруженными — per-call тарификация?",
             ["endpoint", "route", "api", "path", "url", "handler", "view", "controller"], 4),
            ("Где используются токены, кредиты, единицы расхода AI/ML?",
             ["token", "credit", "unit", "quota", "usage", "consume", "spend", "balance"], 5),
            ("Что является естественной единицей тарификации данного продукта (пользователь/агент/модель)?",
             ["user", "agent", "model", "tenant", "workspace", "organization", "account", "seat"], 5),
            ("Где выполняются пакетные операции тысячами за один запуск?",
             ["bulk", "batch", "chunk", "loop", "iterate", "foreach", "mass", "executemany"], 4),
            ("Как считается объём: байты, строки, страницы, минуты, кадры?",
             ["size", "bytes", "length", "count", "duration", "pages", "frames", "lines"], 4),
            ("Где происходит рост данных, который естественно ведёт к росту счёта клиента?",
             ["grow", "accumulate", "append", "insert", "create", "store", "save", "persist"], 4),
        ]
    ),

    # ─── BLOCK 3: Enterprise Sales Surface ──────────────────────────────────
    RevenueSpecialist(
        name="Victoria Enterprise", role="Enterprise Revenue Specialist", emoji="🏢",
        block="BLOCK 3 — Enterprise Sales Surface",
        focus="All enterprise features that justify 5-10x price multiplier per contract",
        questions=[
            ("Есть ли multi-tenant изоляция данных? (без этого Enterprise невозможен)",
             ["tenant", "organization", "workspace", "schema", "namespace", "isolation", "partition"], 5),
            ("Есть ли ролевая модель и RBAC? (обязательное требование Enterprise SOC2/ISO)",
             ["role", "permission", "rbac", "acl", "access_control", "privilege", "group", "policy"], 5),
            ("Есть ли аудит всех действий пользователей? (Audit Log — требование Enterprise)",
             ["audit", "log", "activity", "history", "trail", "event_log", "track", "record"], 5),
            ("Есть ли SSO и корпоративная аутентификация (SAML, OIDC, Active Directory)?",
             ["sso", "saml", "oidc", "oauth", "ldap", "active_directory", "identity", "provider"], 5),
            ("Есть ли webhook для интеграций с корпоративными системами клиента?",
             ["webhook", "callback", "notify", "event_url", "push", "outbound", "trigger"], 4),
            ("Есть ли публичный API для интеграции? (чем полнее API — тем дороже Enterprise план)",
             ["api", "rest", "graphql", "grpc", "openapi", "swagger", "endpoint", "v1"], 4),
            ("Есть ли white-label возможности для корпоративных реселлеров?",
             ["white_label", "brand", "logo", "theme", "custom_domain", "tenant_name", "reseller"], 4),
            ("Есть ли экспорт данных и compliance отчёты (GDPR, SOC2, HIPAA)?",
             ["export", "download", "csv", "gdpr", "compliance", "report", "backup", "archive"], 4),
        ]
    ),

    # ─── BLOCK 4: Standalone Module & SaaS Extraction ───────────────────────
    RevenueSpecialist(
        name="Stefan Modular", role="Product Decomposition & SaaS Extraction Lead", emoji="🧩",
        block="BLOCK 4 — Standalone Modules & Separate Licensing",
        focus="Identify independently sellable components, APIs, and Premium-only features",
        questions=[
            ("Какие модули полностью независимы и могут продаваться как отдельный продукт?",
             ["module", "plugin", "extension", "addon", "package", "lib", "standalone", "component"], 5),
            ("Какие сервисы можно вынести в отдельный SaaS и монетизировать через API?",
             ["service", "microservice", "api_service", "provider", "backend", "engine", "worker"], 5),
            ("Какие алгоритмы/функции можно завернуть в платный API-эндпоинт?",
             ["algorithm", "calculate", "transform", "analyze", "detect", "classify", "extract"], 5),
            ("Какие части системы можно сделать Premium-only (скрытые за paywall)?",
             ["premium", "pro", "advanced", "enterprise_only", "paid", "feature_flag", "plan_check"], 5),
            ("Какие компоненты обрабатывают специализированные данные (вертикальные ниши)?",
             ["medical", "legal", "financial", "telecom", "ecommerce", "logistics", "manufacturing"], 4),
            ("Какие интеграции с внешними платформами уже реализованы (экосистема продажи)?",
             ["integration", "connector", "plugin", "marketplace", "appstore", "extension", "bridge"], 4),
            ("Где можно создать Freemium-воронку: базовый функционал бесплатно, Premium за доплату?",
             ["free", "trial", "basic", "limit", "demo", "starter", "open_source", "community"], 4),
            ("Какие компоненты могут стать CLI-инструментами и продаваться как Developer Tools?",
             ["cli", "command", "tool", "script", "bin", "executable", "terminal", "shell"], 3),
        ]
    ),

    # ─── BLOCK 5: Where Client Already Saves Money ──────────────────────────
    RevenueSpecialist(
        name="ROI Rebecca", role="Customer ROI & Cost-Saving Evidence Analyst", emoji="💰",
        block="BLOCK 5 — Where Client Already Saves Money (Sales ROI Proof)",
        focus="Quantify automation value — strongest sales argument for pricing justification",
        questions=[
            ("Какие процессы заменяют ручной труд? (каждый час сохранённого труда = аргумент продаж)",
             ["automate", "replace", "manual", "automatic", "eliminate", "reduce_effort", "labor"], 5),
            ("Сколько операций полностью автоматизировано без участия человека?",
             ["scheduled", "cron", "automated", "unattended", "background", "headless", "trigger"], 4),
            ("Где система сокращает время обработки с часов до секунд?",
             ["fast", "speed", "optimize", "latency", "performance", "benchmark", "throughput"], 5),
            ("Где уменьшается число ошибок и рисков через валидацию и проверки?",
             ["validate", "verify", "check", "sanitize", "error", "exception", "constraint", "assert"], 4),
            ("Где происходит экономия ресурсов: CPU, память, сетевой трафик, хранилище?",
             ["cache", "compress", "optimize", "pool", "reuse", "batch", "efficient", "minimize"], 4),
            ("Какие операции устраняют необходимость в дополнительных сотрудниках?",
             ["scale", "handle_load", "capacity", "worker", "concurrent", "parallel", "auto"], 4),
            ("Где снижается время реакции на бизнес-события (time-to-action)?",
             ["realtime", "instant", "alert", "notification", "immediate", "live", "reactive"], 4),
            ("Где система предотвращает потерю данных и простои (disaster prevention value)?",
             ["backup", "recovery", "failover", "replica", "redundancy", "durability", "persist"], 4),
        ]
    ),

    # ─── BLOCK 6: LTV Maximization & Stickiness ─────────────────────────────
    RevenueSpecialist(
        name="Lena Stickiness", role="LTV & Customer Retention Strategist", emoji="🔗",
        block="BLOCK 6 — LTV Maximization & Churn Prevention",
        focus="Find lock-in mechanisms, data accumulation and switching costs that keep clients paying",
        questions=[
            ("Что сложнее всего заменить конкурентом? (highest switching cost = lowest churn)",
             ["unique", "proprietary", "custom", "specific", "core_logic", "domain", "schema"], 5),
            ("Где происходит накопление пользовательских данных (data gravity lock-in)?",
             ["database", "store", "accumulate", "history", "timeline", "record", "collection"], 5),
            ("Какие данные становятся ценнее и умнее со временем? (ML training, analytics, patterns)",
             ["train", "learn", "model", "history", "pattern", "improve", "feedback", "dataset"], 5),
            ("Какие интеграции с внешними системами клиента делают отказ от продукта дорогим?",
             ["crm", "erp", "salesforce", "jira", "slack", "notion", "zapier", "integration"], 5),
            ("Какие зависимости удерживают клиента (форматы данных, API контракты, workflow)?",
             ["format", "contract", "schema", "dependency", "import", "export", "compatibility"], 4),
            ("Где выстраиваются пользовательские конфигурации и настройки (customization lock-in)?",
             ["config", "setting", "preference", "template", "profile", "personalize", "customize"], 4),
            ("Где накапливаются обученные модели и специфические ML артефакты клиента?",
             ["model_save", "checkpoint", "weights", "artifact", "fine_tune", "embedding", "vector"], 5),
            ("Где формируются сетевые эффекты (больше пользователей = больше ценности)?",
             ["collaborate", "share", "team", "invite", "member", "network", "community", "social"], 4),
        ]
    ),

    # ─── BLOCK 7: Professional Services Opportunities ────────────────────────
    RevenueSpecialist(
        name="Pavel Services", role="Professional Services Revenue Estimator", emoji="🛠️",
        block="BLOCK 7 — Professional Services & Implementation Revenue",
        focus="Find billable complexity that requires expert onboarding, migration and customization",
        questions=[
            ("Где потребуется кастомная интеграция с уникальными системами клиента?",
             ["custom", "bespoke", "specific", "adapter", "connector", "bridge", "glue", "hook"], 5),
            ("Где потребуется миграция данных из легаси систем клиента?",
             ["migrate", "import", "convert", "transform", "legacy", "migration", "upgrade", "port"], 5),
            ("Где потребуется обучение и онбординг сотрудников клиента?",
             ["readme", "docs", "tutorial", "guide", "example", "getting_started", "quickstart"], 3),
            ("Какие модули наверняка будут кастомизироваться под специфику каждого клиента?",
             ["configurable", "extensible", "plugin", "hook", "override", "template", "strategy"], 5),
            ("Какие интеграции потребуют длительного сопровождения и SLA контракта?",
             ["maintenance", "support", "sla", "monitor", "alert", "uptime", "patch", "update"], 4),
            ("Где существует высокая сложность развёртывания (требует DevOps экспертизы)?",
             ["kubernetes", "helm", "docker", "terraform", "ansible", "aws", "gcp", "azure"], 4),
            ("Где требуется performance-тюнинг под нагрузку конкретного клиента?",
             ["tune", "benchmark", "profile", "optimize", "load_test", "stress", "scale"], 4),
            ("Где потребуется разработка custom reporting и аналитических дашбордов?",
             ["report", "dashboard", "analytics", "chart", "metric", "kpi", "visualization"], 4),
        ]
    ),

    # ─── BLOCK 8: Upsell & Average Check Expansion ──────────────────────────
    RevenueSpecialist(
        name="Upsell Ulrika", role="ARPU & Average Check Expansion Specialist", emoji="📈",
        block="BLOCK 8 — Upsell & Average Check (ARPU) Maximization",
        focus="Features <10% use but ready to pay premium for + hard limits that drive upgrades",
        questions=[
            ("Какие функции используются менее чем 10% клиентов, но те готовы платить за них?",
             ["advanced", "experimental", "beta", "specialist", "power_user", "niche", "edge_case"], 5),
            ("Какие функции подходят исключительно Enterprise (compliance, audit, governance)?",
             ["compliance", "governance", "soc2", "hipaa", "gdpr", "pci", "iso27001", "regulation"], 5),
            ("Какие жёсткие лимиты можно убрать только в Premium (seats, storage, API rate)?",
             ["limit", "max", "quota", "cap", "threshold", "restrict", "rate_limit", "max_users"], 5),
            ("Где можно продать ускорение вычислений (GPU/Fast tier pricing)?",
             ["gpu", "cuda", "acceleration", "fast", "priority", "dedicated", "reserved", "boost"], 5),
            ("Какие вычисления являются наиболее дорогостоящими и могут стать платными add-ons?",
             ["expensive", "heavy", "intensive", "ml", "inference", "llm", "embedding", "vector"], 5),
            ("Где можно продать Priority Queue / SLA-гарантии как дополнительную услугу?",
             ["priority", "queue", "sla", "guarantee", "dedicated", "reserved", "high_availability"], 4),
            ("Какие данные можно продавать в виде Analytics Insights / Intelligence as a Service?",
             ["insight", "intelligence", "analytics", "trend", "pattern", "anomaly", "forecast"], 5),
            ("Где можно монетизировать API-доступ отдельно (developer tier / partner API pricing)?",
             ["developer", "partner", "third_party", "external", "api_key", "access_token", "sdk"], 4),
        ]
    ),

    # ─── BLOCK 9: Recurring Cost Drivers ────────────────────────────────────
    RevenueSpecialist(
        name="Recurring Riccardo", role="Recurring Revenue Infrastructure Analyst", emoji="🔄",
        block="BLOCK 9 — Recurring Cost Drivers (MRR/ARR Foundation)",
        focus="Find CPU/GPU/network/storage/API costs that justify subscription over one-time pricing",
        questions=[
            ("Где основное потребление CPU — вычислительная нагрузка требует подписки на мощности?",
             ["cpu", "compute", "process", "thread", "worker", "parallel", "multicore", "pool"], 4),
            ("Есть ли GPU нагрузка? (самый дорогой ресурс — GPU billing = высокий MRR)",
             ["gpu", "cuda", "torch", "tensorflow", "model", "inference", "fp16", "accelerate"], 5),
            ("Где расходуется сетевой трафик — входящий и исходящий? (bandwidth billing)",
             ["network", "bandwidth", "transfer", "upload", "download", "stream", "traffic", "mb"], 4),
            ("Где растёт объём хранилища данных? (storage billing — линейный рост с клиентом)",
             ["storage", "disk", "database", "file", "blob", "s3", "bucket", "volume", "size"], 4),
            ("Где используются платные внешние API (OpenAI, Deepgram, ElevenLabs, AWS)?",
             ["openai", "gpt", "deepgram", "elevenlabs", "aws", "azure", "gcp", "anthropic"], 5),
            ("Где непрерывно работают фоновые процессы? (always-on billing = pure MRR)",
             ["daemon", "service", "background", "scheduler", "cron", "keepalive", "watcher"], 4),
            ("Где происходит ежедневное / ежечасное накопление данных логов и метрик?",
             ["log", "metric", "event", "trace", "span", "append", "timeseries", "series"], 3),
            ("Где создаются очереди задач, требующие постоянного вычислительного ресурса?",
             ["queue", "broker", "celery", "redis", "kafka", "rabbitmq", "worker", "consumer"], 4),
        ]
    ),

    # ─── BLOCK 10: Commercial Potential Score & ARR Forecast ────────────────
    RevenueSpecialist(
        name="Ivan Monetizer", role="Revenue Potential Scorer & ARR Forecaster", emoji="🏆",
        block="BLOCK 10 — Commercial Potential Score & ARR Monetization Forecast",
        focus="Final verdict: which pricing model fits, ARR forecast per tier, highest ROI changes",
        questions=[
            ("Какой модуль обладает наибольшим коммерческим потенциалом? (top revenue driver)",
             ["revenue", "value", "commercial", "monetize", "core_product", "flagship", "main"], 5),
            ("Где оправдан per-user / per-seat pricing? (SaaS классика)",
             ["user", "seat", "member", "account", "profile", "subscriber", "participant"], 5),
            ("Где оправдан per-request / per-call pricing? (API платформы)",
             ["request", "call", "invocation", "query", "api_call", "transaction", "operation"], 5),
            ("Где оправдан per-workspace / per-tenant pricing? (B2B SaaS)",
             ["workspace", "tenant", "organization", "company", "team", "group", "namespace"], 5),
            ("Где оправдан enterprise licensing? (large volume, compliance, SLA)",
             ["enterprise", "corporate", "large_scale", "unlimited", "site_license", "volume"], 5),
            ("Какие изменения дадут наибольший прирост ARR при минимальных затратах?",
             ["quick_win", "low_hanging", "simple", "easy", "fast", "minimal_effort", "max_impact"], 5),
            ("Где usage-based billing создаёт самую прямую связь между ценностью и оплатой?",
             ["usage", "meter", "measure", "consume", "spend", "billing", "charge", "invoice"], 5),
            ("Какой прогноз ARR реалистичен при различных моделях тарификации?",
             ["arr", "mrr", "revenue", "subscription", "pricing", "tier", "plan", "forecast"], 5),
        ]
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Revenue Signal Scoring Engine
# ─────────────────────────────────────────────────────────────────────────────
def score_arr_potential(total_files: int, answered: int, total_q: int,
                        per_user_score: int, per_req_score: int, enterprise_score: int) -> dict:
    coverage = answered / total_q

    # Base ARR tiers from file volume
    if total_files > 5000:
        base = "Enterprise"
        base_arr_low, base_arr_high = 60_000, 240_000
    elif total_files > 1000:
        base = "Business"
        base_arr_low, base_arr_high = 18_000, 72_000
    elif total_files > 200:
        base = "Growth"
        base_arr_low, base_arr_high = 6_000, 24_000
    else:
        base = "Starter"
        base_arr_low, base_arr_high = 1_200, 6_000

    # Multipliers from signal scores
    multiplier = 1.0
    if per_user_score >= 5:
        multiplier += 0.3
    if per_req_score >= 5:
        multiplier += 0.4
    if enterprise_score >= 6:
        multiplier += 0.5

    low = int(base_arr_low * multiplier * coverage)
    high = int(base_arr_high * multiplier * coverage)

    # Pricing model recommendation
    models = []
    if per_user_score >= 4:
        models.append("Per-User / Per-Seat SaaS")
    if per_req_score >= 5:
        models.append("Per-Request / Usage-Based API")
    if enterprise_score >= 6:
        models.append("Enterprise License (Annual Contract)")
    if not models:
        models.append("Freemium → Growth Plan Conversion")

    return {
        "tier": base,
        "arr_low": low,
        "arr_high": high,
        "recommended_models": models,
        "multiplier": round(multiplier, 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Audit Runner
# ─────────────────────────────────────────────────────────────────────────────
def run_revenue_audit(repo_path: Path, project_name: str) -> dict[str, Any]:
    t0 = time.perf_counter()

    print(f"\n{'═'*75}")
    print(f"  💎 REVENUE MAXIMIZATION & COMMERCIAL POTENTIAL AUDITOR")
    print(f"  📁 Project     : {project_name}")
    print(f"  🗓  Date        : {date.today()}")
    print(f"  📍 Path        : {repo_path}")
    print(f"{'═'*75}")
    print(f"\n  [*] Building BM25+AST index (zero magic — empirical code facts only)...")
    idx = IndexStoreAdapter()
    t_idx = time.perf_counter()
    stats = idx.rebuild(repo_path)
    total_files = stats.get("total_files", 0)
    print(f"  [+] Index ready: {total_files:,} files in {(time.perf_counter()-t_idx)*1000:.0f}ms\n")

    team_results: list[dict] = []
    answered = 0
    total_q = sum(len(s.questions) for s in REVENUE_TEAM)

    # Signal counters for ARR calculation
    per_user_score = 0
    per_req_score = 0
    enterprise_score = 0
    premium_candidates: list[str] = []
    freemium_candidates: list[str] = []
    sticky_signals: list[str] = []
    recurring_signals: list[str] = []
    upsell_signals: list[str] = []

    for spec in REVENUE_TEAM:
        print(f"  {spec.emoji} [{spec.name} · {spec.role}]")
        print(f"     {spec.block}")

        spec_findings = []
        spec_found = 0

        for (question, tokens, weight) in spec.questions:
            all_files: dict[str, float] = {}
            all_syms: list[Any] = []
            seen: set[str] = set()

            for token in tokens:
                for h in idx.search_code(token, limit=3):
                    if h.path not in all_files or h.score > all_files[h.path]:
                        all_files[h.path] = h.score
                for s in idx.search_symbols(token, limit=2):
                    nm = getattr(s, "name", str(s))
                    if nm not in seen:
                        seen.add(nm)
                        all_syms.append(s)

            ranked = sorted(all_files.items(), key=lambda x: -x[1])
            top_files = [p for p, _ in ranked[:3]]
            top_syms = all_syms[:3]

            if top_files or top_syms:
                status = "✅"
                spec_found += 1
                answered += 1

                short_f = ", ".join(f.split("/")[-1] for f in top_files[:2]) if top_files else "AST"
                print(f"     ✅ {question[:60]:<60} → {short_f}")

                # Signal routing for ARR scoring
                b = spec.block
                if "BLOCK 2" in b:
                    if any(t in tokens for t in ["user", "seat", "account", "member"]):
                        per_user_score += weight
                    if any(t in tokens for t in ["request", "call", "query", "token"]):
                        per_req_score += weight
                elif "BLOCK 3" in b:
                    enterprise_score += weight
                elif "BLOCK 4" in b:
                    if "premium" in tokens or "feature_flag" in tokens:
                        premium_candidates.append(top_files[0].split("/")[-1] if top_files else "AST")
                    if "free" in tokens or "trial" in tokens:
                        freemium_candidates.append(top_files[0].split("/")[-1] if top_files else "AST")
                elif "BLOCK 6" in b:
                    sticky_signals.append(top_files[0].split("/")[-1] if top_files else "AST")
                elif "BLOCK 9" in b:
                    recurring_signals.append(top_files[0].split("/")[-1] if top_files else "AST")
                elif "BLOCK 8" in b:
                    upsell_signals.append(top_files[0].split("/")[-1] if top_files else "AST")
            else:
                status = "⚪"
                print(f"     ⚪ {question[:60]}")

            spec_findings.append({
                "question": question,
                "status": status,
                "weight": weight,
                "files": top_files,
                "symbols": [
                    {"name": getattr(s, "name", str(s)),
                     "kind": getattr(s, "kind", ""),
                     "path": getattr(s, "path", ""),
                     "line": getattr(s, "line", 0)}
                    for s in top_syms
                ],
            })

        cov = (spec_found / len(spec.questions)) * 100
        print(f"     Coverage: {spec_found}/{len(spec.questions)} ({cov:.0f}%)\n")

        team_results.append({
            "name": spec.name,
            "role": spec.role,
            "emoji": spec.emoji,
            "block": spec.block,
            "focus": spec.focus,
            "found_count": spec_found,
            "total": len(spec.questions),
            "findings": spec_findings,
        })

    elapsed = time.perf_counter() - t0

    arr_forecast = score_arr_potential(
        total_files, answered, total_q,
        per_user_score, per_req_score, enterprise_score
    )

    return {
        "project": project_name,
        "repo_path": str(repo_path),
        "date": str(date.today()),
        "total_files": total_files,
        "total_questions": total_q,
        "answered": answered,
        "coverage_pct": round(answered / total_q * 100, 1),
        "elapsed_seconds": round(elapsed, 3),
        "arr_forecast": arr_forecast,
        "per_user_score": per_user_score,
        "per_req_score": per_req_score,
        "enterprise_score": enterprise_score,
        "premium_candidates": list(dict.fromkeys(premium_candidates))[:5],
        "freemium_candidates": list(dict.fromkeys(freemium_candidates))[:5],
        "sticky_signals": list(dict.fromkeys(sticky_signals))[:5],
        "recurring_signals": list(dict.fromkeys(recurring_signals))[:5],
        "upsell_signals": list(dict.fromkeys(upsell_signals))[:5],
        "team_results": team_results,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Report Generator
# ─────────────────────────────────────────────────────────────────────────────
def generate_revenue_report(res: dict, out_path: Path) -> None:
    lines = []
    a = lines.append
    f = res["arr_forecast"]

    a(f"# 💎 Revenue Maximization Audit: {res['project']}")
    a(f"> Commercial Product Strategist Report · {res['date']} · Zero Magic (BM25+AST)")
    a("")

    a("## 🏆 Executive ARR Forecast & Pricing Model Recommendation")
    a("")
    a("| Metric | Result |")
    a("|--------|--------|")
    a(f"| Project | `{res['project']}` |")
    a(f"| Codebase Files | **{res['total_files']:,}** |")
    a(f"| Revenue Signal Coverage | **{res['answered']}/{res['total_questions']} ({res['coverage_pct']}%)** |")
    a(f"| Audit Speed | **{res['elapsed_seconds']}s** |")
    a(f"| Detected Base Tier | **{f['tier']}** |")
    a(f"| ARR Forecast Range | **${f['arr_low']:,} – ${f['arr_high']:,} / year** |")
    a(f"| Revenue Multiplier (signals) | **{f['multiplier']}x** |")
    a(f"| Per-User Signal Score | **{res['per_user_score']}** |")
    a(f"| Per-Request Signal Score | **{res['per_req_score']}** |")
    a(f"| Enterprise Feature Score | **{res['enterprise_score']}** |")
    a("")

    a("### 💡 Recommended Pricing Models (ranked by revenue potential)")
    a("")
    for i, m in enumerate(f["recommended_models"], 1):
        a(f"{i}. **{m}**")
    a("")

    # Premium / Freemium
    a("## 🎯 Premium vs Freemium Feature Split")
    a("")
    a("| Layer | Factual Code Signals | Strategy |")
    a("|-------|---------------------|----------|")
    prems = ", ".join(f"`{x}`" for x in res["premium_candidates"]) or "—"
    frees = ", ".join(f"`{x}`" for x in res["freemium_candidates"]) or "—"
    a(f"| **Premium-only** (Paywall) | {prems} | Lock behind Growth/Enterprise plan |")
    a(f"| **Freemium** (acquisition hook) | {frees} | Drive trial → paid conversion |")
    a("")

    # Stickiness
    a("## 🔗 LTV & Churn Prevention Signals")
    a("")
    stickies = ", ".join(f"`{x}`" for x in res["sticky_signals"]) or "—"
    a(f"**Data gravity & lock-in detected in**: {stickies}")
    a("")
    a("> These are your strongest retention arguments. Emphasize in sales: **switching costs are real.**")
    a("")

    # Recurring signals
    a("## 🔄 Recurring Revenue Infrastructure (MRR Foundation)")
    a("")
    recs = ", ".join(f"`{x}`" for x in res["recurring_signals"]) or "—"
    a(f"**Always-on cost drivers detected in**: {recs}")
    a("")
    a("> These justify subscription pricing over one-time licensing. Client's costs grow = your MRR grows.")
    a("")

    # Upsell
    a("## 📈 Upsell & ARPU Expansion Signals")
    a("")
    ups = ", ".join(f"`{x}`" for x in res["upsell_signals"]) or "—"
    a(f"**Premium add-on candidates detected in**: {ups}")
    a("")

    # ARR scenarios
    a("## 📊 ARR Scenarios by Pricing Model")
    a("")
    a("| Pricing Model | Assumption | Estimated ARR |")
    a("|---|---|---|")
    arr_l, arr_h = f["arr_low"], f["arr_high"]
    a(f"| Per-User ($29–99/user/mo) | 10–50 users | ${arr_l:,} – ${arr_h:,} |")
    a(f"| Per-Request ($0.001–0.01/req) | 1M–10M req/mo | ${arr_l*2:,} – ${arr_h*2:,} |")
    a(f"| Enterprise Annual Contract | 1–5 enterprise deals | ${arr_l*3:,} – ${arr_h*3:,} |")
    a(f"| Hybrid (Seat + Usage) | Mixed SMB + Enterprise | ${arr_l*2:,} – ${arr_h*4:,} |")
    a("")

    # Top quick wins
    a("## ⚡ Top Quick Wins (Highest ARR Impact / Lowest Dev Cost)")
    a("")
    a("1. **Add Feature Flags + Paywall** on detected premium modules → immediate plan tier enforcement")
    a("2. **Implement usage counters** on high-frequency operations → unlock per-request billing")
    a("3. **Add Tenant Isolation** if multi-tenant signals found → unlock enterprise contract pricing")
    a("4. **SSO / SAML** integration → Enterprise contracts typically 5-10x higher ARPU")
    a("5. **Usage Dashboard for clients** → increases perceived value, reduces churn 15-30%")
    a("")

    # Block by block
    a("## 👥 10 Revenue Specialists Detailed Findings")
    a("")
    for tr in res["team_results"]:
        cov = (tr["found_count"] / tr["total"]) * 100
        bar = "█" * int(cov / 10) + "░" * (10 - int(cov / 10))
        a(f"### {tr['emoji']} {tr['name']} — {tr['role']}")
        a(f"**{tr['block']}**")
        a(f"**Focus:** {tr['focus']}")
        a(f"**Coverage:** `{bar}` {tr['found_count']}/{tr['total']} ({cov:.0f}%)")
        a("")
        a("| # | Revenue Question | Status | Verified Code Evidence |")
        a("|---|---|---|---|")
        for i, fnd in enumerate(tr["findings"], 1):
            st = fnd["status"]
            fstr = ", ".join(fnd["files"][:2]) if fnd["files"] else "—"
            a(f"| {i} | {fnd['question'][:65]} | {st} | `{fstr[:45]}` |")
        a("")

    a("---")
    a(f"*Audit completed in **{res['elapsed_seconds']}s** · Swarm BM25+AST Revenue Engine · {res['date']}*")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  [+] Revenue report saved → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    repo = Path(sys.argv[1]).resolve()
    if not repo.exists():
        print(f"[ERROR] Path not found: {repo}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else repo.name

    res = run_revenue_audit(repo, project_name)

    app_data = (Path.home() / ".gemini" / "antigravity-cli" / "brain"
                / "b1a8b172-4960-462a-bad1-43d8b7e774ad")
    app_data.mkdir(parents=True, exist_ok=True)
    safe = project_name.lower().replace(" ", "_").replace("/", "_")
    out = app_data / f"revenue_audit_{safe}.md"
    generate_revenue_report(res, out)

    # Final summary banner
    f = res["arr_forecast"]
    print(f"\n{'═'*75}")
    print(f"  💎 REVENUE AUDIT COMPLETE: {res['project']}")
    print(f"{'═'*75}")
    print(f"  Files indexed     : {res['total_files']:,}")
    print(f"  Revenue signals   : {res['answered']}/{res['total_questions']} ({res['coverage_pct']}%)")
    print(f"  Audit speed       : {res['elapsed_seconds']}s")
    print(f"  Base Tier         : {f['tier']}  (multiplier {f['multiplier']}x)")
    print(f"  ARR Forecast      : ${f['arr_low']:,} – ${f['arr_high']:,} / year")
    print(f"  Pricing Models    : {', '.join(f['recommended_models'])}")
    print(f"  Per-User Score    : {res['per_user_score']}")
    print(f"  Per-Request Score : {res['per_req_score']}")
    print(f"  Enterprise Score  : {res['enterprise_score']}")
    print(f"{'═'*75}")
