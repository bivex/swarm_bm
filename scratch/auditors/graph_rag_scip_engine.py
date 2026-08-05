#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🕸️ Graph-RAG & SCIP Codebase Navigation Engine                          ║
║   AST Symbol Contour + Call Graph + Personalized PageRank + Graph-RAG     ║
║                                                                           ║
║   PURPOSE: Extends SwarmBM Codebase Intelligence with Graph-RAG:          ║
║   - Direct Call-Graph (Who calls X / What does X call)                    ║
║   - Inheritance & Interface Contour Slicing                               ║
║   - Personalized PageRank for Architectural Symbol Centrality             ║
║   - Graph-RAG Context Generation for AI Agent Swarms                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python3 scratch/auditors/graph_rag_scip_engine.py /path/to/project [SymbolNameOrQuery]
"""
from __future__ import annotations

import json
import math
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from collections import defaultdict, Counter
from typing import Any

root_dir = next(p for p in Path(__file__).resolve().parents if (p / "bm25_server_FS_for-AI-asking").exists())
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "bm25_server_FS_for-AI-asking"))

from swarm_mcp.infrastructure.index_store_adapter import IndexStoreAdapter
from ramdisk_fs_server.skeleton_dsl import render_symbol_dsl, render_contour_skeleton_dsl


@dataclass
class CodeNode:
    symbol_id: str          # qualname or path:Lline
    name: str
    kind: str               # class, function, method, interface
    path: str
    line: int
    signature: str = ""
    docstring: str = ""
    pagerank_score: float = 0.0


@dataclass
class CodeCallEdge:
    source_id: str
    target_id: str
    kind: str               # CALLS / INHERITS / REFERENCES


class GraphRAGEngine:
    """Graph-RAG & AST/SCIP Call Graph Navigator for SwarmBM."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.idx = IndexStoreAdapter()
        self.stats = self.idx.rebuild(root)
        
        self.nodes: dict[str, CodeNode] = {}
        self.outgoing_edges: dict[str, list[CodeCallEdge]] = defaultdict(list)
        self.incoming_edges: dict[str, list[CodeCallEdge]] = defaultdict(list)
        self.symbol_lookup: dict[str, str] = {}  # name or qualname -> symbol_id
        
        self._build_code_graph()
        self._compute_pagerank()

    def _build_code_graph(self) -> None:
        """Construct directed graph from AST extracted symbols and call relations."""
        # 1. Index all nodes
        for sym in self.idx.store.python_symbols:
            sym_id = f"{sym.path}:L{sym.line}:{sym.name}"
            node = CodeNode(
                symbol_id=sym_id,
                name=sym.name,
                kind=sym.kind,
                path=sym.path,
                line=sym.line,
                signature=sym.signature or "()",
                docstring=sym.docstring or "",
            )
            self.nodes[sym_id] = node
            self.symbol_lookup[sym.name] = sym_id
            self.symbol_lookup[sym.qualname] = sym_id

        # 2. Build edges for calls & inheritance
        for sym in self.idx.store.python_symbols:
            src_id = f"{sym.path}:L{sym.line}:{sym.name}"
            
            # Calls edges
            for call_target in sym.calls:
                target_short = call_target.split(".")[-1]
                tgt_id = self.symbol_lookup.get(call_target) or self.symbol_lookup.get(target_short)
                if tgt_id and tgt_id != src_id:
                    edge = CodeCallEdge(source_id=src_id, target_id=tgt_id, kind="CALLS")
                    self.outgoing_edges[src_id].append(edge)
                    self.incoming_edges[tgt_id].append(edge)

            # Inheritance edges
            for parent_class in sym.inherits:
                parent_short = parent_class.split(".")[-1]
                tgt_id = self.symbol_lookup.get(parent_class) or self.symbol_lookup.get(parent_short)
                if tgt_id and tgt_id != src_id:
                    edge = CodeCallEdge(source_id=src_id, target_id=tgt_id, kind="INHERITS")
                    self.outgoing_edges[src_id].append(edge)
                    self.incoming_edges[tgt_id].append(edge)

    def _compute_pagerank(self, damping: float = 0.85, max_iter: int = 20) -> None:
        """Compute Personalized PageRank for centrality ranking of key architectural symbols."""
        num_nodes = len(self.nodes)
        if num_nodes == 0:
            return

        initial_score = 1.0 / num_nodes
        scores = {node_id: initial_score for node_id in self.nodes}

        for _ in range(max_iter):
            new_scores: dict[str, float] = {}
            for node_id in self.nodes:
                incoming = self.incoming_edges.get(node_id, [])
                rank_sum = 0.0
                for edge in incoming:
                    src_out_count = len(self.outgoing_edges.get(edge.source_id, []))
                    if src_out_count > 0:
                        rank_sum += scores[edge.source_id] / src_out_count

                new_scores[node_id] = ((1.0 - damping) / num_nodes) + (damping * rank_sum)
            scores = new_scores

        for node_id, score in scores.items():
            self.nodes[node_id].pagerank_score = score

    def query_graph_rag(self, query: str, depth: int = 2, top_k: int = 5) -> dict[str, Any]:
        """Perform Graph-RAG context extraction starting from matching seed symbols."""
        matching_symbols = self.idx.search_symbols(query, limit=top_k)
        if not matching_symbols:
            # Fallback to BM25 search
            bm25_hits = self.idx.search_code(query, limit=top_k)
            seed_ids = [self.symbol_lookup[r.path.split('/')[-1]] for r in bm25_hits if r.path.split('/')[-1] in self.symbol_lookup]
        else:
            seed_ids = [f"{s.path}:L{s.line}:{s.name}" for s in matching_symbols if f"{s.path}:L{s.line}:{s.name}" in self.nodes]

        visited: set[str] = set(seed_ids)
        frontier: list[tuple[str, int]] = [(sid, 0) for sid in seed_ids]
        extracted_subgraph_nodes: list[CodeNode] = []
        extracted_edges: list[dict[str, str]] = []

        while frontier:
            curr_id, curr_depth = frontier.pop(0)
            if curr_id in self.nodes:
                extracted_subgraph_nodes.append(self.nodes[curr_id])

            if curr_depth < depth:
                # Add callers
                for edge in self.incoming_edges.get(curr_id, []):
                    if edge.source_id not in visited:
                        visited.add(edge.source_id)
                        frontier.append((edge.source_id, curr_depth + 1))
                    extracted_edges.append({"from": self.nodes[edge.source_id].name if edge.source_id in self.nodes else edge.source_id,
                                            "to": self.nodes[curr_id].name if curr_id in self.nodes else curr_id,
                                            "relation": edge.kind})

                # Add callees
                for edge in self.outgoing_edges.get(curr_id, []):
                    if edge.target_id not in visited:
                        visited.add(edge.target_id)
                        frontier.append((edge.target_id, curr_depth + 1))
                    extracted_edges.append({"from": self.nodes[curr_id].name if curr_id in self.nodes else curr_id,
                                            "to": self.nodes[edge.target_id].name if edge.target_id in self.nodes else edge.target_id,
                                            "relation": edge.kind})

        # Sort extracted nodes by PageRank centrality
        extracted_subgraph_nodes.sort(key=lambda n: n.pagerank_score, reverse=True)

        # Build Graph-RAG Skeleton Prompt Context
        dsl_lines = [f"# GRAPH-RAG EXTRACTED CONTEXT FOR: '{query}'", f"# Nodes: {len(extracted_subgraph_nodes)} | Edges: {len(extracted_edges)}", ""]
        for node in extracted_subgraph_nodes:
            dsl_lines.append(f"# [{node.kind.upper()}] {node.name} ({node.path}:L{node.line}) [PageRank: {node.pagerank_score:.4f}]")
            if node.docstring:
                dsl_lines.append(f'  """{node.docstring.splitlines()[0]}"""')
            
            # Show graph relations
            callers = [self.nodes[e.source_id].name for e in self.incoming_edges.get(node.symbol_id, []) if e.source_id in self.nodes]
            callees = [self.nodes[e.target_id].name for e in self.outgoing_edges.get(node.symbol_id, []) if e.target_id in self.nodes]
            if callers:
                dsl_lines.append(f"  # callers: {', '.join(callers[:5])}")
            if callees:
                dsl_lines.append(f"  # callees: {', '.join(callees[:5])}")
            dsl_lines.append("")

        return {
            "query": query,
            "seed_symbols": seed_ids,
            "total_nodes": len(extracted_subgraph_nodes),
            "total_edges": len(extracted_edges),
            "graph_rag_context_dsl": "\n".join(dsl_lines),
            "top_nodes": [
                {
                    "name": n.name,
                    "kind": n.kind,
                    "path": n.path,
                    "line": n.line,
                    "pagerank": round(n.pagerank_score, 5),
                }
                for n in extracted_subgraph_nodes[:10]
            ]
        }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scratch/auditors/graph_rag_scip_engine.py /path/to/project [SymbolNameOrQuery]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).expanduser().resolve()
    query = sys.argv[2] if len(sys.argv) > 2 else "audit"

    print(f"🕸️ Building Graph-RAG & SCIP Call Graph for: {project_path.name}...")
    t0 = time.perf_counter()
    engine = GraphRAGEngine(project_path)
    result = engine.query_graph_rag(query, depth=2, top_k=5)
    elapsed = time.perf_counter() - t0

    SEP = "═" * 75
    print(f"\n{SEP}")
    print(f"  🕸️ GRAPH-RAG & SCIP CODEBASE NAVIGATION ENGINE: {project_path.name}")
    print(SEP)
    print(f"  Graph Nodes (AST Symbols)  : {len(engine.nodes):,}")
    print(f"  Query                       : '{query}'")
    print(f"  Sub-Graph Extracted Nodes   : {result['total_nodes']}")
    print(f"  Sub-Graph Extracted Edges   : {result['total_edges']}")
    print(f"  Graph-RAG Slicing Speed     : {elapsed:.3f}s")
    print(SEP)
    print("\n📜 --- GRAPH-RAG CONTEXT PROMPT FOR AI AGENTS ---")
    print(result["graph_rag_context_dsl"][:2000])
    print(f"\n{SEP}\n")


if __name__ == "__main__":
    main()
