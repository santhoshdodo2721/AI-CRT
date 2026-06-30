"""
Module: lateral_movement.ssh_check
Checks SSH reachability and configuration weaknesses.
Does NOT attempt brute force. Read-only config checks.
MITRE: T1021.004 - Remote Services: SSH
"""
import socket
import subprocess
import shutil


def run(params: dict) -> dict:
    target  = params.get("target", "")
    network = params.get("network", "")
    results = {"findings": [], "hosts_with_ssh": []}

    # Single target or scan a list
    targets = []
    if target:
        targets = [target] if isinstance(target, str) else target
    elif network:
        targets = _hosts_from_network(network)

    for host in targets[:50]:   # cap at 50 hosts
        if _port_open(host, 22):
            ssh_info = _check_ssh(host)
            results["hosts_with_ssh"].append(host)
            results["findings"].extend(ssh_info)

    # Local SSH config check
    results["local_ssh_config"] = _check_local_config()
    results["authorized_keys"]  = _check_authorized_keys()

    return results


def _port_open(host: str, port: int = 22) -> bool:
    try:
        s = socket.create_connection((host, port), timeout=3)
        s.close()
        return True
    except Exception:
        return False


def _check_ssh(host: str) -> list:
    findings = []
    if not shutil.which("ssh"):
        return [{"host": host, "issue": "ssh client not installed"}]

    # Banner grab to get version
    try:
        s = socket.create_connection((host, 22), timeout=5)
        banner = s.recv(256).decode(errors="ignore").strip()
        s.close()
        findings.append({
            "host":     host,
            "banner":   banner,
            "severity": "info",
        })
        # Old SSH versions
        if "SSH-2.0-OpenSSH_6" in banner or "SSH-2.0-OpenSSH_5" in banner:
            findings.append({
                "host":     host,
                "issue":    f"Outdated SSH version: {banner}",
                "severity": "high",
                "mitre":    "T1021.004",
            })
    except Exception as e:
        findings.append({"host": host, "error": str(e)})

    # Check weak algorithms via ssh -vvv (no connection, just negotiation info)
    try:
        r = subprocess.run(
            ["ssh", "-vvv", "-o", "StrictHostKeyChecking=no",
             "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", host],
            capture_output=True, text=True, timeout=10
        )
        stderr = r.stderr
        if "diffie-hellman-group1" in stderr or "diffie-hellman-group14" in stderr:
            findings.append({
                "host":     host,
                "issue":    "Weak Diffie-Hellman key exchange accepted",
                "severity": "medium",
                "mitre":    "T1021.004",
            })
        if "arcfour" in stderr or "3des" in stderr:
            findings.append({
                "host":     host,
                "issue":    "Weak cipher (arcfour/3des) supported",
                "severity": "medium",
                "mitre":    "T1021.004",
            })
    except Exception:
        pass

    return findings


def _check_local_config() -> dict:
    """Check local SSH daemon config for misconfigurations."""
    config_paths = ["/etc/ssh/sshd_config", "/etc/openssh/sshd_config"]
    issues = []

    for path in config_paths:
        try:
            with open(path) as f:
                content = f.read()
            lines = {
                line.split()[0].lower(): line.split()[1]
                for line in content.splitlines()
                if line.strip() and not line.startswith("#") and len(line.split()) >= 2
            }

            if lines.get("permitrootlogin", "").lower() in ("yes", "without-password"):
                issues.append({"issue": "PermitRootLogin enabled", "severity": "high"})
            if lines.get("passwordauthentication", "yes").lower() == "yes":
                issues.append({"issue": "Password authentication enabled (prefer keys)", "severity": "medium"})
            if lines.get("permitemptypasswords", "no").lower() == "yes":
                issues.append({"issue": "Empty passwords allowed", "severity": "critical"})
            if lines.get("x11forwarding", "no").lower() == "yes":
                issues.append({"issue": "X11 forwarding enabled", "severity": "low"})

            return {"config_file": path, "issues": issues}
        except PermissionError:
            return {"config_file": path, "error": "Permission denied (need root to read sshd_config)"}
        except FileNotFoundError:
            continue

    return {"config_file": None, "error": "sshd_config not found"}


def _check_authorized_keys() -> list:
    """Find authorized_keys files that may allow lateral movement."""
    import os
    import glob
    found = []
    patterns = [
        "/home/*/.ssh/authorized_keys",
        "/root/.ssh/authorized_keys",
    ]
    for pattern in patterns:
        for path in glob.glob(pattern):
            try:
                with open(path) as f:
                    keys = [l.strip() for l in f if l.strip() and not l.startswith("#")]
                found.append({"path": path, "key_count": len(keys)})
            except PermissionError:
                found.append({"path": path, "error": "permission denied"})
    return found


def _hosts_from_network(network: str) -> list:
    import ipaddress
    try:
        return [str(h) for h in ipaddress.ip_network(network, strict=False).hosts()]
    except Exception:
        return []
