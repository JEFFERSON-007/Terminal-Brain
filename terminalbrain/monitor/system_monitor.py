"""
System resource monitoring (CPU, RAM, Disk, Battery)
"""

import psutil
import os
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class SystemMetrics:
    """System metrics data"""
    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    battery_percent: Optional[float]
    battery_charging: Optional[bool]
    uptime_seconds: int


class SystemMonitor:
    """Monitor system resources"""

    @staticmethod
    def get_cpu_percent() -> float:
        """Get CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0

    @staticmethod
    def get_ram_info() -> Dict[str, float]:
        """Get RAM usage information"""
        try:
            ram = psutil.virtual_memory()
            return {
                "percent": ram.percent,
                "used_gb": ram.used / (1024**3),
                "total_gb": ram.total / (1024**3),
                "available_gb": ram.available / (1024**3),
            }
        except Exception:
            return {"percent": 0, "used_gb": 0, "total_gb": 0, "available_gb": 0}

    @staticmethod
    def get_disk_info(path: str = "/") -> Dict[str, float]:
        """Get disk usage information"""
        try:
            disk = psutil.disk_usage(path)
            return {
                "percent": disk.percent,
                "used_gb": disk.used / (1024**3),
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
            }
        except Exception:
            return {"percent": 0, "used_gb": 0, "total_gb": 0, "free_gb": 0}

    @staticmethod
    def get_battery_info() -> Dict[str, Optional[float | bool]]:
        """Get battery information"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "charging": battery.power_plugged,
                    "remaining_seconds": battery.secsleft,
                }
            else:
                return {"percent": None, "charging": None, "remaining_seconds": None}
        except Exception:
            return {"percent": None, "charging": None, "remaining_seconds": None}

    @staticmethod
    def get_uptime() -> int:
        """Get system uptime in seconds"""
        try:
            return int(psutil.boot_time())
        except Exception:
            return 0

    @staticmethod
    def get_metrics() -> SystemMetrics:
        """Get all system metrics"""
        cpu = SystemMonitor.get_cpu_percent()
        ram = SystemMonitor.get_ram_info()
        disk = SystemMonitor.get_disk_info()
        battery = SystemMonitor.get_battery_info()
        uptime = SystemMonitor.get_uptime()

        return SystemMetrics(
            cpu_percent=cpu,
            ram_percent=ram.get("percent", 0),
            ram_used_gb=ram.get("used_gb", 0),
            ram_total_gb=ram.get("total_gb", 0),
            disk_percent=disk.get("percent", 0),
            disk_used_gb=disk.get("used_gb", 0),
            disk_total_gb=disk.get("total_gb", 0),
            battery_percent=battery.get("percent"),
            battery_charging=battery.get("charging"),
            uptime_seconds=uptime,
        )

    @staticmethod
    def get_metrics_dict() -> Dict:
        """Get metrics as dictionary"""
        metrics = SystemMonitor.get_metrics()
        return {
            "cpu": metrics.cpu_percent,
            "ram": {
                "percent": metrics.ram_percent,
                "used_gb": round(metrics.ram_used_gb, 2),
                "total_gb": round(metrics.ram_total_gb, 2),
            },
            "disk": {
                "percent": metrics.disk_percent,
                "used_gb": round(metrics.disk_used_gb, 2),
                "total_gb": round(metrics.disk_total_gb, 2),
            },
            "battery": {
                "percent": metrics.battery_percent,
                "charging": metrics.battery_charging,
            },
            "uptime": metrics.uptime_seconds,
        }
