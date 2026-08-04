from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class WorkerState(Enum):
    INITIALIZED = auto()
    RUNNING = auto()
    FROZEN = auto()
    TRIMMED = auto()
    TERMINATED = auto()


@dataclass(frozen=True)
class ResourceBudget:
    """Value Object defining execution resource boundaries for a Swarm Agent."""
    max_memory_mb: int = 512
    cpu_rate_cap: int = 100
    max_iops: int = 1000
    max_net_bandwidth_mbps: int = 100
    sandbox_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_memory_mb": self.max_memory_mb,
            "cpu_rate_cap": self.cpu_rate_cap,
            "max_iops": self.max_iops,
            "max_net_bandwidth_mbps": self.max_net_bandwidth_mbps,
            "sandbox_enabled": self.sandbox_enabled,
        }


@dataclass(frozen=True)
class DomainSymbol:
    """Value Object representing an extracted code symbol across languages."""
    name: str
    kind: str
    path: str
    line: int
    signature: str = ""
    calls: list[str] = field(default_factory=list)
    used_by: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DomainSkeleton:
    """Value Object representing Skeleton DSL / Contour of a codebase file."""
    path: str
    dsl_text: str


@dataclass(frozen=True)
class DomainSearchResult:
    """Value Object representing ranked BM25 search match."""
    path: str
    score: float
    matches: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DomainAskAnswer:
    """Value Object for AI codebase architectural answers."""
    question: str
    answer: str
    files: list[str] = field(default_factory=list)
    symbols: list[str] = field(default_factory=list)


@dataclass
class SwarmWorker:
    """Aggregate Root Entity representing a managed Swarm Worker Process bound to AgentJobEngine."""
    worker_id: str
    pid: int
    session_handle: Any
    budget: ResourceBudget
    state: WorkerState = WorkerState.RUNNING
    current_memory_mb: float = 0.0

    def mark_frozen(self) -> None:
        self.state = WorkerState.FROZEN

    def mark_thawed(self) -> None:
        self.state = WorkerState.RUNNING

    def mark_trimmed(self) -> None:
        self.state = WorkerState.TRIMMED

    def mark_terminated(self) -> None:
        self.state = WorkerState.TERMINATED

    def to_dict(self) -> dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "pid": self.pid,
            "state": self.state.name,
            "budget": self.budget.to_dict(),
            "current_memory_mb": self.current_memory_mb,
        }
