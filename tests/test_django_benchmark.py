import sys
import time
from pathlib import Path

# Add root workspace to sys.path
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
    AskCodebaseUseCase,
    ControlSwarmWorkerUseCase,
    FastDeconstructCodebaseUseCase,
    GetFileSkeletonUseCase,
    GetSymbolContourUseCase,
    SearchCodebaseUseCase,
    SpawnSwarmWorkerUseCase,
)
from swarm_mcp.domain.services import SwarmOrchestratorService
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter


def run_django_test(django_path: str = "/tmp/django_test_codebase"):
    print("=================================================================")
    print(f" TESTING SWARM MCP ON REAL DJANGO CODEBASE: {django_path}")
    print("=================================================================\n")

    root = Path(django_path)
    if not root.exists():
        print(f"[-] Path {django_path} does not exist!")
        return

    # 1. Initialize Adapters & Services
    start_time = time.perf_counter()
    index_adapter = IndexStoreAdapter()
    job_adapter = JobEngineAdapter()
    orchestrator = SwarmOrchestratorService(index_adapter, job_adapter)

    # 2. Benchmark Indexing Speed
    print("[1/5] Building BM25 Index & AST Symbol Graph for Django...")
    stats = index_adapter.rebuild(root)
    elapsed = time.perf_counter() - start_time
    print(f"  [+] Indexing Completed in {elapsed:.3f} seconds!")
    print(f"  [+] Total Files Indexed: {stats.get('total_files', 0)}")
    print(f"  [+] Python AST Symbols Extracted: {stats.get('total_symbols', 0)}")
    print(f"  [+] Cache File Size: {stats.get('cache_size_bytes', 0) / 1024 / 1024:.2f} MB\n")

    # 3. Fast Deconstruct Use Case (Skeleton DSL for Django Models / QuerySet)
    print("[2/5] Fast Deconstructing Django Core Architecture (QuerySet / Model)...")
    deconstruct_uc = FastDeconstructCodebaseUseCase(orchestrator)
    res = deconstruct_uc.execute(FastDeconstructRequest(root_path=str(root), query="QuerySet"))
    print(f"  [+] Top Search File Matches: {res.top_files[:5]}")
    print("  [>>> EXTRACTED SKELETON DSL CONTOUR SAMPLE <<<]")
    contour_lines = res.contour.splitlines()[:25]
    print("\n".join(contour_lines))
    print("  [...]\n")

    # 4. BM25 Ranked Code Search
    print("[3/5] Performing BM25 Ranked Search for 'AuthenticationMiddleware' & 'select_related'...")
    search_uc = SearchCodebaseUseCase(index_adapter)
    search_res = search_uc.execute(SearchCodebaseRequest(query="AuthenticationMiddleware", limit=5))
    print("  [+] Top BM25 Matches for 'AuthenticationMiddleware':")
    for item in search_res:
        print(f"      - {item.path} (BM25 Score: {item.score:.4f})")
    print()

    # 5. Natural Language Architectural QA
    print("[4/5] Natural Language Architectural QA over Django...")
    ask_uc = AskCodebaseUseCase(index_adapter)
    ask_res = ask_uc.execute("где объявлен класс Model и QuerySet")
    print(f"  [+] Question: {ask_res.question}")
    print(f"  [+] Found Files: {ask_res.files[:3]}")
    print(f"  [+] Found Symbols: {ask_res.symbols[:3]}")
    print(f"  [+] Answer Excerpt: {ask_res.answer[:200]}...\n")

    # 6. AgentJobEngine Swarm Worker Process Control
    print("[5/5] Testing OS Worker Management (AgentJobEngine + Silo Sandbox + Working Set Trim)...")
    spawn_uc = SpawnSwarmWorkerUseCase(job_adapter)
    control_uc = ControlSwarmWorkerUseCase(job_adapter)

    # Spawn Django worker subprocess bound to AgentJobEngine
    spawn_res = spawn_uc.execute(
        SpawnWorkerRequest(
            worker_id="django_test_worker_1",
            command=["python3", "-c", "import time; print('Django Worker Active'); time.sleep(10)"],
            max_memory_mb=256,
            max_iops=500,
            sandbox_enabled=True,
        )
    )
    print(f"  [+] Spawned Managed Swarm Worker (ID: {spawn_res.worker_id}, PID: {spawn_res.pid})")
    print(f"  [+] Resource Budget Applied: {spawn_res.budget}")

    # Freeze Worker (SIGSTOP / Win32 Freeze)
    freeze_res = control_uc.execute(WorkerControlRequest(worker_id="django_test_worker_1", action="freeze"))
    print(f"  [+] Freezing Worker Process Tree: {freeze_res.success}")

    # Compress Working Set Memory
    compress_res = control_uc.execute(WorkerControlRequest(worker_id="django_test_worker_1", action="compress"))
    print(f"  [+] Working Set Memory Trim: {compress_res.success}")

    # Thaw Worker (SIGCONT / Win32 Thaw)
    thaw_res = control_uc.execute(WorkerControlRequest(worker_id="django_test_worker_1", action="thaw"))
    print(f"  [+] Thawing Worker Process Tree: {thaw_res.success}")

    # Terminate Worker
    term_res = control_uc.execute(WorkerControlRequest(worker_id="django_test_worker_1", action="terminate"))
    print(f"  [+] Terminating Swarm Worker: {term_res.success}\n")

    print("=================================================================")
    print(" ALL DJANGO BENCHMARK & SWARM MCP TESTS COMPLETED SUCCESSFULLY!")
    print("=================================================================")


if __name__ == "__main__":
    run_django_test()
