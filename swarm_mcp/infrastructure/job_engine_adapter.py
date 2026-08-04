from __future__ import annotations

import ctypes
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

from swarm_mcp.domain.models import ResourceBudget, SwarmWorker, WorkerState
from swarm_mcp.domain.ports import JobEnginePort


class JobEngineAdapter(JobEnginePort):
    """Infrastructure Outbound Adapter connecting to C++ AgentJobEngine shared library."""

    def __init__(self) -> None:
        self.workers: dict[str, SwarmWorker] = {}
        self.lib = self._load_agent_job_engine_lib()

    def _load_agent_job_engine_lib(self) -> ctypes.CDLL | None:
        """Find and load libAgentJobEngineC shared library."""
        root = Path(__file__).resolve().parents[2] / "JobObjects_RD" / "out" / "build" / "lib"
        possible_names = [
            "libAgentJobEngineC.dylib",
            "libAgentJobEngineC.so",
            "AgentJobEngineC.dll",
        ]
        for name in possible_names:
            lib_path = root / name
            if lib_path.exists():
                try:
                    lib = ctypes.CDLL(str(lib_path))
                    # Setup C signatures
                    lib.AgentEngine_CreateSession.argtypes = [
                        ctypes.c_char_p,
                        ctypes.c_uint64,
                        ctypes.c_uint32,
                        ctypes.c_bool,
                    ]
                    lib.AgentEngine_CreateSession.restype = ctypes.c_void_p

                    lib.AgentEngine_DestroySession.argtypes = [ctypes.c_void_p]
                    lib.AgentEngine_DestroySession.restype = None

                    lib.AgentEngine_AssignProcess.argtypes = [ctypes.c_void_p, ctypes.c_int32]
                    lib.AgentEngine_AssignProcess.restype = ctypes.c_bool

                    lib.AgentEngine_TrimWorkingSet.argtypes = [ctypes.c_void_p]
                    lib.AgentEngine_TrimWorkingSet.restype = ctypes.c_bool

                    lib.AgentEngine_FreezeJobTree.argtypes = [ctypes.c_void_p]
                    lib.AgentEngine_FreezeJobTree.restype = ctypes.c_bool

                    lib.AgentEngine_ThawJobTree.argtypes = [ctypes.c_void_p]
                    lib.AgentEngine_ThawJobTree.restype = ctypes.c_bool

                    lib.AgentEngine_SetIoRateLimit.argtypes = [
                        ctypes.c_void_p,
                        ctypes.c_char_p,
                        ctypes.c_uint64,
                        ctypes.c_uint64,
                    ]
                    lib.AgentEngine_SetIoRateLimit.restype = ctypes.c_bool

                    lib.AgentEngine_SetNetworkRateLimit.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
                    lib.AgentEngine_SetNetworkRateLimit.restype = ctypes.c_bool

                    lib.AgentEngine_CreateSiloSandbox.argtypes = [ctypes.c_void_p]
                    lib.AgentEngine_CreateSiloSandbox.restype = ctypes.c_bool

                    return lib
                except Exception:
                    pass
        return None

    def spawn_worker(self, worker_id: str, command: list[str], budget: ResourceBudget) -> SwarmWorker:
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if hasattr(os, "setsid") else None,
        )

        session_handle = None
        if self.lib:
            session_handle = self.lib.AgentEngine_CreateSession(
                worker_id.encode("utf-8"),
                budget.max_memory_mb * 1024 * 1024,
                budget.cpu_rate_cap,
                True,
            )
            if session_handle:
                self.lib.AgentEngine_AssignProcess(session_handle, proc.pid)
                if budget.sandbox_enabled:
                    self.lib.AgentEngine_CreateSiloSandbox(session_handle)
                self.lib.AgentEngine_SetIoRateLimit(
                    session_handle, b"/", budget.max_iops, budget.max_iops * 4096
                )
                self.lib.AgentEngine_SetNetworkRateLimit(
                    session_handle, budget.max_net_bandwidth_mbps * 1000 * 1000
                )

        worker = SwarmWorker(
            worker_id=worker_id,
            pid=proc.pid,
            session_handle=session_handle,
            budget=budget,
            state=WorkerState.RUNNING,
            current_memory_mb=0.0,
        )
        self.workers[worker_id] = worker
        return worker

    def freeze_worker(self, worker_id: str) -> bool:
        worker = self.workers.get(worker_id)
        if not worker:
            return False

        if self.lib and worker.session_handle:
            res = self.lib.AgentEngine_FreezeJobTree(worker.session_handle)
            if res:
                worker.mark_frozen()
                return True

        # Fallback POSIX signal
        try:
            os.kill(worker.pid, signal.SIGSTOP)
            worker.mark_frozen()
            return True
        except Exception:
            return False

    def thaw_worker(self, worker_id: str) -> bool:
        worker = self.workers.get(worker_id)
        if not worker:
            return False

        if self.lib and worker.session_handle:
            res = self.lib.AgentEngine_ThawJobTree(worker.session_handle)
            if res:
                worker.mark_thawed()
                return True

        # Fallback POSIX signal
        try:
            os.kill(worker.pid, signal.SIGCONT)
            worker.mark_thawed()
            return True
        except Exception:
            return False

    def compress_memory(self, worker_id: str | None = None) -> dict[str, Any]:
        targets = [self.workers[worker_id]] if worker_id and worker_id in self.workers else list(self.workers.values())
        trimmed_count = 0
        for worker in targets:
            if self.lib and worker.session_handle:
                res = self.lib.AgentEngine_TrimWorkingSet(worker.session_handle)
                if res:
                    worker.mark_trimmed()
                    trimmed_count += 1

        return {"status": "success", "workers_trimmed": trimmed_count}

    def terminate_worker(self, worker_id: str) -> bool:
        worker = self.workers.get(worker_id)
        if not worker:
            return False

        if self.lib and worker.session_handle:
            self.lib.AgentEngine_DestroySession(worker.session_handle)

        try:
            os.kill(worker.pid, signal.SIGKILL)
        except Exception:
            pass

        worker.mark_terminated()
        del self.workers[worker_id]
        return True

    def get_worker(self, worker_id: str) -> SwarmWorker | None:
        return self.workers.get(worker_id)

    def list_workers(self) -> list[SwarmWorker]:
        return list(self.workers.values())
