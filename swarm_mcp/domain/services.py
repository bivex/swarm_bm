from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import DomainAskAnswer, ResourceBudget, SwarmWorker
from .ports import IndexPort, JobEnginePort


class SwarmOrchestratorService:
    """Domain Service for high-speed codebase deconstruction and Swarm resource management."""

    def __init__(self, index_port: IndexPort, job_engine_port: JobEnginePort) -> None:
        self.index_port = index_port
        self.job_engine_port = job_engine_port

    def deconstruct_codebase_fast(self, root: Path, query: str = "") -> dict[str, Any]:
        """Fast codebase analysis combining index stats, symbol contour, and BM25 search."""
        stats = self.index_port.rebuild(root)
        contour = self.index_port.get_symbol_contour(query if query else "main")
        search_matches = self.index_port.search_code(query if query else "config")
        symbols = self.index_port.search_symbols(query if query else "")

        return {
            "root_path": str(root),
            "stats": stats,
            "contour": contour.dsl_text,
            "top_search_matches": [res.path for res in search_matches[:10]],
            "symbol_count": len(symbols),
        }

    def execute_managed_swarm_task(
        self,
        worker_id: str,
        command: list[str],
        budget: ResourceBudget,
    ) -> SwarmWorker:
        """Spawns worker under OS resource control for high-density execution."""
        return self.job_engine_port.spawn_worker(worker_id, command, budget)

    def optimize_idle_swarm_memory(self) -> dict[str, Any]:
        """Compresses memory for all active idle workers in the swarm."""
        return self.job_engine_port.compress_memory()
