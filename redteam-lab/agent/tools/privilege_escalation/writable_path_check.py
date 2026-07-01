#!/usr/bin/env python3
import subprocess
import json
import sys
import os

def run_privesc(target: str) -> dict:
    sys.stderr.write(f"[*] Checking for Writable Paths in $PATH (T1574.007) on {target}...\n")
    
    results = []
    vulns = []
    
    try:
        path_env = os.environ.get('PATH', '')
        paths = path_env.split(':')
        
        sys.stderr.write(f"[DEBUG] Checking {len(paths)} directories in PATH...\n")
        
        writable_paths = []
        for p in paths:
            if not p:
                continue
                
            # Check if directory exists and is writable by current user
            if os.path.isdir(p) and os.access(p, os.W_OK):
                # Also check if it's world writable
                mode = os.stat(p).st_mode
                is_world_writable = bool(mode & 0o002)
                
                writable_paths.append({
                    "path": p,
                    "world_writable": is_world_writable
                })
        
        results.append({
            "action": "check_path_env",
            "writable_paths": writable_paths
        })
        
        if writable_paths:
            sys.stderr.write(f"[!] ALERT: Found {len(writable_paths)} writable directories in PATH!\n")
            paths_str = ", ".join([p["path"] for p in writable_paths])
            vulns.append({
                "title": "Writable Directory in PATH",
                "description": f"The current user can write to directories in their PATH, allowing for execution flow hijacking.\nPaths: {paths_str}",
                "severity": "medium",
                "mitre_id": "T1574.007"
            })
        else:
            sys.stderr.write("[+] No writable directories found in PATH.\n")
            
    except Exception as e:
        results.append({"action": "check_path_env", "error": str(e)})
        sys.stderr.write(f"[-] ERROR checking PATH: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1574.007",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_privesc(target), indent=2))
