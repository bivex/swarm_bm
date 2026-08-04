import sys
import tempfile
from pathlib import Path

root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from swarm_mcp.application.senior_audit import SENIOR_QUESTIONS_BY_DOMAIN, SeniorCodebaseAuditEngine
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter


def test_10_agent_senior_audit():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "main.py").write_text("class SeniorApp:\n    def start(self): pass\n")
        (root / "models.py").write_text("class User:\n    id: int\n")
        (root / "auth.py").write_text("def jwt_auth(): pass\n")

        index_adapter = IndexStoreAdapter(root=root)
        job_adapter = JobEngineAdapter()
        engine = SeniorCodebaseAuditEngine(index_adapter, job_adapter)

        res = engine.run_10_agent_senior_audit(root)

        assert res["agents_count"] == 10
        assert res["total_questions_audited"] == 50
        assert len(res["domain_results"]) == 10

        # Check domains
        for domain_res in res["domain_results"]:
            assert "agent_id" in domain_res
            assert "domain" in domain_res
            assert len(domain_res["findings"]) == 5
