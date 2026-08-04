import cProfile
import pstats
import sys
import time
from io import StringIO
from pathlib import Path

# Add root workspace to sys.path
root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


def profile_indexing(repo_path: str = "/tmp/django_profile"):
    print("=================================================================")
    print(" PROFILING SWARM BM25 & AST INDEXER BOTTLENECKS")
    print("=================================================================\n")

    root = Path(repo_path)
    if not root.exists():
        print(f"[-] Directory {repo_path} not found!")
        return

    adapter = IndexStoreAdapter()

    # 1. Profile IndexStore.rebuild()
    print("[1] Profiling IndexStore.rebuild() ...")
    pr = cProfile.Profile()
    pr.enable()

    t0 = time.perf_counter()
    stats = adapter.rebuild(root)
    t1 = time.perf_counter()

    pr.disable()
    print(f"  [+] Rebuild Total Time: {t1 - t0:.4f}s")
    print(f"  [+] Files: {stats.get('total_files')}, Symbols: {stats.get('total_symbols')}\n")

    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
    ps.print_stats(30)
    print("--- TOP 30 CUMULATIVE TIME FUNCTIONS ---")
    print(s.getvalue()[:3000])

    s_t = StringIO()
    ps_t = pstats.Stats(pr, stream=s_t).sort_stats(pstats.SortKey.TIME)
    ps_t.print_stats(30)
    print("\n--- TOP 30 SELF TIME (BOTTLENECKS) ---")
    print(s_t.getvalue()[:3000])

    # 2. Profile BM25 Search (100 Queries)
    print("\n[2] Profiling BM25 Search (100 query executions) ...")
    pr_search = cProfile.Profile()
    pr_search.enable()

    t_s0 = time.perf_counter()
    queries = ["Model", "QuerySet", "AuthenticationMiddleware", "select_related", "migration", "render", "url", "admin", "csrf", "cache"] * 10
    for q in queries:
        adapter.search_code(q, limit=20)
    t_s1 = time.perf_counter()

    pr_search.disable()
    print(f"  [+] 100 Search Queries Total Time: {t_s1 - t_s0:.4f}s ({((t_s1 - t_s0)/100)*1000:.2f} ms/query)\n")

    s_search = StringIO()
    ps_search = pstats.Stats(pr_search, stream=s_search).sort_stats(pstats.SortKey.TIME)
    ps_search.print_stats(20)
    print("--- TOP SEARCH SELF TIME BOTTLENECKS ---")
    print(s_search.getvalue()[:2000])

    # 3. Profile Contour Skeleton DSL Generation
    print("\n[3] Profiling Skeleton DSL Contour Generation (20 executions) ...")
    pr_contour = cProfile.Profile()
    pr_contour.enable()

    t_c0 = time.perf_counter()
    for q in queries[:20]:
        adapter.get_symbol_contour(q, limit=10)
    t_c1 = time.perf_counter()

    pr_contour.disable()
    print(f"  [+] 20 Contour Generations Total Time: {t_c1 - t_c0:.4f}s ({((t_c1 - t_c0)/20)*1000:.2f} ms/contour)\n")

    s_contour = StringIO()
    ps_contour = pstats.Stats(pr_contour, stream=s_contour).sort_stats(pstats.SortKey.TIME)
    ps_contour.print_stats(20)
    print("--- TOP CONTOUR SELF TIME BOTTLENECKS ---")
    print(s_contour.getvalue()[:2000])


if __name__ == "__main__":
    profile_indexing()
