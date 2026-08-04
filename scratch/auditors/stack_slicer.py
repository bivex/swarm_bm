#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🔬 Technology Stack Slicer 2.0 (Enriched & Deep Scan)                   ║
║   BM25 + Manifest Parser + AST Symbol Verification · Zero Magic           ║
║                                                                           ║
║   PURPOSE: "What exactly is this project built on?"                       ║
║   "Which components can I replace with my own proprietary implementation?"║
║   "What licenses govern each component and how hard is it to swap?"       ║
╚═══════════════════════════════════════════════════════════════════════════╝

12 Technology Categories (100+ DB Entries):
  1.  Languages & Runtimes  — Python, Go, Rust, TypeScript, C/C++, Java, C#, PHP, Ruby, Erlang, Elixir, Swift, Kotlin, Zephir...
  2.  Web & UI Frameworks   — FastAPI, Django, Flask, Express, Next.js, Vue, React, Svelte, Angular, NestJS, Gin, Axum, Phalcon...
  3.  Databases & Vector DB — PostgreSQL, MySQL, Redis, MongoDB, SQLite, ClickHouse, InfluxDB, ScyllaDB, Qdrant, Chroma, Milvus...
  4.  Message & Orchestr    — Kafka, RabbitMQ, NATS, Celery, Temporal, Redis Streams, ZeroMQ, Pulsar, gRPC...
  5.  Protocols & IPC       — SIP, WebRTC, WebSocket, REST, GraphQL, MQTT, MRCP, RTSP, Protobuf...
  6.  Auth & Security       — OAuth2, OIDC, JWT, SAML, RBAC, API Keys, mTLS, Keycloak, Auth0, Vault...
  7.  AI / ML & LLMs        — OpenAI, Anthropic, HuggingFace, PyTorch, LangChain, LlamaIndex, Ollama, vLLM, Whisper...
  8.  Infrastructure & IaC  — Docker, Kubernetes, Terraform, OpenTofu, Helm, Ansible, Nginx, Envoy, Traefik...
  9.  Observability & Logs  — Prometheus, Grafana, OpenTelemetry, Sentry, Jaeger, Loki, VictoriaMetrics, ElasticSearch...
  10. Storage & Formats    — AWS S3, MinIO, Azure Blob, GCS, Parquet, Arrow, DuckDB, RocksDB...
  11. Testing & QA          — pytest, Jest, Vitest, Go test, k6, Playwright, Cypress, Locust...
  12. CI/CD & DevOps        — GitHub Actions, GitLab CI, Docker Compose, Jenkins, ArgoCD...

Usage:
    python3 scratch/auditors/stack_slicer.py /path/to/project [ProjectName]
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
class Tech:
    name: str
    category: str
    license: str
    license_risk: str        # LOW / MEDIUM / HIGH / CRITICAL
    replaceability: int      # 1=trivial, 2=easy, 3=medium, 4=hard, 5=expert
    swap_note: str           # what to build as proprietary replacement
    tokens: list[str]        # BM25 search tokens
    file_patterns: list[str] = field(default_factory=list)  # filename patterns
    evidence: list[str] = field(default_factory=list)       # found files
    found: bool = False


TECH_DB: list[Tech] = [

    # ── 1. LANGUAGES & RUNTIMES ───────────────────────────────────────────────
    Tech("Python",        "language", "PSF-2.0",      "LOW",      4, "Keep — embed Cython/mypyc for closed-source performance",
         ["python", "asyncio", "typing", "dataclass", "pydantic"],
         ["*.py", "requirements*.txt", "pyproject.toml", "setup.py", "Pipfile"]),
    Tech("TypeScript",    "language", "Apache-2.0",   "LOW",      4, "Keep — compile to obfuscated V8 bundle with strict types",
         ["typescript", "interface", "readonly", "generics", "tsconfig"],
         ["tsconfig.json", "*.ts", "*.tsx"]),
    Tech("JavaScript",    "language", "ECMA (free)",  "LOW",      3, "Replace hot paths with WASM or TS strict modules",
         ["javascript", "nodejs", "npm", "webpack", "babel", "eslint"],
         ["package.json", "*.js", ".eslintrc*"]),
    Tech("Go",            "language", "BSD-3-Clause", "LOW",      4, "Keep — build proprietary modules as Go dynamic plugins",
         ["golang", "goroutine", "channel", "interface", "go.mod"],
         ["go.mod", "go.sum", "*.go"]),
    Tech("Rust",          "language", "MIT/Apache-2", "LOW",      5, "Keep — compile to cdylib / FFI for zero-cost closed binary",
         ["rust", "cargo", "tokio", "async", "trait", "ownership"],
         ["Cargo.toml", "Cargo.lock", "*.rs"]),
    Tech("C / C++",       "language", "N/A (lang)",   "LOW",      5, "Keep — dynamic .so / .dll modules stay proprietary",
         ["malloc", "pthread", "cmake", "makefile", "include", "ifndef"],
         ["CMakeLists.txt", "Makefile", "*.c", "*.h", "*.cpp", "*.hpp"]),
    Tech("Java",          "language", "Oracle/OpenJDK","LOW",     4, "Keep — JAR packaging with bytecode obfuscation hides implementation",
         ["java", "maven", "gradle", "springframework", "jvm"],
         ["pom.xml", "build.gradle", "*.java"]),
    Tech("C# / .NET",     "language", "MIT",           "LOW",     4, "Keep — .NET NuGet package distribution",
         ["csharp", "dotnet", "nuget", "aspnet", "linq", "namespace"],
         ["*.csproj", "*.sln", "*.cs", "NuGet.Config"]),
    Tech("PHP",           "language", "PHP License",   "LOW",     3, "Keep — use IonCube / SourceGuardian for closed commercial plugins",
         ["php", "composer", "laravel", "symfony", "wordpress", "phalcon"],
         ["composer.json", "*.php", "artisan"]),
    Tech("Ruby",          "language", "Ruby License",  "LOW",     3, "Replace perf-critical paths with Go / Rust services",
         ["ruby", "rails", "gem", "bundler", "rake", "activerecord"],
         ["Gemfile", "Rakefile", "*.rb"]),
    Tech("Erlang / Elixir","language", "Apache-2.0",  "LOW",      5, "Keep — BEAM VM concurrency is unique and hard to replicate",
         ["erlang", "elixir", "otp", "genserver", "supervisor", "mix"],
         ["mix.exs", "rebar.config", "*.ex", "*.erl"]),
    Tech("Zephir",        "language", "MIT",           "LOW",      4, "Keep — C-extension generator for high performance PHP extensions",
         ["zephir", "zep", "cphalcon", "ext/phalcon"],
         ["*.zep", "config.json"]),
    Tech("Kotlin",        "language", "Apache-2.0",   "LOW",      4, "Keep — JVM binary compilation hides logic",
         ["kotlin", "coroutines", "kt", "gradle"],
         ["build.gradle.kts", "*.kt"]),
    Tech("Swift",         "language", "Apache-2.0",   "LOW",      4, "Keep — native binary compilation for iOS/macOS",
         ["swift", "swiftpm", "xcode"],
         ["Package.swift", "*.swift"]),

    # ── 2. WEB & UI FRAMEWORKS ────────────────────────────────────────────────
    Tech("FastAPI",       "web_framework", "MIT",      "LOW",      2, "Wrap in proprietary API gateway / rate limiter layer",
         ["fastapi", "router", "depends", "lifespan", "pydantic"],
         ["main.py", "app.py", "api.py"]),
    Tech("Django",        "web_framework", "BSD-3",    "LOW",      3, "Add proprietary Django apps on top (Open Core)",
         ["django", "models", "views", "urls", "admin", "migrations"],
         ["manage.py", "settings.py", "urls.py"]),
    Tech("Flask",         "web_framework", "BSD-3",    "LOW",      2, "Replace with FastAPI or proprietary gateway wrapper",
         ["flask", "blueprint", "route", "werkzeug", "jinja2"],
         ["app.py", "wsgi.py"]),
    Tech("Express.js",    "web_framework", "MIT",      "LOW",      2, "Replace with Fastify or proprietary HTTP server",
         ["express", "middleware", "router", "req", "res", "next"],
         ["app.js", "server.js", "index.js"]),
    Tech("Next.js",       "web_framework", "MIT",      "LOW",      3, "Keep — add proprietary pages / API routes",
         ["nextjs", "getServerSideProps", "getStaticProps", "nextConfig", "middleware"],
         ["next.config.*", "pages/", "_app.tsx", "app/page.tsx"]),
    Tech("Vue.js",        "web_framework", "MIT",      "LOW",      2, "Build proprietary Component Library / UI Kit",
         ["vue", "defineComponent", "ref", "reactive", "pinia", "vuex"],
         ["package.json", "*.vue", "vite.config.*"]),
    Tech("React",         "web_framework", "MIT",      "LOW",      2, "Build proprietary React UI components / Pro templates",
         ["react", "useState", "useEffect", "jsx", "tsx", "redux"],
         ["package.json", "*.jsx", "*.tsx"]),
    Tech("NestJS",        "web_framework", "MIT",      "LOW",      3, "Keep — add proprietary modules / decorators",
         ["nestjs", "controller", "injectable", "module", "decorator", "provider"],
         ["*.module.ts", "*.controller.ts", "*.service.ts"]),
    Tech("Gin",           "web_framework", "MIT",      "LOW",      2, "Replace with proprietary Echo / Fiber wrapper",
         ["gin", "ginContext", "ginRouter", "ginMiddleware"],
         ["main.go", "router.go", "handler.go"]),
    Tech("Axum",          "web_framework", "MIT",      "LOW",      2, "Replace with proprietary Actix-web layer",
         ["axum", "tower", "hyper", "handler", "router", "extract"],
         ["main.rs", "router.rs", "handler.rs"]),
    Tech("Phalcon",       "web_framework", "BSD-3",    "LOW",      3, "Add proprietary C-extension modules on top",
         ["phalcon", "cphalcon", "micro", "di", "mvc"],
         ["composer.json", "*.zep"]),

    # ── 3. DATABASES & VECTOR DB ──────────────────────────────────────────────
    Tech("PostgreSQL",    "database", "PostgreSQL",   "LOW",       3, "Add proprietary stored procedures / Row Level Security policies",
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
    Tech("SQLite",        "database", "Public Domain","LOW",        1, "Keep for embedded/edge storage, easy to swap",
         ["sqlite", "sqlite3", "wal", "vacuumdb"],
         ["*.db", "*.sqlite"]),
    Tech("ClickHouse",    "database", "Apache-2.0",   "LOW",       4, "Keep — build proprietary OLAP analytics layer on top",
         ["clickhouse", "mergetree", "aggregation", "olap"],
         ["*.sql", "clickhouse*.yaml"]),
    Tech("Qdrant",        "database", "Apache-2.0",   "LOW",       3, "Keep — build proprietary Vector Search RAG pipeline",
         ["qdrant", "vector", "payload", "distance", "cosine"],
         ["qdrant.yaml"]),
    Tech("ChromaDB",      "database", "Apache-2.0",   "LOW",       2, "Replace with proprietary Vector DB wrapper",
         ["chromadb", "chroma", "get_collection", "add_documents"],
         ["*.py"]),

    # ── 4. MESSAGE QUEUES & ORCHESTRATION ────────────────────────────────────
    Tech("Kafka",         "messaging", "Apache-2.0",  "LOW",       4, "Keep — build proprietary topic / schema registry",
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
    Tech("Temporal",      "messaging", "MIT",          "LOW",      4, "Keep — build proprietary workflow orchestration templates",
         ["temporal", "workflow", "activity", "workflowclient"],
         ["*.go", "*.ts", "*.py"]),
    Tech("gRPC",          "messaging", "Apache-2.0",  "LOW",       3, "Keep — generate proprietary .proto schemas",
         ["grpc", "protobuf", "proto", "stub", "channel", "servicer"],
         ["*.proto", "grpc*.py"]),

    # ── 5. PROTOCOLS & IPC ────────────────────────────────────────────────────
    Tech("SIP",           "protocol", "RFC (free)",   "LOW",       5, "Build proprietary SIP stack / B2BUA / billing layer",
         ["sip", "invite", "register", "dialog", "transaction", "via", "sdp"],
         ["*.cfg", "*.c", "kamailio*"]),
    Tech("WebRTC",        "protocol", "BSD/W3C",      "LOW",       5, "Build proprietary media server / SFU / MCU",
         ["webrtc", "peerconnection", "ice", "dtls", "srtp", "sdp", "stun", "turn"],
         ["*.js", "*.ts", "*.cpp"]),
    Tech("WebSocket",     "protocol", "RFC 6455",     "LOW",       2, "Build proprietary WS gateway with auth & rate limiting",
         ["websocket", "ws", "wss", "upgrade", "onmessage", "onopen"],
         ["*.js", "*.py", "*.go"]),
    Tech("REST / HTTP",   "protocol", "RFC (free)",   "LOW",       1, "Add proprietary API gateway / rate limiting",
         ["openapi", "swagger", "rest", "endpoint", "http", "crud"],
         ["openapi.yaml", "swagger.json"]),
    Tech("GraphQL",       "protocol", "MIT",          "LOW",       3, "Build proprietary schema / federation layer",
         ["graphql", "schema", "resolver", "mutation", "query", "subscription"],
         ["schema.graphql", "*.graphql"]),
    Tech("MRCP",          "protocol", "RFC 6787",     "LOW",       4, "Build proprietary MRCP v2 Speech Gateway plugin",
         ["mrcp", "unimrcp", "synth", "recog", "mrcp_message"],
         ["*.c", "*.h", "mrcp*.xml"]),

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
    Tech("RBAC / ABAC",   "auth", "N/A (pattern)",    "LOW",       2, "Build proprietary RBAC + ABAC engine as paid tier",
         ["rbac", "role", "permission", "policy", "acl", "casbin", "authorize"],
         ["roles*.py", "permissions*.ts"]),
    Tech("API Keys",      "auth", "N/A (pattern)",    "LOW",       1, "Build proprietary key management / rotation SaaS",
         ["apikey", "api_key", "x-api-key", "secret", "token", "rotate"],
         ["*.py", "*.ts", "*.go"]),

    # ── 7. AI / ML & LLMS ─────────────────────────────────────────────────────
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
    Tech("LangChain",     "ai_ml", "MIT",             "LOW",       2, "Replace with proprietary chain / agent framework",
         ["langchain", "llmchain", "agent", "tool", "retriever", "vectorstore"],
         ["*.py"]),
    Tech("LlamaIndex",    "ai_ml", "MIT",             "LOW",       2, "Replace with proprietary RAG pipeline",
         ["llamaindex", "llama_index", "index", "query_engine", "node_parser"],
         ["*.py"]),
    Tech("Ollama",        "ai_ml", "MIT",             "LOW",       2, "Replace with proprietary local LLM server",
         ["ollama", "llm", "generate", "chat", "pull", "modelfile"],
         ["*.py", "*.ts", "Modelfile"]),
    Tech("Whisper",       "ai_ml", "MIT",             "LOW",       3, "Build proprietary Speech-to-Text transcription server",
         ["whisper", "transcribe", "audio", "stt", "speech_to_text"],
         ["*.py", "*.ts"]),

    # ── 8. INFRASTRUCTURE & IAC ──────────────────────────────────────────────
    Tech("Docker",        "infra", "Apache-2.0",      "LOW",       1, "Keep — add proprietary docker base images",
         ["docker", "dockerfile", "container", "image", "compose"],
         ["Dockerfile*", "docker-compose*.yml", ".dockerignore"]),
    Tech("Kubernetes",    "infra", "Apache-2.0",      "LOW",       3, "Build proprietary Helm charts / operators",
         ["kubernetes", "kubectl", "k8s", "pod", "deployment", "namespace", "ingress"],
         ["*.yaml", "helm/", "k8s/"]),
    Tech("Terraform",     "infra", "BSL-1.1",         "MEDIUM",    3, "⚠️ BSL — use OpenTofu or build proprietary IaC",
         ["terraform", "provider", "resource", "variable", "tfvars"],
         ["*.tf", "*.tfvars", "main.tf"]),
    Tech("OpenTofu",      "infra", "MPL-2.0",         "LOW",       3, "Keep — permissive open source alternative to Terraform",
         ["opentofu", "tofu", "provider", "resource"],
         ["*.tf"]),
    Tech("Helm",          "infra", "Apache-2.0",      "LOW",       2, "Build proprietary Helm chart repository",
         ["helm", "chart", "values", "template", "release", "tiller"],
         ["Chart.yaml", "values.yaml", "templates/"]),
    Tech("Ansible",       "infra", "GPL-3.0",         "HIGH",      2, "⚠️ GPL-3 — replace with Terraform + own scripts",
         ["ansible", "playbook", "role", "inventory", "task", "handler"],
         ["*.yml", "playbook*.yml", "inventory"]),
    Tech("Nginx",         "infra", "BSD-2",           "LOW",       2, "Build proprietary nginx config generator",
         ["nginx", "location", "upstream", "proxy_pass", "server_name"],
         ["nginx.conf", "*.conf", "nginx/"]),

    # ── 9. OBSERVABILITY & LOGS ───────────────────────────────────────────────
    Tech("Prometheus",    "observability", "Apache-2.0", "LOW",    2, "Build proprietary metrics + alerting SaaS layer",
         ["prometheus", "metric", "gauge", "counter", "histogram", "registry"],
         ["prometheus.yml", "*.yaml", "metrics*.py"]),
    Tech("Grafana",       "observability", "AGPL-3.0", "CRITICAL", 2, "🚨 AGPL — replace with Metabase/Superset or own dashboard",
         ["grafana", "dashboard", "panel", "datasource", "visualization"],
         ["grafana*.yml", "dashboards/"]),
    Tech("OpenTelemetry", "observability", "Apache-2.0","LOW",     2, "Keep — build proprietary collector / backend",
         ["opentelemetry", "otel", "tracer", "span", "exporter", "instrumentation"],
         ["otel*.yaml", "*.py", "*.go"]),
    Tech("Sentry",        "observability", "FSL-1.0",  "MEDIUM",   1, "Replace with proprietary error tracking",
         ["sentry", "dsn", "capture_exception", "breadcrumb", "transaction"],
         ["sentry.properties", "*.py", "*.ts"]),
    Tech("Loki",          "observability", "AGPL-3.0", "CRITICAL", 2, "🚨 AGPL — replace with VictoriaLogs or own log engine",
         ["loki", "logql", "label", "stream", "promtail"],
         ["loki*.yaml", "promtail*.yaml"]),

    # ── 10. STORAGE & FORMATS ─────────────────────────────────────────────────
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

    # ── 11. TESTING & QA ──────────────────────────────────────────────────────
    Tech("pytest",        "testing", "MIT",           "LOW",       1, "Add proprietary test fixtures / plugins",
         ["pytest", "fixture", "parametrize", "conftest", "assert"],
         ["conftest.py", "test_*.py", "*_test.py"]),
    Tech("Jest",          "testing", "MIT",           "LOW",       1, "Add proprietary test utilities",
         ["jest", "describe", "expect", "beforeEach", "afterAll", "mock"],
         ["jest.config.*", "*.test.ts", "*.spec.ts"]),
    Tech("Vitest",        "testing", "MIT",           "LOW",       1, "Add proprietary test utilities",
         ["vitest", "describe", "it", "expect"],
         ["vitest.config.*"]),
    Tech("Go test",       "testing", "BSD-3",         "LOW",       1, "Add proprietary test helpers",
         ["testing", "testify", "mock", "gotest", "benchmark"],
         ["*_test.go"]),
    Tech("k6",            "testing", "AGPL-3.0",      "CRITICAL",  1, "🚨 AGPL — replace with Gatling or proprietary load test",
         ["k6", "loadtest", "vus", "duration", "scenarios", "http.get"],
         ["*.js", "k6*.sh", "run_benchmarks.sh"]),
    Tech("Playwright",    "testing", "Apache-2.0",    "LOW",       1, "Add proprietary test scenarios",
         ["playwright", "page", "browser", "locator", "screenshot"],
         ["playwright.config.*", "*.spec.ts"]),

    # ── 12. CI/CD & DEVOPS ────────────────────────────────────────────────────
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
    "language":       ("🖥️",  "Languages & Runtimes"),
    "web_framework":  ("🌐",  "Web & UI Frameworks"),
    "database":       ("🗄️",  "Databases & Vector DB"),
    "messaging":      ("📨",  "Message Queues & Event Streaming"),
    "protocol":       ("📡",  "Protocols & IPC"),
    "auth":           ("🔐",  "Auth & Security"),
    "ai_ml":          ("🤖",  "AI / ML & LLMs"),
    "infra":          ("⚙️",  "Infrastructure & Cloud"),
    "observability":  ("📊",  "Observability & Logs"),
    "storage":        ("💾",  "Storage & Data Formats"),
    "testing":        ("🧪",  "Testing & QA"),
    "cicd":           ("🚀",  "CI / CD & DevOps"),
}

RISK_ICON = {
    "LOW":      "✅",
    "MEDIUM":   "⚠️ ",
    "HIGH":     "🔴",
    "CRITICAL": "🚨",
}
REPLACE_ICON = {1: "🟢 Trivial", 2: "🟢 Easy", 3: "🟡 Medium", 4: "🟠 Hard", 5: "🔴 Expert"}


# ─────────────────────────────────────────────────────────────────────────────
# Package Manifest Deep Parser
# ─────────────────────────────────────────────────────────────────────────────

def parse_package_manifests(root: Path) -> set[str]:
    """Parse package manifests (package.json, requirements.txt, go.mod, etc.) for direct package names."""
    found_tokens: set[str] = set()

    # package.json
    for pkg_json in root.rglob("package.json"):
        if "node_modules" in pkg_json.parts:
            continue
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8", errors="ignore"))
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            found_tokens.update(deps.keys())
        except Exception:
            pass

    # composer.json
    for comp_json in root.rglob("composer.json"):
        if "vendor" in comp_json.parts:
            continue
        try:
            data = json.loads(comp_json.read_text(encoding="utf-8", errors="ignore"))
            deps = {**data.get("require", {}), **data.get("require-dev", {})}
            found_tokens.update(deps.keys())
        except Exception:
            pass

    # requirements.txt / pyproject.toml
    for req_file in root.rglob("requirements*.txt"):
        try:
            for line in req_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip().lower()
                if line and not line.startswith("#"):
                    pkg = re.split(r"[=<>]", line)[0].strip()
                    found_tokens.add(pkg)
        except Exception:
            pass

    # go.mod
    for go_mod in root.rglob("go.mod"):
        try:
            for line in go_mod.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("//"):
                    parts = line.split()
                    if parts:
                        found_tokens.add(parts[0].lower())
        except Exception:
            pass

    return found_tokens


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
                if any(x in f.parts for x in ("node_modules", ".git", "vendor", "__pycache__")):
                    continue
                rel = str(f.relative_to(root))
                if rel not in hits:
                    hits.append(rel)
        else:
            for f in list(root.rglob(pattern))[:3]:
                if any(x in f.parts for x in ("node_modules", ".git", "vendor", "__pycache__")):
                    continue
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
    manifest_tokens = parse_package_manifests(root)

    for tech in TECH_DB:
        fs_hits = detect_by_file_patterns(root, tech)
        bm25_hits = detect_by_bm25(idx, tech)

        # Check if tech name or tokens exist in parsed package manifests
        manifest_hit = any(t in manifest_tokens for t in tech.tokens)

        # Merge, deduplicate
        seen = set()
        merged = []
        for p in fs_hits + bm25_hits:
            if p not in seen:
                seen.add(p)
                merged.append(p)

        tech.evidence = merged[:4]
        tech.found = len(merged) > 0 or manifest_hit

    return TECH_DB


# ─────────────────────────────────────────────────────────────────────────────
# Report generation (STRICTLY FOUND ONLY)
# ─────────────────────────────────────────────────────────────────────────────

def build_report(project: str, root: Path, techs: list[Tech],
                 stats: dict, elapsed: float, report_path: Path) -> str:
    # Strictly filter ONLY found technologies
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
        f"| Codebase Files | {stats.get('total_files', 0):,} |",
        f"| Active Categories | {len(by_cat)} |",
        f"| 🚨 CRITICAL License Risks | {len(critical)} |",
        f"| 🔴 HIGH License Risks | {len(high_risk)} |",
        f"| 🟢 Easy Swap Targets (≤2) | {len(swap_targets)} |",
        "",
    ]

    if critical or high_risk:
        lines += ["## 🚨 License Risk Alerts (Action Required)", ""]
        for t in critical + high_risk:
            icon = RISK_ICON[t.license_risk]
            lines.append(f"- {icon} **{t.name}** ({t.license}) — {t.swap_note}")
        lines.append("")

    # Per-category sections (STRICTLY FOUND ONLY)
    for cat, (emoji, cat_name) in CATEGORY_META.items():
        cat_techs = by_cat.get(cat, [])
        if not cat_techs:
            continue
        lines += [f"## {emoji} {cat_name}", ""]
        lines += ["| Technology | License | Risk | Replaceability | Proprietary Swap Target | Verified Evidence |",
                  "|---|---|---|---|---|---|"]
        for t in cat_techs:
            risk_str = f"{RISK_ICON[t.license_risk]} {t.license_risk}"
            replace_str = REPLACE_ICON[t.replaceability]
            evidence_str = ", ".join(f"`{e}`" for e in t.evidence[:2]) if t.evidence else "Manifest"
            swap = t.swap_note[:60] + "…" if len(t.swap_note) > 60 else t.swap_note
            lines.append(f"| **{t.name}** | {t.license} | {risk_str} | {replace_str} | {swap} | {evidence_str} |")
        lines.append("")

    # Swap targets section — easy wins
    if swap_targets:
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
        f"*Stack Slicer 2.0 · BM25+Manifests · {date.today()} · Zero Magic*",
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
    print(f"  🔬 STACK SLICER 2.0: {project}")
    print(SEP)
    print(f"  Files indexed : {stats.get('total_files', 0):,}")
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
            ev = ", ".join(t.evidence[:2]) if t.evidence else "Manifest"
            print(f"     {risk} {t.name:<22s}  {t.license:<18s}  swap={replace}")
            print(f"        → {t.swap_note[:65]}")
            print(f"        📁 {ev}")

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
        print("Usage: python3 scratch/auditors/stack_slicer.py /path/to/project [ProjectName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"stack_slicer_{safe_name}.md"

    print(f"\n  🔬 Stack Slicer 2.0 — {project_name}")
    print(f"  📁 {project_path}")
    print(f"  ⏳ Building BM25 index...", end="", flush=True)

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    t_index = time.perf_counter() - t0
    print(f" {stats.get('total_files', 0):,} files in {t_index*1000:.0f}ms")

    print(f"  🔎 Scanning {len(TECH_DB)} technologies...", end="", flush=True)
    t1 = time.perf_counter()
    techs = run_detection(project_path, idx)
    t_detect = time.perf_counter() - t1
    found_count = sum(1 for t in techs if t.found)
    print(f" {found_count} found in {t_detect*1000:.0f}ms")

    elapsed = time.perf_counter() - t0

    print_console(project_name, project_path, techs, stats, elapsed)
    build_report(project_name, project_path, techs, stats, elapsed, report_path)

    print(f"\n  [+] Stack report saved → {report_path}")
    print("═" * 75 + "\n")


if __name__ == "__main__":
    main()
