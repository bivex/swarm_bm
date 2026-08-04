"""
C/C++ Codebase Profiling Script for SeniorCodebaseAuditEngine.
Runs full micro-benchmarks + cProfile on Redis source tree.
"""
import cProfile
import io
import pstats
import sys
import time
from pathlib import Path

root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.application.senior_audit import SeniorCodebaseAuditEngine, SENIOR_QUESTIONS_BY_DOMAIN
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter

REPO = Path("/tmp/redis_prof")
print(f"[*] Target C codebase: {REPO}")
print(f"[*] C/H files: {len(list(REPO.rglob('*.c')) + list(REPO.rglob('*.h')))}")
print(f"[*] Total files: {len(list(REPO.rglob('*')))}")

# ─────────────────────────────────────────────────────────────────────
# Phase 0: Index build timing
# ─────────────────────────────────────────────────────────────────────
print("\n[*] Building BM25+AST index over C codebase...")
t0 = time.perf_counter()
index_adapter = IndexStoreAdapter(root=REPO)
job_adapter = JobEngineAdapter()
engine = SeniorCodebaseAuditEngine(index_adapter, job_adapter)
idx_time = time.perf_counter() - t0

stats = index_adapter.stats()
print(f"[+] Index built in {idx_time:.3f}s")
print(f"    Files indexed  : {stats.get('total_files', 0)}")
print(f"    Symbols (AST)  : {stats.get('python_symbols', stats.get('total_symbols', 0))}")
print(f"    BM25 tokens    : {stats.get('bm25_tokens', 'n/a')}")

# ─────────────────────────────────────────────────────────────────────
# Phase 1: Micro-benchmarks tailored for C code tokens
# ─────────────────────────────────────────────────────────────────────
print("\n[*] Micro-benchmarks (1000 iterations, C-specific tokens):")

C_TOKENS = [
    "authenticate", "malloc", "free", "socket", "pthread",
    "mutex", "errno", "signal", "fork", "select",
]

def bench(fn, n=1000):
    t = [None] * n
    for i in range(n):
        s = time.perf_counter()
        fn()
        t[i] = time.perf_counter() - s
    t.sort()
    return t[0]*1000, (sum(t)/n)*1000, t[int(n*0.95)]*1000, t[int(n*0.99)]*1000

# search_code
mn, avg, p95, p99 = bench(lambda: index_adapter.search_code("malloc free memory", limit=5))
print(f"  search_code()        min={mn:.3f}ms  avg={avg:.3f}ms  p95={p95:.3f}ms  p99={p99:.3f}ms")

# search_symbols (exact — hits index)
mn, avg, p95, p99 = bench(lambda: index_adapter.search_symbols("authenticate", limit=5))
print(f"  search_symbols(exact) min={mn:.3f}ms  avg={avg:.3f}ms  p95={p95:.3f}ms  p99={p99:.3f}ms")

# search_symbols (prefix fallback — misses exact index)
mn, avg, p95, p99 = bench(lambda: index_adapter.search_symbols("acl_check_perm", limit=5))
print(f"  search_symbols(pfx)  min={mn:.3f}ms  avg={avg:.3f}ms  p95={p95:.3f}ms  p99={p99:.3f}ms")

# get_file_skeleton on a big C file
try:
    big_c = next(REPO.rglob("src/server.c"), None) or next(REPO.rglob("*.c"), None)
    if big_c:
        rel = str(big_c.relative_to(REPO))
        mn, avg, p95, p99 = bench(lambda: index_adapter.get_file_skeleton(rel), n=500)
        print(f"  get_skeleton({rel[-30:]}) min={mn:.3f}ms  avg={avg:.3f}ms  p95={p95:.3f}ms")
except Exception as e:
    print(f"  get_file_skeleton() SKIP: {e}")

# 10-token multi-search (как один вопрос аудита)
mn, avg, p95, p99 = bench(
    lambda: [index_adapter.search_code(t, limit=5) or index_adapter.search_symbols(t, limit=3) for t in C_TOKENS],
    n=200
)
print(f"  10-token question     min={mn:.3f}ms  avg={avg:.3f}ms  p95={p95:.3f}ms  p99={p99:.3f}ms")

# ─────────────────────────────────────────────────────────────────────
# Phase 2: Full cProfile of run_senior_audit on C codebase
# ─────────────────────────────────────────────────────────────────────
print("\n[*] cProfile: full 150-question audit on C codebase...")
pr = cProfile.Profile()
pr.enable()
result = engine.run_senior_audit(REPO)
pr.disable()

print(f"\n[+] Audit result:")
print(f"    Questions audited      : {result['total_questions_audited']}")
print(f"    With real findings     : {result['questions_with_real_findings']}")
print(f"    Elapsed                : {result['elapsed_seconds']}s")
print(f"    Files in index         : {result['total_files']}")

# ─────────────────────────────────────────────────────────────────────
# Phase 3: Per-domain breakdown
# ─────────────────────────────────────────────────────────────────────
print(f"\n{'Domain':<55} {'Q found':>7}")
print("─" * 65)
for dr in result["domain_results"]:
    print(f"  {dr['domain']:<53} {dr['questions_with_findings']:>7}")

# ─────────────────────────────────────────────────────────────────────
# Phase 4: cProfile top bottlenecks
# ─────────────────────────────────────────────────────────────────────
def print_top(sort_by: str, n: int = 15, label: str = ""):
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s)
    ps.sort_stats(sort_by)
    ps.print_stats(n)
    print(f"\n{'═'*72}")
    print(f"TOP {n} — {label} ({sort_by})")
    print(f"{'═'*72}")
    for line in s.getvalue().split("\n"):
        stripped = line.strip()
        if stripped and not stripped.startswith(("ncalls", "Ordered")):
            if ".py:" in line or "{built-in" in line:
                print(line)

print_top("cumulative", 15, "cumulative time")
print_top("tottime",    15, "self CPU time (hogs)")

# ─────────────────────────────────────────────────────────────────────
# Phase 5: Per-question hotspot analysis
# ─────────────────────────────────────────────────────────────────────
print(f"\n{'═'*72}")
print("HOTTEST QUESTIONS (most matched files + symbols):")
print(f"{'═'*72}")
all_findings = []
for dr in result["domain_results"]:
    for f in dr["findings"]:
        all_findings.append((
            len(f["matched_files"]) + len(f["symbols"]),
            dr["domain"],
            f["question"],
            f["matched_files"][:3],
            [s["name"] for s in f["symbols"][:3]],
        ))
all_findings.sort(reverse=True)
for score, domain, q, files, syms in all_findings[:10]:
    print(f"\n  [{score:3d}] {q}")
    print(f"        Domain : {domain}")
    print(f"        Files  : {', '.join(files[:3])}")
    if syms:
        print(f"        Symbols: {', '.join(syms[:3])}")

print("\n[DONE]")
