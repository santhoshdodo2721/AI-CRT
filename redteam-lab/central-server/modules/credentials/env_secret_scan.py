"""
Module: credentials.env_secret_scan
Scans environment variables and common config files for exposed secrets.
Read-only. Does not exfiltrate data.
"""
import os
import re
import glob
from pathlib import Path


# Patterns for common secret types
SECRET_PATTERNS = {
    "aws_access_key":     re.compile(r"AKIA[0-9A-Z]{16}"),
    "aws_secret_key":     re.compile(r"(?i)aws[_\-.]?secret[_\-.]?access[_\-.]?key\s*[=:]\s*\S+"),
    "github_token":       re.compile(r"ghp_[A-Za-z0-9]{36}"),
    "generic_api_key":    re.compile(r"(?i)(api[_\-]?key|apikey)\s*[=:]\s*['\"]?([A-Za-z0-9\-_]{20,})['\"]?"),
    "password_in_url":    re.compile(r"://[^:]+:[^@]+@"),
    "private_key_header": re.compile(r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----"),
    "jwt_token":          re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "slack_token":        re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,}"),
    "generic_password":   re.compile(r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?([^\s'\"]{8,})['\"]?"),
}

SCAN_FILES = [
    ".env", ".env.local", ".env.production", ".env.development",
    "*.yaml", "*.yml", "*.json", "*.toml", "*.ini", "*.conf", "*.cfg",
    ".git/config", "docker-compose.yml", "docker-compose.yaml",
    "Makefile", "*.sh",
]

MAX_FILE_SIZE = 1 * 1024 * 1024   # 1 MB


def run(params: dict) -> dict:
    scan_dirs = params.get("dirs", [str(Path.home()), "/opt", "/srv", "/var/www"])
    findings  = []

    # 1. Scan environment variables
    findings += _scan_env()

    # 2. Scan config files
    for scan_dir in scan_dirs:
        findings += _scan_directory(scan_dir)

    return {
        "findings":       findings,
        "total_secrets":  len(findings),
        "by_type":        _count_by_type(findings),
    }


def _scan_env() -> list:
    env_findings = []
    for key, value in os.environ.items():
        for secret_type, pattern in SECRET_PATTERNS.items():
            combined = f"{key}={value}"
            if pattern.search(combined):
                # Mask the value
                masked = value[:4] + "****" + value[-2:] if len(value) > 6 else "****"
                env_findings.append({
                    "source":      "environment_variable",
                    "key":         key,
                    "value":       masked,
                    "secret_type": secret_type,
                    "severity":    _get_severity(secret_type),
                })
    return env_findings


def _scan_directory(root: str) -> list:
    dir_findings = []
    if not os.path.isdir(root):
        return dir_findings

    for pattern in SCAN_FILES:
        for filepath in glob.glob(os.path.join(root, "**", pattern), recursive=True):
            try:
                if os.path.getsize(filepath) > MAX_FILE_SIZE:
                    continue
                with open(filepath, "r", errors="ignore") as f:
                    content = f.read()
                for secret_type, regex in SECRET_PATTERNS.items():
                    matches = regex.findall(content)
                    if matches:
                        dir_findings.append({
                            "source":      "file",
                            "file":        filepath,
                            "secret_type": secret_type,
                            "matches":     len(matches),
                            "severity":    _get_severity(secret_type),
                        })
            except (PermissionError, OSError):
                pass

    return dir_findings


def _get_severity(secret_type: str) -> str:
    high_severity = {"aws_access_key", "aws_secret_key", "github_token", "private_key_header", "jwt_token"}
    if secret_type in high_severity:
        return "high"
    return "medium"


def _count_by_type(findings: list) -> dict:
    counts = {}
    for f in findings:
        t = f["secret_type"]
        counts[t] = counts.get(t, 0) + 1
    return counts
