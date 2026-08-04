from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from swarm_mcp.application.dtos import (
    FastDeconstructRequest,
    SearchCodebaseRequest,
    SpawnWorkerRequest,
    WorkerControlRequest,
)
from swarm_mcp.application.use_cases import (
    AskCodebaseUseCase,
    ControlSwarmWorkerUseCase,
    FastDeconstructCodebaseUseCase,
    GetFileSkeletonUseCase,
    AutoRouteSwarmCodebaseUseCase,
    GetSymbolContourUseCase,
    SearchCodebaseUseCase,
    SpawnSwarmWorkerUseCase,
)
from swarm_mcp.domain.services import SwarmAutoRouterService, SwarmOrchestratorService
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter


def create_swarm_mcp_server(root_path: Path | None = None) -> FastMCP:
    """Inbound Hexagonal Adapter creating standard MCP Server for Swarm BM25 & AgentJobEngine."""

    mcp = FastMCP("swarm-bm25-jobengine-mcp", instructions="Hexagonal Swarm BM25 & JobEngine MCP Server")

    # Wire Hexagonal Adapters & Use Cases
    index_adapter = IndexStoreAdapter(root=root_path)
    job_engine_adapter = JobEngineAdapter()
    orchestrator = SwarmOrchestratorService(index_adapter, job_engine_adapter)
    auto_router = SwarmAutoRouterService(index_adapter, job_engine_adapter)

    fast_deconstruct_uc = FastDeconstructCodebaseUseCase(orchestrator)
    autoroute_uc = AutoRouteSwarmCodebaseUseCase(auto_router)
    search_code_uc = SearchCodebaseUseCase(index_adapter)
    skeleton_uc = GetFileSkeletonUseCase(index_adapter)
    contour_uc = GetSymbolContourUseCase(index_adapter)
    ask_uc = AskCodebaseUseCase(index_adapter)
    spawn_worker_uc = SpawnSwarmWorkerUseCase(job_engine_adapter)
    control_worker_uc = ControlSwarmWorkerUseCase(job_engine_adapter)

    @mcp.tool()
    def fast_deconstruct_codebase(root_path: str, query: str = "") -> str:
        """Fast deconstruct and analyze codebase architecture using BM25 index & AST symbol contours."""
        req = FastDeconstructRequest(root_path=root_path, query=query)
        res = fast_deconstruct_uc.execute(req)
        return json.dumps(
            {
                "root_path": res.root_path,
                "stats": res.stats,
                "contour": res.contour,
                "top_files": res.top_files,
                "symbol_count": res.symbol_count,
            },
            indent=2,
            ensure_ascii=False,
        )

    @mcp.tool()
    def autoroute_swarm_codebase(root_path: str, max_agents: int = 0) -> str:
        """Dynamically partitions codebase across auto-routed Swarm Agents with memory & IO budgets."""
        res = autoroute_uc.execute(root_path=root_path, max_agents_cap=max_agents)
        return json.dumps(res, indent=2, ensure_ascii=False)

    @mcp.tool()
    def search_codebase(query: str, content_query: str = "", limit: int = 20) -> str:
        """Ranked BM25 search across files and content."""
        req = SearchCodebaseRequest(query=query, content_query=content_query, limit=limit)
        results = search_code_uc.execute(req)
        return json.dumps([{"path": r.path, "score": r.score, "matches": r.matches} for r in results], indent=2)

    @mcp.tool()
    def get_file_skeleton(path: str) -> str:
        """Extract Skeleton DSL for a specified file path."""
        res = skeleton_uc.execute(path)
        return res.dsl_text

    @mcp.tool()
    def get_symbol_contour(query: str) -> str:
        """Extract Skeleton DSL contour for matching symbol query."""
        res = contour_uc.execute(query)
        return res.dsl_text

    @mcp.tool()
    def ask_codebase(question: str) -> str:
        """Ask natural language architectural questions over indexed codebase."""
        res = ask_uc.execute(question)
        return json.dumps(
            {
                "question": res.question,
                "answer": res.answer,
                "files": res.files,
                "symbols": res.symbols,
            },
            indent=2,
            ensure_ascii=False,
        )

    @mcp.tool()
    def spawn_swarm_worker(
        worker_id: str,
        command: list[str],
        max_memory_mb: int = 512,
        cpu_rate_cap: int = 100,
        max_iops: int = 1000,
        max_net_bandwidth_mbps: int = 100,
        sandbox_enabled: bool = True,
    ) -> str:
        """Spawn a managed Swarm Worker process bound to AgentJobEngine OS resource limits."""
        req = SpawnWorkerRequest(
            worker_id=worker_id,
            command=command,
            max_memory_mb=max_memory_mb,
            cpu_rate_cap=cpu_rate_cap,
            max_iops=max_iops,
            max_net_bandwidth_mbps=max_net_bandwidth_mbps,
            sandbox_enabled=sandbox_enabled,
        )
        res = spawn_worker_uc.execute(req)
        return json.dumps(
            {
                "worker_id": res.worker_id,
                "pid": res.pid,
                "state": res.state,
                "budget": res.budget,
            },
            indent=2,
        )

    @mcp.tool()
    def control_swarm_worker(worker_id: str, action: str) -> str:
        """Control a Swarm Worker process (freeze, thaw, compress, terminate)."""
        req = WorkerControlRequest(worker_id=worker_id, action=action)
        res = control_worker_uc.execute(req)
        return json.dumps(
            {
                "worker_id": res.worker_id,
                "action": res.action,
                "success": res.success,
            },
            indent=2,
        )

    @mcp.tool()
    def get_swarm_stats() -> str:
        """Get global status of codebase BM25 index and active Swarm Workers."""
        index_stats = index_adapter.stats()
        workers = [w.to_dict() for w in job_engine_adapter.list_workers()]
        return json.dumps(
            {
                "index_stats": index_stats,
                "active_workers": workers,
            },
            indent=2,
        )

    return mcp
