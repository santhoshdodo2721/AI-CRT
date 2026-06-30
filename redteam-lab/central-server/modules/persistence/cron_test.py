"""
Module: persistence.cron_test
Simulates cron-based persistence. Creates a harmless cron entry,
checks detection, then removes it. Net-zero impact.
MITRE: T1053.003 – Scheduled Task/Job: Cron
"""
import subprocess
import time
import shutil


TEST_COMMENT   = "# REDTEAM-LAB-PERSISTENCE-TEST"
TEST_CRON_LINE = f"@reboot echo redteam-lab-test > /tmp/redteam_cron_test.txt {TEST_COMMENT}"


def run(params: dict) -> dict:
    results = {}

    # 1. Read current crontab
    results["original_crontab"] = _get_crontab()

    # 2. Add test entry
    add_ok, add_err = _add_cron_entry()
    results["add_result"] = {"ok": add_ok, "error": add_err}

    if add_ok:
        time.sleep(1)
        results["crontab_after_add"] = _get_crontab()

        # 3. Check if SIEM/monitoring would detect (look for auditd logs)
        results["detection_check"] = _check_detection()

        # 4. Remove test entry
        remove_ok, remove_err = _remove_cron_entry()
        results["remove_result"] = {"ok": remove_ok, "error": remove_err}
        results["crontab_after_remove"] = _get_crontab()

    results["summary"] = (
        "Persistence simulation complete. Cron entry added and removed. "
        "Check detection_check for SIEM/auditd detection status."
    )
    return results


def _get_crontab() -> str:
    try:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        return r.stdout
    except Exception as e:
        return f"Error: {e}"


def _add_cron_entry() -> tuple:
    if not shutil.which("crontab"):
        return False, "crontab not available"
    try:
        current = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
        new_crontab = current + "\n" + TEST_CRON_LINE + "\n"
        proc = subprocess.run(["crontab", "-"], input=new_crontab, capture_output=True, text=True)
        if proc.returncode == 0:
            return True, None
        return False, proc.stderr
    except Exception as e:
        return False, str(e)


def _remove_cron_entry() -> tuple:
    try:
        current = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
        lines   = [l for l in current.splitlines() if TEST_COMMENT not in l and TEST_CRON_LINE not in l]
        new_crontab = "\n".join(lines) + "\n"
        proc = subprocess.run(["crontab", "-"], input=new_crontab, capture_output=True, text=True)
        return proc.returncode == 0, proc.stderr
    except Exception as e:
        return False, str(e)


def _check_detection() -> dict:
    """Check if auditd logged crontab modification."""
    detection = {"auditd": False, "syslog": False}

    if shutil.which("ausearch"):
        r = subprocess.run(
            ["ausearch", "-k", "cron", "--start", "today"],
            capture_output=True, text=True, timeout=10
        )
        detection["auditd"] = bool(r.stdout.strip())

    try:
        with open("/var/log/syslog") as f:
            content = f.read()
        detection["syslog"] = "crontab" in content.lower()
    except Exception:
        pass

    return detection
