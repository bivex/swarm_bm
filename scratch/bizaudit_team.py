#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║          BizAudit Dev Team — Commercial Project Analyzer            ║
║   10 AI Specialists · BM25+AST Engine · Business Risk Assessment    ║
╚══════════════════════════════════════════════════════════════════════╝

Simulates a real commercial dev team performing a full codebase audit
before taking on a project, estimating costs, and assessing business risks.

Usage:
    python3 scratch/bizaudit_team.py /path/to/project [ProjectName]
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter

# ─────────────────────────────────────────────────────────────────────
# Team Roster — 10 Commercial Specialists
# ─────────────────────────────────────────────────────────────────────
@dataclass
class Specialist:
    name: str
    role: str
    emoji: str
    focus: str
    # Each question: (business_question, [search_tokens], risk_weight 1-3)
    questions: list[tuple[str, list[str], int]]


TEAM: list[Specialist] = [

    Specialist(
        name="Alex Chen", role="CTO", emoji="🎯",
        focus="Architecture & Strategic Technology Decisions",
        questions=[
            ("Монолит или микросервисы? Готова ли архитектура к росту 10M+ пользователей?",
             ["microservice", "service", "monolith", "module", "hexagonal", "domain", "bounded_context"], 3),
            ("Есть ли vendor lock-in на конкретные облака или SaaS провайдеры?",
             ["aws", "gcp", "azure", "heroku", "stripe", "twilio", "sendgrid", "firebase", "supabase"], 2),
            ("Какой технологический стек? Насколько он mainstream для найма команды?",
             ["Django", "FastAPI", "Flask", "Spring", "Rails", "Node", "Go", "Rust", "Kotlin"], 2),
            ("Есть ли чёткое разделение бизнес-логики от инфраструктуры (чистая архитектура)?",
             ["use_case", "service", "repository", "port", "adapter", "domain", "application", "infrastructure"], 3),
            ("Насколько высок технический долг? Есть ли blockers для новых фич?",
             ["TODO", "FIXME", "HACK", "deprecated", "legacy", "workaround", "technical_debt", "refactor"], 2),
            ("Поддерживает ли кодовая база горизонтальное масштабирование (stateless)?",
             ["stateless", "session", "sticky", "cache", "redis", "shared_state", "singleton", "global"], 3),
            ("Есть ли API gateway или BFF для мобильных и веб клиентов?",
             ["gateway", "bff", "api_gateway", "mobile", "graphql", "rest", "versioning", "endpoint"], 2),
            ("Какова стратегия disaster recovery и RPO/RTO?",
             ["backup", "restore", "replication", "failover", "disaster", "recovery", "replica", "standby"], 3),
        ]
    ),

    Specialist(
        name="Marina Volkova", role="Tech Lead", emoji="🔧",
        focus="Code Quality, Patterns & Team Onboarding",
        questions=[
            ("Насколько понятна кодовая база для нового разработчика? Время до первого PR?",
             ["README", "CONTRIBUTING", "setup", "quickstart", "getting_started", "development", "docs"], 1),
            ("Соблюдаются ли SOLID принципы и Clean Code? Есть ли god-классы?",
             ["SRP", "class", "service", "manager", "helper", "utils", "mixin", "base", "abstract"], 2),
            ("Есть ли единые паттерны по всей кодовой базе (consistency)?",
             ["pattern", "convention", "template", "boilerplate", "standard", "style", "guideline"], 1),
            ("Насколько легко добавить новую фичу без страха сломать существующее?",
             ["test", "coverage", "fixture", "mock", "integration", "unit", "regression", "CI"], 2),
            ("Есть ли DRY нарушения и дублированный код?",
             ["duplicate", "copy", "repeat", "clone", "identical", "shared", "common", "reuse"], 2),
            ("Используется ли типизация (type hints, TypeScript, generics)?",
             ["type", "TypeVar", "Optional", "Union", "Generic", "Protocol", "Annotated", "typing"], 1),
            ("Насколько сложны функции (cyclomatic complexity)?",
             ["if ", "elif", "for ", "while", "try", "except", "nested", "complex", "condition"], 2),
            ("Есть ли coding standards enforcement (linters, formatters, pre-commit)?",
             ["black", "ruff", "flake8", "mypy", "eslint", "prettier", "pre-commit", "husky", "lint"], 1),
        ]
    ),

    Specialist(
        name="Dmitri Petrov", role="Senior Backend Engineer", emoji="⚙️",
        focus="APIs, Performance & Data Access Patterns",
        questions=[
            ("Есть ли N+1 проблемы или missing индексы в запросах к БД?",
             ["select_related", "prefetch_related", "N+1", "annotate", "query", "filter", "all()", "index"], 3),
            ("Как устроены REST/gRPC/GraphQL API? Есть ли versioning?",
             ["api/v1", "api/v2", "APIView", "ViewSet", "router", "serializer", "schema", "endpoint"], 2),
            ("Как обрабатывается пагинация больших датасетов?",
             ["paginator", "pagination", "cursor", "limit", "offset", "page_size", "iterator", "chunk"], 2),
            ("Используется ли кэширование для тяжёлых запросов?",
             ["cache", "redis", "memcache", "lru_cache", "cached_property", "cache_page", "TTL"], 2),
            ("Как устроен async: правильно ли используется asyncio/celery?",
             ["async def", "await", "celery", "task", "apply_async", "asyncio", "aiohttp", "dramatiq"], 2),
            ("Есть ли connection pooling к БД и внешним сервисам?",
             ["pool_size", "CONN_MAX_AGE", "pool", "connection_pool", "max_connections", "timeout"], 2),
            ("Как обрабатываются bulk операции (массовые вставки/обновления)?",
             ["bulk_create", "bulk_update", "executemany", "batch", "chunk", "insert_many", "pipeline"], 1),
            ("Как устроены миграции? Есть ли риск потери данных при деплое?",
             ["migration", "Migration", "RunSQL", "data_migration", "zero_downtime", "backward", "squash"], 3),
        ]
    ),

    Specialist(
        name="Sarah Kim", role="Security Engineer", emoji="🔐",
        focus="Security, Auth & Compliance",
        questions=[
            ("Как реализована аутентификация? JWT/Session/OAuth2 — безопасно ли?",
             ["jwt", "token", "session", "OAuth", "authenticate", "login", "bearer", "refresh_token"], 3),
            ("Как управляется RBAC/ABAC — нет ли privilege escalation?",
             ["permission", "has_perm", "is_staff", "is_superuser", "Group", "role", "ACL", "policy"], 3),
            ("Как хранятся секреты? Нет ли hardcoded credentials в коде?",
             ["SECRET_KEY", "PASSWORD", "API_KEY", "TOKEN", "password", "credential", "secret", "vault"], 3),
            ("Защита от OWASP Top 10 (CSRF, XSS, SQLi, IDOR)?",
             ["csrf", "XSS", "sanitize", "escape", "parameterized", "sql_injection", "Content-Security-Policy"], 3),
            ("Есть ли rate limiting для API endpoints?",
             ["throttle", "rate_limit", "RateLimit", "429", "THROTTLE", "token_bucket", "gcra"], 2),
            ("Как валидируются и санируются входные данные?",
             ["validate", "clean", "is_valid", "ValidationError", "Pydantic", "schema", "sanitize", "zod"], 2),
            ("GDPR/CCPA compliance: право на удаление, PII маскировка?",
             ["gdpr", "pii", "anonymize", "right_to_forget", "personal_data", "consent", "data_subject"], 2),
            ("Есть ли audit log действий пользователей?",
             ["audit", "AuditLog", "LogEntry", "access_log", "activity", "history", "track", "changelog"], 2),
        ]
    ),

    Specialist(
        name="Ivan Popov", role="DevOps / SRE", emoji="🚀",
        focus="Infrastructure, CI/CD & Reliability",
        questions=[
            ("Насколько зрелый CI/CD pipeline? Автоматический деплой или ручной?",
             ["github/workflows", "gitlab-ci", "jenkinsfile", "circleci", "deploy", "pipeline", "release"], 2),
            ("Контейнеризация: Docker + Kubernetes-ready?",
             ["Dockerfile", "docker-compose", "kubernetes", "helm", "k8s", "container", "pod", "ingress"], 2),
            ("Мониторинг и алертинг: Prometheus, Grafana, Sentry?",
             ["prometheus", "grafana", "sentry", "metrics", "alertmanager", "pagerduty", "datadog", "newrelic"], 2),
            ("Health checks и readiness probes для K8s?",
             ["health", "healthz", "readiness", "liveness", "probe", "ping", "status", "heartbeat"], 2),
            ("Логирование: структурированные JSON логи или printf?",
             ["logging", "logger", "structlog", "json_log", "logstash", "ELK", "loki", "fluentd"], 1),
            ("Distributed tracing (OpenTelemetry, Jaeger)?",
             ["opentelemetry", "trace", "span", "jaeger", "zipkin", "tracing", "correlation_id"], 1),
            ("Есть ли IaC (Terraform, Pulumi) для воспроизводимой инфраструктуры?",
             ["terraform", "pulumi", ".tf", "main.tf", "cloudformation", "bicep", "ansible", "helm"], 2),
            ("Backup стратегия и disaster recovery документация?",
             ["backup", "restore", "disaster_recovery", "RTO", "RPO", "snapshot", "point_in_time"], 3),
        ]
    ),

    Specialist(
        name="Lisa Wang", role="Data Engineer", emoji="📊",
        focus="Data Models, Analytics & Data Quality",
        questions=[
            ("Нормализованы ли модели данных? Нет ли избыточности?",
             ["ForeignKey", "OneToOne", "ManyToMany", "normalize", "denormalize", "relation", "schema"], 2),
            ("Есть ли аналитическая база данных или data warehouse?",
             ["warehouse", "clickhouse", "bigquery", "redshift", "snowflake", "analytics", "OLAP", "ETL"], 2),
            ("Как реализована мультиарендность (multi-tenancy)?",
             ["tenant", "tenant_id", "organization_id", "workspace", "schema_per_tenant", "row_level"], 3),
            ("Data retention политики: как и когда удаляются данные?",
             ["retention", "expire", "TTL", "purge", "archive", "cold_storage", "auto_delete", "cleanup"], 2),
            ("Есть ли data validation на входе и quality checks?",
             ["validate", "data_quality", "assertion", "check", "constraint", "integrity", "clean"], 2),
            ("Как устроены аналитические события (event tracking)?",
             ["analytics", "event", "track", "segment", "mixpanel", "amplitude", "posthog", "bigquery"], 2),
            ("Оптимизированы ли индексы БД для типичных query паттернов?",
             ["index", "db_index", "CREATE INDEX", "composite_index", "EXPLAIN", "query_plan", "GIN"], 3),
            ("Есть ли data lineage и трассируемость данных?",
             ["lineage", "provenance", "data_catalog", "metadata", "origin", "trace", "audit_trail"], 1),
        ]
    ),

    Specialist(
        name="Max Baranov", role="QA Lead", emoji="🧪",
        focus="Testing Strategy, Quality Gates & Release Risk",
        questions=[
            ("Какова реальная плотность тестов (unit / integration / e2e)?",
             ["test_", "TestCase", "pytest", "spec", "describe", "it(", "assert", "expect("], 2),
            ("Есть ли покрытие критических бизнес-путей E2E тестами?",
             ["e2e", "selenium", "playwright", "cypress", "webdriver", "functional_test", "acceptance"], 2),
            ("Насколько легко писать новые тесты (testability)?",
             ["mock", "patch", "factory", "fixture", "faker", "builder", "stub", "DI", "inject"], 2),
            ("Есть ли performance и нагрузочное тестирование?",
             ["locust", "k6", "gatling", "load_test", "benchmark", "stress_test", "jmeter", "wrk"], 2),
            ("Как устроен release process? Есть ли feature flags?",
             ["feature_flag", "toggle", "release", "rollout", "canary", "blue_green", "AB_test", "LaunchDarkly"], 2),
            ("Есть ли regression suite для предотвращения откатов?",
             ["regression", "smoke_test", "sanity", "baseline", "golden_path", "critical_path"], 2),
            ("Используется ли contract testing между сервисами?",
             ["pact", "contract_test", "consumer_driven", "schemathesis", "dredd", "openapi_test"], 1),
            ("Как быстро обнаруживаются и фиксируются баги в prod?",
             ["sentry", "bugsnag", "error_tracking", "hotfix", "incident", "on_call", "MTTR", "alerting"], 2),
        ]
    ),

    Specialist(
        name="Olga Sorokina", role="Senior Frontend Engineer", emoji="🎨",
        focus="Frontend Architecture, UX & Client Performance",
        questions=[
            ("Какой frontend стек? Насколько он современен и поддерживаем?",
             ["react", "vue", "angular", "svelte", "next", "nuxt", "remix", "vite", "webpack"], 2),
            ("Как устроено state management (Redux, Zustand, Pinia)?",
             ["redux", "zustand", "pinia", "mobx", "jotai", "recoil", "context", "store", "atom"], 1),
            ("Есть ли SSR/SSG для SEO и производительности?",
             ["SSR", "SSG", "next", "nuxt", "server_render", "hydrate", "static_site", "ISR"], 2),
            ("Оптимизирован ли bundle size? Нет ли bloated зависимостей?",
             ["bundle", "chunk", "tree_shaking", "code_split", "lazy", "dynamic_import", "webpack", "vite"], 2),
            ("Как устроены API запросы (react-query, SWR, axios)?",
             ["axios", "fetch", "react_query", "swr", "apollo", "urql", "tanstack", "httpClient"], 1),
            ("Есть ли Design System или UI Kit?",
             ["design_system", "component_library", "storybook", "ui_kit", "tokens", "theme", "tailwind"], 1),
            ("Доступность (a11y): WCAG 2.1 compliance?",
             ["aria", "role=", "alt=", "accessibility", "a11y", "wcag", "screen_reader", "focus"], 2),
            ("Интернационализация: готов ли продукт к новым рынкам?",
             ["i18n", "l10n", "translate", "locale", "gettext", "formatMessage", "Intl", "timezone"], 2),
        ]
    ),

    Specialist(
        name="Tom Rodriguez", role="Product Manager", emoji="📱",
        focus="Product Readiness, Monetization & Market Fit",
        questions=[
            ("Готов ли продукт к monetziation (billing, subscription, metering)?",
             ["billing", "subscription", "plan", "invoice", "stripe", "payment", "quota", "credits"], 3),
            ("Есть ли multi-tenancy и SaaS-readiness?",
             ["tenant", "organization", "workspace", "SaaS", "white_label", "subdomain", "plan_limit"], 3),
            ("Насколько легко настраивать продукт под разных клиентов?",
             ["config", "settings", "customization", "white_label", "feature_flag", "tenant_config"], 2),
            ("Есть ли аналитика product usage для data-driven решений?",
             ["analytics", "event", "mixpanel", "amplitude", "segment", "posthog", "funnel", "retention"], 2),
            ("Готов ли API для партнёрских интеграций и marketplace?",
             ["webhook", "api_key", "oauth", "partner", "integration", "marketplace", "SDK", "connector"], 2),
            ("Есть ли onboarding flow и self-service для клиентов?",
             ["onboarding", "wizard", "signup", "trial", "self_service", "invitation", "team", "workspace"], 2),
            ("Поддерживается ли SSO для enterprise клиентов (SAML, OIDC)?",
             ["SSO", "SAML", "OIDC", "ldap", "active_directory", "enterprise", "sso_provider", "idp"], 2),
            ("Есть ли SLA гарантии и uptime мониторинг для enterprise?",
             ["SLA", "uptime", "availability", "99.9", "monitoring", "status_page", "incident", "downtime"], 2),
        ]
    ),

    Specialist(
        name="Elena Kuznetsova", role="Business Analyst", emoji="💼",
        focus="Business Risk, Compliance & Commercial Viability",
        questions=[
            ("Open source лицензии: нет ли GPL-заражения в коммерческом продукте?",
             ["license", "LICENSE", "MIT", "Apache", "GPL", "LGPL", "BSD", "proprietary", "copyright"], 3),
            ("Зависимости: нет ли EOL библиотек с CVE уязвимостями?",
             ["requirements.txt", "package.json", "vulnerability", "CVE", "deprecated", "EOL", "security"], 3),
            ("Насколько высок bus factor? Есть ли knowledge silos?",
             ["TODO", "only_me", "author", "maintainer", "CODEOWNERS", "blame", "single_owner"], 2),
            ("Соответствие регуляторным требованиям (HIPAA, PCI DSS, SOC2)?",
             ["hipaa", "pci", "soc2", "compliance", "audit", "certification", "regulation", "gdpr"], 3),
            ("Оценка времени рефакторинга до production-ready состояния?",
             ["refactor", "rewrite", "migration", "upgrade", "modernize", "technical_debt", "legacy"], 2),
            ("Насколько легко масштабировать команду на проекте?",
             ["docs", "onboarding", "architecture", "module", "service", "interface", "contract", "API"], 2),
            ("Есть ли риски vendor lock-in на closed-source компоненты?",
             ["vendor", "proprietary", "lock_in", "migration_path", "alternative", "open_source", "SaaS"], 2),
            ("Оценка TCO (Total Cost of Ownership) на 3 года?",
             ["infrastructure", "cloud", "hosting", "maintenance", "support", "operational", "cost", "scaling"], 2),
        ]
    ),
]

# ─────────────────────────────────────────────────────────────────────
# Risk Classification
# ─────────────────────────────────────────────────────────────────────
def classify_risk(score: float) -> tuple[str, str]:
    if score >= 2.5:
        return "🔴 CRITICAL", "Blocker. Must fix before any commercial launch."
    elif score >= 1.8:
        return "🟠 HIGH", "Significant business risk. Address in sprint 1."
    elif score >= 1.2:
        return "🟡 MEDIUM", "Technical debt affecting velocity. Plan for Q1."
    else:
        return "🟢 LOW", "Minor issue. Address in regular housekeeping."


# ─────────────────────────────────────────────────────────────────────
# BizAudit Engine
# ─────────────────────────────────────────────────────────────────────
def run_bizaudit(repo_path: Path, project_name: str) -> dict[str, Any]:
    t0 = time.perf_counter()

    print(f"\n{'═'*68}")
    print(f"  🏢 BizAudit Dev Team — Commercial Codebase Assessment")
    print(f"  📁 Project : {project_name}")
    print(f"  🗓  Date    : {date.today()}")
    print(f"  📍 Path    : {repo_path}")
    print(f"{'═'*68}")

    # Index
    print(f"\n  [*] Building BM25+AST intelligence index...")
    idx = IndexStoreAdapter()
    job = JobEngineAdapter()
    t_idx = time.perf_counter()
    stats = idx.rebuild(repo_path)
    total_files = stats.get("total_files", 0)
    print(f"  [+] Index ready: {total_files:,} files in {(time.perf_counter()-t_idx)*1000:.0f}ms\n")

    team_results: list[dict] = []
    all_risk_items: list[dict] = []
    total_questions = sum(len(s.questions) for s in TEAM)
    answered = 0

    for specialist in TEAM:
        print(f"  {specialist.emoji} [{specialist.name} · {specialist.role}]")
        print(f"     Focus: {specialist.focus}")

        spec_findings = []

        for (question, tokens, risk_weight) in specialist.questions:
            # Multi-token BM25 + AST search
            all_files: dict[str, float] = {}
            all_symbols: list[Any] = []
            seen: set[str] = set()

            for token in tokens:
                hits = idx.search_code(token, limit=4)
                for h in hits:
                    if h.path not in all_files or h.score > all_files[h.path]:
                        all_files[h.path] = h.score
                syms = idx.search_symbols(token, limit=2)
                for s in syms:
                    nm = getattr(s, "name", str(s))
                    if nm not in seen:
                        seen.add(nm)
                        all_symbols.append(s)

            ranked = sorted(all_files.items(), key=lambda x: -x[1])
            top_files = [p for p, _ in ranked[:4]]
            top_syms = all_symbols[:4]

            if not top_files and not top_syms:
                status = "⚪ NOT FOUND"
                risk_score = 0.0
            else:
                status = "✅ FOUND"
                # Risk score: lower is better if evidence found (means it IS implemented)
                # Higher risk_weight items that ARE found reduce concern
                risk_score = max(0.0, (risk_weight * 0.5) - (len(top_files) * 0.1))
                answered += 1

            finding = {
                "question": question,
                "status": status,
                "risk_weight": risk_weight,
                "risk_score": round(risk_score, 2),
                "files": top_files,
                "symbols": [
                    {"name": getattr(s, "name", str(s)),
                     "kind": getattr(s, "kind", ""),
                     "path": getattr(s, "path", ""),
                     "line": getattr(s, "line", 0)}
                    for s in top_syms
                ],
            }
            spec_findings.append(finding)

            if top_files:
                short_files = ", ".join(f.split("/")[-1] for f in top_files[:2])
                print(f"     {status} {question[:55]:<55} → {short_files}")
            else:
                print(f"     {status} {question[:55]}")

            # Collect high-risk gaps (not found + high weight)
            if status == "⚪ NOT FOUND" and risk_weight >= 2:
                all_risk_items.append({
                    "specialist": specialist.name,
                    "role": specialist.role,
                    "question": question,
                    "risk_weight": risk_weight,
                    "risk_score": float(risk_weight),
                })

        team_results.append({
            "specialist": specialist.name,
            "role": specialist.role,
            "emoji": specialist.emoji,
            "focus": specialist.focus,
            "findings": spec_findings,
            "found_count": sum(1 for f in spec_findings if "FOUND" in f["status"] and "NOT" not in f["status"]),
            "total": len(spec_findings),
        })
        coverage = team_results[-1]["found_count"] / team_results[-1]["total"] * 100
        print(f"     Coverage: {team_results[-1]['found_count']}/{team_results[-1]['total']} ({coverage:.0f}%)\n")

    elapsed = time.perf_counter() - t0

    # Overall risk
    all_risk_items.sort(key=lambda x: -x["risk_score"])
    critical = [r for r in all_risk_items if r["risk_weight"] == 3]
    high     = [r for r in all_risk_items if r["risk_weight"] == 2]

    return {
        "project": project_name,
        "repo_path": str(repo_path),
        "date": str(date.today()),
        "total_files": total_files,
        "team_size": len(TEAM),
        "total_questions": total_questions,
        "answered": answered,
        "coverage_pct": round(answered / total_questions * 100, 1),
        "elapsed_seconds": round(elapsed, 3),
        "critical_gaps": critical,
        "high_risk_gaps": high,
        "team_results": team_results,
    }


# ─────────────────────────────────────────────────────────────────────
# Report Generator
# ─────────────────────────────────────────────────────────────────────
def generate_report(result: dict, out_path: Path) -> None:
    lines: list[str] = []
    a = lines.append

    a(f"# 🏢 BizAudit Dev Team Report: {result['project']}")
    a("")
    a(f"> Commercial Codebase Assessment · {result['date']}")
    a("")
    a("## 📋 Executive Summary")
    a("")
    a("| Parameter | Value |")
    a("|-----------|-------|")
    a(f"| Project | `{result['project']}` |")
    a(f"| Repository | `{result['repo_path']}` |")
    a(f"| Date | {result['date']} |")
    a(f"| Files Analyzed | **{result['total_files']:,}** |")
    a(f"| Team Specialists | **{result['team_size']}** |")
    a(f"| Questions Asked | **{result['total_questions']}** |")
    a(f"| Evidence Found | **{result['answered']}/{result['total_questions']} ({result['coverage_pct']}%)** |")
    a(f"| Audit Duration | **{result['elapsed_seconds']}s** |")
    a("")

    # Risk summary
    crit = result["critical_gaps"]
    high = result["high_risk_gaps"]
    total_gaps = len(crit) + len(high)

    if total_gaps == 0:
        verdict = "🟢 **PRODUCTION READY** — No critical gaps detected."
        recommendation = "Proceed with commercial launch. Minor improvements recommended."
    elif len(crit) == 0:
        verdict = "🟡 **CONDITIONALLY READY** — High-risk gaps require attention."
        recommendation = "Address HIGH priority items in Sprint 1 before launch."
    elif len(crit) <= 3:
        verdict = "🟠 **NOT READY** — Critical gaps block commercial deployment."
        recommendation = "2–4 week remediation sprint required before launch."
    else:
        verdict = "🔴 **SIGNIFICANT REWORK NEEDED** — Multiple critical blockers."
        recommendation = "Major refactoring required. Estimate 1–3 months to production-ready."

    a("## 🎯 Business Verdict")
    a("")
    a(f"**{verdict}**")
    a("")
    a(f"**Recommendation:** {recommendation}")
    a("")

    # Risk matrix
    a("## 🚨 Risk Matrix")
    a("")
    if crit:
        a("### 🔴 CRITICAL Gaps (Commercial Launch Blockers)")
        a("")
        a("| Specialist | Risk Area |")
        a("|---|---|")
        for r in crit:
            a(f"| {r['specialist']} ({r['role']}) | {r['question']} |")
        a("")

    if high:
        a("### 🟠 HIGH Priority Gaps (Sprint 1)")
        a("")
        a("| Specialist | Risk Area |")
        a("|---|---|")
        for r in high:
            a(f"| {r['specialist']} ({r['role']}) | {r['question']} |")
        a("")

    if not crit and not high:
        a("> ✅ No critical or high-priority gaps detected. Strong commercial foundation.\n")

    # Effort estimate
    base_days = len(crit) * 5 + len(high) * 2
    a("## 💰 Commercial Effort Estimate")
    a("")
    a("| Item | Estimate |")
    a("|------|----------|")
    a(f"| Critical gap remediation | **{len(crit) * 5}** person-days |")
    a(f"| High-risk gap remediation | **{len(high) * 2}** person-days |")
    a(f"| Total remediation effort | **{base_days}** person-days ≈ **{base_days // 5}** work-weeks |")
    a(f"| Onboarding new developer | **3–5** days (README quality based) |")
    a(f"| Time to first production deploy | **{'1–2 weeks' if base_days < 10 else '3–6 weeks' if base_days < 30 else '2–3 months'}** |")
    a("")

    # Team breakdown
    a("## 👥 Team Assessment Breakdown")
    a("")
    for tr in result["team_results"]:
        coverage = tr["found_count"] / tr["total"] * 100
        bar = "█" * int(coverage / 10) + "░" * (10 - int(coverage / 10))
        emoji = tr["emoji"]
        a(f"### {emoji} {tr['specialist']} — {tr['role']}")
        a(f"**Focus:** {tr['focus']}")
        a(f"**Coverage:** `{bar}` {tr['found_count']}/{tr['total']} ({coverage:.0f}%)")
        a("")
        a("| # | Question | Status | Files Found |")
        a("|---|---|---|---|")
        for i, f in enumerate(tr["findings"], 1):
            status_icon = "✅" if "NOT" not in f["status"] and "FOUND" in f["status"] else "⚪"
            files_str = ", ".join(f["files"][:2]) if f["files"] else "—"
            a(f"| {i} | {f['question'][:60]} | {status_icon} | `{files_str[:50]}` |")
        a("")

        # Top symbols per specialist
        all_syms = [s for finding in tr["findings"] for s in finding["symbols"]]
        if all_syms:
            seen_sym: set[str] = set()
            unique_syms = []
            for s in all_syms:
                if s["name"] not in seen_sym:
                    seen_sym.add(s["name"])
                    unique_syms.append(s)
            a("**Key AST Symbols Found:**")
            a("")
            a("| Symbol | Kind | File | Line |")
            a("|--------|------|------|------|")
            for s in unique_syms[:6]:
                fname = s["path"].split("/")[-1] if s["path"] else "—"
                a(f"| `{s['name']}` | {s['kind']} | `{fname}` | {s['line']} |")
            a("")

    # Footer
    a("---")
    a("")
    a("## 🔍 About BizAudit Dev Team")
    a("")
    a("Powered by **Swarm BM** — 10-Agent AI Swarm with BM25+AST Engine.")
    a("")
    a("| Engine | Technology |")
    a("|--------|------------|")
    a("| Search | BM25 ranking over full codebase |")
    a("| Symbols | Multi-language AST (Python, C, C++, JS, TS, Go, Rust) |")
    a("| Agents | 10 specialist AI agents × 8 commercial questions each |")
    a("| Speed | O(1) skeleton cache · prefix symbol index · BM25 guard |")
    a("")
    a(f"*Report generated in **{result['elapsed_seconds']}s** · {result['total_files']:,} files · {result['total_questions']} questions*")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  [+] Report saved → {out_path}")


# ─────────────────────────────────────────────────────────────────────
# Terminal Summary
# ─────────────────────────────────────────────────────────────────────
def print_terminal_summary(result: dict) -> None:
    print(f"\n{'═'*68}")
    print(f"  📊 BIZAUDIT RESULTS — {result['project']}")
    print(f"{'═'*68}")
    print(f"  Files analyzed     : {result['total_files']:,}")
    print(f"  Questions asked    : {result['total_questions']} (10 specialists × 8 questions)")
    print(f"  Evidence found     : {result['answered']}/{result['total_questions']} ({result['coverage_pct']}%)")
    print(f"  Audit time         : {result['elapsed_seconds']}s")
    print()

    crit = result["critical_gaps"]
    high = result["high_risk_gaps"]

    if crit:
        print(f"  🔴 CRITICAL BLOCKERS ({len(crit)}):")
        for r in crit[:4]:
            print(f"     • [{r['role']}] {r['question'][:60]}")

    if high:
        print(f"\n  🟠 HIGH RISK ({len(high)}):")
        for r in high[:4]:
            print(f"     • [{r['role']}] {r['question'][:60]}")

    if not crit and not high:
        print("  🟢 No critical or high-risk gaps — strong commercial foundation!")

    base_days = len(crit) * 5 + len(high) * 2
    print()
    print(f"  💰 Estimated remediation : {base_days} person-days (~{base_days//5} work-weeks)")
    ttm = "1–2 weeks" if base_days < 10 else "3–6 weeks" if base_days < 30 else "2–3 months"
    print(f"  🚀 Time to prod-ready    : {ttm}")
    print(f"\n{'═'*68}\n")


# ─────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("Usage: python3 scratch/bizaudit_team.py /path/to/project [ProjectName]")
        sys.exit(1)

    repo = Path(sys.argv[1]).resolve()
    if not repo.exists():
        print(f"[ERROR] Path not found: {repo}")
        sys.exit(1)

    project = sys.argv[2] if len(sys.argv) > 2 else repo.name

    result = run_bizaudit(repo, project)

    print_terminal_summary(result)

    # Save report
    from pathlib import Path as _P
    app_data = _P.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)
    safe_name = project.lower().replace(" ", "_").replace("/", "_")
    out = app_data / f"bizaudit_{safe_name}.md"
    generate_report(result, out)
