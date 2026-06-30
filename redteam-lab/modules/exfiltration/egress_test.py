"""
Module: exfiltration.egress_test
Tests whether data can leave the network via common channels.
Uses ONLY dummy/synthetic data – never real sensitive data.
Checks firewall/DLP effectiveness.
"""
import socket
import requests
import tempfile
import os


DUMMY_CONTENT = "REDTEAM-LAB-DUMMY-EXFIL-TEST-NOT-REAL-DATA-12345"
EGRESS_TARGETS = [
    {"host": "ifconfig.me",    "port": 80,  "proto": "http"},
    {"host": "ifconfig.me",    "port": 443, "proto": "https"},
    {"host": "1.1.1.1",        "port": 53,  "proto": "dns"},
    {"host": "github.com",     "port": 443, "proto": "https"},
    {"host": "portquiz.net",   "port": 8080, "proto": "http"},
]


def run(params: dict) -> dict:
    results     = []
    blocked     = []
    allowed     = []

    for target in EGRESS_TARGETS:
        result = _test_egress(target)
        results.append(result)
        if result["reachable"]:
            allowed.append(f"{target['proto']}://{target['host']}:{target['port']}")
        else:
            blocked.append(f"{target['proto']}://{target['host']}:{target['port']}")

    # HTTP POST test (simulate data upload)
    post_result = _test_http_post()
    results.append(post_result)

    return {
        "note":         "All tests use dummy synthetic data only.",
        "results":      results,
        "allowed_paths": allowed,
        "blocked_paths": blocked,
        "dlp_effective": len(allowed) == 0,
        "recommendation": (
            "DLP/firewall appears effective." if len(allowed) == 0
            else f"{len(allowed)} egress paths open – review firewall rules."
        ),
    }


def _test_egress(target: dict) -> dict:
    host = target["host"]
    port = target["port"]
    try:
        s = socket.create_connection((host, port), timeout=5)
        s.close()
        return {"host": host, "port": port, "proto": target["proto"], "reachable": True}
    except Exception as e:
        return {"host": host, "port": port, "proto": target["proto"], "reachable": False, "reason": str(e)}


def _test_http_post() -> dict:
    """Attempt to POST dummy content to a public endpoint."""
    try:
        r = requests.post(
            "https://httpbin.org/post",
            data={"test": DUMMY_CONTENT},
            timeout=10,
        )
        return {
            "test":      "http_post_to_external",
            "reachable": r.status_code == 200,
            "note":      "Dummy data only",
        }
    except Exception as e:
        return {
            "test":      "http_post_to_external",
            "reachable": False,
            "reason":    str(e),
        }
