#!/usr/bin/env python3
import os, json, tempfile
d, fpath = tempfile.mkstemp(suffix=".txt", prefix="redteam_sensitive_dummy_")
with os.fdopen(d, "w") as f: f.write("FAKE_SENSITIVE_DATA_12345")
print(json.dumps({"technique_id":"T1005","technique_name":"Data from Local System","risk_level":"Low","summary":f"Dummy file created at {fpath}","details":{"file_path":fpath,"status":"created"}}, indent=2))