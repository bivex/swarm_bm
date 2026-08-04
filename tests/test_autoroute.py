import sys
import tempfile
from pathlib import Path

root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from swarm_mcp.domain.services import SwarmAutoRouterService
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter


def test_swarm_autorouting():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # Create mock Django app modules
        (root / "contrib" / "auth").mkdir(parents=True)
        (root / "contrib" / "auth" / "models.py").write_text("class User: pass")

        (root / "db" / "models").mkdir(parents=True)
        (root / "db" / "models" / "query.py").write_text("class QuerySet: pass")

        (root / "views" / "generic").mkdir(parents=True)
        (root / "views" / "generic" / "list.py").write_text("class ListView: pass")

        (root / "forms").mkdir(parents=True)
        (root / "forms" / "fields.py").write_text("class Field: pass")

        index_adapter = IndexStoreAdapter(root=root)
        job_adapter = JobEngineAdapter()
        auto_router = SwarmAutoRouterService(index_adapter, job_adapter)

        res = auto_router.autoroute_codebase_swarm(root)

        assert res["total_files"] >= 4
        assert res["optimal_agents_count"] > 0
        assert len(res["assignments"]) == res["optimal_agents_count"]

        # Check assignment budget structure
        for assign in res["assignments"]:
            assert "worker_id" in assign
            assert "target_paths" in assign
            assert "budget" in assign
            assert assign["budget"]["max_memory_mb"] == 128
            assert assign["budget"]["sandbox_enabled"] is True
