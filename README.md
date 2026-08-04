# Swarm BM — High-Density AI Agent Swarm Architecture

[![C++20](https://img.shields.io/badge/C%2B%2B-20-blue.svg)](https://en.wikipedia.org/wiki/C%2B%2B20)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![macOS & Windows](https://img.shields.io/badge/OS-macOS%20%7C%20Windows-brightgreen.svg)]()
[![MCP Server](https://img.shields.io/badge/Protocol-MCP-purple.svg)](https://modelcontextprotocol.io)

**Swarm BM** is an integrated, high-performance ecosystem for multi-tenant AI coding agents (Claude Code, Antigravity, OpenHands, SWE-agent). It combines:

1. **`JobObjects_RD` (`AgentJobEngine`)** — A C++20 OS Resource Controller for macOS (Darwin Kernel) and Windows (`_EJOB`). Enables **10× – 75× Agent Swarm Concurrency** via Working Set Memory Compression, Process Tree Freezing, Disk I/O & Network Rate Limits, and Container Sandboxing.
2. **`bm25_server_FS_for-AI-asking`** — A RAM disk fast search and AST symbol extraction server using **BM25 ranking** and multi-language AST parsing (Python, C, C++, JS, TS, Go, Rust).
3. **`swarm_mcp`** — A **DDD (Domain-Driven Design) Hexagonal Architecture** MCP (Model Context Protocol) server integrating both projects into a unified interface for AI agent swarms.

---

## 📐 Architecture (DDD Hexagonal / Ports & Adapters)

```text
swarm_bm/
├── JobObjects_RD/                      # C++ AgentJobEngine Core Library & C API
│   ├── include/AgentJobEngine_C_API.h  # C API Export Header
│   └── src/AgentJobEngine_C_API.cpp    # C API Implementation for ctypes
├── bm25_server_FS_for-AI-asking/       # Python BM25 Search & Multi-Lang AST Engine
└── swarm_mcp/                          # DDD Hexagonal Architecture Package
    ├── domain/                         # Core Domain Logic & Entities
    │   ├── models.py                   # Domain Entities (SwarmWorker, ResourceBudget, Symbol)
    │   ├── ports.py                    # Abstract Ports Interfaces (IndexPort, JobEnginePort)
    │   └── services.py                 # Domain Services (SwarmOrchestratorService)
    ├── application/                    # Application Use Cases & DTOs
    │   ├── dtos.py                     # Request/Response Data Transfer Objects
    │   └── use_cases.py                # Use Cases (FastDeconstruct, Search, SpawnWorker, Control)
    ├── infrastructure/                 # Outbound & Inbound Hexagonal Adapters
    │   ├── index_store_adapter.py      # Outbound Adapter -> BM25 IndexStore
    │   ├── job_engine_adapter.py       # Outbound Adapter -> C++ libAgentJobEngineC (ctypes)
    │   └── mcp_server_adapter.py       # Inbound Adapter -> FastMCP Protocol Server
    └── main.py                         # Application Entry Point
```

---

## 🛠️ MCP Server Tools & Capabilities

The integrated MCP server exposes standardized tools for AI agents:

| Tool Name | Parameters | Description |
|---|---|---|
| `fast_deconstruct_codebase` | `root_path`, `query` | Rebuilds index in RAM, generates Skeleton DSL contour, and extracts top files & symbols. |
| `search_codebase` | `query`, `content_query`, `limit` | Ranked BM25 search across files and content. |
| `get_file_skeleton` | `path` | Extracts Skeleton DSL for a specific code file. |
| `get_symbol_contour` | `query` | Extracts Skeleton DSL contour for matching symbol query. |
| `ask_codebase` | `question` | Answers natural language architectural queries over the codebase. |
| `spawn_swarm_worker` | `worker_id`, `command`, `max_memory_mb`, `max_iops` | Spawns a Swarm Worker process under `AgentJobEngine` OS resource limits. |
| `control_swarm_worker` | `worker_id`, `action` | Controls worker state: `freeze` (`SIGSTOP`), `thaw` (`SIGCONT`), `compress` (memory trim), or `terminate`. |
| `get_swarm_stats` | - | Returns current index stats and active managed Swarm Workers. |

---

## 🚀 Quick Start & Building

### 1. Build C++ Engine & Shared Library

```bash
# macOS / Linux
cd JobObjects_RD
./run_build_and_tests.sh
cd ..

# Windows
cd JobObjects_RD
.\run_build_and_tests.cmd
cd ..
```

### 2. Run Integrated MCP Server

```bash
PYTHONPATH=bm25_server_FS_for-AI-asking:. python3 swarm_mcp/main.py
```

### 3. Run Test Suites

```bash
# Test Hexagonal Integration
PYTHONPATH=bm25_server_FS_for-AI-asking:. python3 -m pytest tests/test_swarm_mcp_hex.py

# Run Full Test Suite (38 tests)
PYTHONPATH=bm25_server_FS_for-AI-asking:. python3 -m pytest bm25_server_FS_for-AI-asking/tests tests/test_swarm_mcp_hex.py
```

---

## 📄 Submodules

- **[bm25_server_FS_for-AI-asking](https://github.com/bivex/bm25_server_FS_for-AI-asking)** — Fast RAM Disk BM25 search & symbol extractor.
- **[JobObjects_RD](https://github.com/bivex/JobObjects_RD)** — C++ OS Resource Engine for AI Agent Swarms (macOS & Windows).

---

## 📜 License

MIT License.
