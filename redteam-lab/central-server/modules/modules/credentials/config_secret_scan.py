#!/usr/bin/env python3
import os, re, json
findings = []
pats = [r'api_?key\s*=\s*["']?[\w-]{20,}', r'secret\s*=\s*["']?[\w-]{20,}']
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in ["__pycache__","node_modules",".git"]]
    for f in files:
        if f.endswith((".yml",".yaml",".json",".conf")):
            path = os.path.join(root,f)
            try:
                with open(path,"r") as fh:
                    for i,line in enumerate(fh,1):
                        if any(re.search(p, line, re.I) for p in pats):
                            findings.append({"file":path,"line":i})
            except: pass
print(json.dumps({"technique_id":"T1552.004","technique_name":"Private Keys","risk_level":"Medium" if findings else "Low","summary":f"Found {len(findings)} potential keys/secrets in configs","details":findings[:10]}, indent=2))