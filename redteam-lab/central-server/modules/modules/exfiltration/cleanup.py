#!/usr/bin/env python3
import os, glob, json
files = glob.glob("/tmp/redteam_sensitive_dummy_*")
removed = []
for f in files:
    try:
        os.remove(f)
        removed.append(f)
    except: pass
print(json.dumps({"technique_id":"T1070.004","technique_name":"File Deletion","risk_level":"Low","summary":f"Cleaned up {len(removed)} dummy files","details":{"removed_files":removed}}, indent=2))