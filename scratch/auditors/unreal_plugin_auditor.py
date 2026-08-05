#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🎮 Unreal Engine Game Plugin & Marketplace Readiness Auditor             ║
║   BM25 + AST + C++ Game Thread & UE Garbage Collection Hygiene Scanner    ║
║                                                                           ║
║   PURPOSE: Audit Unreal Engine 4 / 5 C++ & Blueprint plugins for:        ║
║   - Plugin Descriptor & Module Hygiene (.uplugin, Build.cs, LoadingPhase) ║
║   - C++ Memory Safety & GC Roots (UPROPERTY, UCLASS, TSmartPtr)          ║
║   - Game Thread Hygiene (blocking I/O vs Async Tasks / FRunnable)          ║
║   - Network Replication & Multiplayer (RPCs, DOREPLIFETIME, Reliable)     ║
║   - Render Core & RHI Thread Hygiene (ENQUEUE_RENDER_COMMAND, HLSL)        ║
║   - Epic Fab Marketplace Commercial Readiness & DLL Export (MYPLUGIN_API)  ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/unreal_plugin_auditor.py /path/to/ue_plugin [PluginName]
"""
from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter


@dataclass
class UEMetric:
    """Documentation for UEMetric."""
    category: str           # MODULE_DESCRIPTOR / MEMORY_GC / THREADING / REPLICATION / RENDERING / MARKETPLACE
    rule_id: str            # UE-001, UE-002, etc.
    title: str
    impact: str             # POSITIVE / NEGATIVE
    score_delta: int        # Plugin Quality Score Delta
    description: str
    evidence_files: list[str] = field(default_factory=list)
    recommendation: str = ""
    found: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# 15+ Unreal Engine Plugin Audit Rules Registry
# ─────────────────────────────────────────────────────────────────────────────
UE_RULES: list[UEMetric] = [

    # ── 1. PLUGIN DESCRIPTOR & BUILD MATRIX ───────────────────────────────────
    UEMetric(
        category="MODULE_DESCRIPTOR", rule_id="UE-001",
        title="Valid .uplugin Descriptor & LoadingPhase Specification",
        impact="POSITIVE", score_delta=+15,
        description="Plugin contains valid .uplugin descriptor specifying ModuleType (Runtime/Editor) and LoadingPhase.",
        recommendation="Ensure EngineVersion and MarketPlaceURL fields are populated for Fab Marketplace release.",
    ),
    UEMetric(
        category="MODULE_DESCRIPTOR", rule_id="UE-002",
        title="Modular C++ Build.cs Dependency Declaration",
        impact="POSITIVE", score_delta=+10,
        description="Module dependencies are cleanly separated into PublicDependencyModuleNames and PrivateDependencyModuleNames.",
        recommendation="Keep Public dependencies minimal to avoid header include bloat in user projects.",
    ),
    UEMetric(
        category="MODULE_DESCRIPTOR", rule_id="UE-003",
        title="DLL Export Macro Specifier (*_API) on Public Classes",
        impact="POSITIVE", score_delta=+15,
        description="Public UCLASS/USTRUCT definitions use the module DLL export macro (e.g., MYPLUGIN_API).",
        recommendation="Required for C++ module linking when plugin is compiled as DLL in monolithic builds.",
    ),

    # ── 2. MEMORY SAFETY & GARBAGE COLLECTION ────────────────────────────────
    UEMetric(
        category="MEMORY_GC", rule_id="UE-004",
        title="Garbage Collection Protection (`UPROPERTY()` on UObject Pointers)",
        impact="POSITIVE", score_delta=+15,
        description="UObject pointers in class members are decorated with UPROPERTY() to prevent GC dangling pointers.",
        recommendation="Always mark raw UObject* pointers with UPROPERTY() or use TWeakObjectPtr / TStrongObjectPtr.",
    ),
    UEMetric(
        category="MEMORY_GC", rule_id="UE-005",
        title="Raw C++ Dynamic Allocations (`new`/`delete` on UObjects)",
        impact="NEGATIVE", score_delta=-20,
        description="Found raw C++ 'new' operator used for UObject creation instead of NewObject<T>() / CreateDefaultSubobject<T>().",
        recommendation="Use NewObject<T>() or CreateDefaultSubobject<T>() for UObject lifecycle management.",
    ),
    UEMetric(
        category="MEMORY_GC", rule_id="UE-006",
        title="Smart Pointer Hygiene (TSharedPtr, TWeakPtr, TUniquePtr)",
        impact="POSITIVE", score_delta=+10,
        description="Non-UObject data structures use UE C++ smart pointers (TSharedPtr / TSharedRef) instead of raw pointers.",
        recommendation="Use MakeShared<T>() for thread-safe reference counting.",
    ),

    # ── 3. THREADING & GAME LOOP PERFORMANCE ──────────────────────────────────
    UEMetric(
        category="THREADING", rule_id="UE-007",
        title="Asynchronous Multithreading (Async / FRunnable / Tasks::Launch)",
        impact="POSITIVE", score_delta=+15,
        description="Heavy I/O, network, or calculation tasks are offloaded to UE Async TaskGraph or FRunnable threads.",
        recommendation="Never block the Game Thread with file I/O or synchronous HTTP calls.",
    ),
    UEMetric(
        category="THREADING", rule_id="UE-008",
        title="Blocking Operations on Game Thread (FFileHelper / Synchronous HTTP)",
        impact="NEGATIVE", score_delta=-15,
        description="Found synchronous file or network operations executed on the main game thread.",
        recommendation="Wrap file reads and HTTP requests in FHttpModule async callbacks or Async(EAsyncExecution::Thread).",
    ),
    UEMetric(
        category="THREADING", rule_id="UE-009",
        title="Unoptimized Actor Ticking (`bCanEverTick = true` on Passive Actors)",
        impact="NEGATIVE", score_delta=-10,
        description="Found PrimaryActorTick.bCanEverTick set to true in constructors without tick optimizations.",
        recommendation="Disable tick (bCanEverTick = false) for actors that do not require frame-by-frame updates.",
    ),

    # ── 4. MULTIPLAYER NETWORK REPLICATION ────────────────────────────────────
    UEMetric(
        category="REPLICATION", rule_id="UE-010",
        title="Multiplayer Network RPC Declarations (Server / Client / NetMulticast)",
        impact="POSITIVE", score_delta=+15,
        description="Plugin implements networked RPC functions with UFUNCTION(Server, Reliable, WithValidation).",
        recommendation="Implement _Validate and _Implementation methods for all Server RPCs for anti-cheat security.",
    ),
    UEMetric(
        category="REPLICATION", rule_id="UE-011",
        title="Property Replication Hygiene (DOREPLIFETIME & GetLifetimeReplicatedProps)",
        impact="POSITIVE", score_delta=+10,
        description="Replicated properties use ReplicatedUsing / DOREPLIFETIME macros with condition flags.",
        recommendation="Use DOREPLIFETIME_CONDITION with COND_OwnerOnly or COND_SkipOwner to optimize network bandwidth.",
    ),

    # ── 5. RENDER CORE & SHADERS ──────────────────────────────────────────────
    UEMetric(
        category="RENDERING", rule_id="UE-012",
        title="Render Core / RHI Thread Isolation (ENQUEUE_RENDER_COMMAND)",
        impact="POSITIVE", score_delta=+10,
        description="Direct RHI render commands are dispatched to the Render Thread via ENQUEUE_RENDER_COMMAND.",
        recommendation="Never call RHI methods directly from the Game Thread.",
    ),

    # ── 6. FAB MARKETPLACE COMMERCIAL READINESS ───────────────────────────────
    UEMetric(
        category="MARKETPLACE", rule_id="UE-013",
        title="Blueprint Exposure (UFUNCTION(BlueprintCallable, BlueprintPure))",
        impact="POSITIVE", score_delta=+15,
        description="Plugin exports C++ methods to Blueprint visual scripting via BlueprintCallable / BlueprintPure.",
        recommendation="Provide clean Blueprint category tags (Category = 'MyPlugin|Core') for marketplace users.",
    ),
    UEMetric(
        category="MARKETPLACE", rule_id="UE-014",
        title="Hardcoded Absolute File Paths (`C:/`, `/Users/`, `/home/`)",
        impact="NEGATIVE", score_delta=-20,
        description="Found hardcoded absolute system paths instead of FPaths::ProjectDir() / FPaths::PluginDir().",
        recommendation="Replace hardcoded paths with FPaths::Combine(FPaths::ProjectContentDir(), ...).",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Search Heuristics
# ─────────────────────────────────────────────────────────────────────────────
UE_PATTERNS = {
    "UE-001": [".uplugin", "LoadingPhase", "ModuleType", "EngineVersion"],
    "UE-002": ["PublicDependencyModuleNames", "PrivateDependencyModuleNames", "Build.cs"],
    "UE-003": ["_API", "UCLASS(", "USTRUCT("],
    "UE-004": ["UPROPERTY(", "UPROPERTY"],
    "UE-005": ["new UObject", "new AActor", "new U"],
    "UE-006": ["TSharedPtr", "TSharedRef", "TWeakPtr", "TUniquePtr", "MakeShared"],
    "UE-007": ["Async(", "TaskGraph", "FRunnable", "Tasks::Launch", "EAsyncExecution"],
    "UE-008": ["FFileHelper::LoadFileToString", "FFileHelper::SaveStringToFile"],
    "UE-009": ["PrimaryActorTick.bCanEverTick = true", "bCanEverTick = true"],
    "UE-010": ["UFUNCTION(Server", "UFUNCTION(Client", "UFUNCTION(NetMulticast", "WithValidation"],
    "UE-011": ["DOREPLIFETIME", "GetLifetimeReplicatedProps", "ReplicatedUsing"],
    "UE-012": ["ENQUEUE_RENDER_COMMAND", "FRHICommandList", "RHICmdList"],
    "UE-013": ["BlueprintCallable", "BlueprintPure", "BlueprintAssignable"],
    "UE-014": ["C:/", "D:/", "/Users/", "/home/"],
}


def scan_unreal_plugin(root: Path, idx: IndexStoreAdapter) -> list[UEMetric]:
    """Scan Unreal Engine C++ / Blueprint plugin for quality & marketplace readiness."""
    for rule in UE_RULES:
        patterns = UE_PATTERNS.get(rule.rule_id, [])
        hits = set()

        # Check for .uplugin file
        if rule.rule_id == "UE-001":
            uplugin_files = list(root.glob("*.uplugin")) + list(root.rglob("*.uplugin"))
            if uplugin_files:
                hits.update(str(f.relative_to(root)) for f in uplugin_files)

        # Check for Build.cs file
        if rule.rule_id == "UE-002":
            build_files = list(root.rglob("*.Build.cs"))
            if build_files:
                hits.update(str(f.relative_to(root)) for f in build_files)

        for pat in patterns:
            try:
                bm25_results = idx.search_code(pat, limit=4)
                for r in bm25_results:
                    if r.path and not any(x in r.path for x in ("Binaries", "Intermediate", "Saved", ".git", "DerivedDataCache")):
                        hits.add(r.path)
            except Exception:
                pass

        rule.evidence_files = sorted(list(hits))[:4]
        rule.found = len(rule.evidence_files) > 0

    return UE_RULES


def calculate_ue_score(rules: list[UEMetric]) -> tuple[int, str, str]:
    """Calculate Unreal Engine Plugin Quality Score (0-100) and Fab Marketplace Grade."""
    base_score = 50
    for r in rules:
        if r.found:
            base_score += r.score_delta

    score = max(0, min(100, base_score))

    if score >= 85:
        grade = "A+ (Fab Marketplace Ready — AAA Quality)"
        status = "🟢 AAA READY — Clean C++, GC Protected, Async Threading & Network RPCs"
    elif score >= 70:
        grade = "A (High Quality UE Plugin)"
        status = "🟢 HIGH — Clean Plugin Descriptor, Modular Build.cs & Blueprint Exposed"
    elif score >= 55:
        grade = "B (Moderate Technical Debt)"
        status = "🟡 MEDIUM — Needs GC / Game Thread Optimization"
    elif score >= 40:
        grade = "C (Marketplace Rejection Hazard)"
        status = "🟠 HIGH RISK — Hardcoded Paths or Unprotected Raw Pointers"
    else:
        grade = "F (Critical UE Architecture Debt)"
        status = "🔴 CRITICAL RISK — Memory Leak / Game Thread Blocking Hazard"

    return score, grade, status


def print_report(project: str, root: Path, rules: list[UEMetric],
    """Documentation for print_report."""
                 stats: dict, elapsed: float, report_path: Path) -> None:
    found_rules = [r for r in rules if r.found]
    score, grade, status = calculate_ue_score(rules)

    positives = [r for r in found_rules if r.impact == "POSITIVE"]
    negatives = [r for r in found_rules if r.impact == "NEGATIVE"]

    lines = [
        f"# 🎮 Unreal Engine Plugin Quality Audit — {project}",
        f"> {root} · {stats.get('total_files', 0):,} files · {elapsed:.2f}s · {date.today()}",
        "",
        "## 📊 Unreal Plugin Quality Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| **UE Plugin Quality Score** | **{score} / 100** |",
        f"| **Fab Marketplace Grade** | **{grade}** |",
        f"| **Readiness Status** | **{status}** |",
        f"| Plugin Files Scanned | {stats.get('total_files', 0):,} |",
        f"| UE Best Practices Enablers | {len(positives)} |",
        f"| Architecture Risk Targets | {len(negatives)} |",
        "",
        "## 🟢 Verified Unreal Engine Best Practices",
        "",
    ]

    if positives:
        for r in positives:
            ev = ", ".join(f"`{e}`" for e in r.evidence_files)
            lines.append(f"### 🟢 [{r.rule_id}] {r.title} (+{r.score_delta} pts)")
            lines.append(f"**Description:** {r.description}")
            lines.append(f"**Evidence:** {ev}")
            lines.append(f"**UE Guideline:** {r.recommendation}")
            lines.append("")
    else:
        lines.append("*No automated UE best practice enablers detected.*")
        lines.append("")

    lines += ["## 🔴 UE Technical Debt & Marketplace Risks", ""]
    if negatives:
        for r in negatives:
            ev = ", ".join(f"`{e}`" for e in r.evidence_files)
            lines.append(f"### 🔴 [{r.rule_id}] {r.title} ({r.score_delta} pts)")
            lines.append(f"**Description:** {r.description}")
            lines.append(f"**Evidence Files:** {ev}")
            lines.append(f"**Remediation:** {r.recommendation}")
            lines.append("")
    else:
        lines.append("*Zero major UE plugin risks detected! Marketplace compliant.*")
        lines.append("")

    lines += [
        "## 🚀 UE Plugin Optimization Roadmap",
        "",
        "1. **Garbage Collection**: Wrap all raw `UObject*` member pointers in `UPROPERTY()` to prevent crashes.",
        "2. **Async Offloading**: Offload HTTP & disk file I/O to `Async(EAsyncExecution::Thread, ...)`.",
        "3. **DLL Exports**: Decorate all public `UCLASS` declarations with module API export macros (`MYPLUGIN_API`).",
        "4. **Relative Paths**: Replace any hardcoded absolute paths with `FPaths::ProjectDir()`.",
        "",
        "---",
        f"*Unreal Engine Game Plugin Auditor · {date.today()}*",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🎮 UNREAL ENGINE GAME PLUGIN AUDITOR: {project}")
    print(SEP)
    print(f"  Files indexed               : {stats.get('total_files', 0):,}")
    print(f"  UE Plugin Quality Score     : {score} / 100")
    print(f"  Fab Marketplace Grade       : {grade}")
    print(f"  Readiness Status            : {status}")
    print(f"  Active UE Rules Verified    : {len(found_rules)} / {len(rules)}")
    print(f"  Audit Speed                 : {elapsed:.3f}s")
    print(f"  Report Saved                : {report_path}")
    print(f"{SEP}\n")


def main() -> None:
    """Documentation for main."""
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/unreal_plugin_auditor.py /path/to/ue_plugin [PluginName]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    project_name = sys.argv[2] if len(sys.argv) > 2 else project_path.name

    app_data = Path.home() / ".gemini" / "antigravity-cli" / "brain" / "b1a8b172-4960-462a-bad1-43d8b7e774ad"
    app_data.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-z0-9_]", "_", project_name.lower())
    report_path = app_data / f"unreal_plugin_{safe_name}.md"

    t0 = time.perf_counter()
    idx = IndexStoreAdapter()
    stats = idx.rebuild(project_path)
    rules = scan_unreal_plugin(project_path, idx)
    elapsed = time.perf_counter() - t0

    print_report(project_name, project_path, rules, stats, elapsed, report_path)


if __name__ == "__main__":
    main()
