"""
Module: defense_evasion.encoded_command_test
Tests if encoded/obfuscated commands are detected by local security tools.
Simulates T1027 - Obfuscated Files or Information.
Safe - uses harmless payloads only.
"""
import subprocess
import base64
import os
import shutil
import time


HARMLESS_COMMAND = "echo redteam-lab-evasion-test"


def run(params: dict) -> dict:
    results = {
        "tests":     [],
        "detected":  [],
        "evaded":    [],
        "note":      "All payloads are harmless. Tests detection capability only.",
    }

    # Test 1: Base64 encoded command
    results["tests"].append(_test_base64_encoding())

    # Test 2: Hex encoded command
    results["tests"].append(_test_hex_encoding())

    # Test 3: Environment variable substitution
    results["tests"].append(_test_env_substitution())

    # Test 4: Command in /tmp (watch for file-based detection)
    results["tests"].append(_test_tmp_script())

    # Test 5: Check if auditd/syslog captured any of it
    time.sleep(1)
    results["detection_check"] = _check_logs()

    for t in results["tests"]:
        if t.get("detected"):
            results["detected"].append(t["name"])
        else:
            results["evaded"].append(t["name"])

    results["summary"] = (
        f"{len(results['detected'])}/{len(results['tests'])} techniques detected. "
        f"{'Good detection coverage.' if results['detected'] else 'No detection - review SIEM/EDR rules.'}"
    )
    return results


def _test_base64_encoding() -> dict:
    """Run a base64-encoded harmless command."""
    encoded = base64.b64encode(HARMLESS_COMMAND.encode()).decode()
    cmd = f"echo {encoded} | base64 -d | sh"
    try:
        r = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True, timeout=10)
        return {
            "name":     "base64_encoded_command",
            "command":  cmd,
            "output":   r.stdout.strip(),
            "success":  r.returncode == 0,
            "detected": False,   # would need EDR integration to know
            "mitre":    "T1027",
        }
    except Exception as e:
        return {"name": "base64_encoded_command", "error": str(e)}


def _test_hex_encoding() -> dict:
    """Hex-encode a command string."""
    hex_cmd = HARMLESS_COMMAND.encode().hex()
    cmd = f"echo {hex_cmd} | xxd -r -p | sh"
    if not shutil.which("xxd"):
        return {"name": "hex_encoded_command", "skipped": "xxd not installed"}
    try:
        r = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True, timeout=10)
        return {
            "name":     "hex_encoded_command",
            "command":  cmd,
            "output":   r.stdout.strip(),
            "success":  r.returncode == 0,
            "detected": False,
            "mitre":    "T1027",
        }
    except Exception as e:
        return {"name": "hex_encoded_command", "error": str(e)}


def _test_env_substitution() -> dict:
    """Use env var substitution to hide command."""
    env = os.environ.copy()
    env["_RT_CMD"] = HARMLESS_COMMAND
    try:
        r = subprocess.run(["sh", "-c", "$_RT_CMD"], env=env, capture_output=True, text=True, timeout=10)
        return {
            "name":     "env_var_substitution",
            "technique": "Command hidden in environment variable",
            "output":   r.stdout.strip(),
            "success":  r.returncode == 0,
            "detected": False,
            "mitre":    "T1027",
        }
    except Exception as e:
        return {"name": "env_var_substitution", "error": str(e)}


def _test_tmp_script() -> dict:
    """Write harmless script to /tmp and execute it."""
    script_path = "/tmp/.rt_evasion_test.sh"
    try:
        with open(script_path, "w") as f:
            f.write(f"#!/bin/sh\n{HARMLESS_COMMAND}\n")
        os.chmod(script_path, 0o700)
        r = subprocess.run([script_path], capture_output=True, text=True, timeout=10)
        os.remove(script_path)   # cleanup
        return {
            "name":     "tmp_script_execution",
            "path":     script_path,
            "output":   r.stdout.strip(),
            "success":  r.returncode == 0,
            "detected": False,
            "cleaned":  True,
            "mitre":    "T1027",
        }
    except Exception as e:
        try:
            os.remove(script_path)
        except Exception:
            pass
        return {"name": "tmp_script_execution", "error": str(e)}


def _check_logs() -> dict:
    """Check if any of the above triggered alerts in syslog/auditd."""
    detection = {"auditd": False, "syslog": False, "journald": False}

    if shutil.which("ausearch"):
        try:
            r = subprocess.run(
                ["ausearch", "-k", "exec", "--start", "today", "-i"],
                capture_output=True, text=True, timeout=10
            )
            detection["auditd"] = "redteam" in r.stdout or "base64" in r.stdout
        except Exception:
            pass

    if shutil.which("journalctl"):
        try:
            r = subprocess.run(
                ["journalctl", "-n", "50", "--since", "1 minute ago"],
                capture_output=True, text=True, timeout=10
            )
            detection["journald"] = "redteam" in r.stdout
        except Exception:
            pass

    return detection
