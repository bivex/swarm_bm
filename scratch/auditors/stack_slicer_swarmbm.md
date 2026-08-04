# 🔬 Technology Stack Slicer — SwarmBM
> /Volumes/External/Code/swarm_bm · 177 files · 0.95s · 2026-08-04

## 📋 Summary

| Metric | Value |
|---|---|
| **Technologies detected** | **75** |
| Files indexed | 177 |
| Categories | 12 |
| 🚨 CRITICAL license risks | 4 |
| 🔴 HIGH license risks | 9 |
| 🟡 Easy swap targets (≤2) | 39 |

## 🚨 License Alerts (Action Required)

- 🚨 **Grafana** (AGPL-3.0) — 🚨 AGPL — replace with Metabase/Superset or own
- 🚨 **Loki** (AGPL-3.0) — 🚨 AGPL — replace with VictoriaLogs or own
- 🚨 **MinIO** (AGPL-3.0) — 🚨 AGPL — replace with Ceph or proprietary S3 impl
- 🚨 **k6** (AGPL-3.0) — 🚨 AGPL — replace with Gatling or proprietary load test
- 🔴 **MongoDB** (SSPL-1.0) — 🚨 SSPL — replace with PostgreSQL JSONB or FerretDB
- 🔴 **Elasticsearch** (SSPL/Elastic) — 🚨 Elastic license — replace with OpenSearch or own
- 🔴 **DynamoDB** (AWS Proprietary) — Vendor lock-in — abstract via DAL layer
- 🔴 **OpenAI API** (Proprietary) — Build proprietary LLM abstraction / model router
- 🔴 **Anthropic** (Proprietary) — Abstract behind LLM router layer
- 🔴 **Ansible** (GPL-3.0) — ⚠️ GPL-3 — replace with Terraform + own scripts
- 🔴 **AWS S3** (Proprietary) — Vendor lock-in — abstract with S3-compatible API
- 🔴 **Azure Blob** (Proprietary) — Vendor lock-in — abstract behind storage interface
- 🔴 **GCS** (Proprietary) — Vendor lock-in — abstract behind storage interface

## 🖥️ Languages

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **Python** | PSF-2.0 | ✅ LOW | 🔴 Hard | Keep — embed Cython/mypyc for performance | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **TypeScript** | Apache-2.0 | ✅ LOW | 🔴 Hard | Keep — compile to V8 bundle, add TS strict mode | `JobObjects_RD/out/build/CMakeFiles/AgentJobEngine_EdgeCases_Test.dir/compiler_depend.ts`, `JobObjects_RD/out/build/CMakeFiles/AgentJobEngine.dir/compiler_depend.ts` |
| **JavaScript** | ECMA (free) | ✅ LOW | 🟠 Medium | Replace hot paths with WASM or TS strict | `bm25_server_FS_for-AI-asking/ramdisk_fs_server/ast_grep_symbols.py`, `JobObjects_RD/docs/Swarm_Scalability_Benchmark.md` |
| **Go** | BSD-3-Clause | ✅ LOW | 🔴 Hard | Keep — build proprietary modules as Go plugins | `swarm_mcp/application/senior_audit.py`, `JobObjects_RD/docs/JobObjects_Internals_Win11.md` |
| **Rust** | MIT/Apache-2 | ✅ LOW | 🔵 Expert | Keep — compile to cdylib for FFI licensing | `bm25_server_FS_for-AI-asking/ramdisk_fs_server/ast_grep_symbols.py`, `JobObjects_RD/out/build/CMakeFiles/CMakeConfigureLog.yaml` |
| **C / C++** | N/A (lang) | ✅ LOW | 🔵 Expert | Keep — dynamic .so modules stay proprietary | `JobObjects_RD/CMakeLists.txt`, `JobObjects_RD/out/build/Makefile` |
| **Java** | Oracle/OpenJDK | ✅ LOW | 🔴 Hard | Keep — JAR packaging hides implementation | `bm25_server_FS_for-AI-asking/README.md`, `bm25_server_FS_for-AI-asking/ramdisk_fs_server/indexer.py` |
| **C#/.NET** | MIT | ✅ LOW | 🔴 Hard | Keep — .NET NuGet package distribution | `JobObjects_RD/out/build/CMakeFiles/CMakeConfigureLog.yaml` |
| **PHP** | PHP License | ✅ LOW | 🟠 Medium | Replace with Go/Python for new services | `JobObjects_RD/out/build/CMakeFiles/CMakeConfigureLog.yaml` |

## 🌐 Web Frameworks

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **FastAPI** | MIT | ✅ LOW | 🟡 Easy | Wrap in proprietary API gateway layer | `swarm_mcp/main.py`, `tests/test_autoroute.py` |
| **Django** | BSD-3 | ✅ LOW | 🟠 Medium | Add proprietary Django apps on top | `tests/test_autoroute.py`, `tests/test_django_benchmark.py` |
| **Flask** | BSD-3 | ✅ LOW | 🟡 Easy | Replace with FastAPI or proprietary wrapper | `swarm_mcp/application/use_cases.py`, `swarm_mcp/infrastructure/mcp_server_adapter.py` |
| **Express.js** | MIT | ✅ LOW | 🟡 Easy | Replace with Fastify or proprietary HTTP server | `swarm_mcp/application/use_cases.py`, `swarm_mcp/infrastructure/mcp_server_adapter.py` |
| **NestJS** | MIT | ✅ LOW | 🟠 Medium | Keep — add proprietary modules/decorators | `JobObjects_RD/out/build/CMakeCache.txt`, `swarm_mcp/application/senior_audit.py` |
| **Gin** | MIT | ✅ LOW | 🟡 Easy | Replace with proprietary Echo/Fiber wrapper | `swarm_mcp/application/senior_audit.py` |
| **Axum** | MIT | ✅ LOW | 🟡 Easy | Replace with proprietary Actix-web layer | `bm25_server_FS_for-AI-asking/ramdisk_fs_server/server.py`, `bm25_server_FS_for-AI-asking/tests/test_skeleton_and_scip.py` |
| **Rails** | MIT | ✅ LOW | 🟠 Medium | Add proprietary Rails engines on top | `swarm_mcp/domain/services.py`, `swarm_mcp/application/senior_audit.py` |
| **Spring Boot** | Apache-2 | ✅ LOW | 🟠 Medium | Add proprietary Spring modules/starters | `bm25_server_FS_for-AI-asking/tests/test_skeleton_and_scip.py`, `bm25_server_FS_for-AI-asking/README.md` |

## 🗄️ Databases

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **Redis** | RSAL/BSD | ⚠️  MEDIUM | 🟠 Medium | Replace hot-path with own in-memory store or Valkey | `bm25_server_FS_for-AI-asking/src/redis_demo.c`, `swarm_mcp/application/senior_audit.py` |
| **MongoDB** | SSPL-1.0 | 🔴 HIGH | 🟠 Medium | 🚨 SSPL — replace with PostgreSQL JSONB or FerretDB | `JobObjects_RD/out/build/CMakeFiles/AgentJobEngine_EdgeCases_Test.dir/compiler_depend.ts`, `JobObjects_RD/out/build/CMakeFiles/AgentJobEngine.dir/compiler_depend.ts` |
| **ClickHouse** | Apache-2.0 | ✅ LOW | 🔴 Hard | Keep — build proprietary analytics layer on top | `swarm_mcp/application/senior_audit.py` |
| **InfluxDB** | MIT/Proprietary | ⚠️  MEDIUM | 🟠 Medium | Replace with VictoriaMetrics (MIT) or proprietary TSDB | `JobObjects_RD/out/build/CMakeFiles/CMakeConfigureLog.yaml`, `swarm_mcp/domain/services.py` |
| **Cassandra** | Apache-2.0 | ✅ LOW | 🔴 Hard | Keep — add proprietary CQL abstraction layer | `swarm_mcp/application/senior_audit.py` |
| **Elasticsearch** | SSPL/Elastic | 🔴 HIGH | 🔴 Hard | 🚨 Elastic license — replace with OpenSearch or own | `swarm_mcp/application/senior_audit.py` |
| **DynamoDB** | AWS Proprietary | 🔴 HIGH | 🔴 Hard | Vendor lock-in — abstract via DAL layer | `swarm_mcp/application/senior_audit.py` |

## 📨 Message Queues & IPC

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **Kafka** | Apache-2.0 | ✅ LOW | 🔴 Hard | Keep — build proprietary topic/schema registry | `JobObjects_RD/out/build/CMakeFiles/CMakeConfigureLog.yaml`, `swarm_mcp/application/senior_audit.py` |
| **RabbitMQ** | MPL-2.0 | ✅ LOW | 🟠 Medium | Replace with NATS or proprietary broker | `JobObjects_RD/out/build/CMakeFiles/CMakeConfigureLog.yaml`, `swarm_mcp/application/senior_audit.py` |
| **NATS** | Apache-2.0 | ✅ LOW | 🟠 Medium | Keep — add proprietary subject namespacing | `bm25_server_FS_for-AI-asking/ramdisk_fs_server/server.py`, `swarm_mcp/application/senior_audit.py` |
| **Celery** | BSD-3 | ✅ LOW | 🟡 Easy | Replace with proprietary task queue (Dramatiq/etc.) | `swarm_mcp/application/senior_audit.py`, `swarm_mcp/domain/services.py` |
| **Redis Streams** | RSAL/BSD | ⚠️  MEDIUM | 🟡 Easy | Replace with Kafka or proprietary stream | `swarm_mcp/application/senior_audit.py` |
| **gRPC** | Apache-2.0 | ✅ LOW | 🟠 Medium | Keep — generate proprietary .proto schemas | `swarm_mcp/application/senior_audit.py`, `bm25_server_FS_for-AI-asking/README.md` |

## 📡 Protocols

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **SIP** | RFC (free) | ✅ LOW | 🔵 Expert | Build proprietary SIP stack / B2BUA / billing layer | `bm25_server_FS_for-AI-asking/src/redis_demo.c`, `JobObjects_RD/out/build/CMakeFiles/4.3.3/CompilerIdC/CMakeCCompilerId.c` |
| **WebRTC** | BSD/W3C | ✅ LOW | 🔵 Expert | Build proprietary media server / SFU / MCU | `JobObjects_RD/out/build/CMakeFiles/AgentJobEngine_EdgeCases_Test.dir/compiler_depend.ts`, `JobObjects_RD/out/build/CMakeFiles/AgentJobEngine.dir/compiler_depend.ts` |
| **WebSocket** | RFC 6455 | ✅ LOW | 🟡 Easy | Build proprietary WS gateway with auth/billing | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **REST/HTTP** | RFC (free) | ✅ LOW | 🟢 Trivial | Add proprietary API gateway / rate limiting | `swarm_mcp/application/senior_audit.py`, `bm25_server_FS_for-AI-asking/tests/test_server.py` |
| **GraphQL** | MIT | ✅ LOW | 🟠 Medium | Build proprietary schema / federation layer | `swarm_mcp/application/senior_audit.py`, `bm25_server_FS_for-AI-asking/server.json` |
| **MQTT** | Apache-2.0 | ✅ LOW | 🟠 Medium | Build proprietary MQTT broker / topic auth | `JobObjects_RD/out/build/CMakeFiles/CMakeConfigureLog.yaml`, `bm25_server_FS_for-AI-asking/ramdisk_fs_server/server.py` |
| **RTSP/RTP** | RFC (free) | ✅ LOW | 🔴 Hard | Build proprietary media relay / recording tier | `bm25_server_FS_for-AI-asking/src/redis_demo.c`, `JobObjects_RD/out/build/CMakeFiles/4.3.3/CompilerIdC/CMakeCCompilerId.c` |

## 🔐 Auth & Security

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **OAuth2 / OIDC** | RFC (free) | ✅ LOW | 🟠 Medium | Build proprietary IdP / add enterprise SSO tier | `JobObjects_RD/out/build/CMakeFiles/CMakeConfigureLog.yaml`, `JobObjects_RD/launch.vs.json` |
| **JWT** | RFC 7519 | ✅ LOW | 🟢 Trivial | Build proprietary JWT signing service | `swarm_mcp/application/senior_audit.py`, `tests/test_senior_audit.py` |
| **SAML** | OASIS (free) | ✅ LOW | 🔴 Hard | Build proprietary SAML SP — Enterprise SSO gate | `bm25_server_FS_for-AI-asking/tests/test_server.py` |
| **RBAC** | N/A (pattern) | ✅ LOW | 🟡 Easy | Build proprietary RBAC + ABAC engine as paid tier | `swarm_mcp/application/senior_audit.py`, `JobObjects_RD/docs/AgentJobObject_Kernel_Research.md` |
| **API Keys** | N/A (pattern) | ✅ LOW | 🟢 Trivial | Build proprietary key management / rotation SaaS | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **mTLS / TLS** | RFC (free) | ✅ LOW | 🟠 Medium | Build proprietary cert manager / PKI service | `JobObjects_RD/out/build/CMakeFiles/CMakeConfigureLog.yaml` |

## 🤖 AI / ML

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **OpenAI API** | Proprietary | 🔴 HIGH | 🟡 Easy | Build proprietary LLM abstraction / model router | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **Anthropic** | Proprietary | 🔴 HIGH | 🟡 Easy | Abstract behind LLM router layer | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **HuggingFace** | Apache-2.0 | ✅ LOW | 🟠 Medium | Keep — fine-tune proprietary models on top | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **PyTorch** | BSD-3 | ✅ LOW | 🔵 Expert | Keep — build proprietary model architecture | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **LangChain** | MIT | ✅ LOW | 🟡 Easy | Replace with proprietary chain/agent framework | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **LlamaIndex** | MIT | ✅ LOW | 🟡 Easy | Replace with proprietary RAG pipeline | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **Ollama** | MIT | ✅ LOW | 🟡 Easy | Replace with proprietary local LLM server | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |

## ⚙️ Infrastructure

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **Docker** | Apache-2.0 | ✅ LOW | 🟢 Trivial | Keep — add proprietary docker base images | `JobObjects_RD/docs/JobObjects_Internals_Win11.md`, `JobObjects_RD/docs/Swarm_Scalability_Benchmark.md` |
| **Kubernetes** | Apache-2.0 | ✅ LOW | 🟠 Medium | Build proprietary Helm charts / operators | `JobObjects_RD/out/build/CMakeFiles/CMakeConfigureLog.yaml`, `swarm_mcp/application/senior_audit.py` |
| **Terraform** | BSL-1.1 | ⚠️  MEDIUM | 🟠 Medium | ⚠️ BSL — use OpenTofu or build proprietary IaC | `JobObjects_RD/out/build/CMakeCache.txt`, `swarm_mcp/application/senior_audit.py` |
| **Helm** | Apache-2.0 | ✅ LOW | 🟡 Easy | Build proprietary Helm chart repository | `swarm_mcp/application/senior_audit.py`, `swarm_mcp/infrastructure/job_engine_adapter.py` |
| **Ansible** | GPL-3.0 | 🔴 HIGH | 🟡 Easy | ⚠️ GPL-3 — replace with Terraform + own scripts | `bm25_server_FS_for-AI-asking/ramdisk_fs_server/scip_integration.py` |
| **nginx** | BSD-2 | ✅ LOW | 🟡 Easy | Build proprietary nginx config generator | `bm25_server_FS_for-AI-asking/ramdisk_fs_server/ask.py`, `swarm_mcp/application/senior_audit.py` |

## 📊 Observability

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **Prometheus** | Apache-2.0 | ✅ LOW | 🟡 Easy | Build proprietary metrics + alerting SaaS layer | `JobObjects_RD/out/build/CMakeFiles/CMakeConfigureLog.yaml`, `swarm_mcp/application/senior_audit.py` |
| **Grafana** | AGPL-3.0 | 🚨 CRITICAL | 🟡 Easy | 🚨 AGPL — replace with Metabase/Superset or own | `swarm_mcp/application/senior_audit.py` |
| **OpenTelemetry** | Apache-2.0 | ✅ LOW | 🟡 Easy | Keep — build proprietary collector/backend | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **Sentry** | FSL-1.0 | ⚠️  MEDIUM | 🟢 Trivial | Replace with proprietary error tracking | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **Jaeger** | Apache-2.0 | ✅ LOW | 🟡 Easy | Replace with proprietary distributed tracing | `swarm_mcp/application/senior_audit.py` |
| **Loki** | AGPL-3.0 | 🚨 CRITICAL | 🟡 Easy | 🚨 AGPL — replace with VictoriaLogs or own | `bm25_server_FS_for-AI-asking/ramdisk_fs_server/ramdisk.py`, `swarm_mcp/application/senior_audit.py` |

## 💾 Storage

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **AWS S3** | Proprietary | 🔴 HIGH | 🟡 Easy | Vendor lock-in — abstract with S3-compatible API | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **MinIO** | AGPL-3.0 | 🚨 CRITICAL | 🟡 Easy | 🚨 AGPL — replace with Ceph or proprietary S3 impl | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **Azure Blob** | Proprietary | 🔴 HIGH | 🟡 Easy | Vendor lock-in — abstract behind storage interface | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **GCS** | Proprietary | 🔴 HIGH | 🟡 Easy | Vendor lock-in — abstract behind storage interface | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |
| **Parquet** | Apache-2.0 | ✅ LOW | 🟡 Easy | Keep — add proprietary columnar format layer | `swarm_mcp/__init__.py`, `swarm_mcp/main.py` |

## 🧪 Testing

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **pytest** | MIT | ✅ LOW | 🟢 Trivial | Add proprietary test fixtures / plugins | `tests/test_senior_audit.py`, `tests/test_django_benchmark.py` |
| **Go test** | BSD-3 | ✅ LOW | 🟢 Trivial | Add proprietary test helpers | `swarm_mcp/application/senior_audit.py`, `JobObjects_RD/tests/AgentJobEngine_EdgeCases_Test.cpp` |
| **k6** | AGPL-3.0 | 🚨 CRITICAL | 🟢 Trivial | 🚨 AGPL — replace with Gatling or proprietary load test | `JobObjects_RD/tests/AgentSwarm_Benchmark.cpp`, `swarm_mcp/application/senior_audit.py` |
| **Playwright** | Apache-2.0 | ✅ LOW | 🟢 Trivial | Add proprietary test scenarios | `JobObjects_RD/docs/AgentJobObject_Kernel_Research.md`, `JobObjects_RD/src/AgentJobEngine.cpp` |

## 🚀 CI / CD

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **GitHub Actions** | Proprietary | ⚠️  MEDIUM | 🟢 Trivial | Vendor lock-in — abstract pipeline logic | `swarm_mcp/application/senior_audit.py`, `JobObjects_RD/docs/AgentJobObject_Kernel_Research.md` |
| **GitLab CI** | MIT | ✅ LOW | 🟢 Trivial | Add proprietary CI templates | `swarm_mcp/application/senior_audit.py`, `README.md` |
| **Docker Compose** | Apache-2.0 | ✅ LOW | 🟢 Trivial | Replace with K8s or proprietary orchestration | `JobObjects_RD/out/build/CMakeFiles/TargetDirectories.txt`, `swarm_mcp/domain/__init__.py` |

## 🔄 Proprietary Swap Targets (Replaceability ≤ 2 — Easy Wins)

Technologies that can be replaced with your own proprietary implementation
to remove open-source license constraints and create revenue gates:

| Technology | Current License | Your Implementation | Effort |
|---|---|---|---|
| **REST/HTTP** | RFC (free) | Add proprietary API gateway / rate limiting | 🟢 Trivial |
| **JWT** | RFC 7519 | Build proprietary JWT signing service | 🟢 Trivial |
| **API Keys** | N/A (pattern) | Build proprietary key management / rotation SaaS | 🟢 Trivial |
| **Docker** | Apache-2.0 | Keep — add proprietary docker base images | 🟢 Trivial |
| **Sentry** | FSL-1.0 | Replace with proprietary error tracking | 🟢 Trivial |
| **pytest** | MIT | Add proprietary test fixtures / plugins | 🟢 Trivial |
| **Go test** | BSD-3 | Add proprietary test helpers | 🟢 Trivial |
| **k6** | AGPL-3.0 | 🚨 AGPL — replace with Gatling or proprietary load test | 🟢 Trivial |
| **Playwright** | Apache-2.0 | Add proprietary test scenarios | 🟢 Trivial |
| **GitHub Actions** | Proprietary | Vendor lock-in — abstract pipeline logic | 🟢 Trivial |
| **GitLab CI** | MIT | Add proprietary CI templates | 🟢 Trivial |
| **Docker Compose** | Apache-2.0 | Replace with K8s or proprietary orchestration | 🟢 Trivial |
| **FastAPI** | MIT | Wrap in proprietary API gateway layer | 🟡 Easy |
| **Flask** | BSD-3 | Replace with FastAPI or proprietary wrapper | 🟡 Easy |
| **Express.js** | MIT | Replace with Fastify or proprietary HTTP server | 🟡 Easy |
| **Gin** | MIT | Replace with proprietary Echo/Fiber wrapper | 🟡 Easy |
| **Axum** | MIT | Replace with proprietary Actix-web layer | 🟡 Easy |
| **Celery** | BSD-3 | Replace with proprietary task queue (Dramatiq/etc.) | 🟡 Easy |
| **Redis Streams** | RSAL/BSD | Replace with Kafka or proprietary stream | 🟡 Easy |
| **WebSocket** | RFC 6455 | Build proprietary WS gateway with auth/billing | 🟡 Easy |
| **RBAC** | N/A (pattern) | Build proprietary RBAC + ABAC engine as paid tier | 🟡 Easy |
| **OpenAI API** | Proprietary | Build proprietary LLM abstraction / model router | 🟡 Easy |
| **Anthropic** | Proprietary | Abstract behind LLM router layer | 🟡 Easy |
| **LangChain** | MIT | Replace with proprietary chain/agent framework | 🟡 Easy |
| **LlamaIndex** | MIT | Replace with proprietary RAG pipeline | 🟡 Easy |
| **Ollama** | MIT | Replace with proprietary local LLM server | 🟡 Easy |
| **Helm** | Apache-2.0 | Build proprietary Helm chart repository | 🟡 Easy |
| **Ansible** | GPL-3.0 | ⚠️ GPL-3 — replace with Terraform + own scripts | 🟡 Easy |
| **nginx** | BSD-2 | Build proprietary nginx config generator | 🟡 Easy |
| **Prometheus** | Apache-2.0 | Build proprietary metrics + alerting SaaS layer | 🟡 Easy |
| **Grafana** | AGPL-3.0 | 🚨 AGPL — replace with Metabase/Superset or own | 🟡 Easy |
| **OpenTelemetry** | Apache-2.0 | Keep — build proprietary collector/backend | 🟡 Easy |
| **Jaeger** | Apache-2.0 | Replace with proprietary distributed tracing | 🟡 Easy |
| **Loki** | AGPL-3.0 | 🚨 AGPL — replace with VictoriaLogs or own | 🟡 Easy |
| **AWS S3** | Proprietary | Vendor lock-in — abstract with S3-compatible API | 🟡 Easy |
| **MinIO** | AGPL-3.0 | 🚨 AGPL — replace with Ceph or proprietary S3 impl | 🟡 Easy |
| **Azure Blob** | Proprietary | Vendor lock-in — abstract behind storage interface | 🟡 Easy |
| **GCS** | Proprietary | Vendor lock-in — abstract behind storage interface | 🟡 Easy |
| **Parquet** | Apache-2.0 | Keep — add proprietary columnar format layer | 🟡 Easy |

## 🗺️ Full Stack Snapshot

```
Project: SwarmBM
├── 🖥️ Languages
│   ├── Python (PSF-2.0) ✅
│   ├── TypeScript (Apache-2.0) ✅
│   ├── JavaScript (ECMA (free)) ✅
│   ├── Go (BSD-3-Clause) ✅
│   ├── Rust (MIT/Apache-2) ✅
│   ├── C / C++ (N/A (lang)) ✅
│   ├── Java (Oracle/OpenJDK) ✅
│   ├── C#/.NET (MIT) ✅
│   └── PHP (PHP License) ✅
├── 🌐 Web Frameworks
│   ├── FastAPI (MIT) ✅
│   ├── Django (BSD-3) ✅
│   ├── Flask (BSD-3) ✅
│   ├── Express.js (MIT) ✅
│   ├── NestJS (MIT) ✅
│   ├── Gin (MIT) ✅
│   ├── Axum (MIT) ✅
│   ├── Rails (MIT) ✅
│   └── Spring Boot (Apache-2) ✅
├── 🗄️ Databases
│   ├── Redis (RSAL/BSD) ⚠️ 
│   ├── MongoDB (SSPL-1.0) 🔴
│   ├── ClickHouse (Apache-2.0) ✅
│   ├── InfluxDB (MIT/Proprietary) ⚠️ 
│   ├── Cassandra (Apache-2.0) ✅
│   ├── Elasticsearch (SSPL/Elastic) 🔴
│   └── DynamoDB (AWS Proprietary) 🔴
├── 📨 Message Queues & IPC
│   ├── Kafka (Apache-2.0) ✅
│   ├── RabbitMQ (MPL-2.0) ✅
│   ├── NATS (Apache-2.0) ✅
│   ├── Celery (BSD-3) ✅
│   ├── Redis Streams (RSAL/BSD) ⚠️ 
│   └── gRPC (Apache-2.0) ✅
├── 📡 Protocols
│   ├── SIP (RFC (free)) ✅
│   ├── WebRTC (BSD/W3C) ✅
│   ├── WebSocket (RFC 6455) ✅
│   ├── REST/HTTP (RFC (free)) ✅
│   ├── GraphQL (MIT) ✅
│   ├── MQTT (Apache-2.0) ✅
│   └── RTSP/RTP (RFC (free)) ✅
├── 🔐 Auth & Security
│   ├── OAuth2 / OIDC (RFC (free)) ✅
│   ├── JWT (RFC 7519) ✅
│   ├── SAML (OASIS (free)) ✅
│   ├── RBAC (N/A (pattern)) ✅
│   ├── API Keys (N/A (pattern)) ✅
│   └── mTLS / TLS (RFC (free)) ✅
├── 🤖 AI / ML
│   ├── OpenAI API (Proprietary) 🔴
│   ├── Anthropic (Proprietary) 🔴
│   ├── HuggingFace (Apache-2.0) ✅
│   ├── PyTorch (BSD-3) ✅
│   ├── LangChain (MIT) ✅
│   ├── LlamaIndex (MIT) ✅
│   └── Ollama (MIT) ✅
├── ⚙️ Infrastructure
│   ├── Docker (Apache-2.0) ✅
│   ├── Kubernetes (Apache-2.0) ✅
│   ├── Terraform (BSL-1.1) ⚠️ 
│   ├── Helm (Apache-2.0) ✅
│   ├── Ansible (GPL-3.0) 🔴
│   └── nginx (BSD-2) ✅
├── 📊 Observability
│   ├── Prometheus (Apache-2.0) ✅
│   ├── Grafana (AGPL-3.0) 🚨
│   ├── OpenTelemetry (Apache-2.0) ✅
│   ├── Sentry (FSL-1.0) ⚠️ 
│   ├── Jaeger (Apache-2.0) ✅
│   └── Loki (AGPL-3.0) 🚨
├── 💾 Storage
│   ├── AWS S3 (Proprietary) 🔴
│   ├── MinIO (AGPL-3.0) 🚨
│   ├── Azure Blob (Proprietary) 🔴
│   ├── GCS (Proprietary) 🔴
│   └── Parquet (Apache-2.0) ✅
├── 🧪 Testing
│   ├── pytest (MIT) ✅
│   ├── Go test (BSD-3) ✅
│   ├── k6 (AGPL-3.0) 🚨
│   └── Playwright (Apache-2.0) ✅
├── 🚀 CI / CD
│   ├── GitHub Actions (Proprietary) ⚠️ 
│   ├── GitLab CI (MIT) ✅
│   └── Docker Compose (Apache-2.0) ✅
```

---
*Stack Slicer · BM25+FileSystem · 2026-08-04 · Zero Magic*