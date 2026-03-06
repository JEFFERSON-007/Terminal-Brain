"""
Process monitoring
"""

import psutil
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ProcessStatus(Enum):
    """Process status types"""
    RUNNING = "running"
    SLEEPING = "sleeping"
    STOPPED = "stopped"
    ZOMBIE = "zombie"


@dataclass
class ProcessInfo:
    """Information about a single process"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    num_threads: int


class ProcessMonitor:
    """Monitor running processes"""

    @staticmethod
    def get_top_processes(n: int = 10, sort_by: str = "cpu") -> List[ProcessInfo]:
        """
        Get top N processes

        Args:
            n: Number of processes to return
            sort_by: Sort by 'cpu' or 'memory'

        Returns:
            List of ProcessInfo
        """
        processes = []

        try:
            for proc in psutil.process_iter(["pid", "name", "status", "cpu_percent", "memory_percent"]):
                try:
                    info = proc.info
                    process_info = ProcessInfo(
                        pid=info["pid"],
                        name=info["name"][:30],  # Limit name length
                        status=info["status"],
                        cpu_percent=info.get("cpu_percent", 0) or 0,
                        memory_percent=info.get("memory_percent", 0) or 0,
                        memory_mb=proc.memory_info().rss / (1024**2),
                        num_threads=proc.num_threads(),
                    )
                    processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass

        # Sort by requested metric
        if sort_by == "cpu":
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda p: p.memory_percent, reverse=True)

        return processes[:n]

    @staticmethod
    def get_process_info(pid: int) -> Optional[ProcessInfo]:
        """Get information about a specific process"""
        try:
            proc = psutil.Process(pid)
            return ProcessInfo(
                pid=pid,
                name=proc.name(),
                status=proc.status(),
                cpu_percent=proc.cpu_percent(),
                memory_percent=proc.memory_percent(),
                memory_mb=proc.memory_info().rss / (1024**2),
                num_threads=proc.num_threads(),
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    @staticmethod
    def find_process_by_name(name: str) -> List[ProcessInfo]:
        """Find processes by name"""
        processes = []

        try:
            for proc in psutil.process_iter(["pid", "name"]):
                if name.lower() in proc.info["name"].lower():
                    try:
                        info = proc.info
                        process_info = ProcessInfo(
                            pid=info["pid"],
                            name=info["name"],
                            status=proc.status(),
                            cpu_percent=proc.cpu_percent(),
                            memory_percent=proc.memory_percent(),
                            memory_mb=proc.memory_info().rss / (1024**2),
                            num_threads=proc.num_threads(),
                        )
                        processes.append(process_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        except Exception:
            pass

        return processes

    @staticmethod
    def kill_process(pid: int, force: bool = False) -> bool:
        """Kill a process"""
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    @staticmethod
    def get_process_tree(pid: Optional[int] = None) -> Dict:
        """Get process tree/children"""
        if pid is None:
            pid = psutil.os.getpid()

        try:
            proc = psutil.Process(pid)
            children = []

            for child in proc.children(recursive=True):
                try:
                    children.append(
                        {
                            "pid": child.pid,
                            "name": child.name(),
                            "cpu_percent": child.cpu_percent(),
                            "memory_mb": child.memory_info().rss / (1024**2),
                        }
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return {
                "parent": {
                    "pid": proc.pid,
                    "name": proc.name(),
                    "cpu_percent": proc.cpu_percent(),
                    "memory_mb": proc.memory_info().rss / (1024**2),
                },
                "children": children,
            }
        except psutil.NoSuchProcess:
            return {}
