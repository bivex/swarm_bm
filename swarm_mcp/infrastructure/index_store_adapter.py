from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Ensure bm25_server_FS_for-AI-asking is importable
_bm25_path = Path(__file__).resolve().parents[2] / "bm25_server_FS_for-AI-asking"
if str(_bm25_path) not in sys.path:
    sys.path.insert(0, str(_bm25_path))

from ramdisk_fs_server.ask import answer_question
from ramdisk_fs_server.indexer import IndexStore

from swarm_mcp.domain.models import (
    DomainAskAnswer,
    DomainSearchResult,
    DomainSkeleton,
    DomainSymbol,
)
from swarm_mcp.domain.ports import IndexPort


class IndexStoreAdapter(IndexPort):
    """Infrastructure Outbound Adapter wrapping BM25 RAM Indexer & AST Symbol Engine."""

    def __init__(self, root: Path | None = None) -> None:
        self.store = IndexStore()
        if root is not None:
            self.rebuild(root)

    def rebuild(self, root: Path) -> dict[str, Any]:
        return self.store.rebuild(root)

    def get_file_skeleton(self, path: str) -> DomainSkeleton:
        dsl_text = self.store.get_skeleton_dsl(path)
        return DomainSkeleton(path=path, dsl_text=dsl_text)

    def get_symbol_contour(self, query: str, limit: int = 10) -> DomainSkeleton:
        dsl_text = self.store.get_contour_skeleton_dsl(query, limit=limit)
        return DomainSkeleton(path=query, dsl_text=dsl_text)

    def search_symbols(self, name: str, kind: str | None = None, limit: int = 20) -> list[DomainSymbol]:
        raw_symbols = self.store.search_symbols(name=name, kind=kind, limit=limit)
        result: list[DomainSymbol] = []
        for sym in raw_symbols:
            result.append(
                DomainSymbol(
                    name=getattr(sym, "name", ""),
                    kind=getattr(sym, "kind", ""),
                    path=getattr(sym, "path", getattr(sym, "file_path", "")),
                    line=getattr(sym, "line", 1),
                    signature=getattr(sym, "signature", ""),
                    calls=list(getattr(sym, "calls", [])),
                    used_by=list(getattr(sym, "used_by", [])),
                )
            )
        return result

    def search_code(self, query: str, content_query: str = "", limit: int = 20) -> list[DomainSearchResult]:
        c_query = content_query or query
        raw_matches = self.store.search_with_scores(query="", content_query=c_query, limit=limit)
        if not raw_matches and query:
            raw_matches = self.store.search_with_scores(query=query, limit=limit)
        results: list[DomainSearchResult] = []
        for model, score in raw_matches:
            path = getattr(model, "path", str(model))
            results.append(DomainSearchResult(path=path, score=float(score)))
        return results

    def ask_question(self, question: str) -> DomainAskAnswer:
        raw_answer = answer_question(question, self.store)
        return DomainAskAnswer(
            question=str(raw_answer.get("question", question)),
            answer=str(raw_answer.get("answer", "")),
            files=list(raw_answer.get("files", [])),
            symbols=list(raw_answer.get("symbols", [])),
        )

    def stats(self) -> dict[str, Any]:
        return self.store.stats()
