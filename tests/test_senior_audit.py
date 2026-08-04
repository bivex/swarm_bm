import sys
import tempfile
from pathlib import Path

root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from swarm_mcp.application.senior_audit import SENIOR_QUESTIONS_BY_DOMAIN, SeniorCodebaseAuditEngine
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter


def test_150_question_senior_audit_structure():
    """Verify 15 domains x 10 questions = 150 total."""
    assert len(SENIOR_QUESTIONS_BY_DOMAIN) == 15
    for domain, questions in SENIOR_QUESTIONS_BY_DOMAIN.items():
        assert len(questions) == 10, f"{domain} should have 10 questions, got {len(questions)}"

    total = sum(len(q) for q in SENIOR_QUESTIONS_BY_DOMAIN.values())
    assert total == 150, f"Expected 150 questions, got {total}"


def test_audit_runs_on_real_codebase():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "main.py").write_text(
            "import redis\nclass SeniorApp:\n    def start(self): pass\n"
        )
        (root / "models.py").write_text(
            "from django.db import models\nclass User(models.Model):\n    id = models.IntegerField()\n"
        )
        (root / "auth.py").write_text(
            "def jwt_auth(): pass\ndef authenticate(user, password): pass\n"
        )
        (root / "celery.py").write_text(
            "from celery import Celery\napp = Celery('tasks')\n"
        )
        (root / "settings.py").write_text(
            "SECRET_KEY = 'test'\nDATABASES = {}\nLOGGING = {}\n"
        )

        index_adapter = IndexStoreAdapter(root=root)
        job_adapter = JobEngineAdapter()
        engine = SeniorCodebaseAuditEngine(index_adapter, job_adapter)

        res = engine.run_senior_audit(root)

        assert res["agents_count"] == 15
        assert res["total_questions_audited"] == 150
        assert res["questions_with_real_findings"] >= 1
        assert len(res["domain_results"]) == 15


def test_backward_compat_alias():
    """run_10_agent_senior_audit must still work."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "main.py").write_text("def main(): pass\n")
        engine = SeniorCodebaseAuditEngine(IndexStoreAdapter(), JobEngineAdapter())
        res = engine.run_10_agent_senior_audit(root)
        assert res["total_questions_audited"] == 150
