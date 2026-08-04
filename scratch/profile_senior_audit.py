"""
Profiling script for SeniorCodebaseAuditEngine (150 questions).
Runs cProfile + line-level timing on hot functions.
"""
import cProfile
import io
import pstats
import time
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.application.senior_audit import SeniorCodebaseAuditEngine, SENIOR_QUESTIONS_BY_DOMAIN
from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from swarm_mcp.infrastructure.job_engine_adapter import JobEngineAdapter

# ---- Use swarm_bm itself as codebase --------------------------------
REPO = Path("/Volumes/External/Code/swarm_bm")
# (или Django если нужно: REPO = Path("/tmp/django_pr"))

print(f"[*] Target codebase: {REPO}")


# ─────────────────────────────────────────────────────────────────────
# Phase 0: warm up index (don't count in audit profiling)
# ─────────────────────────────────────────────────────────────────────
print("[*] Building index...")
t0 = time.perf_counter()
index_adapter = IndexStoreAdapter(root=REPO)
job_adapter = JobEngineAdapter()
engine = SeniorCodebaseAuditEngine(index_adapter, job_adapter)
# pre-build
index_adapter.rebuild(REPO)
idx_time = time.perf_counter() - t0
print(f"[+] Index built in {idx_time:.3f}s")

# ─────────────────────────────────────────────────────────────────────
# Phase 1: per-operation micro-benchmarks
# ─────────────────────────────────────────────────────────────────────
print("\n[*] Micro-benchmarks (1000 iterations each):")

TOKENS = ["transaction", "authenticate", "migrations", "cache", "serializer",
          "ForeignKey", "async def", "logging", "middleware", "permission"]

# BM25 search_code
times = []
for _ in range(1000):
    t = time.perf_counter()
    index_adapter.search_code("authentication token", limit=5)
    times.append(time.perf_counter() - t)
avg_search = sum(times) / len(times)
print(f"  search_code()       avg={avg_search*1000:.3f}ms  p95={sorted(times)[950]*1000:.3f}ms  p99={sorted(times)[990]*1000:.3f}ms")

# AST symbol search
times = []
for _ in range(1000):
    t = time.perf_counter()
    index_adapter.search_symbols("authenticate", limit=5)
    times.append(time.perf_counter() - t)
avg_sym = sum(times) / len(times)
print(f"  search_symbols()    avg={avg_sym*1000:.3f}ms  p95={sorted(times)[950]*1000:.3f}ms  p99={sorted(times)[990]*1000:.3f}ms")

# Multi-token BM25 (как в аудите)
times = []
for _ in range(200):
    t = time.perf_counter()
    for tok in TOKENS:
        index_adapter.search_code(tok, limit=5)
        index_adapter.search_symbols(tok, limit=3)
    times.append(time.perf_counter() - t)
avg_multi = sum(times) / len(times)
print(f"  10-token question    avg={avg_multi*1000:.3f}ms  p95={sorted(times)[190]*1000:.3f}ms")

# File skeleton
times = []
try:
    sample_file = next(REPO.rglob("*.py"), None)
    if sample_file:
        rel = str(sample_file.relative_to(REPO))
        for _ in range(500):
            t = time.perf_counter()
            index_adapter.get_file_skeleton(rel)
            times.append(time.perf_counter() - t)
        avg_skel = sum(times) / len(times)
        print(f"  get_file_skeleton()  avg={avg_skel*1000:.3f}ms  p95={sorted(times)[475]*1000:.3f}ms")
except Exception as e:
    print(f"  get_file_skeleton()  SKIP: {e}")

# ─────────────────────────────────────────────────────────────────────
# Phase 2: full cProfile of run_senior_audit
# ─────────────────────────────────────────────────────────────────────
print("\n[*] cProfile: full run_senior_audit (150 questions)...")
pr = cProfile.Profile()
pr.enable()
result = engine.run_senior_audit(REPO)
pr.disable()

stream = io.StringIO()
ps = pstats.Stats(pr, stream=stream)
ps.sort_stats("cumulative")
ps.print_stats(40)
report = stream.getvalue()

print(f"\n[+] Audit done: {result['total_questions_audited']} q / "
      f"{result['questions_with_real_findings']} with findings / "
      f"{result['elapsed_seconds']}s\n")
print(report)

# ─────────────────────────────────────────────────────────────────────
# Phase 3: per-domain timing breakdown
# ─────────────────────────────────────────────────────────────────────
print("\n[*] Per-domain timing breakdown (one audit pass):\n")
print(f"{'Domain':<55} {'Q found':>7} {'~ms est':>8}")
print("─" * 75)

questions_per_domain = {d: q for d, q in SENIOR_QUESTIONS_BY_DOMAIN.items()}
for dr in result["domain_results"]:
    domain = dr["domain"]
    q_found = dr["questions_with_findings"]
    n_tokens = sum(len(tokens) for _, tokens in questions_per_domain[domain])
    # estimate = tokens * avg single search
    est_ms = n_tokens * (avg_search + avg_sym) * 1000
    print(f"  {domain:<53} {q_found:>7} {est_ms:>7.1f}ms")

# ─────────────────────────────────────────────────────────────────────
# Phase 4: identify top bottlenecks from cProfile
# ─────────────────────────────────────────────────────────────────────
print("\n" + "═" * 75)
print("TOP 15 BOTTLENECKS (cumulative time):")
print("═" * 75)
stream2 = io.StringIO()
ps2 = pstats.Stats(pr, stream=stream2)
ps2.sort_stats("cumulative")
ps2.print_stats(15)
lines = stream2.getvalue().split("\n")
# print only the function lines
for line in lines:
    stripped = line.strip()
    if stripped and not stripped.startswith("ncalls") and ".py:" in line:
        print(line)

print("\n" + "═" * 75)
print("TOP 15 BY TOTTIME (self time — actual CPU hogs):")
print("═" * 75)
stream3 = io.StringIO()
ps3 = pstats.Stats(pr, stream=stream3)
ps3.sort_stats("tottime")
ps3.print_stats(15)
lines = stream3.getvalue().split("\n")
for line in lines:
    stripped = line.strip()
    if stripped and not stripped.startswith("ncalls") and ".py:" in line:
        print(line)

print("\n[DONE]")
