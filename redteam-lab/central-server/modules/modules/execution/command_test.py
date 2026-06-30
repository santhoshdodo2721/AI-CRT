#!/usr/bin/env python3
import subprocess, json, sys
def r(c): 
    return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=5).stdout.strip()
cmds = [("whoami","Current User"),("id","User/Group IDs"),("hostname","Hostname"),("uname -a","OS Info")]
details = [{"command":c,"description":d,"output":r(c)} for c,d in cmds]
print(json.dumps({"technique_id":"T1059.004","technique_name":"Unix Shell","risk_level":"Info","summary":f"Executed {len(cmds) local commands","details":details}, indent=2))