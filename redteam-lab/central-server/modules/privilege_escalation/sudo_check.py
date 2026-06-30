"""
Module: privilege_escalation.sudo_check
Checks for sudo misconfigurations and SUID binaries.
Safe read-only checks – does not exploit anything.
"""
import subprocess
import os
import stat
import shutil


def run(params: dict) -> dict:
    results = {}

    # 1. Sudo -l (list current user's sudo permissions)
    results["sudo_permissions"] = _sudo_check()

    # 2. SUID binaries
    results["suid_binaries"] = _suid_check()

    # 3. World-writable directories in PATH
    results["writable_path_dirs"] = _writable_path_check()

    # 4. Running services with misconfigs
    results["service_misconfiguration"] = _service_check()

    # Score risk
    risk_score = 0
    if results["suid_binaries"]:
        risk_score += len(results["suid_binaries"]) * 5
    if results["sudo_permissions"].get("all_commands"):
        risk_score += 50
    if results["writable_path_dirs"]:
        risk_score += len(results["writable_path_dirs"]) * 10

    results["risk_score"] = min(risk_score, 100)
    return results


def _sudo_check() -> dict:
    try:
        r = subprocess.run(["sudo", "-l"], capture_output=True, text=True, timeout=10)
        lines = r.stdout.splitlines()
        all_commands = any("ALL" in line for line in lines)
        return {
            "output":       r.stdout.strip(),
            "all_commands": all_commands,
            "nopasswd":     "NOPASSWD" in r.stdout,
        }
    except Exception as e:
        return {"error": str(e)}


def _suid_check() -> list:
    """Find SUID binaries in common locations."""
    suid_bins = []
    search_paths = ["/usr/bin", "/usr/sbin", "/bin", "/sbin", "/usr/local/bin"]
    known_safe = {"sudo", "passwd", "su", "ping", "mount", "umount"}

    for path in search_paths:
        if not os.path.isdir(path):
            continue
        try:
            for fname in os.listdir(path):
                fpath = os.path.join(path, fname)
                try:
                    st = os.stat(fpath)
                    if st.st_mode & stat.S_ISUID:
                        if fname not in known_safe:
                            suid_bins.append(fpath)
                except PermissionError:
                    pass
        except Exception:
            pass
    return suid_bins


def _writable_path_check() -> list:
    """Check for world-writable dirs in $PATH."""
    path_dirs = os.environ.get("PATH", "").split(":")
    writable = []
    for d in path_dirs:
        if not os.path.isdir(d):
            continue
        try:
            st = os.stat(d)
            if st.st_mode & stat.S_IWOTH:
                writable.append(d)
        except Exception:
            pass
    return writable


def _service_check() -> list:
    """Look for services running as root with writable config files."""
    misconfigs = []
    if not shutil.which("systemctl"):
        return misconfigs
    try:
        r = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager", "--plain"],
            capture_output=True, text=True, timeout=15
        )
        for line in r.stdout.splitlines()[1:]:
            parts = line.split()
            if parts:
                unit = parts[0]
                # Check if unit file is world-writable
                unit_path = f"/etc/systemd/system/{unit}"
                if os.path.exists(unit_path):
                    st = os.stat(unit_path)
                    if st.st_mode & stat.S_IWOTH:
                        misconfigs.append({"unit": unit, "issue": "world-writable unit file"})
    except Exception:
        pass
    return misconfigs
