from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .models import (
    DomainAskAnswer,
    DomainSearchResult,
    DomainSkeleton,
    DomainSymbol,
    ResourceBudget,
    SwarmWorker,
)


class IndexPort(ABC):
    """Abstract Outbound Port Interface for Codebase BM25 Search & Symbol Indexing."""

    @abstractmethod
    def rebuild(self, root: Path) -> dict[str, Any]:
        """Rebuild in-memory BM25 search index and AST symbol graph."""
        ...

    @abstractmethod
    def get_file_skeleton(self, path: str) -> DomainSkeleton:
        """Extract Skeleton DSL for a specified file path."""
        ...

    @abstractmethod
    def get_symbol_contour(self, query: str, limit: int = 10) -> DomainSkeleton:
        """Extract Skeleton DSL contour matching a symbol query."""
        ...

    @abstractmethod
    def search_symbols(self, name: str, kind: str | None = None, limit: int = 20) -> list[DomainSymbol]:
        """Search AST symbols across Python, C/C++, JS/TS, Go, Rust."""
        ...

    @abstractmethod
    def search_code(self, query: str, content_query: str = "", limit: int = 20) -> list[DomainSearchResult]:
        """Ranked BM25 search across files and content."""
        ...

    @abstractmethod
    def ask_question(self, question: str) -> DomainAskAnswer:
        """Ask natural language question over codebase architecture."""
        ...

    @abstractmethod
    def stats(self) -> dict[str, Any]:
        """Get index statistics."""
        ...


class JobEnginePort(ABC):
    """Abstract Outbound Port Interface for AgentJobEngine OS Resource Controller."""

    @abstractmethod
    def spawn_worker(self, worker_id: str, command: list[str], budget: ResourceBudget) -> SwarmWorker:
        """Spawn a managed background Swarm Worker bound to AgentJobEngine limits."""
        ...

    @abstractmethod
    def freeze_worker(self, worker_id: str) -> bool:
        """Freeze Swarm Worker process tree (SIGSTOP / Win32 Freeze)."""
        ...

    @abstractmethod
    def thaw_worker(self, worker_id: str) -> bool:
        """Thaw Swarm Worker process tree (SIGCONT / Win32 Thaw)."""
        ...

    @abstractmethod
    def compress_memory(self, worker_id: str | None = None) -> dict[str, Any]:
        """Trim & compress Working Set of idle LLM reasoning workers."""
        ...

    @abstractmethod
    def terminate_worker(self, worker_id: str) -> bool:
        """Terminate worker process and clean up session."""
        ...

    @abstractmethod
    def get_worker(self, worker_id: str) -> SwarmWorker | None:
        """Retrieve worker state by ID."""
        ...

    @abstractmethod
    def list_workers(self) -> list[SwarmWorker]:
        """List all active Swarm Workers."""
        ...
