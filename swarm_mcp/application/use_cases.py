from __future__ import annotations

from pathlib import Path
from typing import Any

from swarm_mcp.domain.models import (
    DomainAskAnswer,
    DomainSearchResult,
    DomainSkeleton,
    DomainSymbol,
    ResourceBudget,
)
from swarm_mcp.domain.ports import IndexPort, JobEnginePort
from swarm_mcp.domain.services import SwarmAutoRouterService, SwarmOrchestratorService

from .dtos import (
    FastDeconstructRequest,
    FastDeconstructResponse,
    SearchCodebaseRequest,
    SpawnWorkerRequest,
    SpawnWorkerResponse,
    WorkerControlRequest,
    WorkerControlResponse,
)


class FastDeconstructCodebaseUseCase:
    """Use case to quickly index and deconstruct a codebase with BM25 + AST contours."""

    def __init__(self, orchestrator: SwarmOrchestratorService) -> None:
        self.orchestrator = orchestrator

    def execute(self, req: FastDeconstructRequest) -> FastDeconstructResponse:
        res = self.orchestrator.deconstruct_codebase_fast(Path(req.root_path), req.query)
        return FastDeconstructResponse(
            root_path=res["root_path"],
            stats=res["stats"],
            contour=res["contour"],
            top_files=res["top_search_matches"],
            symbol_count=res["symbol_count"],
        )


class SearchCodebaseUseCase:
    """Use case for ranked BM25 search over codebase content."""

    def __init__(self, index_port: IndexPort) -> None:
        self.index_port = index_port

    def execute(self, req: SearchCodebaseRequest) -> list[DomainSearchResult]:
        return self.index_port.search_code(req.query, req.content_query, req.limit)


class GetFileSkeletonUseCase:
    """Use case for extracting Skeleton DSL of a codebase file."""

    def __init__(self, index_port: IndexPort) -> None:
        self.index_port = index_port

    def execute(self, path: str) -> DomainSkeleton:
        return self.index_port.get_file_skeleton(path)


class GetSymbolContourUseCase:
    """Use case for extracting Skeleton DSL contour for a symbol query."""

    def __init__(self, index_port: IndexPort) -> None:
        self.index_port = index_port

    def execute(self, query: str) -> DomainSkeleton:
        return self.index_port.get_symbol_contour(query)


class AskCodebaseUseCase:
    """Use case for answering architectural queries."""

    def __init__(self, index_port: IndexPort) -> None:
        self.index_port = index_port

    def execute(self, question: str) -> DomainAskAnswer:
        return self.index_port.ask_question(question)


class SpawnSwarmWorkerUseCase:
    """Use case to spawn background worker processes governed by AgentJobEngine limits."""

    def __init__(self, job_engine_port: JobEnginePort) -> None:
        self.job_engine_port = job_engine_port

    def execute(self, req: SpawnWorkerRequest) -> SpawnWorkerResponse:
        budget = ResourceBudget(
            max_memory_mb=req.max_memory_mb,
            cpu_rate_cap=req.cpu_rate_cap,
            max_iops=req.max_iops,
            max_net_bandwidth_mbps=req.max_net_bandwidth_mbps,
            sandbox_enabled=req.sandbox_enabled,
        )
        worker = self.job_engine_port.spawn_worker(req.worker_id, req.command, budget)
        return SpawnWorkerResponse(
            worker_id=worker.worker_id,
            pid=worker.pid,
            state=worker.state.name,
            budget=worker.budget.to_dict(),
        )


class ControlSwarmWorkerUseCase:
    """Use case for controlling Swarm Workers (freeze, thaw, compress, terminate)."""

    def __init__(self, job_engine_port: JobEnginePort) -> None:
        self.job_engine_port = job_engine_port

    def execute(self, req: WorkerControlRequest) -> WorkerControlResponse:
        action = req.action.lower()
        success = False
        if action == "freeze":
            success = self.job_engine_port.freeze_worker(req.worker_id)
        elif action == "thaw":
            success = self.job_engine_port.thaw_worker(req.worker_id)
        elif action == "compress":
            res = self.job_engine_port.compress_memory(req.worker_id)
            success = res.get("success", True)
        elif action == "terminate":
            success = self.job_engine_port.terminate_worker(req.worker_id)

        return WorkerControlResponse(
            worker_id=req.worker_id,
            action=action,
            success=success,
        )


class AutoRouteSwarmCodebaseUseCase:
    """Use case to auto-calculate optimal swarm count and partition codebase across agents."""

    def __init__(self, auto_router: SwarmAutoRouterService) -> None:
        self.auto_router = auto_router

    def execute(self, root_path: str, max_agents_cap: int = 0) -> dict[str, Any]:
        return self.auto_router.autoroute_codebase_swarm(Path(root_path), max_agents_cap=max_agents_cap)
