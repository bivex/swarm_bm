# 🔬 Technology Stack Slicer — MikoPBX_Core
> /private/tmp/mikopbx_audit · 4369 files · 13.12s · 2026-08-04

## 📋 Summary

| Metric | Value |
|---|---|
| **Technologies detected** | **79** |
| Files indexed | 4369 |
| Categories | 12 |
| 🚨 CRITICAL license risks | 4 |
| 🔴 HIGH license risks | 9 |
| 🟡 Easy swap targets (≤2) | 40 |

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
| **Python** | PSF-2.0 | ✅ LOW | 🔴 Hard | Keep — embed Cython/mypyc for performance | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **TypeScript** | Apache-2.0 | ✅ LOW | 🔴 Hard | Keep — compile to V8 bundle, add TS strict mode | `.claude/playwright/tsconfig.json`, `.claude/playwright/playwright.config.ts` |
| **JavaScript** | ECMA (free) | ✅ LOW | 🟠 Medium | Replace hot paths with WASM or TS strict | `sites/admin-cabinet/assets/js/vendor/moment-timezone/package.json`, `sites/admin-cabinet/assets/js/vendor/moment/package.json` |
| **Go** | BSD-3-Clause | ✅ LOW | 🔴 Hard | Keep — build proprietary modules as Go plugins | `sites/admin-cabinet/assets/js/vendor/ace/ext-modelist.js`, `tests/pycalltests/helpers/asterisk_helper.py` |
| **Rust** | MIT/Apache-2 | ✅ LOW | 🔵 Expert | Keep — compile to cdylib for FFI licensing | `sites/admin-cabinet/assets/js/vendor/ace/ext-modelist.js`, `sites/admin-cabinet/assets/js/vendor/ace/ext-options.js` |
| **C / C++** | N/A (lang) | ✅ LOW | 🔵 Expert | Keep — dynamic .so modules stay proprietary | `sites/admin-cabinet/assets/js/vendor/ace/ext-modelist.js`, `sites/admin-cabinet/assets/js/vendor/ace/ext-options.js` |
| **Java** | Oracle/OpenJDK | ✅ LOW | 🔴 Hard | Keep — JAR packaging hides implementation | `.claude/agents/js-optimizer-mikopbx.md`, `docs/xss-protection-guidelines.md` |
| **C#/.NET** | MIT | ✅ LOW | 🔴 Hard | Keep — .NET NuGet package distribution | `sites/admin-cabinet/assets/js/vendor/moment/package.json`, `sites/admin-cabinet/assets/js/vendor/ace/ext-modelist.js` |
| **Ruby** | Ruby License | ✅ LOW | 🟠 Medium | Replace with Python/Go for perf-critical parts | `sites/admin-cabinet/assets/js/vendor/ace/ext-modelist.js`, `sites/admin-cabinet/assets/js/vendor/ace/ext-options.js` |
| **PHP** | PHP License | ✅ LOW | 🟠 Medium | Replace with Go/Python for new services | `composer.json`, `src/AdminCabinet/Module.php` |
| **Erlang/Elixir** | Apache-2.0 | ✅ LOW | 🔵 Expert | Keep — BEAM VM is unique, hard to replicate | `sites/admin-cabinet/assets/js/vendor/ace/ext-modelist.js`, `sites/admin-cabinet/assets/js/vendor/ace/ext-options.js` |

## 🌐 Web Frameworks

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **FastAPI** | MIT | ✅ LOW | 🟡 Easy | Wrap in proprietary API gateway layer | `.claude/.backup-202512230937432/tasks/done/t-test-public-endpoints-hybrid-system.md`, `.claude/.backup-202512230938433/tasks/done/t-test-public-endpoints-hybrid-system.md` |
| **Django** | BSD-3 | ✅ LOW | 🟠 Medium | Add proprietary Django apps on top | `.claude/skills/mikopbx-module/reference/module-structure.md`, `tests/AdminCabinet/Scripts/ensure-browserstack-targets.sh` |
| **Flask** | BSD-3 | ✅ LOW | 🟡 Easy | Replace with FastAPI or proprietary wrapper | `tests/api/test_23_incoming_routes_default.py`, `tests/api/test_25_outbound_routes_default.py` |
| **Express.js** | MIT | ✅ LOW | 🟡 Easy | Replace with Fastify or proprietary HTTP server | `.claude/.backup-202512230937432/tasks/m-refactor-router-provider-public-endpoints.md`, `.claude/.backup-202512230938433/tasks/m-refactor-router-provider-public-endpoints.md` |
| **NestJS** | MIT | ✅ LOW | 🟠 Medium | Keep — add proprietary modules/decorators | `src/AdminCabinet/CLAUDE.md`, `src/PBXCoreREST/CLAUDE.md` |
| **Axum** | MIT | ✅ LOW | 🟡 Easy | Replace with proprietary Actix-web layer | `README.ru.md`, `tests/api/test_40_sysinfo.py` |
| **Rails** | MIT | ✅ LOW | 🟠 Medium | Add proprietary Rails engines on top | `sites/admin-cabinet/assets/css/vendor/semantic/rail.css`, `tests/api/test_25_outbound_routes_default.py` |
| **Spring Boot** | Apache-2 | ✅ LOW | 🟠 Medium | Add proprietary Spring modules/starters | `CONTRIBUTING.md`, `docs/superpowers/plans/2026-07-13-incoming-routes-provider-binding.md` |

## 🗄️ Databases

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **PostgreSQL** | PostgreSQL | ✅ LOW | 🟠 Medium | Add proprietary stored procedures / RLS policies | `tests/api/fixtures/cdr_seed_data.sql`, `sites/admin-cabinet/assets/js/vendor/ace/mode-php.js` |
| **MySQL** | GPL-2.0 | ⚠️  MEDIUM | 🟠 Medium | ⚠️ GPL-2 — switch to PostgreSQL or MariaDB | `tests/api/fixtures/cdr_seed_data.sql`, `sites/admin-cabinet/assets/js/vendor/ace/mode-php.js` |
| **Redis** | RSAL/BSD | ⚠️  MEDIUM | 🟠 Medium | Replace hot-path with own in-memory store or Valkey | `src/Core/Workers/CLAUDE.md`, `src/Core/System/RootFS/etc/php.d/55-redis.ini` |
| **MongoDB** | SSPL-1.0 | 🔴 HIGH | 🟠 Medium | 🚨 SSPL — replace with PostgreSQL JSONB or FerretDB | `sites/admin-cabinet/assets/js/vendor/jquery.debounce-1.0.5.min.js`, `sites/admin-cabinet/assets/js/vendor/jquery.debounce-1.0.5.js` |
| **SQLite** | Public Domain | ✅ LOW | 🟢 Trivial | Keep for embedded/edge, easy to swap | `tests/Calls/db/mikopbx.db`, `resources/db/mikopbx.db` |
| **ClickHouse** | Apache-2.0 | ✅ LOW | 🔴 Hard | Keep — build proprietary analytics layer on top | `tests/api/fixtures/cdr_seed_data.sql`, `sites/admin-cabinet/assets/js/vendor/ace/mode-php.js` |
| **InfluxDB** | MIT/Proprietary | ⚠️  MEDIUM | 🟠 Medium | Replace with VictoriaMetrics (MIT) or proprietary TSDB | `sites/admin-cabinet/assets/js/src/PbxAPI/storage-api.js`, `sites/admin-cabinet/assets/js/src/Storage/storage-index.js` |
| **Elasticsearch** | SSPL/Elastic | 🔴 HIGH | 🔴 Hard | 🚨 Elastic license — replace with OpenSearch or own | `sites/admin-cabinet/assets/js/vendor/ace/ext-modelist.js`, `sites/admin-cabinet/assets/js/vendor/ace/ext-options.js` |
| **DynamoDB** | AWS Proprietary | 🔴 HIGH | 🔴 Hard | Vendor lock-in — abstract via DAL layer | `tests/pycalltests/bin/pjsua2/linux-arm64/pjsua2.py`, `tests/pycalltests/bin/pjsua2/darwin-arm64/pjsua2.py` |

## 📨 Message Queues & IPC

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **Kafka** | Apache-2.0 | ✅ LOW | 🔴 Hard | Keep — build proprietary topic/schema registry | `CONTRIBUTING.md`, `sites/admin-cabinet/assets/js/vendor/jquery.debounce-1.0.5.js` |
| **RabbitMQ** | MPL-2.0 | ✅ LOW | 🟠 Medium | Replace with NATS or proprietary broker | `resources/sounds-base/en-en/core-sounds-en.txt`, `CLAUDE.md` |
| **NATS** | Apache-2.0 | ✅ LOW | 🟠 Medium | Keep — add proprietary subject namespacing | `sites/admin-cabinet/assets/js/src/main/event-bus.js`, `src/Common/Providers/CLAUDE.md` |
| **Celery** | BSD-3 | ✅ LOW | 🟡 Easy | Replace with proprietary task queue (Dramatiq/etc.) | `.claude/.backup-202512230937432/tasks/done/m-implement-wav2webm-worker.md`, `.claude/.backup-202512230938433/tasks/done/m-implement-wav2webm-worker.md` |
| **Redis Streams** | RSAL/BSD | ⚠️  MEDIUM | 🟡 Easy | Replace with Kafka or proprietary stream | `sites/admin-cabinet/assets/js/vendor/webrtc/MediaStreamRecorder.min.js`, `sites/admin-cabinet/assets/js/vendor/webrtc/MediaStreamRecorder.js` |
| **gRPC** | Apache-2.0 | ✅ LOW | 🟠 Medium | Keep — generate proprietary .proto schemas | `sites/admin-cabinet/assets/js/vendor/ace/ext-modelist.js`, `tests/Calls/asterisk/sorcery.conf` |

## 📡 Protocols

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **SIP** | RFC (free) | ✅ LOW | 🔵 Expert | Build proprietary SIP stack / B2BUA / billing layer | `.claude/.backup-202512230937432/tasks/done/h-implement-pjsua-python-swig.md`, `.claude/.backup-202512230938433/tasks/done/h-implement-pjsua-python-swig.md` |
| **WebRTC** | BSD/W3C | ✅ LOW | 🔵 Expert | Build proprietary media server / SFU / MCU | `sites/admin-cabinet/assets/js/vendor/jquery.debounce-1.0.5.min.js`, `sites/admin-cabinet/assets/js/vendor/jquery.debounce-1.0.5.js` |
| **WebSocket** | RFC 6455 | ✅ LOW | 🟡 Easy | Build proprietary WS gateway with auth/billing | `sites/admin-cabinet/assets/js/vendor/jquery.debounce-1.0.5.min.js`, `sites/admin-cabinet/assets/js/vendor/jquery.debounce-1.0.5.js` |
| **REST/HTTP** | RFC (free) | ✅ LOW | 🟢 Trivial | Add proprietary API gateway / rate limiting | `tests/api/test_49_openapi.py`, `.claude/skills/openapi-analyzer/examples/integration-examples.md` |
| **GraphQL** | MIT | ✅ LOW | 🟠 Medium | Build proprietary schema / federation layer | `docs/superpowers/specs/2026-07-10-resolver-unbound-config-design.md`, `src/PBXCoreREST/CLAUDE.md` |
| **MQTT** | Apache-2.0 | ✅ LOW | 🟠 Medium | Build proprietary MQTT broker / topic auth | `sites/admin-cabinet/assets/js/src/main/event-bus.js`, `src/Common/Providers/CLAUDE.md` |
| **RTSP/RTP** | RFC (free) | ✅ LOW | 🔴 Hard | Build proprietary media relay / recording tier | `sites/admin-cabinet/assets/js/vendor/webrtc/adapter-latest.js`, `sites/admin-cabinet/assets/js/vendor/webrtc/adapter-latest.min.js` |

## 🔐 Auth & Security

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **OAuth2 / OIDC** | RFC (free) | ✅ LOW | 🟠 Medium | Build proprietary IdP / add enterprise SSO tier | `config.json`, `.mcp.json` |
| **JWT** | RFC 7519 | ✅ LOW | 🟢 Trivial | Build proprietary JWT signing service | `.claude/skills/auth-token-manager/SKILL.md`, `.claude/skills/auth-token-manager/README.md` |
| **SAML** | OASIS (free) | ✅ LOW | 🔴 Hard | Build proprietary SAML SP — Enterprise SSO gate | `sites/admin-cabinet/assets/img/browserconfig.xml`, `tests/Unit/phpunit.xml` |
| **RBAC** | N/A (pattern) | ✅ LOW | 🟡 Easy | Build proprietary RBAC + ABAC engine as paid tier | `src/PBXCoreREST/CLAUDE.md`, `src/PBXCoreREST/Middleware/README.md` |
| **API Keys** | N/A (pattern) | ✅ LOW | 🟢 Trivial | Build proprietary key management / rotation SaaS | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **mTLS / TLS** | RFC (free) | ✅ LOW | 🟠 Medium | Build proprietary cert manager / PKI service | `sites/admin-cabinet/assets/js/src/MailSettings/mail-settings-tooltip-manager.js`, `sites/admin-cabinet/assets/js/src/GeneralSettings/general-settings-modify.js` |

## 🤖 AI / ML

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **OpenAI API** | Proprietary | 🔴 HIGH | 🟡 Easy | Build proprietary LLM abstraction / model router | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **Anthropic** | Proprietary | 🔴 HIGH | 🟡 Easy | Abstract behind LLM router layer | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **HuggingFace** | Apache-2.0 | ✅ LOW | 🟠 Medium | Keep — fine-tune proprietary models on top | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **PyTorch** | BSD-3 | ✅ LOW | 🔵 Expert | Keep — build proprietary model architecture | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **LangChain** | MIT | ✅ LOW | 🟡 Easy | Replace with proprietary chain/agent framework | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **LlamaIndex** | MIT | ✅ LOW | 🟡 Easy | Replace with proprietary RAG pipeline | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **Ollama** | MIT | ✅ LOW | 🟡 Easy | Replace with proprietary local LLM server | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |

## ⚙️ Infrastructure

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **Docker** | Apache-2.0 | ✅ LOW | 🟢 Trivial | Keep — add proprietary docker base images | `tests/api/docker-compose.s3-providers.yml`, `tests/AdminCabinet/Scripts/ensure-browserstack-targets.sh` |
| **Kubernetes** | Apache-2.0 | ✅ LOW | 🟠 Medium | Build proprietary Helm charts / operators | `sites/admin-cabinet/assets/js/vendor/semantic/sidebar.min.js`, `sites/admin-cabinet/assets/js/vendor/semantic/sidebar.js` |
| **Terraform** | BSL-1.1 | ⚠️  MEDIUM | 🟠 Medium | ⚠️ BSL — use OpenTofu or build proprietary IaC | `.claude/skills/mikopbx-module/reference/recipes.md`, `.claude/.backup-202512230937432/tasks/m-refactor-router-provider-public-endpoints.md` |
| **Helm** | Apache-2.0 | ✅ LOW | 🟡 Easy | Build proprietary Helm chart repository | `.claude/skills/endpoint-validator/templates`, `.claude/skills/mikopbx-module/templates` |
| **Ansible** | GPL-3.0 | 🔴 HIGH | 🟡 Easy | ⚠️ GPL-3 — replace with Terraform + own scripts | `.github/FUNDING.yml`, `.github/workflows/mirror-to-gitverse.yml` |
| **nginx** | BSD-2 | ✅ LOW | 🟡 Easy | Build proprietary nginx config generator | `src/Core/System/RootFS/etc/nginx/nginx.conf`, `src/Core/System/RootFS/etc/mdev.conf` |

## 📊 Observability

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **Prometheus** | Apache-2.0 | ✅ LOW | 🟡 Easy | Build proprietary metrics + alerting SaaS layer | `sites/admin-cabinet/assets/js/vendor/ace/ext-static_highlight.js`, `sites/admin-cabinet/assets/js/src/main/event-bus.js` |
| **Grafana** | AGPL-3.0 | 🚨 CRITICAL | 🟡 Easy | 🚨 AGPL — replace with Metabase/Superset or own | `sites/admin-cabinet/assets/js/src/Fail2Ban/fail-to-ban-index.js`, `sites/admin-cabinet/assets/js/src/SystemDiagnostic/CLAUDE.md` |
| **OpenTelemetry** | Apache-2.0 | ✅ LOW | 🟡 Easy | Keep — build proprietary collector/backend | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **Sentry** | FSL-1.0 | ⚠️  MEDIUM | 🟢 Trivial | Replace with proprietary error tracking | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **Jaeger** | Apache-2.0 | ✅ LOW | 🟡 Easy | Replace with proprietary distributed tracing | `sites/admin-cabinet/assets/js/vendor/ace/ext-searchbox.js`, `sites/admin-cabinet/assets/js/vendor/sentry/bundle.min.js` |
| **Loki** | AGPL-3.0 | 🚨 CRITICAL | 🟡 Easy | 🚨 AGPL — replace with VictoriaLogs or own | `sites/admin-cabinet/assets/js/src/SoundFiles/sound-file-modify-webkit-recorder.js`, `sites/admin-cabinet/assets/js/vendor/webrtc/adapter-latest.min.js` |

## 💾 Storage

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **AWS S3** | Proprietary | 🔴 HIGH | 🟡 Easy | Vendor lock-in — abstract with S3-compatible API | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **MinIO** | AGPL-3.0 | 🚨 CRITICAL | 🟡 Easy | 🚨 AGPL — replace with Ceph or proprietary S3 impl | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **Azure Blob** | Proprietary | 🔴 HIGH | 🟡 Easy | Vendor lock-in — abstract behind storage interface | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **GCS** | Proprietary | 🔴 HIGH | 🟡 Easy | Vendor lock-in — abstract behind storage interface | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |
| **Parquet** | Apache-2.0 | ✅ LOW | 🟡 Easy | Keep — add proprietary columnar format layer | `.claude/skills/api-test-generator/templates/test-template.py`, `.claude/skills/api-test-generator/templates/crud-tests.py` |

## 🧪 Testing

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **pytest** | MIT | ✅ LOW | 🟢 Trivial | Add proprietary test fixtures / plugins | `tests/pycalltests/conftest.py`, `tests/api/conftest.py` |
| **Jest** | MIT | ✅ LOW | 🟢 Trivial | Add proprietary test utilities | `.claude/playwright/tests/seed.spec.ts`, `.claude/playwright/tests/js-crash-fixes.spec.ts` |
| **Go test** | BSD-3 | ✅ LOW | 🟢 Trivial | Add proprietary test helpers | `sites/admin-cabinet/assets/js/vendor/semantic/api.min.js`, `sites/admin-cabinet/assets/js/vendor/semantic/api.js` |
| **k6** | AGPL-3.0 | 🚨 CRITICAL | 🟢 Trivial | 🚨 AGPL — replace with Gatling or proprietary load test | `sites/admin-cabinet/assets/js/vendor/jquery.debounce-1.0.5.min.js`, `sites/admin-cabinet/assets/js/vendor/jquery.debounce-1.0.5.js` |
| **Playwright** | Apache-2.0 | ✅ LOW | 🟢 Trivial | Add proprietary test scenarios | `.claude/playwright/playwright.config.ts`, `.claude/playwright/tests/seed.spec.ts` |

## 🚀 CI / CD

| Technology | License | Risk | Replace | Swap Target | Evidence |
|---|---|---|---|---|---|
| **GitHub Actions** | Proprietary | ⚠️  MEDIUM | 🟢 Trivial | Vendor lock-in — abstract pipeline logic | `.github/workflows/mirror-to-gitverse.yml`, `.github/workflows/code-quality.yml` |
| **GitLab CI** | MIT | ✅ LOW | 🟢 Trivial | Add proprietary CI templates | `.claude/skills/teamcity-monitor/SKILL.md`, `tests/AdminCabinet/JUNIT_UPLOAD_GUIDE.md` |
| **Docker Compose** | Apache-2.0 | ✅ LOW | 🟢 Trivial | Replace with K8s or proprietary orchestration | `tests/api/docker-compose.s3-providers.yml`, `tests/api/bootstrap-s3-providers.sh` |

## 🔄 Proprietary Swap Targets (Replaceability ≤ 2 — Easy Wins)

Technologies that can be replaced with your own proprietary implementation
to remove open-source license constraints and create revenue gates:

| Technology | Current License | Your Implementation | Effort |
|---|---|---|---|
| **SQLite** | Public Domain | Keep for embedded/edge, easy to swap | 🟢 Trivial |
| **REST/HTTP** | RFC (free) | Add proprietary API gateway / rate limiting | 🟢 Trivial |
| **JWT** | RFC 7519 | Build proprietary JWT signing service | 🟢 Trivial |
| **API Keys** | N/A (pattern) | Build proprietary key management / rotation SaaS | 🟢 Trivial |
| **Docker** | Apache-2.0 | Keep — add proprietary docker base images | 🟢 Trivial |
| **Sentry** | FSL-1.0 | Replace with proprietary error tracking | 🟢 Trivial |
| **pytest** | MIT | Add proprietary test fixtures / plugins | 🟢 Trivial |
| **Jest** | MIT | Add proprietary test utilities | 🟢 Trivial |
| **Go test** | BSD-3 | Add proprietary test helpers | 🟢 Trivial |
| **k6** | AGPL-3.0 | 🚨 AGPL — replace with Gatling or proprietary load test | 🟢 Trivial |
| **Playwright** | Apache-2.0 | Add proprietary test scenarios | 🟢 Trivial |
| **GitHub Actions** | Proprietary | Vendor lock-in — abstract pipeline logic | 🟢 Trivial |
| **GitLab CI** | MIT | Add proprietary CI templates | 🟢 Trivial |
| **Docker Compose** | Apache-2.0 | Replace with K8s or proprietary orchestration | 🟢 Trivial |
| **FastAPI** | MIT | Wrap in proprietary API gateway layer | 🟡 Easy |
| **Flask** | BSD-3 | Replace with FastAPI or proprietary wrapper | 🟡 Easy |
| **Express.js** | MIT | Replace with Fastify or proprietary HTTP server | 🟡 Easy |
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
Project: MikoPBX_Core
├── 🖥️ Languages
│   ├── Python (PSF-2.0) ✅
│   ├── TypeScript (Apache-2.0) ✅
│   ├── JavaScript (ECMA (free)) ✅
│   ├── Go (BSD-3-Clause) ✅
│   ├── Rust (MIT/Apache-2) ✅
│   ├── C / C++ (N/A (lang)) ✅
│   ├── Java (Oracle/OpenJDK) ✅
│   ├── C#/.NET (MIT) ✅
│   ├── Ruby (Ruby License) ✅
│   ├── PHP (PHP License) ✅
│   └── Erlang/Elixir (Apache-2.0) ✅
├── 🌐 Web Frameworks
│   ├── FastAPI (MIT) ✅
│   ├── Django (BSD-3) ✅
│   ├── Flask (BSD-3) ✅
│   ├── Express.js (MIT) ✅
│   ├── NestJS (MIT) ✅
│   ├── Axum (MIT) ✅
│   ├── Rails (MIT) ✅
│   └── Spring Boot (Apache-2) ✅
├── 🗄️ Databases
│   ├── PostgreSQL (PostgreSQL) ✅
│   ├── MySQL (GPL-2.0) ⚠️ 
│   ├── Redis (RSAL/BSD) ⚠️ 
│   ├── MongoDB (SSPL-1.0) 🔴
│   ├── SQLite (Public Domain) ✅
│   ├── ClickHouse (Apache-2.0) ✅
│   ├── InfluxDB (MIT/Proprietary) ⚠️ 
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
│   ├── Jest (MIT) ✅
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