#!/usr/bin/env python3
import json
import sys
import os
import shutil

def run_impact(target: str) -> dict:
    sys.stderr.write(f"[*] Simulating Data Encrypted for Impact (Ransomware/T1486) on {target}...\n")
    
    results = []
    vulns = []
    
    sim_dir = "/tmp/redteam_ransom_sim"
    files_to_create = ["financials_2026.xlsx", "passwords.txt", "architecture_diagram.docx"]
    
    try:
        # Ensure clean state
        if os.path.exists(sim_dir):
            shutil.rmtree(sim_dir)
            
        os.makedirs(sim_dir)
        sys.stderr.write(f"[DEBUG] Created mock directory at {sim_dir}\n")
        
        # 1. Create mock files
        for fname in files_to_create:
            path = os.path.join(sim_dir, fname)
            with open(path, "w") as f:
                f.write(f"Mock sensitive data for {fname}\n")
        
        sys.stderr.write(f"[DEBUG] Created {len(files_to_create)} mock files.\n")
        
        # 2. Simulate Ransomware by renaming them to .locked
        renamed_count = 0
        for fname in os.listdir(sim_dir):
            old_path = os.path.join(sim_dir, fname)
            new_path = old_path + ".locked"
            os.rename(old_path, new_path)
            renamed_count += 1
            
        sys.stderr.write(f"[+] Ransomware simulation successful. 'Encrypted' (renamed) {renamed_count} files.\n")
        
        results.append({
            "action": "ransomware_simulation",
            "directory": sim_dir,
            "files_affected": renamed_count,
            "success": True
        })
        
        vulns.append({
            "title": "Data Encrypted for Impact Simulation",
            "description": f"Successfully simulated a ransomware payload by rapidly encrypting (renaming) {renamed_count} files in `{sim_dir}`.",
            "severity": "high",
            "mitre_id": "T1486"
        })
            
    except Exception as e:
        results.append({"action": "ransomware_simulation", "error": str(e)})
        sys.stderr.write(f"[-] ERROR during ransomware simulation: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1486",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_impact(target), indent=2))
