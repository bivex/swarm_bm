from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from swarm_mcp.domain.models import ResourceBudget, SwarmWorker
from swarm_mcp.domain.ports import IndexPort, JobEnginePort

# ---------------------------------------------------------------------------
# 50 Senior Architect Onboarding Questions — 10 domains x 5 questions each
# Each question is paired with targeted short BM25/AST search tokens that
# maximise recall from a real codebase index.
# ---------------------------------------------------------------------------
SENIOR_QUESTIONS_BY_DOMAIN: dict[str, list[tuple[str, list[str]]]] = {
    "Domain 1: System Topography & Entry Points": [
        ("Где находится главная точка входа?",
         ["manage.py", "main.py", "app.py", "__main__.py", "wsgi.py", "asgi.py", "server.py"]),
        ("Какова макро-архитектура проекта?",
         ["hexagonal", "clean architecture", "domain", "application", "infrastructure", "ports", "adapters"]),
        ("Как устроена файловая структура по каталогам?",
         ["apps", "modules", "packages", "contrib", "core", "services", "handlers"]),
        ("Какие синглтоны/реестры инициализируются при старте?",
         ["registry", "AppConfig", "app_config", "setup()", "configure()", "init_app", "startup"]),
        ("Как передаётся конфигурация приложения?",
         ["settings", "environ", "config", "DJANGO_SETTINGS_MODULE", ".env", "os.getenv", "getenv"]),
    ],
    "Domain 2: Data Models & Persistence": [
        ("Какие ORM/СУБД/Хранилища используются?",
         ["models.Model", "SQLAlchemy", "Base", "session", "db.session", "redis", "MongoDB"]),
        ("Как объявлены сущности данных?",
         ["class.*Model", "ForeignKey", "CharField", "IntegerField", "fields", "Column", "mapped_column"]),
        ("Как устроены связи между моделями?",
         ["ForeignKey", "ManyToManyField", "OneToOneField", "relationship", "backref", "related_name"]),
        ("Есть ли механизмы миграций?",
         ["migrations", "Migration", "RunSQL", "RunPython", "Alembic", "alembic", "upgrade", "downgrade"]),
        ("Используется ли транзакционность?",
         ["transaction", "atomic", "commit", "rollback", "savepoint", "with transaction"]),
    ],
    "Domain 3: Security, Auth & Permissions": [
        ("Как реализована аутентификация?",
         ["authenticate", "login", "jwt", "token", "session_key", "OAuth", "ApiKey", "bearer"]),
        ("Как устроена авторизация и права доступа?",
         ["permission", "has_perm", "Permission", "Group", "RBAC", "is_staff", "is_superuser", "decorator"]),
        ("Как обрабатываются секреты и пароли?",
         ["SECRET_KEY", "make_password", "check_password", "hashlib", "bcrypt", "argon2", "HMAC", "encrypt"]),
        ("Есть ли защита от CORS/CSRF/SQLi/XSS?",
         ["csrf", "CsrfViewMiddleware", "CORS", "escape", "mark_safe", "parameterized", "sanitize"]),
        ("Как валидируются входные данные?",
         ["validate", "clean", "Form", "Serializer", "Pydantic", "is_valid", "ValidationError", "schema"]),
    ],
    "Domain 4: API Contracts & Routing": [
        ("Как устроена маршрутизация запросов?",
         ["urlpatterns", "path(", "re_path(", "router.register", "include(", "APIRouter", "Blueprint"]),
        ("Какие протоколы и контракты используются?",
         ["REST", "HTTP", "WebSocket", "GraphQL", "gRPC", "JSONResponse", "View", "APIView", "ViewSet"]),
        ("Как сериализуются данные?",
         ["serializer", "Serializer", "to_representation", "to_internal_value", "jsonify", "schema", "Pydantic"]),
        ("Версионируются ли API эндпоинты?",
         ["api/v1", "api/v2", "versioning", "namespace", "DEFAULT_VERSION", "URLPathVersioning"]),
        ("Есть ли документация API?",
         ["OpenAPI", "swagger", "schema_view", "drf_spectacular", "drf-yasg", "api_view", "docstring"]),
    ],
    "Domain 5: Concurrency & Async Execution": [
        ("Какова парадигма выполнения (async/threads/processes)?",
         ["async def", "await", "asyncio", "ThreadPoolExecutor", "ProcessPoolExecutor", "celery", "dramatiq"]),
        ("Есть ли блокирующий I/O внутри async контекста?",
         ["sync_to_async", "async_to_sync", "sync_unsafe", "blocking", "asgiref"]),
        ("Как управляется Graceful Shutdown?",
         ["signal.SIGTERM", "signal.SIGINT", "atexit", "on_startup", "on_shutdown", "lifespan", "shutdown"]),
        ("Используются ли примитивы синхронизации?",
         ["Lock()", "RLock", "Semaphore", "asyncio.Lock", "threading.Event", "Queue(", "Condition"]),
        ("Thread safety shared состояния?",
         ["threading.local", "contextvars", "ContextVar", "thread_local", "local()", "atomic"]),
    ],
    "Domain 6: Error Handling & Resilience": [
        ("Как обрабатываются исключения глобально?",
         ["handler500", "handler404", "EXCEPTION_HANDLER", "process_exception", "middleware", "dispatch"]),
        ("Используется ли Retry / Exponential Backoff?",
         ["retry", "backoff", "tenacity", "max_retries", "RETRY", "celery retry", "exponential"]),
        ("Есть ли Circuit Breaker / Bulkhead?",
         ["circuit_breaker", "CircuitBreaker", "pybreaker", "bulkhead", "timeout", "fallback"]),
        ("Глотаются ли исключения без логирования?",
         ["except:", "except Exception:", "pass", "bare except", "suppress"]),
        ("Возвращаются ли безопасные ошибки клиентам?",
         ["JsonResponse", "Response(", "status=400", "status=500", "error_response", "detail", "Http404"]),
    ],
    "Domain 7: Performance & Caching": [
        ("Есть ли проблемы N+1 запросов?",
         ["select_related", "prefetch_related", "only(", "defer(", "annotate", "Q(", "queryset"]),
        ("Как устроено кэширование?",
         ["cache.get", "cache.set", "cache_page", "lru_cache", "cached_property", "redis", "memcache"]),
        ("Есть ли утечки памяти / незакрытые соединения?",
         ["close()", "connection.close", "pool", "with closing", "__del__", "weakref", "gc.collect"]),
        ("Кэшируются ли тяжёлые вычислений?",
         ["@lru_cache", "@cache", "functools.cache", "memoize", "TTL", "cache_key", "computed_value"]),
        ("Контроль объёма временных объектов в RAM?",
         ["iterator()", "values_list", "chunk_size", "batch_size", "pagination", "Paginator", "yield"]),
    ],
    "Domain 8: Technical Debt & Code Smells": [
        ("God Classes / файлы > 1000 строк?",
         ["class.*View", "class.*Manager", "class.*Service", "class.*Handler", "class.*Mixin"]),
        ("Дублирование кода (DRY violations)?",
         ["copy", "duplicate", "TODO", "FIXME", "HACK", "XXX", "copy-paste"]),
        ("High Coupling — жёсткие зависимости?",
         ["import django", "from django", "import celery", "from celery", "hardcoded", "global"]),
        ("Доменные службы завязаны на инфраструктуру?",
         ["from django.db", "from sqlalchemy", "from redis", "from celery import", "ORM", "direct DB"]),
        ("Мёртвый / закомментированный код?",
         ["# TODO", "# FIXME", "# HACK", "# noqa", "deprecated", "unused", "dead_code"]),
    ],
    "Domain 9: Quality & Testability": [
        ("Типы тестов (Unit, Integration, E2E)?",
         ["TestCase", "test_", "pytest", "unittest", "SimpleTestCase", "TransactionTestCase", "APITestCase"]),
        ("Лёгкость изоляции компонентов (Mocks/Stubs)?",
         ["mock", "patch", "MagicMock", "Mock(", "mocker", "stub", "factory_boy", "fixture"]),
        ("Структура тестовых данных (Fixtures/Factories)?",
         ["fixture", "Factory", "baker", "mommy", "mixer", "create(", "bulk_create", "loaddata"]),
        ("Статический анализ (Linters/Type Checking)?",
         ["mypy", "pyright", "flake8", "pylint", "ruff", "bandit", ".pre-commit", "setup.cfg", "pyproject"]),
        ("CI/CD конфигурация?",
         [".github/workflows", "tox.ini", "Makefile", "Dockerfile", "circleci", "gitlab-ci", "jenkins"]),
    ],
    "Domain 10: Infrastructure, Build & Submodules": [
        ("Как собирается проект?",
         ["setup.py", "pyproject.toml", "CMakeLists", "Makefile", "poetry", "flit", "hatch", "build"]),
        ("Контейнеризация (Docker/Kubernetes)?",
         ["Dockerfile", "docker-compose", "kubernetes", "helm", "k8s", ".dockerignore", "entrypoint"]),
        ("Внешние зависимости и библиотеки?",
         ["requirements.txt", "pyproject.toml", "dependencies", "install_requires", "poetry.lock"]),
        ("Git Submodules и интеграции?",
         [".gitmodules", "submodule", "git submodule", "third_party", "vendor", "extern"]),
        ("Логирование и трассировка?",
         ["logging", "logger", "LOGGING", "sentry", "structlog", "opentelemetry", "jaeger", "loguru"]),
    ],
}


@dataclass
class DomainAuditResult:
    domain_name: str
    agent_id: str
    questions_answered: int
    findings: list[dict[str, Any]] = field(default_factory=list)


def _make_factual_summary(question: str, matched_files: list[str], symbols: list[Any]) -> str:
    """Build a 100% factual summary from real engine data only."""
    parts: list[str] = []

    if matched_files:
        top = matched_files[:5]
        parts.append(f"Найдено {len(matched_files)} файлов: " + ", ".join(top))

    if symbols:
        sym_names = [
            f"{getattr(s, 'name', str(s))} ({getattr(s, 'kind', '?')})"
            for s in symbols[:5]
        ]
        parts.append(f"Символы: " + ", ".join(sym_names))

    # If nothing found at all — return empty string so caller can skip this finding
    return " | ".join(parts) if parts else ""


class SeniorCodebaseAuditEngine:
    """10-Agent Swarm Senior Architect Codebase Auditor.

    Emits ONLY factual findings from the BM25+AST engine.
    Questions with zero matches are silently skipped.
    """

    def __init__(self, index_port: IndexPort, job_engine_port: JobEnginePort) -> None:
        self.index_port = index_port
        self.job_engine_port = job_engine_port

    # ------------------------------------------------------------------
    def run_10_agent_senior_audit(self, root: Path) -> dict[str, Any]:
        t0 = time.perf_counter()
        stats = self.index_port.rebuild(root)
        total_files = stats.get("total_files", 0)

        print(f"[+] Launching 10-Agent Swarm Audit on {root} ({total_files} files)...")

        audit_results: list[dict[str, Any]] = []
        total_answered = 0

        for idx, (domain_name, q_tuples) in enumerate(SENIOR_QUESTIONS_BY_DOMAIN.items()):
            worker_id = f"swarm_senior_agent_{idx + 1}"
            budget = ResourceBudget(
                max_memory_mb=128,
                cpu_rate_cap=20,
                max_iops=200,
                max_net_bandwidth_mbps=20,
                sandbox_enabled=True,
            )

            worker: SwarmWorker = self.job_engine_port.spawn_worker(
                worker_id=worker_id,
                command=["python3", "-c", f"print('Agent {idx+1}: {domain_name}')"],
                budget=budget,
            )

            domain_findings: list[dict[str, Any]] = []

            for (question, search_tokens) in q_tuples:
                # ---- Run multi-token BM25 searches ----------------------
                all_files: dict[str, float] = {}  # path -> best score
                all_symbols: list[Any] = []

                for token in search_tokens:
                    hits = self.index_port.search_code(token, limit=5)
                    for h in hits:
                        if h.path not in all_files or h.score > all_files[h.path]:
                            all_files[h.path] = h.score
                    syms = self.index_port.search_symbols(token, limit=3)
                    all_symbols.extend(syms)

                # ---- Deduplicate and rank --------------------------------
                ranked_files = sorted(all_files.items(), key=lambda x: -x[1])
                top_files = [p for p, _ in ranked_files[:6]]

                seen_names: set[str] = set()
                unique_syms: list[Any] = []
                for s in all_symbols:
                    nm = getattr(s, "name", str(s))
                    if nm not in seen_names:
                        seen_names.add(nm)
                        unique_syms.append(s)
                top_symbols = unique_syms[:6]

                # ---- Only emit if engine found something real ------------
                summary = _make_factual_summary(question, top_files, top_symbols)
                if not summary:
                    continue  # skip — engine found nothing real for this question

                finding: dict[str, Any] = {
                    "question": question,
                    "matched_files": top_files,
                    "symbols": [
                        {
                            "name": getattr(s, "name", str(s)),
                            "kind": getattr(s, "kind", ""),
                            "path": getattr(s, "path", ""),
                            "line": getattr(s, "line", 0),
                        }
                        for s in top_symbols
                    ],
                    "answer_summary": summary,
                }
                domain_findings.append(finding)
                total_answered += 1

            self.job_engine_port.compress_memory(worker_id)
            self.job_engine_port.terminate_worker(worker_id)

            audit_results.append({
                "agent_id": worker_id,
                "domain": domain_name,
                "questions_with_findings": len(domain_findings),
                "findings": domain_findings,
            })

        t1 = time.perf_counter()

        return {
            "root_path": str(root),
            "total_files": total_files,
            "total_symbols": stats.get("total_symbols", 0),
            "agents_count": 10,
            "total_questions_audited": sum(len(q) for q in SENIOR_QUESTIONS_BY_DOMAIN.values()),
            "questions_with_real_findings": total_answered,
            "elapsed_seconds": round(t1 - t0, 3),
            "domain_results": audit_results,
        }
