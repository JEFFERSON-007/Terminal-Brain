"""
Network monitoring and speed testing
"""

import subprocess
from typing import Dict, Optional
from dataclasses import dataclass
import time


@dataclass
class NetworkMetrics:
    """Network metrics data"""
    download_mbps: float
    upload_mbps: float
    latency_ms: float
    connected: bool


class NetworkMonitor:
    """Monitor network connectivity and speed"""

    @staticmethod
    def check_connectivity() -> bool:
        """Check if connected to internet"""
        try:
            # Ping Google DNS
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                capture_output=True,
                timeout=3,
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def get_latency() -> Optional[float]:
        """Get latency to a reliable server in ms"""
        try:
            start = time.time()
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", "8.8.8.8"],
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode == 0:
                # Parse latency from output
                for line in result.stdout.split("\n"):
                    if "time=" in line:
                        time_str = line.split("time=")[1].split()[0]
                        return float(time_str)

            return None
        except Exception:
            return None

    @staticmethod
    def measure_speed() -> Optional[Dict[str, float]]:
        """
        Measure internet speed using speedtest-cli

        Returns:
            Dictionary with download, upload, and latency speeds
        """
        try:
            import speedtest

            st = speedtest.Speedtest()

            # Get servers
            st.get_servers()

            # Get best server
            best_server = st.get_best_server()

            # Measure download and upload
            download = st.download() / 1_000_000  # Convert to Mbps
            upload = st.upload() / 1_000_000  # Convert to Mbps
            latency = best_server.get("latency", 0)

            return {
                "download_mbps": round(download, 2),
                "upload_mbps": round(upload, 2),
                "latency_ms": round(latency, 2),
            }
        except Exception:
            return None

    @staticmethod
    def get_wifi_signal_strength() -> Optional[int]:
        """
        Get WiFi signal strength as percentage

        Returns:
            Signal strength 0-100, or None if not on WiFi
        """
        try:
            # Try Linux approach
            result = subprocess.run(
                ["grep", "ESSID", "/proc/net/wireless"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # On Linux with WiFi
                result = subprocess.run(
                    ["nmcli", "device", "wifi", "list"],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    # Parse signal strength from output
                    lines = result.stdout.split("\n")
                    for line in lines:
                        if "*" in line:  # Current connection
                            parts = line.split()
                            for part in parts:
                                if "dBm" in part or part.isdigit():
                                    try:
                                        signal = int(part.replace("dBm", ""))
                                        # Convert dBm to percentage
                                        # Range typically -30 (strong) to -90 (weak)
                                        percentage = min(
                                            100, max(0, 2 * (signal + 100))
                                        )
                                        return percentage
                                    except ValueError:
                                        pass

            return None
        except Exception:
            return None

    @staticmethod
    def get_network_metrics() -> Dict:
        """Get all network metrics"""
        return {
            "connected": NetworkMonitor.check_connectivity(),
            "latency_ms": NetworkMonitor.get_latency(),
            "wifi_signal": NetworkMonitor.get_wifi_signal_strength(),
        }
