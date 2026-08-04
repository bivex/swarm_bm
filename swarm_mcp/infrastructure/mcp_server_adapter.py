from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


def create_swarm_mcp_server(root_path: Path | None = None) -> FastMCP:
    """Inbound Hexagonal Adapter creating standard MCP Server for Swarm Auditor Suite."""

    mcp = FastMCP("swarm-auditors-mcp", instructions="Swarm Codebase & Commercial Auditor Suite MCP Server")

    # ─────────────────────────────────────────────────────────────────────────
    # Single MCP Tool: Custom Swarm Agent Questions Auditor
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool()
    def custom_swarm_audit(root_path: str, questions: list[str]) -> str:
        """Run custom Swarm Agent Audit using ANY arbitrary natural language question over codebase (BM25 + AST)."""
        from pathlib import Path
        import re
        path = Path(root_path).resolve()
        sub_idx = IndexStoreAdapter(root=path)
        stats = sub_idx.rebuild(path)

        # 100+ Concept Translation Dictionary (Russian/English -> Code Search Tokens)
        CONCEPT_MAP = {
            "вход": ["main", "app", "entry", "index", "server", "wsgi", "asgi", "start", "run", "cmd", "bootstrap"],
            "входа": ["main", "app", "entry", "index", "server", "wsgi", "asgi", "start", "run", "cmd"],
            "старт": ["main", "app", "entry", "start", "init", "run"],
            "запуск": ["main", "app", "entry", "start", "run", "cmd", "launch"],
            "главный": ["main", "app", "core", "index", "primary", "master"],
            "архитектура": ["architecture", "hexagonal", "domain", "application", "infrastructure", "core", "adapter", "service", "module", "layer"],
            "устроен": ["architecture", "structure", "core", "design", "component", "module", "system"],
            "структура": ["structure", "tree", "module", "package", "dir", "layer"],
            "слои": ["layer", "domain", "application", "infrastructure", "adapter"],
            "роутинг": ["route", "router", "endpoint", "url", "path", "controller", "handler", "view", "api"],
            "маршрутизация": ["route", "router", "endpoint", "url", "path", "controller", "handler"],
            "эндпоинт": ["endpoint", "route", "api", "path", "url", "handler"],
            "ручка": ["endpoint", "route", "api", "handler", "controller"],
            "контроллер": ["controller", "handler", "view", "route", "endpoint"],
            "запрос": ["request", "req", "call", "query", "http", "fetch"],
            "аутентификация": ["auth", "jwt", "login", "token", "session", "oauth", "password", "bearer"],
            "авторизация": ["auth", "permission", "role", "rbac", "access", "guard", "policy", "allow"],
            "пароль": ["password", "hash", "secret", "bcrypt", "argon2"],
            "токен": ["token", "jwt", "bearer", "access_token", "refresh"],
            "права": ["permission", "role", "rbac", "access", "allow", "guard"],
            "роли": ["role", "group", "permission", "rbac"],
            "доступ": ["access", "permission", "authorize", "allow", "deny", "guard"],
            "секрет": ["secret", "key", "password", "token", "credentials", "api_key", "env", "private"],
            "секреты": ["secret", "key", "password", "token", "credentials", "api_key"],
            "ключ": ["key", "api_key", "secret", "token", "private_key"],
            "база": ["database", "db", "sql", "postgres", "redis", "model", "schema", "entity", "orm", "repository", "table"],
            "модель": ["model", "schema", "entity", "table", "field", "dataclass", "pydantic"],
            "таблица": ["table", "model", "schema", "column", "query", "sql"],
            "данные": ["data", "db", "model", "store", "repository", "persist"],
            "хранение": ["store", "storage", "db", "persist", "save", "repository"],
            "кэш": ["cache", "redis", "memcached", "memory", "store", "ttl", "expire"],
            "кеш": ["cache", "redis", "memcached", "memory", "store"],
            "оплата": ["payment", "billing", "stripe", "paypal", "invoice", "price", "subscription", "charge"],
            "платеж": ["payment", "billing", "stripe", "charge", "amount"],
            "деньги": ["billing", "price", "amount", "currency", "fee", "cost"],
            "подписка": ["subscription", "plan", "tier", "billing", "recurring"],
            "очередь": ["queue", "message", "async", "worker", "job", "celery", "rabbit", "kafka", "redis", "task"],
            "сообщение": ["message", "msg", "event", "publish", "subscribe"],
            "задача": ["task", "job", "worker", "async", "celery", "queue"],
            "лог": ["log", "logger", "logging", "info", "debug", "error"],
            "логирование": ["logging", "logger", "log", "trace", "print"],
            "ошибка": ["error", "exception", "fail", "raise", "catch", "trace"],
            "пользователь": ["user", "account", "profile", "member", "person"],
            "клиент": ["client", "customer", "account", "user"],
            "настройки": ["setting", "config", "configuration", "env", "options", "param"],
            "конфиг": ["config", "settings", "env", "configuration", "yaml", "toml"],
            "тест": ["test", "pytest", "spec", "benchmark", "assert", "mock"],
            "зависимости": ["dependencies", "requirements", "package", "go.mod", "Cargo.toml", "composer.json", "pom.xml", "pip"],
            "зависимость": ["dependency", "package", "module", "import", "require"],
            "программа": ["app", "main", "core", "server", "program", "system"],
            "программу": ["app", "main", "core", "server", "program"],
        }

        findings = []
        for q in questions:
            ask_res = sub_idx.ask_question(q)
            files = ask_res.files if hasattr(ask_res, 'files') else []
            symbols = ask_res.symbols if hasattr(ask_res, 'symbols') else []

            files_dict: dict[str, float] = {f: 1.0 for f in files}
            all_symbols: list[Any] = list(symbols)
            seen_sym_names: set[str] = {getattr(s, 'name', str(s)) for s in symbols}

            words = [w.lower() for w in re.findall(r'\w{2,}', q)]
            search_terms = set()
            for w in words:
                if w in CONCEPT_MAP:
                    search_terms.update(CONCEPT_MAP[w])
                elif len(w) >= 3 and not re.match(r'^[а-яА-Я]+$', w):
                    search_terms.add(w)

            for token in list(search_terms)[:12]:
                hits = sub_idx.search_code(token, limit=5)
                for h in hits:
                    if h.path not in files_dict or h.score > files_dict[h.path]:
                        files_dict[h.path] = h.score
                syms = sub_idx.search_symbols(token, limit=3)
                for s in syms:
                    nm = getattr(s, "name", str(s))
                    if nm not in seen_sym_names:
                        seen_sym_names.add(nm)
                        all_symbols.append(s)

            if not files_dict:
                for fallback_term in ["main", "app", "core", "server", "index", "config"]:
                    hits = sub_idx.search_code(fallback_term, limit=3)
                    for h in hits:
                        if h.path not in files_dict:
                            files_dict[h.path] = h.score

            ranked_files = sorted(files_dict.items(), key=lambda x: -x[1])
            top_files = [p for p, _ in ranked_files[:5]]

            findings.append({
                "question": q,
                "answer_summary": f"Found {len(top_files)} files in codebase",
                "matched_files": top_files,
                "matched_symbols": [
                    {
                        "name": getattr(s, "name", str(s)),
                        "kind": getattr(s, "kind", ""),
                        "path": getattr(s, "path", getattr(s, "file_path", "")),
                        "line": getattr(s, "line", 1),
                    } for s in all_symbols[:5]
                ],
                "status": "✅ FOUND" if top_files or all_symbols else "⚪ UNFOUND"
            })

        return json.dumps({
            "root_path": str(path),
            "total_files": stats.get("total_files", 0),
            "total_questions": len(questions),
            "findings": findings
        }, indent=2, ensure_ascii=False)

    return mcp
