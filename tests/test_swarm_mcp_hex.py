import sys
import tempfile
from pathlib import Path

# Ensure root workspace is in sys.path
root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from swarm_mcp.application.dtos import (
    FastDeconstructRequest,
    SearchCodebaseRequest,
    SpawnWorkerRequest,
    WorkerControlRequest,
)
from swarm_mcp.application.use_cases import (
    ControlSwarmWorkerUseCase,
    FastDeconstructCodebaseUseCase,
    SearchCodebaseUseCase,
    SpawnSwarmWorkerUseCase,
)
from swarm_mcp.domain.services import SwarmOrchestratorService
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter
from swarm_mcp.infrastructure.mcp_server_adapter import create_swarm_mcp_server


def test_ddd_hexagonal_integration():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "main.py").write_text(
            "class SwarmManager:\n"
            "    def run_worker(self, name: str) -> bool:\n"
            "        return True\n"
        )

        # Wire Ports & Adapters
        index_adapter = IndexStoreAdapter(root=tmp_path)
        job_engine_adapter = JobEngineAdapter()
        orchestrator = SwarmOrchestratorService(index_adapter, job_engine_adapter)

        # 1. Fast Deconstruct Use Case
        deconstruct_uc = FastDeconstructCodebaseUseCase(orchestrator)
        deconstruct_res = deconstruct_uc.execute(FastDeconstructRequest(root_path=str(tmp_path), query="SwarmManager"))
        assert deconstruct_res.root_path == str(tmp_path)
        assert "class SwarmManager" in deconstruct_res.contour

        # 2. Ranked Search Use Case
        search_uc = SearchCodebaseUseCase(index_adapter)
        search_res = search_uc.execute(SearchCodebaseRequest(query="SwarmManager"))
        assert len(search_res) > 0
        assert search_res[0].path == "main.py"

        # 3. Spawn Worker Use Case & Control (Freeze / Thaw)
        spawn_uc = SpawnSwarmWorkerUseCase(job_engine_adapter)
        spawn_res = spawn_uc.execute(
            SpawnWorkerRequest(
                worker_id="worker_test_1",
                command=["sleep", "10"],
                max_memory_mb=128,
            )
        )
        assert spawn_res.worker_id == "worker_test_1"
        assert spawn_res.state == "RUNNING"

        control_uc = ControlSwarmWorkerUseCase(job_engine_adapter)
        
        # Freeze Worker
        freeze_res = control_uc.execute(WorkerControlRequest(worker_id="worker_test_1", action="freeze"))
        assert freeze_res.success is True

        # Thaw Worker
        thaw_res = control_uc.execute(WorkerControlRequest(worker_id="worker_test_1", action="thaw"))
        assert thaw_res.success is True

        # Terminate Worker
        term_res = control_uc.execute(WorkerControlRequest(worker_id="worker_test_1", action="terminate"))
        assert term_res.success is True


def test_mcp_server_creation():
    with tempfile.TemporaryDirectory() as tmp:
        mcp_server = create_swarm_mcp_server(root_path=Path(tmp))
        assert mcp_server is not None
        assert mcp_server.name == "swarm-bm25-jobengine-mcp"
