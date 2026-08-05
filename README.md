# Swarm BM — AI Agent Swarm & Enterprise Codebase Intelligence System

[![C++20](https://img.shields.io/badge/C%2B%2B-20-blue.svg)](https://en.wikipedia.org/wiki/C%2B%2B20)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![macOS & Windows](https://img.shields.io/badge/OS-macOS%20%7C%20Windows-brightgreen.svg)]()
[![MCP Server](https://img.shields.io/badge/Protocol-MCP-purple.svg)](https://modelcontextprotocol.io)
[![ISO Audits](https://img.shields.io/badge/Compliance-8%20ISO%20Standards-gold.svg)]()
[![Unreal Engine](https://img.shields.io/badge/UE4%2FUE5-Auditor-orange.svg)]()
[![Tests](https://img.shields.io/badge/Tests-passed-success.svg)]()

---

## 💼 Бизнес-задачи & Возможиости

### 🔍 1. Онбординг на новый проект за секунды
Каждый раз при приёмке нового проекта инженер тратит **от нескольких дней до недель** на понимание архитектуры, точек входа, безопасности и слоёв ответственности.

**Swarm BM** запускает **рой из 10 специализированных AI-агентов**, каждый из которых за секунды реконструирует картину проекта без галлюцинаций — только реальные пути файлов и AST-символы.

---

### 🏛️ 2. Международная ISO Сертификация кодовой базы (8 ISO Стандартов)

Набор специализированных аудиторов в папке `scratch/auditors/iso/` подготавливает кодовую базу к M&A Due Diligence и корпоративной ISO-сертификации:

| Стандарт ISO | Описание & Область аудита | Скрипт-аудитор |
|---|---|---|
| 🛡️ **ISO/IEC 27001:2022** | Информационная безопасность (Анализ A.8.24 Cryptography, A.8.28 Secure Coding, DLP, Secrets) | `scratch/auditors/iso/iso_27001_security_audit.py` |
| ⚙️ **ISO/IEC 25010:2023** | Качество ПО (Maintainability, Performance, Reliability, Security, Compatibility, Portability) | `scratch/auditors/iso/iso_25010_quality_audit.py` |
| 🔒 **ISO/IEC 27701:2019** | Приватность & PII (GDPR compliance, Soft/Hard Delete, шифрование полей, маскирование логов) | `scratch/auditors/iso/iso_27701_privacy_audit.py` |
| ⚡ **ISO 22301:2019** | Отказоустойчивость & Disaster Recovery (Health Probes `/healthz`, Circuit Breakers, HA Replicas) | `scratch/auditors/iso/iso_22301_resilience_audit.py` |
| 🤖 **ISO/IEC 42001:2023** | Безопасность AI / LLM агентов (Prompt Guardrails, Token Budgeting, Schema Enforcement) | `scratch/auditors/iso/iso_42001_ai_audit.py` |
| 📊 **ISO 31000:2018** | Управление рисками ERM (Dependabot/Snyk, детекция SPOF, EOL-библиотеки) | `scratch/auditors/iso/iso_31000_risk_audit.py` |
| 🏅 **ISO 9001:2015** | QMS & Release Engineering (CI/CD workflows, unit tests, CODEOWNERS, CHANGELOG) | `scratch/auditors/iso/iso_9001_qms_audit.py` |
| ☁️ **ISO/IEC 27017:2015** | Cloud Security (Изоляция тенантов RLS, S3 KMS шифрование, CloudTrail аудит) | `scratch/auditors/iso/iso_27017_cloud_security_audit.py` |
| 🏎️ **ISO 26262 / ASIL-D** | Автомобильная безопасность (Отсутствие `malloc` в циклах, Watchdog timers, Fail-Safe states) | `scratch/auditors/iso/iso_26262_automotive_audit.py` |
| 💳 **ISO 20022** | Межбанковский Финтех & Open Banking (pacs/pain/camt XML спеки, Idempotency-Key, mTLS) | `scratch/auditors/iso/iso_20022_fintech_audit.py` |
| 🩺 **ISO 13485 / IEC 62304** | Медицинское ПО SaMD (Проверка диапазонов датчиков, PHI лог доступа, Hazard alarm) | `scratch/auditors/iso/iso_13485_medtech_audit.py` |
| 🌿 **ISO 14001 / Green IT** | Энергоэффективность кода (Gzip/Brotli сжатие, кэширование CPU, детекция busy loops) | `scratch/auditors/iso/iso_14001_green_code_audit.py` |
| 📋 **ISO/IEC 19770** | Управление лицензиями ПО (SBOM генерация, детекция GPL/AGPL конфликтов, LICENSE file) | `scratch/auditors/iso/iso_19770_license_audit.py` |
| ☁️🔒 **ISO/IEC 27018** | Приватность PII в публичных облаках (BYOK шифрование KMS, запрет ad-трекинга, residency) | `scratch/auditors/iso/iso_27018_pii_cloud_audit.py` |
| 🏛️ **ISO/IEC 15408 / EAL** | Common Criteria EAL (Security Target specification, power-on self-test, buffer safety) | `scratch/auditors/iso/iso_15408_common_criteria_audit.py` |
| 🏭 **ISA/IEC 62443** | Промышленная безопасность SCADA/OT (Зонирование air-gap, OPC UA/Modbus, PLC watchdogs) | `scratch/auditors/iso/iso_62443_industrial_security_audit.py` |
| 📌 **ISO 21500** | Управление проектами и Governance (Issue templates, ADR записи в `docs/adr/`, Roadmap) | `scratch/auditors/iso/iso_21500_project_governance_audit.py` |
| 🧪 **ISO/IEC/IEEE 29119** | Стандарты тестирования ПО (Unit test automation, fixtures `conftest.py`, Playwright E2E) | `scratch/auditors/iso/iso_29119_software_testing_audit.py` |

---

### 🎮 3. Аудит игровых плагинов Unreal Engine 4 / 5 (C++ & Fab Marketplace)

Специализированная линейка аудиторов для Unreal Engine:

- 🎮 **`scratch/auditors/unreal_plugin_auditor.py` (Technical C++ Auditor)**:
  - Проверка Garbage Collection (`UPROPERTY()`), сетевых RPC (`UFUNCTION(Server, Reliable)`), отмена динамических `new` операторов в пользу `NewObject<T>()`, вынос асинхронности в `FRunnableThread`, DLL экспорты (`*_API`).
- 💼 **`scratch/auditors/unreal_commercial_audit.py` (60Q Business & UX Publisher Auditor)**:
  - 60 вопросов по 10 нетехническим доменам: B2B сегментация, монетизация Open-Core vs Pro, No-Code Blueprint UX для дизайнеров, наличие демо-карт (`/Content/Maps/Demo.umap`), поддержка в Discord и EULA Epic Fab.

---

### 🔌 4. Commercial Integration & Architectural Audit Suite

Специализированные инженерные аудиторы в `scratch/auditors/`:

1. **`scratch/auditors/architecture_design_audit.py`**: Architectural Health Index (0-100), Clean Architecture, God Objects (>1,000 строк), SOLID, выявление молчаливых `try: pass`.
2. **`scratch/auditors/espocrm_researcher.py`**: Enterprise Commercial Integration Auditor с **62 вопросами по 10 доменам сопряжения** (REST API, Event Hooks, WebSockets/CTI, OAuth2/ACL, Async Queues, Closed AI Engine, Payment Gateways, Messengers, ETL, SDK Loader).
3. **`scratch/auditors/stack_slicer.py`**: Stack Slicer 3.0 Enterprise — детальный анализ 250+ технологий по 26 категориям с 19 парсерами манифестов.
4. **`scratch/auditors/revenue_audit.py`**: Revenue Maximization Auditor — 11 бизнес-блоков монетизации и проверка лицензионной чистоты.
5. **`scratch/auditors/security_compliance_audit.py`**: Security & Compliance Risk Auditor — OWASP Top 10, Secrets, SOC2/GDPR/HIPAA/PCI compliance.
6. **`scratch/auditors/whitelabel_readiness_audit.py`**: White-Label Readiness Auditor — OEM / Rebrand метрики, CSS токены и кастомные домены.

---

### 🧠 5. BM25+AST Поиск и Сжатие для AI-кодинг Агентов

- **BM25-ранкинг** — статистически точный поиск по файлам и коду.
- **AST-граф символов** — точные `class`/`function`/`import` с указанием файла и строки.
- **Multilingual Concept Engine** — понимает запросы на русском и английском языках (`"авторизация"`, `"база данных"`, `"секреты"`).

---

### ⚡ 6. Сверхплотный рой агентов (410+ на 16GB RAM)

Через `AgentJobEngine` (C++20, macOS + Windows):
- **RAM / CPU / IOPS / Network Throttle**
- **Sandbox isolation** (macOS Seatbelt / Windows Silos)
- **Freeze/Thaw** (SIGSTOP/SIGCONT) для временного вытеснения.

---

## 🛠️ MCP-Сервер `swarm-auditors-mcp`

Зарегистрирован в `~/.gemini/config/mcp_config.json` и поставляет единый гибкий инструмент:

| Инструмент MCP | Параметры | Описание |
|---|---|---|
| `custom_swarm_audit` | `target_path`, `questions`, `project_name` | Выполнение произвольного пользовательского списка вопросов над любой кодовой базой |

---

## 🚀 Быстрый запуск аудитов

```bash
# 1. ISO 27001 Аудит информационной безопасности
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/iso_27001_security_audit.py /path/to/project

# 2. ISO 25010 Качество ПО и архитектура
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/iso/iso_25010_quality_audit.py /path/to/project

# 3. Аудит Unreal Engine C++ плагина
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/unreal_plugin_auditor.py /path/to/ue_plugin

# 4. Аудит 60Q Коммерческой готовности плагина Unreal Engine
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/unreal_commercial_audit.py /path/to/ue_plugin

# 5. EspoCRM Enterprise Commercial Integration Audit (62Q)
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/espocrm_researcher.py /path/to/project

# 6. Technology Stack Slicer 3.0 (250+ технологий)
PYTHONPATH=.:bm25_server_FS_for-AI-asking python3 scratch/auditors/stack_slicer.py /path/to/project
```

---

## 📜 Лицензия

MIT License.
