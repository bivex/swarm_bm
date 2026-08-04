#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🔬 Technology Stack Slicer                                              ║
║   BM25 + File Scan · Zero Magic · Evidence-Only                           ║
║                                                                           ║
║   PURPOSE: "What exactly is this project built on?"                       ║
║   "Which parts can I replace with my own proprietary implementation?"     ║
║   "What licenses govern each component?"                                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

Categories detected:
  1.  Languages          — Python, Go, Rust, TypeScript, C, Java, C#, Ruby...
  2.  Web Frameworks     — FastAPI, Django, Express, Next.js, Gin, Axum, Rails...
  3.  Databases          — PostgreSQL, MySQL, Redis, MongoDB, ClickHouse, SQLite...
  4.  Message Queues     — Kafka, RabbitMQ, NATS, Redis Streams, Celery...
  5.  Protocols          — SIP, WebRTC, WebSocket, gRPC, REST, GraphQL, MQTT...
  6.  Auth & Security    — OAuth2, JWT, SAML, OIDC, RBAC, mTLS, API Key...
  7.  AI / ML            — OpenAI, Anthropic, HuggingFace, PyTorch, LangChain...
  8.  Infrastructure     — Docker, Kubernetes, Terraform, Helm, Ansible...
  9.  Observability      — Prometheus, Grafana, OpenTelemetry, Sentry, Jaeger...
  10. Storage            — S3, GCS, MinIO, Azure Blob, local FS, Parquet...
  11. Testing            — pytest, Jest, Go test, k6, Playwright, Cypress...
  12. CI/CD              — GitHub Actions, GitLab CI, Jenkins, CircleCI...

For each technology:
  - Evidence files (from BM25 index — factual hits, no hallucination)
  - License (from built-in DB)
  - Replaceability score 1-5 (1=trivial, 5=very hard)
  - Proprietary swap recommendation

Usage:
    python3 scratch/stack_slicer.py /path/to/project [ProjectName]
"""
from __future__ import annotations

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


# ─────────────────────────────────────────────────────────────────────────────
# Technology Database
# Each entry: (display_name, category, license, license_risk, replaceability, swap_note, tokens, file_patterns)
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Tech:
    name: str
    category: str
    license: str
    license_risk: str        # LOW / MEDIUM / HIGH / CRITICAL
    replaceability: int      # 1=easy to replace, 5=very hard
    swap_note: str           # what to build as proprietary replacement
    tokens: list[str]        # BM25 search tokens
    file_patterns: list[str] = field(default_factory=list)  # filename patterns
    evidence: list[str] = field(default_factory=list)       # found files
    found: bool = False


TECH_DB: list[Tech] = [

    # ── 1. LANGUAGES ──────────────────────────────────────────────────────────
    Tech("Python",        "language", "PSF-2.0",      "LOW",      4, "Keep — embed Cython/mypyc for performance",
         ["python", "asyncio", "typing", "dataclass", "pydantic"],
         ["*.py", "requirements*.txt", "pyproject.toml", "setup.py"]),
    Tech("TypeScript",    "language", "Apache-2.0",   "LOW",      4, "Keep — compile to V8 bundle, add TS strict mode",
         ["typescript", "interface", "readonly", "generics", "tsconfig"],
         ["tsconfig.json", "*.ts", "*.tsx"]),
    Tech("JavaScript",    "language", "ECMA (free)",  "LOW",      3, "Replace hot paths with WASM or TS strict",
         ["javascript", "nodejs", "npm", "webpack", "babel", "eslint"],
         ["package.json", "*.js", ".eslintrc*"]),
    Tech("Go",            "language", "BSD-3-Clause", "LOW",      4, "Keep — build proprietary modules as Go plugins",
         ["golang", "goroutine", "channel", "interface", "go.mod"],
         ["go.mod", "go.sum", "*.go"]),
    Tech("Rust",          "language", "MIT/Apache-2", "LOW",      5, "Keep — compile to cdylib for FFI licensing",
         ["rust", "cargo", "tokio", "async", "trait", "ownership"],
         ["Cargo.toml", "Cargo.lock", "*.rs"]),
    Tech("C / C++",       "language", "N/A (lang)",   "LOW",      5, "Keep — dynamic .so modules stay proprietary",
         ["malloc", "pthread", "cmake", "makefile", "include", "ifndef"],
         ["CMakeLists.txt", "Makefile", "*.c", "*.h", "*.cpp"]),
    Tech("Java",          "language", "Oracle/OpenJDK","LOW",     4, "Keep — JAR packaging hides implementation",
         ["java", "maven", "gradle", "springframework", "jvm"],
         ["pom.xml", "build.gradle", "*.java"]),
    Tech("C#/.NET",       "language", "MIT",           "LOW",     4, "Keep — .NET NuGet package distribution",
         ["csharp", "dotnet", "nuget", "aspnet", "linq", "namespace"],
         ["*.csproj", "*.sln", "*.cs", "NuGet.Config"]),
    Tech("Ruby",          "language", "Ruby License",  "LOW",     3, "Replace with Python/Go for perf-critical parts",
         ["ruby", "rails", "gem", "bundler", "rake", "activerecord"],
         ["Gemfile", "Rakefile", "*.rb"]),
    Tech("PHP",           "language", "PHP License",   "LOW",     3, "Replace with Go/Python for new services",
         ["php", "composer", "laravel", "symfony", "wordpress"],
         ["composer.json", "*.php", "artisan"]),
    Tech("Erlang/Elixir", "language", "Apache-2.0",   "LOW",      5, "Keep — BEAM VM is unique, hard to replicate",
         ["erlang", "elixir", "otp", "genserver", "supervisor", "mix"],
         ["mix.exs", "rebar.config", "*.ex", "*.erl"]),

    # ── 2. WEB FRAMEWORKS ─────────────────────────────────────────────────────
    Tech("FastAPI",       "web_framework", "MIT",      "LOW",      2, "Wrap in proprietary API gateway layer",
         ["fastapi", "router", "depends", "lifespan", "pydantic"],
         ["main.py", "app.py", "api.py"]),
    Tech("Django",        "web_framework", "BSD-3",    "LOW",      3, "Add proprietary Django apps on top",
         ["django", "models", "views", "urls", "admin", "migrations"],
         ["manage.py", "settings.py", "urls.py"]),
    Tech("Flask",         "web_framework", "BSD-3",    "LOW",      2, "Replace with FastAPI or proprietary wrapper",
         ["flask", "blueprint", "route", "werkzeug", "jinja2"],
         ["app.py", "wsgi.py"]),
    Tech("Express.js",    "web_framework", "MIT",      "LOW",      2, "Replace with Fastify or proprietary HTTP server",
         ["express", "middleware", "router", "req", "res", "next"],
         ["app.js", "server.js", "index.js"]),
    Tech("Next.js",       "web_framework", "MIT",      "LOW",      3, "Keep — add proprietary pages/API routes",
         ["nextjs", "getServerSideProps", "getStaticProps", "nextConfig", "middleware"],
         ["next.config.*", "pages/", "_app.tsx"]),
    Tech("NestJS",        "web_framework", "MIT",      "LOW",      3, "Keep — add proprietary modules/decorators",
         ["nestjs", "controller", "injectable", "module", "decorator", "provider"],
         ["*.module.ts", "*.controller.ts", "*.service.ts"]),
    Tech("Gin",           "web_framework", "MIT",      "LOW",      2, "Replace with proprietary Echo/Fiber wrapper",
         ["gin", "ginContext", "ginRouter", "ginMiddleware"],
         ["main.go", "router.go", "handler.go"]),
    Tech("Axum",          "web_framework", "MIT",      "LOW",      2, "Replace with proprietary Actix-web layer",
         ["axum", "tower", "hyper", "handler", "router", "extract"],
         ["main.rs", "router.rs", "handler.rs"]),
    Tech("Rails",         "web_framework", "MIT",      "LOW",      3, "Add proprietary Rails engines on top",
         ["rails", "activerecord", "actioncontroller", "routes", "scaffold"],
         ["config/routes.rb", "Gemfile"]),
    Tech("Spring Boot",   "web_framework", "Apache-2", "LOW",      3, "Add proprietary Spring modules/starters",
         ["springboot", "restcontroller", "service", "repository", "autowired"],
         ["Application.java", "pom.xml"]),

    # ── 3. DATABASES ──────────────────────────────────────────────────────────
    Tech("PostgreSQL",    "database", "PostgreSQL",   "LOW",       3, "Add proprietary stored procedures / RLS policies",
         ["postgresql", "postgres", "psycopg", "asyncpg", "pg_", "libpq"],
         ["*.sql", "migrations/"]),
    Tech("MySQL",         "database", "GPL-2.0",      "MEDIUM",    3, "⚠️ GPL-2 — switch to PostgreSQL or MariaDB",
         ["mysql", "mysqldump", "innodb", "mariadb"],
         ["*.sql"]),
    Tech("Redis",         "database", "RSAL/BSD",     "MEDIUM",    3, "Replace hot-path with own in-memory store or Valkey",
         ["redis", "redisClient", "hset", "lpush", "pubsub", "keydb"],
         ["redis.conf", "*.redis"]),
    Tech("MongoDB",       "database", "SSPL-1.0",     "HIGH",      3, "🚨 SSPL — replace with PostgreSQL JSONB or FerretDB",
         ["mongodb", "mongoose", "findOne", "aggregate", "bson", "objectid"],
         ["*.js", "*.ts"]),
    Tech("SQLite",        "database", "Public Domain","LOW",        1, "Keep for embedded/edge, easy to swap",
         ["sqlite", "sqlite3", "wal", "vacuumdb"],
         ["*.db", "*.sqlite"]),
    Tech("ClickHouse",    "database", "Apache-2.0",   "LOW",       4, "Keep — build proprietary analytics layer on top",
         ["clickhouse", "mergetree", "aggregation", "olap"],
         ["*.sql", "clickhouse*.yaml"]),
    Tech("InfluxDB",      "database", "MIT/Proprietary","MEDIUM",  3, "Replace with VictoriaMetrics (MIT) or proprietary TSDB",
         ["influx", "influxdb", "measurement", "bucket", "flux"],
         ["influxdb.conf", "*.yaml"]),
    Tech("Cassandra",     "database", "Apache-2.0",   "LOW",       4, "Keep — add proprietary CQL abstraction layer",
         ["cassandra", "cqlsh", "keyspace", "scylladb"],
         ["*.cql"]),
    Tech("Elasticsearch", "database", "SSPL/Elastic", "HIGH",      4, "🚨 Elastic license — replace with OpenSearch or own",
         ["elasticsearch", "kibana", "lucene", "searchIndex"],
         ["elasticsearch.yml"]),
    Tech("DynamoDB",      "database", "AWS Proprietary","HIGH",    4, "Vendor lock-in — abstract via DAL layer",
         ["dynamodb", "putItem", "getItem", "scanTable", "aws_dynamodb"],
         ["serverless.yml", "*.tf"]),

    # ── 4. MESSAGE QUEUES ─────────────────────────────────────────────────────
    Tech("Kafka",         "messaging", "Apache-2.0",  "LOW",       4, "Keep — build proprietary topic/schema registry",
         ["kafka", "producer", "consumer", "topic", "partition", "confluent"],
         ["kafka.properties", "*.yaml"]),
    Tech("RabbitMQ",      "messaging", "MPL-2.0",     "LOW",       3, "Replace with NATS or proprietary broker",
         ["rabbitmq", "amqp", "exchange", "queue", "vhost", "pika"],
         ["rabbitmq.conf", "*.yaml"]),
    Tech("NATS",          "messaging", "Apache-2.0",  "LOW",       3, "Keep — add proprietary subject namespacing",
         ["nats", "jetstream", "subscribe", "publish", "natsClient"],
         ["nats.conf", "*.go"]),
    Tech("Celery",        "messaging", "BSD-3",        "LOW",      2, "Replace with proprietary task queue (Dramatiq/etc.)",
         ["celery", "task", "worker", "beat", "apply_async", "shared_task"],
         ["celery*.py", "tasks.py"]),
    Tech("Redis Streams", "messaging", "RSAL/BSD",     "MEDIUM",   2, "Replace with Kafka or proprietary stream",
         ["xadd", "xread", "xgroup", "stream", "consumer_group"],
         []),
    Tech("gRPC",          "messaging", "Apache-2.0",  "LOW",       3, "Keep — generate proprietary .proto schemas",
         ["grpc", "protobuf", "proto", "stub", "channel", "servicer"],
         ["*.proto", "grpc*.py"]),

    # ── 5. PROTOCOLS ──────────────────────────────────────────────────────────
    Tech("SIP",           "protocol", "RFC (free)",   "LOW",       5, "Build proprietary SIP stack / B2BUA / billing layer",
         ["sip", "invite", "register", "dialog", "transaction", "via", "sdp"],
         ["*.cfg", "*.c", "kamailio*"]),
    Tech("WebRTC",        "protocol", "BSD/W3C",      "LOW",       5, "Build proprietary media server / SFU / MCU",
         ["webrtc", "peerconnection", "ice", "dtls", "srtp", "sdp", "stun", "turn"],
         ["*.js", "*.ts", "*.cpp"]),
    Tech("WebSocket",     "protocol", "RFC 6455",     "LOW",       2, "Build proprietary WS gateway with auth/billing",
         ["websocket", "ws", "wss", "upgrade", "onmessage", "onopen"],
         ["*.js", "*.py", "*.go"]),
    Tech("REST/HTTP",     "protocol", "RFC (free)",   "LOW",       1, "Add proprietary API gateway / rate limiting",
         ["openapi", "swagger", "rest", "endpoint", "http", "crud"],
         ["openapi.yaml", "swagger.json"]),
    Tech("GraphQL",       "protocol", "MIT",          "LOW",       3, "Build proprietary schema / federation layer",
         ["graphql", "schema", "resolver", "mutation", "query", "subscription"],
         ["schema.graphql", "*.graphql"]),
    Tech("MQTT",          "protocol", "Apache-2.0",   "LOW",       3, "Build proprietary MQTT broker / topic auth",
         ["mqtt", "broker", "topic", "publish", "subscribe", "qos", "mosquitto"],
         ["mosquitto.conf", "*.yaml"]),
    Tech("RTSP/RTP",      "protocol", "RFC (free)",   "LOW",       4, "Build proprietary media relay / recording tier",
         ["rtsp", "rtp", "rtcp", "sdp", "stream", "media", "codec"],
         ["*.c", "*.cpp", "*.go"]),

    # ── 6. AUTH & SECURITY ────────────────────────────────────────────────────
    Tech("OAuth2 / OIDC", "auth", "RFC (free)",       "LOW",       3, "Build proprietary IdP / add enterprise SSO tier",
         ["oauth", "oidc", "authorization_code", "token_endpoint", "client_credentials"],
         ["*.yaml", "*.json", "auth*.py"]),
    Tech("JWT",           "auth", "RFC 7519",         "LOW",       1, "Build proprietary JWT signing service",
         ["jwt", "jsonwebtoken", "bearer", "claims", "payload", "signature"],
         ["auth*.py", "middleware*.ts"]),
    Tech("SAML",          "auth", "OASIS (free)",     "LOW",       4, "Build proprietary SAML SP — Enterprise SSO gate",
         ["saml", "assertion", "idp", "sp", "metadata", "entityid"],
         ["*.xml", "saml*.py"]),
    Tech("RBAC",          "auth", "N/A (pattern)",    "LOW",       2, "Build proprietary RBAC + ABAC engine as paid tier",
         ["rbac", "role", "permission", "policy", "acl", "casbin", "authorize"],
         ["roles*.py", "permissions*.ts"]),
    Tech("API Keys",      "auth", "N/A (pattern)",    "LOW",       1, "Build proprietary key management / rotation SaaS",
         ["apikey", "api_key", "x-api-key", "secret", "token", "rotate"],
         ["*.py", "*.ts", "*.go"]),
    Tech("mTLS / TLS",    "auth", "RFC (free)",       "LOW",       3, "Build proprietary cert manager / PKI service",
         ["mtls", "tls", "certificate", "x509", "ssl", "handshake"],
         ["*.crt", "*.pem", "*.yaml"]),

    # ── 7. AI / ML ────────────────────────────────────────────────────────────
    Tech("OpenAI API",    "ai_ml", "Proprietary",     "HIGH",      2, "Build proprietary LLM abstraction / model router",
         ["openai", "gpt", "chatgpt", "completion", "embedding", "dall_e"],
         ["*.py", "*.ts", "*.env"]),
    Tech("Anthropic",     "ai_ml", "Proprietary",     "HIGH",      2, "Abstract behind LLM router layer",
         ["anthropic", "claude", "messages", "content_block"],
         ["*.py", "*.ts"]),
    Tech("HuggingFace",   "ai_ml", "Apache-2.0",      "LOW",       3, "Keep — fine-tune proprietary models on top",
         ["huggingface", "transformers", "pipeline", "tokenizer", "from_pretrained"],
         ["*.py", "requirements*.txt"]),
    Tech("PyTorch",       "ai_ml", "BSD-3",           "LOW",       5, "Keep — build proprietary model architecture",
         ["torch", "pytorch", "tensor", "cuda", "autograd", "nn.module"],
         ["*.py", "requirements*.txt"]),
    Tech("LangChain",     "ai_ml", "MIT",             "LOW",       2, "Replace with proprietary chain/agent framework",
         ["langchain", "llmchain", "agent", "tool", "retriever", "vectorstore"],
         ["*.py"]),
    Tech("LlamaIndex",    "ai_ml", "MIT",             "LOW",       2, "Replace with proprietary RAG pipeline",
         ["llamaindex", "llama_index", "index", "query_engine", "node_parser"],
         ["*.py"]),
    Tech("Ollama",        "ai_ml", "MIT",             "LOW",       2, "Replace with proprietary local LLM server",
         ["ollama", "llm", "generate", "chat", "pull", "modelfile"],
         ["*.py", "*.ts", "Modelfile"]),

    # ── 8. INFRASTRUCTURE ─────────────────────────────────────────────────────
    Tech("Docker",        "infra", "Apache-2.0",      "LOW",       1, "Keep — add proprietary docker base images",
         ["docker", "dockerfile", "container", "image", "compose"],
         ["Dockerfile*", "docker-compose*.yml", ".dockerignore"]),
    Tech("Kubernetes",    "infra", "Apache-2.0",      "LOW",       3, "Build proprietary Helm charts / operators",
         ["kubernetes", "kubectl", "k8s", "pod", "deployment", "namespace", "ingress"],
         ["*.yaml", "helm/", "k8s/"]),
    Tech("Terraform",     "infra", "BSL-1.1",         "MEDIUM",    3, "⚠️ BSL — use OpenTofu or build proprietary IaC",
         ["terraform", "provider", "resource", "variable", "tfvars"],
         ["*.tf", "*.tfvars", "main.tf"]),
    Tech("Helm",          "infra", "Apache-2.0",      "LOW",       2, "Build proprietary Helm chart repository",
         ["helm", "chart", "values", "template", "release", "tiller"],
         ["Chart.yaml", "values.yaml", "templates/"]),
    Tech("Ansible",       "infra", "GPL-3.0",         "HIGH",      2, "⚠️ GPL-3 — replace with Terraform + own scripts",
         ["ansible", "playbook", "role", "inventory", "task", "handler"],
         ["*.yml", "playbook*.yml", "inventory"]),
    Tech("nginx",         "infra", "BSD-2",           "LOW",       2, "Build proprietary nginx config generator",
         ["nginx", "location", "upstream", "proxy_pass", "server_name"],
         ["nginx.conf", "*.conf", "nginx/"]),

    # ── 9. OBSERVABILITY ──────────────────────────────────────────────────────
    Tech("Prometheus",    "observability", "Apache-2.0", "LOW",    2, "Build proprietary metrics + alerting SaaS layer",
         ["prometheus", "metric", "gauge", "counter", "histogram", "registry"],
         ["prometheus.yml", "*.yaml", "metrics*.py"]),
    Tech("Grafana",       "observability", "AGPL-3.0", "CRITICAL", 2, "🚨 AGPL — replace with Metabase/Superset or own",
         ["grafana", "dashboard", "panel", "datasource", "visualization"],
         ["grafana*.yml", "dashboards/"]),
    Tech("OpenTelemetry", "observability", "Apache-2.0","LOW",     2, "Keep — build proprietary collector/backend",
         ["opentelemetry", "otel", "tracer", "span", "exporter", "instrumentation"],
         ["otel*.yaml", "*.py", "*.go"]),
    Tech("Sentry",        "observability", "FSL-1.0",  "MEDIUM",   1, "Replace with proprietary error tracking",
         ["sentry", "dsn", "capture_exception", "breadcrumb", "transaction"],
         ["sentry.properties", "*.py", "*.ts"]),
    Tech("Jaeger",        "observability", "Apache-2.0","LOW",     2, "Replace with proprietary distributed tracing",
         ["jaeger", "tracer", "span", "zipkin", "sampling"],
         ["jaeger*.yaml", "*.go"]),
    Tech("Loki",          "observability", "AGPL-3.0", "CRITICAL", 2, "🚨 AGPL — replace with VictoriaLogs or own",
         ["loki", "logql", "label", "stream", "promtail"],
         ["loki*.yaml", "promtail*.yaml"]),

    # ── 10. STORAGE ───────────────────────────────────────────────────────────
    Tech("AWS S3",        "storage", "Proprietary",   "HIGH",      2, "Vendor lock-in — abstract with S3-compatible API",
         ["s3", "bucket", "put_object", "boto3", "aws_s3", "presigned"],
         ["*.py", "*.tf", "serverless.yml"]),
    Tech("MinIO",         "storage", "AGPL-3.0",      "CRITICAL",  2, "🚨 AGPL — replace with Ceph or proprietary S3 impl",
         ["minio", "bucket", "object", "mc", "minioclient"],
         ["minio*.yaml", "*.go", "*.py"]),
    Tech("Azure Blob",    "storage", "Proprietary",   "HIGH",      2, "Vendor lock-in — abstract behind storage interface",
         ["azure", "blob", "storageaccount", "containerclient", "blobclient"],
         ["*.py", "*.ts", "*.tf"]),
    Tech("GCS",           "storage", "Proprietary",   "HIGH",      2, "Vendor lock-in — abstract behind storage interface",
         ["gcs", "gcloud", "storage", "bucket", "google.cloud.storage"],
         ["*.py", "*.tf"]),
    Tech("Parquet",       "storage", "Apache-2.0",    "LOW",       2, "Keep — add proprietary columnar format layer",
         ["parquet", "pyarrow", "arrow", "schema", "rowgroup"],
         ["*.py", "*.go"]),

    # ── 11. TESTING ───────────────────────────────────────────────────────────
    Tech("pytest",        "testing", "MIT",           "LOW",       1, "Add proprietary test fixtures / plugins",
         ["pytest", "fixture", "parametrize", "conftest", "assert"],
         ["conftest.py", "test_*.py", "*_test.py"]),
    Tech("Jest",          "testing", "MIT",           "LOW",       1, "Add proprietary test utilities",
         ["jest", "describe", "expect", "beforeEach", "afterAll", "mock"],
         ["jest.config.*", "*.test.ts", "*.spec.ts"]),
    Tech("Go test",       "testing", "BSD-3",         "LOW",       1, "Add proprietary test helpers",
         ["testing", "testify", "mock", "gotest", "benchmark"],
         ["*_test.go"]),
    Tech("k6",            "testing", "AGPL-3.0",      "CRITICAL",  1, "🚨 AGPL — replace with Gatling or proprietary load test",
         ["k6", "loadtest", "vus", "duration", "scenarios", "http.get"],
         ["*.js", "k6*.sh", "run_benchmarks.sh"]),
    Tech("Playwright",    "testing", "Apache-2.0",    "LOW",       1, "Add proprietary test scenarios",
         ["playwright", "page", "browser", "locator", "screenshot"],
         ["playwright.config.*", "*.spec.ts"]),

    # ── 12. CI/CD ─────────────────────────────────────────────────────────────
    Tech("GitHub Actions","cicd", "Proprietary",      "MEDIUM",    1, "Vendor lock-in — abstract pipeline logic",
         ["github_actions", "workflow", "on_push", "jobs", "steps"],
         [".github/workflows/*.yml"]),
    Tech("GitLab CI",     "cicd", "MIT",              "LOW",       1, "Add proprietary CI templates",
         ["gitlab_ci", "gitlabci", "pipeline", "stages", "script", "artifacts"],
         [".gitlab-ci.yml"]),
    Tech("Docker Compose","cicd", "Apache-2.0",       "LOW",       1, "Replace with K8s or proprietary orchestration",
         ["docker_compose", "compose", "services", "volumes", "networks"],
         ["docker-compose*.yml"]),
]

# Category metadata
CATEGORY_META = {
    "language":       ("🖥️",  "Languages"),
    "web_framework":  ("🌐",  "Web Frameworks"),
    "database":       ("🗄️",  "Databases"),
    "messaging":      ("📨",  "Message Queues & IPC"),
    "protocol":       ("📡",  "Protocols"),
    "auth":           ("🔐",  "Auth & Security"),
    "ai_ml":          ("🤖",  "AI / ML"),
    "infra":          ("⚙️",  "Infrastructure"),
    "observability":  ("📊",  "Observability"),
    "storage":        ("💾",  "Storage"),
    "testing":        ("🧪",  "Testing"),
    "cicd":           ("🚀",  "CI / CD"),
}

RISK_ICON = {
    "LOW":      "✅",
    "MEDIUM":   "⚠️ ",
    "HIGH":     "🔴",
    "CRITICAL": "🚨",
}
REPLACE_ICON = {1: "🟢 Trivial", 2: "🟡 Easy", 3: "🟠 Medium", 4: "🔴 Hard", 5: "🔵 Expert"}


# ─────────────────────────────────────────────────────────────────────────────
# Detection engine
# ─────────────────────────────────────────────────────────────────────────────

def detect_by_file_patterns(root: Path, tech: Tech) -> list[str]:
    """Fast file-system scan for manifest files (Cargo.toml, go.mod, etc.)."""
    hits = []
    for pattern in tech.file_patterns:
        if pattern.startswith("*."):
            ext = pattern[1:]
            for f in list(root.rglob(f"*{ext}"))[:3]:
                rel = str(f.relative_to(root))
                if rel not in hits:
                    hits.append(rel)
        else:
            for f in list(root.rglob(pattern))[:3]:
                rel = str(f.relative_to(root))
                if rel not in hits:
                    hits.append(rel)
    return hits[:3]


def detect_by_bm25(idx: IndexStoreAdapter, tech: Tech, limit: int = 3) -> list[str]:
    """BM25 search across indexed content for technology tokens."""
    query = " ".join(tech.tokens[:4])
    try:
        hits = idx.search_code(query, limit=limit)
        return [h.path for h in hits if h.path]
    except Exception:
        return []


def run_detection(root: Path, idx: IndexStoreAdapter) -> list[Tech]:
    """Detect all technologies in the project."""
    for tech in TECH_DB:
        fs_hits = detect_by_file_patterns(root, tech)
        bm25_hits = detect_by_bm25(idx, tech)
        # Merge, deduplicate
        seen = set()
        merged = []
        for p in fs_hits + bm25_hits:
            if p not in seen:
                seen.add(p)
                merged.append(p)
        tech.evidence = merged[:4]
        tech.found = len(merged) > 0
    return TECH_DB


# ─────────────────────────────────────────────────────────────────────────────
# Report generation
# ─────────────────────────────────────────────────────────────────────────────

def build_report(project: str, root: Path, techs: list[Tech],
                 stats: dict, elapsed: float, report_path: Path) -> str:
    found = [t for t in techs if t.found]
    by_cat = defaultdict(list)
    for t in found:
        by_cat[t.category].append(t)

    critical = [t for t in found if t.license_risk == "CRITICAL"]
    high_risk = [t for t in found if t.license_risk == "HIGH"]
    swap_targets = [t for t in found if t.replaceability <= 2]

    lines = [
        f"# 🔬 Technology Stack Slicer — {project}",
        f"> {root} · {stats.get('total_files', 0)} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📋 Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **Technologies detected** | **{len(found)}** |",
        f"| Files indexed | {stats.get('total_files', 0)} |",
        f"| Categories | {len(by_cat)} |",
        f"| 🚨 CRITICAL license risks | {len(critical)} |",
        f"| 🔴 HIGH license risks | {len(high_risk)} |",
        f"| 🟡 Easy swap targets (≤2) | {len(swap_targets)} |",
        "",
    ]

    if critical or high_risk:
        lines += ["## 🚨 License Alerts (Action Required)", ""]
        for t in critical + high_risk:
            icon = RISK_ICON[t.license_risk]
            lines.append(f"- {icon} **{t.name}** ({t.license}) — {t.swap_note}")
        lines.append("")

    # Per-category sections
    for cat, (emoji, cat_name) in CATEGORY_META.items():
        cat_techs = by_cat.get(cat, [])
        if not cat_techs:
            continue
        lines += [f"## {emoji} {cat_name}", ""]
        lines += ["| Technology | License | Risk | Replace | Swap Target | Evidence |",
                  "|---|---|---|---|---|---|"]
        for t in cat_techs:
            risk_str = f"{RISK_ICON[t.license_risk]} {t.license_risk}"
            replace_str = REPLACE_ICON[t.replaceability]
            evidence_str = ", ".join(f"`{e}`" for e in t.evidence[:2]) if t.evidence else "—"
            swap = t.swap_note[:55] + "…" if len(t.swap_note) > 55 else t.swap_note
            lines.append(f"| **{t.name}** | {t.license} | {risk_str} | {replace_str} | {swap} | {evidence_str} |")
        lines.append("")

    # Swap targets section — easy wins
    lines += [
        "## 🔄 Proprietary Swap Targets (Replaceability ≤ 2 — Easy Wins)",
        "",
        "Technologies that can be replaced with your own proprietary implementation",
        "to remove open-source license constraints and create revenue gates:",
        "",
        "| Technology | Current License | Your Implementation | Effort |",
        "|---|---|---|---|",
    ]
    for t in sorted(swap_targets, key=lambda x: x.replaceability):
        lines.append(f"| **{t.name}** | {t.license} | {t.swap_note} | {REPLACE_ICON[t.replaceability]} |")
    lines.append("")

    # Full stack tree ASCII
    lines += ["## 🗺️ Full Stack Snapshot", "", "```"]
    lines.append(f"Project: {project}")
    for cat, (emoji, cat_name) in CATEGORY_META.items():
        cat_techs = by_cat.get(cat, [])
        if not cat_techs:
            continue
        lines.append(f"├── {emoji} {cat_name}")
        for i, t in enumerate(cat_techs):
            prefix = "│   └──" if i == len(cat_techs) - 1 else "│   ├──"
            risk = RISK_ICON[t.license_risk]
            lines.append(f"{prefix} {t.name} ({t.license}) {risk}")
    lines += ["```", ""]

    lines += [
        "---",
        f"*Stack Slicer · BM25+FileSystem · {date.today()} · Zero Magic*",
    ]

    content = "\n".join(lines)
    report_path.write_text(content, encoding="utf-8")
    return content


def print_console(project: str, root: Path, techs: list[Tech],
                  stats: dict, elapsed: float) -> None:
    found = [t for t in techs if t.found]
    by_cat = defaultdict(list)
    for t in found:
        by_cat[t.category].append(t)

    SEP = "═" * 75
    sep = "─" * 75

    print(f"\n{SEP}")
    print(f"  🔬 STACK SLICER: {project}")
    print(SEP)
    print(f"  Files indexed : {stats.get('total_files', 0)}")
    print(f"  Detected      : {len(found)} technologies")
    print(f"  Scan speed    : {elapsed:.3f}s")
    print(sep)

    for cat, (emoji, cat_name) in CATEGORY_META.items():
        cat_techs = by_cat.get(cat, [])
        if not cat_techs:
            continue
        print(f"\n  {emoji} {cat_name}")
        for t in cat_techs:
            risk = RISK_ICON[t.license_risk]
            replace = REPLACE_ICON[t.replaceability]
            ev = ", ".join(t.evidence[:2]) if t.evidence else "—"
            print(f"     {risk} {t.name:<22s}  {t.license:<18s}  swap={replace}")
            print(f"        → {t.swap_note[:65]}")
            print(f"        📁 {ev}")

    # License alerts
    critical = [t for t in found if t.license_risk in ("CRITICAL", "HIGH")]
    if critical:
        print(f"\n{sep}")
        print("  🚨 LICENSE ALERTS:")
        for t in critical:
            icon = RISK_ICON[t.license_risk]
            print(f"     {icon} {t.name} ({t.license}): {t.swap_note}")

    print(f"\n{SEP}")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/stack_slicer.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    # Locate artifacts dir for report output
    script_dir = Path(__file__).resolve().parent
    artifacts_dir = script_dir.parent.parent.parent / "antigravity-cli" / "brain"
    # Fallback: same dir as script
    if not artifacts_dir.exists():
        artifacts_dir = script_dir.parent / "reports"
        artifacts_dir.mkdir(exist_ok=True)

    # Find conversation artifacts dir
    report_dir = next(
        (p for p in sorted(artifacts_dir.glob("*"), reverse=True)
         if p.is_dir() and not p.name.startswith(".")),
        script_dir
    )

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = report_dir / f"stack_slicer_{safe_name}.md"

    print(f"\n  🔬 Stack Slicer — {project_name}")
    print(f"  📁 {project_path}")
    print(f"  ⏳ Building BM25 index...", end="", flush=True)

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    t_index = time.perf_counter() - t0
    print(f" {stats.get('total_files', 0)} files in {t_index*1000:.0f}ms")

    print(f"  🔎 Scanning {len(TECH_DB)} technologies...", end="", flush=True)
    t1 = time.perf_counter()
    techs = run_detection(project_path, idx)
    t_detect = time.perf_counter() - t1
    found_count = sum(1 for t in techs if t.found)
    print(f" {found_count} found in {t_detect*1000:.0f}ms")

    elapsed = time.perf_counter() - t0

    print_console(project_name, project_path, techs, stats, elapsed)

    build_report(project_name, project_path, techs, stats, elapsed, report_path)
    print(f"\n  [+] Report saved → {report_path}")
    print("═" * 75 + "\n")


if __name__ == "__main__":
    main()
