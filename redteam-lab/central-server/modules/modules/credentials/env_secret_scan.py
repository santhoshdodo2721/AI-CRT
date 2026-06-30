#!/usr/bin/env python3
import os, re, json
findings = []
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in ["__pycache__","node_modules",".git"]]
    for f in files:
        if f.endswith(".env"):
            path = os.path.join(root,f)
            try:
                with open(path,"r") as fh:
                    for i,line in enumerate(fh,1):
                        if re.search(r'(PASSWORD|SECRET|KEY|TOKEN)\s*=', line, re.I) and not line.strip().startswith("#"):
                            findings.append({"file":path,"line":i,"match":line.strip()})
            except: pass
print(json.dumps({"technique_id":"T1552.001","technique_name":"Credentials In Files","risk_level":"Medium" if findings else "Low","summary":f"Found {len(findings)} potential secrets in .env files","details":findings[:10]}, indent=2))