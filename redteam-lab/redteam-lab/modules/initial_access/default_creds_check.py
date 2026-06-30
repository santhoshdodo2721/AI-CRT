"""
Module: initial_access.default_creds_check
Checks common services for default/weak credentials.
Safe - only tests auth, never exploits further.
MITRE: T1078 - Valid Accounts
"""
import socket
import subprocess
import shutil


DEFAULT_CREDS = [
    ("admin",    "admin"),
    ("admin",    "password"),
    ("admin",    ""),
    ("root",     "root"),
    ("root",     "toor"),
    ("root",     ""),
    ("admin",    "1234"),
    ("user",     "user"),
    ("test",     "test"),
    ("guest",    "guest"),
    ("operator", "operator"),
]

SERVICES = {
    21:   "ftp",
    22:   "ssh",
    23:   "telnet",
    80:   "http",
    443:  "https",
    3306: "mysql",
    5432: "postgres",
    6379: "redis",
    27017: "mongodb",
}


def run(params: dict) -> dict:
    target = params.get("target", "127.0.0.1")
    results = {"target": target, "vulnerable_services": [], "checked": []}

    for port, service in SERVICES.items():
        if not _port_open(target, port):
            continue

        results["checked"].append(f"{service}:{port}")

        if service == "redis":
            vuln = _check_redis(target, port)
            if vuln:
                results["vulnerable_services"].append(vuln)

        elif service == "ftp":
            vuln = _check_ftp(target, port)
            if vuln:
                results["vulnerable_services"].append(vuln)

        elif service in ("http", "https"):
            vulns = _check_http_defaults(target, port, service)
            results["vulnerable_services"].extend(vulns)

    results["total_vulnerable"] = len(results["vulnerable_services"])
    results["risk"] = "high" if results["total_vulnerable"] > 0 else "low"
    return results


def _port_open(host: str, port: int) -> bool:
    try:
        s = socket.create_connection((host, port), timeout=3)
        s.close()
        return True
    except Exception:
        return False


def _check_redis(host: str, port: int) -> dict:
    """Redis with no auth is an instant win."""
    try:
        s = socket.create_connection((host, port), timeout=5)
        s.send(b"PING\r\n")
        resp = s.recv(64).decode(errors="ignore")
        s.close()
        if "+PONG" in resp:
            return {
                "service":  "redis",
                "port":     port,
                "issue":    "No authentication required",
                "severity": "critical",
                "mitre":    "T1078",
            }
    except Exception:
        pass
    return None


def _check_ftp(host: str, port: int) -> dict:
    """Check anonymous FTP login."""
    try:
        import ftplib
        ftp = ftplib.FTP(timeout=5)
        ftp.connect(host, port)
        ftp.login("anonymous", "anonymous@lab.local")
        ftp.quit()
        return {
            "service":  "ftp",
            "port":     port,
            "issue":    "Anonymous FTP login allowed",
            "severity": "high",
            "mitre":    "T1078",
        }
    except Exception:
        pass
    return None


def _check_http_defaults(host: str, port: int, scheme: str) -> list:
    """Check common admin panel paths with default creds."""
    import urllib.request
    import urllib.error
    import base64

    found = []
    admin_paths = [
        "/admin", "/admin/login", "/wp-admin", "/manager/html",
        "/phpmyadmin", "/pma", "/console", "/actuator",
    ]

    for path in admin_paths:
        url = f"{scheme}://{host}:{port}{path}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status in (200, 401, 403):
                    found.append({
                        "service":  "http",
                        "port":     port,
                        "path":     path,
                        "status":   resp.status,
                        "issue":    f"Admin panel exposed at {path}",
                        "severity": "medium",
                        "mitre":    "T1078",
                    })
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                # Try default creds
                for user, pwd in DEFAULT_CREDS[:5]:
                    try:
                        creds = base64.b64encode(f"{user}:{pwd}".encode()).decode()
                        req2 = urllib.request.Request(url)
                        req2.add_header("Authorization", f"Basic {creds}")
                        with urllib.request.urlopen(req2, timeout=5) as r2:
                            if r2.status == 200:
                                found.append({
                                    "service":  "http",
                                    "port":     port,
                                    "path":     path,
                                    "issue":    f"Default creds work: {user}:{pwd}",
                                    "severity": "critical",
                                    "mitre":    "T1078",
                                })
                    except Exception:
                        pass
        except Exception:
            pass

    return found
