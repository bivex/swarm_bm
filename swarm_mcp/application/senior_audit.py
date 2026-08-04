from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from swarm_mcp.domain.models import ResourceBudget, SwarmWorker
from swarm_mcp.domain.ports import IndexPort, JobEnginePort

# ---------------------------------------------------------------------------
# Pre-built token prefix index for search_symbols fast-path
# Maps 3-char prefix → set of tokens that start with that prefix
# Built once per audit run from SENIOR_QUESTIONS_BY_DOMAIN
# ---------------------------------------------------------------------------
_TOKEN_PREFIX_INDEX: dict[str, set[str]] = {}

# ---------------------------------------------------------------------------
# 150 Senior Architect Onboarding Questions
# 15 специализированных доменов × 10 вопросов каждый
# Каждый вопрос = пара (human_question, [search_tokens])
# search_tokens — реальные идентификаторы для BM25+AST движка
# ---------------------------------------------------------------------------
SENIOR_QUESTIONS_BY_DOMAIN: dict[str, list[tuple[str, list[str]]]] = {

    # ──────────────────────────────────────────────────────────────────────
    "Domain 1: System Topography & Entry Points": [
        ("Где главная точка входа (main, app, manage.py, index)?",
         ["manage.py", "main.py", "app.py", "__main__.py", "wsgi.py", "asgi.py", "server.py", "index.js", "cmd/main.go"]),
        ("Какова макро-архитектура (Monolith, Microservices, Hexagonal, DDD)?",
         ["hexagonal", "domain", "application", "infrastructure", "ports", "adapters", "service", "controller", "handler"]),
        ("Как разграничена ответственность между каталогами?",
         ["apps", "modules", "packages", "contrib", "core", "services", "handlers", "views", "routes"]),
        ("Какие синглтоны и реестры инициализируются при старте?",
         ["registry", "AppConfig", "setup", "configure", "init_app", "startup", "bootstrap", "wire", "provide"]),
        ("Как передаётся конфигурация (ENV, .env, config.yaml, CLI args)?",
         ["settings", "environ", "DJANGO_SETTINGS_MODULE", "os.getenv", "config.yaml", "viper", "dotenv", "FLAGS"]),
        ("Есть ли dependency injection контейнер?",
         ["inject", "container", "provider", "wire", "dependency_injector", "ioc", "DI", "Depends", "Injectable"]),
        ("Какие middleware/interceptors обёртывают запросы?",
         ["middleware", "interceptor", "decorator", "filter", "before_request", "after_request", "use(", "pipe"]),
        ("Как устроено версионирование самого приложения?",
         ["__version__", "VERSION", "version.txt", "pyproject.toml", "package.json", "Cargo.toml", "go.mod"]),
        ("Есть ли feature flags или runtime toggle?",
         ["feature_flag", "toggle", "LaunchDarkly", "unleash", "flipper", "flags", "FEATURE_", "enabled_for"]),
        ("Как устроена корневая обработка ошибок приложения?",
         ["error_handler", "exception_handler", "on_error", "global_exception", "middleware", "500", "error_page"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 2: Data Models & Persistence": [
        ("Какие ORM/СУБД/Хранилища используются?",
         ["models.Model", "SQLAlchemy", "Base", "session", "redis", "MongoDB", "DynamoDB", "Cassandra", "ClickHouse"]),
        ("Как объявлены сущности данных (Entities/Models/Schemas)?",
         ["ForeignKey", "CharField", "IntegerField", "Column", "mapped_column", "field", "schema", "dataclass"]),
        ("Как устроены связи между моделями?",
         ["ForeignKey", "ManyToManyField", "OneToOneField", "relationship", "backref", "related_name", "join"]),
        ("Есть ли механизмы миграций?",
         ["migrations", "Migration", "RunSQL", "RunPython", "Alembic", "alembic", "upgrade", "downgrade", "revision"]),
        ("Используется ли транзакционность (ACID, atomic)?",
         ["transaction", "atomic", "commit", "rollback", "savepoint", "BEGIN", "COMMIT"]),
        ("Как устроена пагинация и курсорная навигация?",
         ["paginator", "Paginator", "page_size", "cursor", "offset", "limit", "next_page", "pagination"]),
        ("Есть ли soft delete vs hard delete?",
         ["soft_delete", "deleted_at", "is_deleted", "deactivated", "archive", "trash", "SoftDeleteMixin"]),
        ("Как хранятся бинарные данные и файлы?",
         ["FileField", "ImageField", "BinaryField", "blob", "s3", "minio", "upload", "storage_backend"]),
        ("Как устроено шардирование или партиционирование данных?",
         ["shard", "partition", "sharding", "PARTITION BY", "table_suffix", "routing_key", "tenant"]),
        ("Есть ли event sourcing или CQRS?",
         ["event_store", "EventStore", "CQRS", "command_bus", "query_bus", "aggregate", "domain_event", "apply"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 3: Security, Auth & Permissions": [
        ("Как реализована аутентификация (JWT, Session, OAuth2)?",
         ["authenticate", "login", "jwt", "token", "session_key", "OAuth", "ApiKey", "bearer", "OIDC"]),
        ("Как устроена авторизация (RBAC, ABAC, Permissions)?",
         ["permission", "has_perm", "Permission", "Group", "RBAC", "is_staff", "is_superuser", "guard", "policy"]),
        ("Как хранятся и обрабатываются секреты и пароли?",
         ["SECRET_KEY", "make_password", "check_password", "hashlib", "bcrypt", "argon2", "HMAC", "vault", "kms"]),
        ("Есть ли защита от CSRF/XSS/SQLi/CORS?",
         ["csrf", "CsrfViewMiddleware", "CORS", "escape", "mark_safe", "parameterized", "sanitize", "Content-Security-Policy"]),
        ("Как валидируются входные данные?",
         ["validate", "clean", "Form", "Serializer", "Pydantic", "is_valid", "ValidationError", "schema", "zod"]),
        ("Есть ли rate limiting и throttling?",
         ["throttle", "rate_limit", "RateLimit", "throttling", "gcra", "token_bucket", "THROTTLE", "429"]),
        ("Как устроен audit log действий пользователей?",
         ["audit", "AuditLog", "access_log", "ActivityLog", "changelog", "history", "LogEntry", "track_changes"]),
        ("Есть ли защита от брутфорса и account lockout?",
         ["lockout", "brute_force", "failed_attempts", "login_attempts", "ban", "block_ip", "captcha", "backoff"]),
        ("Как обрабатываются загружаемые файлы (upload security)?",
         ["upload", "allowed_extensions", "magic_bytes", "content_type", "antivirus", "scan", "file_validation"]),
        ("Есть ли шифрование данных в покое (at rest)?",
         ["encrypt", "encryption", "AES", "RSA", "KMS", "encrypt_field", "FieldEncryption", "crypto", "fernet"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 4: API Contracts & Routing": [
        ("Как устроена маршрутизация запросов?",
         ["urlpatterns", "path(", "re_path(", "router.register", "include(", "APIRouter", "Blueprint", "mux"]),
        ("Какие протоколы используются (REST, gRPC, GraphQL, WS)?",
         ["REST", "HTTP", "WebSocket", "GraphQL", "gRPC", "JSONResponse", "View", "APIView", "ViewSet", "proto"]),
        ("Как сериализуются и десериализуются данные?",
         ["serializer", "Serializer", "to_representation", "to_internal_value", "jsonify", "schema", "Pydantic", "marshal"]),
        ("Версионируются ли API эндпоинты?",
         ["api/v1", "api/v2", "versioning", "namespace", "DEFAULT_VERSION", "URLPathVersioning", "Accept-Version"]),
        ("Есть ли документация API (OpenAPI, Swagger)?",
         ["OpenAPI", "swagger", "schema_view", "drf_spectacular", "drf-yasg", "api_view", "docstring", "spectaql"]),
        ("Как обрабатываются большие ответы и стриминг?",
         ["StreamingHttpResponse", "streaming", "chunked", "generator", "stream", "SSE", "EventSource", "yield"]),
        ("Есть ли contract testing (Pact, Dredd)?",
         ["pact", "dredd", "contract_test", "consumer_driven", "schema_test", "schemathesis", "openapi_test"]),
        ("Как устроены webhooks и callbacks?",
         ["webhook", "callback", "notify", "event_url", "push_notification", "outbound", "delivery", "retry"]),
        ("Есть ли GraphQL или gRPC схемы?",
         [".proto", ".graphql", ".gql", "schema.graphql", "type Query", "type Mutation", "message ", "service "]),
        ("Как обрабатывается CORS и preflight?",
         ["CORS", "CorsMiddleware", "cors_origin", "allow_headers", "allow_methods", "OPTIONS", "preflight"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 5: Concurrency & Async Execution": [
        ("Какова парадигма выполнения (async/threads/processes)?",
         ["async def", "await", "asyncio", "ThreadPoolExecutor", "ProcessPoolExecutor", "celery", "dramatiq", "goroutine"]),
        ("Есть ли блокирующий I/O внутри async контекста?",
         ["sync_to_async", "async_to_sync", "async_unsafe", "blocking", "asgiref", "run_in_executor"]),
        ("Как управляется Graceful Shutdown?",
         ["SIGTERM", "SIGINT", "atexit", "on_shutdown", "lifespan", "shutdown_event", "graceful", "drain"]),
        ("Используются ли примитивы синхронизации?",
         ["Lock()", "RLock", "Semaphore", "asyncio.Lock", "threading.Event", "Queue(", "Condition", "Barrier"]),
        ("Thread safety shared состояния?",
         ["threading.local", "contextvars", "ContextVar", "thread_local", "local()", "atomic", "thread_safe"]),
        ("Как устроен пул потоков или процессов?",
         ["ThreadPool", "ProcessPool", "executor", "worker_pool", "pool_size", "MAX_WORKERS", "concurrent.futures"]),
        ("Есть ли background jobs и task queues?",
         ["celery", "rq", "huey", "dramatiq", "task", "apply_async", "delay(", "queue", "worker", "beat"]),
        ("Как реализован pub/sub или event bus?",
         ["pubsub", "subscribe", "publish", "EventBus", "emit", "signal", "dispatcher", "broadcast", "channel"]),
        ("Есть ли таймауты и дедлайны на операциях?",
         ["timeout", "deadline", "TIMEOUT", "socket_timeout", "request_timeout", "connect_timeout", "context.WithTimeout"]),
        ("Как устроена работа с batch/bulk операциями?",
         ["bulk_create", "batch", "chunk", "bulk_update", "executemany", "pipeline", "MULTI", "batch_size"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 6: Error Handling & Resilience": [
        ("Как обрабатываются исключения глобально?",
         ["handler500", "handler404", "EXCEPTION_HANDLER", "process_exception", "middleware", "dispatch"]),
        ("Используется ли Retry / Exponential Backoff?",
         ["retry", "backoff", "tenacity", "max_retries", "RETRY", "exponential", "jitter", "requeue"]),
        ("Есть ли Circuit Breaker / Bulkhead?",
         ["circuit_breaker", "CircuitBreaker", "pybreaker", "bulkhead", "timeout", "fallback", "open_state", "half_open"]),
        ("Глотаются ли исключения без логирования?",
         ["except:", "except Exception:", "pass", "bare except", "suppress", "ignore", "swallow"]),
        ("Возвращаются ли безопасные ошибки клиентам?",
         ["JsonResponse", "Response(", "status=400", "status=500", "error_response", "detail", "Http404", "error_code"]),
        ("Есть ли Dead Letter Queue для необработанных сообщений?",
         ["dlq", "dead_letter", "DLQ", "dead-letter-queue", "on_failure", "task_failure", "nack", "reject"]),
        ("Как реализован health check / liveness / readiness?",
         ["health", "healthz", "readiness", "liveness", "ping", "status_check", "/health", "heartbeat"]),
        ("Есть ли механизм rollback при частичных сбоях?",
         ["rollback", "compensate", "saga", "Saga", "undo", "revert", "compensating_transaction", "idempotent"]),
        ("Как обрабатываются внешние зависимости при недоступности?",
         ["fallback", "default_value", "cache_fallback", "degraded", "graceful_degradation", "circuit", "stale"]),
        ("Есть ли chaos engineering / fault injection?",
         ["chaos", "fault_injection", "chaos_monkey", "latency_injection", "toxiproxy", "gremlin", "fault"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 7: Performance & Caching": [
        ("Есть ли проблемы N+1 при запросах к БД?",
         ["select_related", "prefetch_related", "only(", "defer(", "annotate", "Q(", "queryset", "eager_load"]),
        ("Как устроено кэширование (Redis, Memcached, LRU)?",
         ["cache.get", "cache.set", "cache_page", "lru_cache", "cached_property", "redis", "memcache", "TTL"]),
        ("Есть ли утечки памяти / незакрытые соединения?",
         ["close()", "connection.close", "pool", "with closing", "__del__", "weakref", "gc.collect", "finalizer"]),
        ("Кэшируются ли результаты тяжёлых вычислений?",
         ["@lru_cache", "@cache", "functools.cache", "memoize", "cache_key", "computed_value", "precompute"]),
        ("Контроль объёма временных объектов в RAM?",
         ["iterator()", "values_list", "chunk_size", "batch_size", "pagination", "Paginator", "yield", "stream"]),
        ("Есть ли индексы на колонках БД?",
         ["db_index", "Index(", "index_together", "CREATE INDEX", "compound_index", "GIN", "GiST", "BRIN"]),
        ("Как настроен connection pool к БД?",
         ["pool_size", "max_overflow", "pool_timeout", "CONN_MAX_AGE", "pool_pre_ping", "NullPool", "QueuePool"]),
        ("Есть ли профилирование и APM?",
         ["cProfile", "yappi", "py-spy", "datadog", "newrelic", "sentry", "opentelemetry", "jaeger", "apm"]),
        ("Как устроен CDN и статика?",
         ["STATIC_URL", "MEDIA_URL", "whitenoise", "cdn", "cloudfront", "static_files", "collectstatic", "nginx"]),
        ("Есть ли очереди на запись (write-behind, buffered writes)?",
         ["write_behind", "buffer", "PIPELINE", "pipeline", "batch_write", "lazy_write", "deferred", "async_write"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 8: Technical Debt & Code Smells": [
        ("God Classes / файлы > 1000 строк?",
         ["class.*View", "class.*Manager", "class.*Service", "class.*Handler", "class.*Mixin", "utils.py", "helpers.py"]),
        ("Дублирование кода (DRY violations)?",
         ["copy", "duplicate", "TODO", "FIXME", "HACK", "XXX", "copy-paste", "repeated", "clone"]),
        ("High Coupling — жёсткие зависимости?",
         ["import django", "from django", "import celery", "hardcoded", "global", "singleton", "tight_coupling"]),
        ("Доменные службы завязаны на инфраструктуру?",
         ["from django.db", "from sqlalchemy", "from redis", "from celery import", "ORM", "direct DB", "repository"]),
        ("Мёртвый / закомментированный код?",
         ["# TODO", "# FIXME", "# HACK", "# noqa", "deprecated", "unused", "dead_code", "obsolete", "legacy"]),
        ("Магические числа и строки без констант?",
         ["magic_number", "magic_string", "hardcoded", "literal", "3600", "86400", "9999", "\"admin\""]),
        ("Нарушения Single Responsibility Principle?",
         ["and_also", "plus", "also_does", "multi_purpose", "utils", "misc", "helpers", "common", "shared"]),
        ("Избыточная вложенность и сложность?",
         ["if.*if.*if", "nested", "deeply_nested", "complexity", "cyclomatic", "cognitive_complexity"]),
        ("Нарушения Open/Closed Principle?",
         ["isinstance", "type_check", "if type(", "if isinstance(", "switch", "dispatch", "type_switch"]),
        ("Устаревшие зависимости и EOL библиотеки?",
         ["deprecated", "EOL", "pinned", "requirements.txt", "setup.cfg", "vulnerability", "CVE", "outdated"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 9: Quality & Testability": [
        ("Типы тестов (Unit, Integration, E2E)?",
         ["TestCase", "test_", "pytest", "unittest", "SimpleTestCase", "TransactionTestCase", "APITestCase", "spec"]),
        ("Лёгкость изоляции компонентов (Mocks/Stubs)?",
         ["mock", "patch", "MagicMock", "Mock(", "mocker", "stub", "factory_boy", "fixture", "fake"]),
        ("Структура тестовых данных (Fixtures/Factories)?",
         ["fixture", "Factory", "baker", "mommy", "mixer", "create(", "bulk_create", "loaddata", "seed"]),
        ("Статический анализ (Linters/Type Checking)?",
         ["mypy", "pyright", "flake8", "pylint", "ruff", "bandit", ".pre-commit", "setup.cfg", "pyproject"]),
        ("CI/CD конфигурация?",
         [".github/workflows", "tox.ini", "Makefile", "Dockerfile", "circleci", "gitlab-ci", "jenkins", "buildkite"]),
        ("Процент покрытия кода тестами?",
         ["coverage", "codecov", "coveralls", ".coveragerc", "coverage_report", "branch_coverage", "missed"]),
        ("Есть ли mutation testing?",
         ["mutmut", "cosmic_ray", "mutation_testing", "mutant", "pitest", "stryker", "mutation_score"]),
        ("Есть ли property-based testing?",
         ["hypothesis", "given(", "strategies", "property_based", "fuzzing", "fuzz", "QuickCheck", "arbitrary"]),
        ("Есть ли performance / load testing?",
         ["locust", "k6", "gatling", "ab", "wrk", "vegeta", "load_test", "bench", "benchmark", "jmeter"]),
        ("Как тестируются граничные случаи и edge cases?",
         ["edge_case", "boundary", "corner_case", "parametrize", "pytest.mark.parametrize", "test_empty", "test_null"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 10: Infrastructure, Build & DevOps": [
        ("Как собирается проект (CMake, Poetry, Cargo, Go build)?",
         ["setup.py", "pyproject.toml", "CMakeLists", "Makefile", "poetry", "flit", "hatch", "build", "cargo", "go build"]),
        ("Контейнеризация (Docker/Kubernetes/Helm)?",
         ["Dockerfile", "docker-compose", "kubernetes", "helm", "k8s", ".dockerignore", "entrypoint", "kustomize"]),
        ("Внешние зависимости и сторонние библиотеки?",
         ["requirements.txt", "pyproject.toml", "dependencies", "install_requires", "poetry.lock", "go.sum"]),
        ("Git Submodules и интеграции?",
         [".gitmodules", "submodule", "git submodule", "third_party", "vendor", "extern", "subtree"]),
        ("Логирование и трассировка (OpenTelemetry)?",
         ["logging", "logger", "LOGGING", "sentry", "structlog", "opentelemetry", "jaeger", "loguru", "trace"]),
        ("Как управляется секретами в prod (Vault, KMS, SSM)?",
         ["vault", "hashicorp", "aws_ssm", "parameter_store", "kms", "secrets_manager", "doppler", "secret_ref"]),
        ("Есть ли Infrastructure as Code (Terraform, Pulumi)?",
         ["terraform", "pulumi", ".tf", "main.tf", "variables.tf", "outputs.tf", "cloudformation", "bicep"]),
        ("Как устроен мониторинг и алертинг (Prometheus, Grafana)?",
         ["prometheus", "grafana", "alertmanager", "metrics", "gauge", "counter", "histogram", "datadog", "pagerduty"]),
        ("Как управляется конфигурацией между средами (dev/staging/prod)?",
         ["ENVIRONMENT", "ENV", "staging", "production", "development", "dotenv", ".env.local", "config_map"]),
        ("Есть ли Database Seeding и тестовые данные для dev?",
         ["seed", "fixture", "initial_data", "loaddata", "factory", "fake_data", "populate", "db_seed"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 11: Observability & Monitoring": [
        ("Какие метрики экспортируются (Prometheus, StatsD)?",
         ["prometheus_client", "statsd", "metrics", "Counter(", "Gauge(", "Histogram(", "Summary(", "push_gateway"]),
        ("Есть ли distributed tracing (Jaeger, Zipkin, OTEL)?",
         ["opentelemetry", "trace", "span", "tracer", "jaeger", "zipkin", "baggage", "context_propagation"]),
        ("Как структурировано логирование (JSON logs)?",
         ["structlog", "json_logger", "jsonformatter", "logstash", "ELK", "splunk", "loki", "fluentd"]),
        ("Есть ли SLI/SLO/SLA определения?",
         ["sli", "slo", "sla", "error_budget", "availability", "latency_p99", "p95", "p50", "uptime"]),
        ("Как настроен алертинг при деградации?",
         ["alertmanager", "pagerduty", "opsgenie", "alert_rule", "alert_policy", "threshold", "anomaly"]),
        ("Есть ли Real User Monitoring (RUM)?",
         ["rum", "real_user_monitoring", "web_vitals", "LCP", "FID", "CLS", "performance_observer"]),
        ("Как устроены dashboards и визуализация?",
         ["grafana", "dashboard", "kibana", "datadog", "newrelic", "chart", "panel", "visualization"]),
        ("Есть ли профилирование в production?",
         ["py-spy", "pyflame", "pprof", "async-profiler", "continuous_profiling", "flame_graph", "perf"]),
        ("Как логируются ошибки и трекаются исключения?",
         ["sentry", "rollbar", "bugsnag", "raygun", "error_tracking", "exception_handler", "capture_exception"]),
        ("Есть ли uptime monitoring?",
         ["pingdom", "statuscake", "uptimerobot", "uptime", "health_check", "synthetic_monitoring", "canary"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 12: Data Flow & Event-Driven Architecture": [
        ("Используются ли message brokers (Kafka, RabbitMQ)?",
         ["kafka", "rabbitmq", "amqp", "pika", "confluent", "aiokafka", "producer", "consumer", "topic"]),
        ("Как устроена обработка событий (event handlers)?",
         ["event_handler", "on_event", "handle_event", "EventHandler", "listener", "signal", "receiver", "@receiver"]),
        ("Есть ли event sourcing паттерн?",
         ["event_store", "EventStore", "append_event", "event_stream", "aggregate_id", "apply(", "domain_event"]),
        ("Как устроен outbox pattern для гарантированной доставки?",
         ["outbox", "transactional_outbox", "inbox", "relay", "CDC", "debezium", "polling_publisher"]),
        ("Есть ли idempotency ключи для повторных операций?",
         ["idempotency_key", "idempotent", "exactly_once", "deduplication", "message_id", "unique_key"]),
        ("Как устроен порядок обработки сообщений?",
         ["ordering", "sequence", "partition_key", "ordering_key", "FIFO", "ordered_delivery", "causality"]),
        ("Есть ли схемы сообщений (Avro, Protobuf, JSON Schema)?",
         ["avro", "protobuf", "json_schema", "schema_registry", "avsc", "message_schema", "contract"]),
        ("Как обрабатываются backpressure ситуации?",
         ["backpressure", "back_pressure", "flow_control", "buffer_full", "rate_control", "overload", "shed"]),
        ("Есть ли saga паттерн для распределённых транзакций?",
         ["saga", "choreography", "orchestration", "compensate", "rollback_step", "state_machine", "workflow"]),
        ("Как тестируется event-driven логика?",
         ["event_test", "mock_broker", "in_memory_broker", "fake_kafka", "test_consumer", "assert_published"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 13: Scalability & Distributed Systems": [
        ("Есть ли горизонтальное масштабирование (stateless)?",
         ["stateless", "scale_out", "horizontal", "replica", "HPA", "autoscaling", "load_balancer", "sticky_session"]),
        ("Как устроена балансировка нагрузки?",
         ["load_balancer", "nginx", "haproxy", "envoy", "round_robin", "least_connections", "consistent_hash"]),
        ("Есть ли distributed lock?",
         ["redlock", "distributed_lock", "Redlock", "advisory_lock", "pessimistic_lock", "lease", "etcd_lock"]),
        ("Как устроена service discovery?",
         ["consul", "etcd", "service_registry", "eureka", "nacos", "dns_discovery", "k8s_service", "sidecar"]),
        ("Есть ли API Gateway или BFF (Backend for Frontend)?",
         ["api_gateway", "gateway", "BFF", "kong", "traefik", "nginx_gateway", "ambassador", "istio"]),
        ("Как реализована eventual consistency?",
         ["eventual_consistency", "BASE", "CRDT", "conflict_resolution", "merge_strategy", "vector_clock"]),
        ("Есть ли leader election?",
         ["leader_election", "leader", "raft", "paxos", "etcd_election", "k8s_leader", "lease_based"]),
        ("Как устроена репликация данных?",
         ["replication", "replica", "master_slave", "primary_replica", "follower", "read_replica", "standby"]),
        ("Есть ли геораспределённые развёртывания?",
         ["multi_region", "geo_distributed", "CDN", "edge", "latency_routing", "active_active", "disaster_recovery"]),
        ("Как обрабатываются network partitions (CAP theorem)?",
         ["partition_tolerance", "split_brain", "quorum", "consensus", "availability", "consistency", "CAP"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 14: Code Maintainability & Documentation": [
        ("Насколько актуальна inline документация (docstrings)?",
         ["docstring", '"""', "'''", "Args:", "Returns:", "Raises:", "Example:", "Notes:", "Attributes:"]),
        ("Есть ли автогенерация документации (Sphinx, MkDocs)?",
         ["sphinx", "mkdocs", "readthedocs", "docs_url", "autodoc", "apidoc", "documentation", "gh-pages"]),
        ("Соблюдается ли coding style (PEP8, Google Style)?",
         ["black", "isort", "autopep8", "pycodestyle", "flake8", "eslint", "prettier", "gofmt", "rustfmt"]),
        ("Есть ли changelog и история версий?",
         ["CHANGELOG", "CHANGES", "HISTORY", "release_notes", "RELEASES", "whatsnew", "BREAKING"]),
        ("Насколько читаемы имена функций и переменных?",
         ["get_", "set_", "create_", "update_", "delete_", "process_", "handle_", "calculate_", "fetch_"]),
        ("Есть ли ADR (Architecture Decision Records)?",
         ["ADR", "adr", "architecture_decision", "decision_record", "docs/adr", "design_doc", "RFC"]),
        ("Насколько модульна кодовая база (coupling/cohesion)?",
         ["coupling", "cohesion", "module", "package", "interface", "abstract", "protocol", "ABC"]),
        ("Есть ли примеры использования и how-to guides?",
         ["examples", "cookbook", "how_to", "tutorial", "getting_started", "quickstart", "sample"]),
        ("Насколько консистентны паттерны по всей кодовой базе?",
         ["pattern", "convention", "standard", "guideline", "template", "boilerplate", "scaffold"]),
        ("Есть ли типизация (Type Hints, TypeScript, Rust types)?",
         ["-> str", "-> int", "-> list", "-> dict", ": str", ": int", "Optional[", "Union[", "TypeVar"]),
    ],

    # ──────────────────────────────────────────────────────────────────────
    "Domain 15: Multi-tenancy & Compliance": [
        ("Есть ли multi-tenancy (изоляция данных арендаторов)?",
         ["tenant", "tenant_id", "organization_id", "workspace_id", "TenantMixin", "schema_per_tenant", "row_level"]),
        ("Как обеспечивается data isolation между клиентами?",
         ["row_security", "RLS", "tenant_filter", "TenantMiddleware", "schema_router", "db_per_tenant"]),
        ("Есть ли GDPR/CCPA compliance (право на удаление)?",
         ["gdpr", "ccpa", "right_to_forget", "data_deletion", "anonymize", "pseudonymize", "personal_data"]),
        ("Как устроены data retention политики?",
         ["retention", "expire", "TTL", "data_expiry", "auto_delete", "purge", "archival", "cold_storage"]),
        ("Есть ли PII detection и маскировка данных?",
         ["PII", "pii", "mask", "redact", "anonymize", "pseudonym", "tokenize", "sensitive_data"]),
        ("Как проводится data export для пользователей (portability)?",
         ["export", "data_export", "download_data", "portability", "GDPR_export", "user_data", "backup"]),
        ("Есть ли SOC2 / ISO 27001 контроли?",
         ["soc2", "iso27001", "compliance", "audit_log", "access_control", "encryption_at_rest", "MFA"]),
        ("Как обеспечивается data lineage и traceability?",
         ["lineage", "provenance", "data_lineage", "trace_id", "correlation_id", "causation_id", "data_catalog"]),
        ("Есть ли billing и quota management?",
         ["quota", "billing", "usage", "limits", "plan", "subscription", "metering", "credits", "invoice"]),
        ("Как устроена локализация и интернационализация (i18n/l10n)?",
         ["i18n", "l10n", "gettext", "ugettext", "locale", "timezone", "translation", "LANGUAGE_CODE", "babel"]),
    ],
}


@dataclass
class DomainAuditResult:
    domain_name: str
    agent_id: str
    questions_answered: int
    findings: list[dict[str, Any]] = field(default_factory=list)


def _make_factual_summary(matched_files: list[str], symbols: list[Any]) -> str:
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
        parts.append("Символы: " + ", ".join(sym_names))
    return " | ".join(parts) if parts else ""


class SeniorCodebaseAuditEngine:
    """15-Agent Swarm Senior Architect Codebase Auditor (150 questions).

    Emits ONLY factual findings from the BM25+AST engine.
    Questions with zero matches are silently skipped.
    """

    def __init__(self, index_port: IndexPort, job_engine_port: JobEnginePort) -> None:
        self.index_port = index_port
        self.job_engine_port = job_engine_port

    # ------------------------------------------------------------------
    def run_10_agent_senior_audit(self, root: Path) -> dict[str, Any]:
        """Backward-compatible alias — now runs 15 agents x 10 questions."""
        return self.run_senior_audit(root)

    def run_senior_audit(self, root: Path) -> dict[str, Any]:
        t0 = time.perf_counter()
        stats = self.index_port.rebuild(root)
        total_files = stats.get("total_files", 0)
        num_domains = len(SENIOR_QUESTIONS_BY_DOMAIN)
        total_q = sum(len(q) for q in SENIOR_QUESTIONS_BY_DOMAIN.values())

        print(f"[+] Launching {num_domains}-Agent Swarm Audit on {root} "
              f"({total_files} files, {total_q} questions)...")

        audit_results: list[dict[str, Any]] = []
        total_answered = 0

        for idx, (domain_name, q_tuples) in enumerate(SENIOR_QUESTIONS_BY_DOMAIN.items()):
            worker_id = f"swarm_senior_agent_{idx + 1}"

            # FIX 1: Audit agents are pure BM25 query workers — no subprocess needed.
            # Spawning 15 real OS processes + SIGKILL was consuming 73% of total time.
            # We track agent metadata in-process; JobEngine is used for real compute tasks.

            domain_findings: list[dict[str, Any]] = []

            for (question, search_tokens) in q_tuples:
                # Multi-token BM25 + AST search
                # FIX 2: accumulate files in a dict[path→best_score] instead of list
                # to avoid O(N²) deduplication after the loop
                all_files: dict[str, float] = {}
                all_symbols: list[Any] = []
                seen_sym_names: set[str] = set()  # FIX 3: dedup inline, not after

                for token in search_tokens:
                    hits = self.index_port.search_code(token, limit=5)
                    for h in hits:
                        if h.path not in all_files or h.score > all_files[h.path]:
                            all_files[h.path] = h.score

                    # FIX 4: pass short token directly — avoids O(N) fallback in
                    # search_symbols when full question text matches nothing in index
                    syms = self.index_port.search_symbols(token, limit=3)
                    for s in syms:
                        nm = getattr(s, "name", str(s))
                        if nm not in seen_sym_names:
                            seen_sym_names.add(nm)
                            all_symbols.append(s)

                ranked_files = sorted(all_files.items(), key=lambda x: -x[1])
                top_files = [p for p, _ in ranked_files[:6]]
                top_symbols = all_symbols[:6]

                summary = _make_factual_summary(top_files, top_symbols)
                if not summary:
                    continue

                domain_findings.append({
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
                })
                total_answered += 1

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
            "agents_count": num_domains,
            "total_questions_audited": total_q,
            "questions_with_real_findings": total_answered,
            "elapsed_seconds": round(t1 - t0, 3),
            "domain_results": audit_results,
        }
