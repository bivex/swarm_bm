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


from swarm_mcp.application.senior_audit import SeniorCodebaseAuditEngine


def create_swarm_mcp_server(root_path: Path | None = None) -> FastMCP:
    """Inbound Hexagonal Adapter creating standard MCP Server for Swarm BM25 & AgentJobEngine."""

    mcp = FastMCP("swarm-bm25-jobengine-mcp", instructions="Hexagonal Swarm BM25 & JobEngine MCP Server")

    # Wire Hexagonal Adapters & Use Cases
    index_adapter = IndexStoreAdapter(root=root_path)
    job_engine_adapter = JobEngineAdapter()
    orchestrator = SwarmOrchestratorService(index_adapter, job_engine_adapter)
    auto_router = SwarmAutoRouterService(index_adapter, job_engine_adapter)
    senior_audit_engine = SeniorCodebaseAuditEngine(index_adapter, job_engine_adapter)

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
    def run_senior_codebase_audit(root_path: str) -> str:
        """Executes a 10-Agent Swarm Audit answering 50+ Senior Architectural Questions over the codebase."""
        res = senior_audit_engine.run_10_agent_senior_audit(Path(root_path))
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
    def run_stack_slicer(root_path: str, project_name: str = "") -> str:
        """Run Technology Stack Slicer 3.0 (250+ techs, 26 categories, 19 manifest parsers)."""
        from scratch.auditors.stack_slicer import run_detection, TECH_DB
        from pathlib import Path
        path = Path(root_path).resolve()
        sub_idx = IndexStoreAdapter(root=path)
        stats = sub_idx.rebuild(path)
        techs = run_detection(path, sub_idx)
        found = [t for t in techs if t.found]
        return json.dumps({
            "project_name": project_name or path.name,
            "total_files": stats.get("total_files", 0),
            "detected_techs_count": len(found),
            "detected_technologies": [
                {
                    "name": t.name,
                    "category": t.category,
                    "license": t.license,
                    "license_risk": t.license_risk,
                    "replaceability": t.replaceability,
                    "swap_note": t.swap_note,
                    "evidence": t.evidence[:2],
                } for t in found
            ]
        }, indent=2, ensure_ascii=False)

    @mcp.tool()
    def run_revenue_audit(root_path: str, project_name: str = "") -> str:
        """Run Revenue Maximization Auditor over codebase (11 commercial blocks, ARR forecast, license risk)."""
        from scratch.auditors.revenue_audit import analyze_codebase_revenue, calculate_arr_forecast
        from pathlib import Path
        path = Path(root_path).resolve()
        sub_idx = IndexStoreAdapter(root=path)
        stats = sub_idx.rebuild(path)
        findings = analyze_codebase_revenue(path, sub_idx)
        summary = calculate_arr_forecast(findings, stats.get("total_files", 0))
        return json.dumps(summary, indent=2, ensure_ascii=False)

    @mcp.tool()
    def run_security_compliance_audit(root_path: str, project_name: str = "") -> str:
        """Run Security & Compliance Risk Auditor (Secrets, OWASP Top 10, SOC2/GDPR/HIPAA/PCI, Security Debt Score)."""
        from scratch.auditors.security_compliance_audit import scan_codebase_security, calculate_security_debt
        from pathlib import Path
        path = Path(root_path).resolve()
        sub_idx = IndexStoreAdapter(root=path)
        stats = sub_idx.rebuild(path)
        rules = scan_codebase_security(path, sub_idx)
        found = [r for r in rules if r.found]
        score, grade = calculate_security_debt(rules)
        return json.dumps({
            "project_name": project_name or path.name,
            "security_debt_score": score,
            "due_diligence_grade": grade,
            "total_findings": len(found),
            "findings": [
                {
                    "rule_id": r.rule_id,
                    "title": r.title,
                    "severity": r.severity,
                    "penalty": r.penalty,
                    "evidence": r.evidence_files[:2],
                    "recommendation": r.recommendation,
                } for r in found
            ]
        }, indent=2, ensure_ascii=False)

    @mcp.tool()
    def run_whitelabel_readiness_audit(root_path: str, project_name: str = "") -> str:
        """Run Rebrand & White-Label Readiness Auditor (Hardcoded branding leaks, CSS variables, multi-tenancy, custom domain CNAME)."""
        from scratch.auditors.whitelabel_readiness_audit import scan_whitelabel_readiness, calculate_whitelabel_score
        from pathlib import Path
        path = Path(root_path).resolve()
        sub_idx = IndexStoreAdapter(root=path)
        stats = sub_idx.rebuild(path)
        rules = scan_whitelabel_readiness(path, sub_idx)
        found = [r for r in rules if r.found]
        score, grade, effort = calculate_whitelabel_score(rules)
        return json.dumps({
            "project_name": project_name or path.name,
            "whitelabel_score": score,
            "reseller_grade": grade,
            "rebrand_effort_estimate": effort,
            "findings": [
                {
                    "metric_id": r.metric_id,
                    "title": r.title,
                    "impact": r.impact,
                    "score_delta": r.score_delta,
                    "evidence": r.evidence_files[:2],
                } for r in found
            ]
        }, indent=2, ensure_ascii=False)

    return mcp
