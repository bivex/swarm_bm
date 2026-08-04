from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FastDeconstructRequest:
    root_path: str
    query: str = ""


@dataclass(frozen=True)
class FastDeconstructResponse:
    root_path: str
    stats: dict[str, Any]
    contour: str
    top_files: list[str]
    symbol_count: int


@dataclass(frozen=True)
class SearchCodebaseRequest:
    query: str
    content_query: str = ""
    limit: int = 20


@dataclass(frozen=True)
class SpawnWorkerRequest:
    worker_id: str
    command: list[str]
    max_memory_mb: int = 512
    cpu_rate_cap: int = 100
    max_iops: int = 1000
    max_net_bandwidth_mbps: int = 100
    sandbox_enabled: bool = True


@dataclass(frozen=True)
class SpawnWorkerResponse:
    worker_id: str
    pid: int
    state: str
    budget: dict[str, Any]


@dataclass(frozen=True)
class WorkerControlRequest:
    worker_id: str
    action: str  # freeze, thaw, compress, terminate


@dataclass(frozen=True)
class WorkerControlResponse:
    worker_id: str
    action: str
    success: bool
