from __future__ import annotations

import sys
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


class SwarmAutoRouterService:
    """Domain Service that auto-calculates optimal agent swarm count & routes module clusters."""

    def __init__(self, index_port: IndexPort, job_engine_port: JobEnginePort) -> None:
        self.index_port = index_port
        self.job_engine_port = job_engine_port

    def autoroute_codebase_swarm(
        self,
        root: Path | str,
        max_agents_cap: int = 0,
        available_ram_mb: int = 0,
    ) -> dict[str, Any]:
        """Dynamically partitions codebase across auto-routed Swarm Agents based on RAM and CPU limits."""
        root_path = Path(root) if isinstance(root, str) else root
        stats = self.index_port.rebuild(root_path)
        total_files = stats.get("total_files", 0)

        # 1. Discover top-level module/app clusters
        modules: list[dict[str, Any]] = []
        if root_path.exists():
            for child in sorted(root_path.iterdir()):
                if child.is_dir() and not child.name.startswith(".") and child.name not in {"venv", "__pycache__", "out", "build", "node_modules"}:
                    file_cnt = sum(1 for _ in child.rglob("*") if _.is_file() and not _.name.startswith("."))
                    if file_cnt > 0:
                        modules.append({"name": child.name, "path": str(child.relative_to(root_path)), "file_count": file_cnt})

        # 2. Determine System RAM
        if available_ram_mb <= 0:
            try:
                if sys.platform == "darwin":
                    import subprocess
                    out = subprocess.check_output(["sysctl", "-n", "hw.memsize"]).decode().strip()
                    available_ram_mb = int(int(out) / 1024 / 1024)
                else:
                    available_ram_mb = 16384
            except Exception:
                available_ram_mb = 16384

        # 3. Calculate Optimal Agent Count
        suggested_agent_count = max(1, min(len(modules) if modules else 4, total_files // 100 + 1))
        usable_ram = max(512, available_ram_mb // 2)
        max_agents_by_ram = usable_ram // 64  # 64MB per worker budget

        optimal_agents = max(1, min(suggested_agent_count, max_agents_by_ram))
        if max_agents_cap > 0:
            optimal_agents = min(optimal_agents, max_agents_cap)

        # 4. Partition Modules among Auto-Routed Agents
        routed_assignments: list[dict[str, Any]] = []
        if modules:
            buckets: list[list[dict[str, Any]]] = [[] for _ in range(optimal_agents)]
            for idx, mod in enumerate(modules):
                buckets[idx % optimal_agents].append(mod)

            for idx, bucket in enumerate(buckets):
                worker_id = f"swarm_agent_{idx + 1}"
                assigned_paths = [m["path"] for m in bucket]
                total_mod_files = sum(m["file_count"] for m in bucket)

                budget = ResourceBudget(
                    max_memory_mb=128,
                    cpu_rate_cap=min(100, max(20, 100 // optimal_agents)),
                    max_iops=max(100, 1000 // optimal_agents),
                    max_net_bandwidth_mbps=max(10, 100 // optimal_agents),
                    sandbox_enabled=True,
                )

                routed_assignments.append(
                    {
                        "worker_id": worker_id,
                        "target_paths": assigned_paths,
                        "file_count": total_mod_files,
                        "budget": budget.to_dict(),
                    }
                )

        return {
            "root_path": str(root),
            "total_files": total_files,
            "system_ram_mb": available_ram_mb,
            "optimal_agents_count": optimal_agents,
            "per_agent_ram_budget_mb": 128,
            "assignments": routed_assignments,
        }
