import platform
import socket
import psutil
import subprocess

def get_system_inventory() -> dict:
    """Collects system information and tool availability."""
    
    # Check what tools are installed
    tools_available = []
    common_tools = ["nmap", "nuclei", "netexec", "impacket-psexec", "sqlmap", "nikto"]
    for tool in common_tools:
        try:
            subprocess.run([tool, "-h"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            tools_available.append(tool)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
            
    # IP Address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_addr = s.getsockname()[0]
    except Exception:
        ip_addr = "127.0.0.1"

    return {
        "os_info": platform.platform(),
        "hostname": socket.gethostname(),
        "ip_address": ip_addr,
        "cpu_cores": psutil.cpu_count(),
        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "tools_available": tools_available
    }
