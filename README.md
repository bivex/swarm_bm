# Swarm BM — AI Agent Swarm для инженерной разведки кодовой базы

[![C++20](https://img.shields.io/badge/C%2B%2B-20-blue.svg)](https://en.wikipedia.org/wiki/C%2B%2B20)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![macOS & Windows](https://img.shields.io/badge/OS-macOS%20%7C%20Windows-brightgreen.svg)]()
[![MCP Server](https://img.shields.io/badge/Protocol-MCP-purple.svg)](https://modelcontextprotocol.io)
[![Tests](https://img.shields.io/badge/Tests-40%20passed-success.svg)]()

---

## 💼 Бизнес-задачи

### 🔍 1. Онбординг на новый проект за минуты, а не за недели

Каждый раз когда инженер (человек или AI-агент) берёт новый проект — он тратит **от нескольких дней до недель** на понимание архитектуры, точек входа, слоёв ответственности, связей между модулями.

**Swarm BM** запускает **рой из 10 специализированных AI-агентов**, каждый из которых за секунды отвечает на 5+ ключевых вопросов Senior-инженера:

- Где точки входа? Какова макро-архитектура?
- Какая БД/ORM? Как устроены миграции и связи?
- Как реализована аутентификация и авторизация?
- Есть ли защита от CSRF/SQLi/XSS?
- Как устроен async и Thread safety?

> **Результат**: за **8–10 секунд** на кодовой базе из 7000+ файлов получаете структурированный аудит с реальными путями файлов и AST-символами. Без галлюцинаций — только то, что реально есть в коде.

---

### 🧠 2. Контекстный BM25+AST поиск для AI-кодинг агентов

Современные AI-агенты (Claude Code, Cursor, Copilot) страдают от **контекстного окна** — они не могут держать всю кодовую базу в голове. При этом наивный `grep` или семантический поиск часто возвращают нерелевантные результаты.

**Swarm BM** решает это через:
- **BM25-ранкинг** — статистически точный поиск по именам файлов и содержимому
- **AST-граф символов** — точные `class`/`function`/`import` с указанием файла и строки
- **Skeleton DSL** — компактное структурное представление файла без шума

> **Результат**: AI-агент получает в запрос **точный контекст** (конкретные файлы + символы + их связи), а не весь проект целиком. Экономия токенов в 10–50×.

---

### ⚡ 3. Плотный рой агентов: 410+ одновременно на одной машине

Стандартный подход — один AI-агент на одну задачу. При параллельном запуске нескольких агентов они конкурируют за RAM/CPU/IO, что приводит к OOM-kilам, подвисаниям и неконтролируемому потреблению ресурсов.

**Swarm BM** через `AgentJobEngine` (C++20, macOS + Windows) даёт каждому агенту:
- **RAM-лимит** (128 МБ/агент, Working Set Memory Compression)
- **CPU-лимит** (rate cap %)
- **IOPS-лимит** (Disk I/O throttle)
- **Network-лимит** (bandwidth cap)
- **Sandbox** (macOS Seatbelt / Windows Silos)
- **Freeze/Thaw** (SIGSTOP/SIGCONT) для временного вытеснения

> **Результат**: **410 активных агентов** (1000+ в сжатом состоянии) на 16GB MacBook Pro. Без OOM. Без неконтролируемого потребления. Детерминированная среда.

---

### 🗺️ 4. Авто-роутинг задач по агентам без ручной конфигурации

При большом проекте нужно решить: сколько агентов запустить и как между ними разбить работу? Ручная конфигурация — трудоёмкая, медленная, не масштабируется.

**`SwarmAutoRouterService`** автоматически:
1. Анализирует физическую RAM и CPU через `sysctl`
2. Вычисляет оптимальное число агентов с учётом бюджета 128 МБ/агент
3. Разбивает кодовую базу по топ-уровневым модулям между агентами
4. Спавнит рой с OS-уровневыми лимитами через `AgentJobEngine`

> **Результат**: вызов одного MCP-инструмента `autoroute_swarm_codebase` — и рой настроен и запущен автоматически под текущее железо.

---

### 🏛️ 5. Senior Architect Audit — автоматический ответ на 50 вопросов при приёмке проекта

При приёмке нового проекта в команду Senior-инженер тратит **1–4 недели** на architectural review. Типовой набор вопросов один и тот же: точки входа, ORM, auth, CSRF, async, ошибки, кэш, технический долг, тесты, CI/CD.

**`SeniorCodebaseAuditEngine`** запускает рой из **10 специализированных агентов** (по одному на домен), каждый задаёт **5 архитектурных вопросов** через многотокенный BM25+AST поиск. Результат — структурированный отчёт с реальными файлами и символами из кода.

> **Результат**: architectural onboarding на **Django (7078 файлов)** занял **8.7 секунд**. 50 из 50 вопросов получили реальные ответы из кода.

---

## 📐 Архитектура (DDD Hexagonal / Ports & Adapters)

```
swarm_bm/
├── JobObjects_RD/                       # C++20 AgentJobEngine — OS Resource Controller
│   ├── include/AgentJobEngine_C_API.h   # C API Export Header
│   └── src/AgentJobEngine_C_API.cpp     # Python ctypes Bridge
├── bm25_server_FS_for-AI-asking/        # Python BM25 Search + Multi-Lang AST Engine
└── swarm_mcp/                           # DDD Hexagonal Architecture MCP Package
    ├── domain/
    │   ├── models.py                    # SwarmWorker, ResourceBudget, DomainSymbol
    │   ├── ports.py                     # IndexPort, JobEnginePort (абстракции)
    │   └── services.py                  # SwarmOrchestratorService, SwarmAutoRouterService
    ├── application/
    │   ├── dtos.py                      # Request / Response DTOs
    │   ├── use_cases.py                 # FastDeconstruct, Search, Spawn, AutoRoute
    │   └── senior_audit.py             # SeniorCodebaseAuditEngine (10 агентов × 5 вопросов)
    ├── infrastructure/
    │   ├── index_store_adapter.py       # BM25 IndexStore Adapter
    │   ├── job_engine_adapter.py        # libAgentJobEngineC.dylib (ctypes)
    │   └── mcp_server_adapter.py        # FastMCP Inbound Adapter
    └── main.py                          # Entry Point
```

---

## 🛠️ MCP-инструменты для AI-агентов

| Инструмент | Параметры | Что делает |
|---|---|---|
| `fast_deconstruct_codebase` | `root_path`, `query` | RAM-индексирование + Skeleton DSL + топ файлы/символы |
| `search_codebase` | `query`, `content_query`, `limit` | BM25-поиск по файлам и содержимому |
| `get_file_skeleton` | `path` | Skeleton DSL структура конкретного файла |
| `get_symbol_contour` | `query` | DSL-контур по имени символа (class/function/import) |
| `ask_codebase` | `question` | Вопрос на естественном языке — ответ из кода |
| `spawn_swarm_worker` | `worker_id`, `command`, `max_memory_mb`, `max_iops` | Спавн процесса под OS-лимитами AgentJobEngine |
| `control_swarm_worker` | `worker_id`, `action` | `freeze` / `thaw` / `compress` / `terminate` |
| `autoroute_swarm_codebase` | `root_path`, `max_agents` | Авто-роутинг роя по RAM/CPU/модулям |
| `run_senior_codebase_audit` | `root_path` | 10-агентный Senior Architect Audit (50 вопросов) |

---

## ⚡ Характеристики производительности

| Метрика | Значение |
|---|---|
| Индексирование Django (7078 файлов) | **6.65 сек** |
| BM25-поиск по запросу | **0.15 мс** |
| Рендеринг DSL-контура символа | **0.15 мс** (944× ускорение) |
| Senior Audit (50 вопросов, 7078 файлов) | **8.7 сек** |
| Плотность роя (16GB RAM) | **410 активных / 1000+ сжатых** |

---

## 🚀 Быстрый старт

### 1. Сборка C++ движка

```bash
cd JobObjects_RD
./run_build_and_tests.sh   # macOS
# или
.\run_build_and_tests.cmd  # Windows
cd ..
```

### 2. Запуск MCP-сервера

```bash
PYTHONPATH=bm25_server_FS_for-AI-asking:. python3 swarm_mcp/main.py
```

### 3. Senior Architect Audit на своей кодовой базе

```bash
PYTHONPATH=bm25_server_FS_for-AI-asking:. python3 -c "
import json
from pathlib import Path
from swarm_mcp.application.senior_audit import SeniorCodebaseAuditEngine
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter

engine = SeniorCodebaseAuditEngine(IndexStoreAdapter(), JobEngineAdapter())
result = engine.run_10_agent_senior_audit(Path('/path/to/your/project'))
print(json.dumps(result, indent=2, ensure_ascii=False))
"
```

### 4. Все тесты (40 тестов)

```bash
PYTHONPATH=bm25_server_FS_for-AI-asking:. python3 -m pytest tests bm25_server_FS_for-AI-asking/tests
```

---

## 📦 Подмодули

- **[bm25_server_FS_for-AI-asking](https://github.com/bivex/bm25_server_FS_for-AI-asking)** — RAM Disk BM25 + Multi-Lang AST
- **[JobObjects_RD](https://github.com/bivex/JobObjects_RD)** — C++20 OS Resource Engine (macOS & Windows)

---

## 📜 Лицензия

MIT License.
