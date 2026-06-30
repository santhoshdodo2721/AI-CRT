#!/usr/bin/env python3
"""
Network Reachability Scanner - Fixed Version
Addresses: timeout, high ports, filtered port detection
"""

import socket
import sys
import json
import concurrent.futures
import time
from datetime import datetime

# Common high ports for AD/Windows (often missed by 1-1000 scans)
COMMON_HIGH_PORTS = [
    3268, 3269, 3389, 5985, 5986, 636, 9389,
    49664, 49665, 49666, 49667, 49668, 49669, 49670,
    49671, 49672, 49673, 49674, 49675, 49676, 49677,
    49704, 49705, 49706, 49707, 49708, 49709, 49710,
    49711, 49712, 49713, 49714, 49715, 49720
]

# Service mapping
SERVICE_MAP = {
    53: "domain", 88: "kerberos-sec", 135: "msrpc", 139: "netbios-ssn",
    389: "ldap", 445: "microsoft-ds", 464: "kpasswd5", 593: "http-rpc-epmap",
    636: "ldaps", 3268: "globalcatLDAP", 3269: "globalcatLDAPssl",
    3389: "ms-wbt-server", 5985: "wsman", 5986: "wsman-ssl",
    9389: "adws", 49664: "unknown", 49665: "unknown"
}

def parse_port_range(port_str):
    """Parse port string like '1-1000', '80,443', '1-1000,8080'"""
    ports = set()
    for part in port_str.split(','):
        part = part.strip()
    if '-' in part:
            start, end = part.split('-')
            ports.update(range(int(start), int(end) + 1))
        else:
            ports.add(int(part))
    return sorted(ports)

def scan_port(ip, port, timeout=2.5):
    """
    Scan a single port with proper timeout for filtered networks.
    Returns: (port, state, service)
    """
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        
        if result == 0:
            service = SERVICE_MAP.get(port, "unknown")
            return (port, "open", service)
        else:
            return (port, "closed", None)
            
    except socket.timeout:
        return (port, "filtered", None)
    except Exception as e:
        return (port, "error", str(e))
    finally:
        if sock:
            sock.close()

def scan_host(ip, ports, threads=30, timeout=2.5):
    """Scan a host with proper concurrency and timeout"""
    open_ports = []
    filtered_count = 0
    
    print(f"[*] Scanning {ip} - {len(ports)} ports, {threads} threads, {timeout}s timeout")
    print(f"[*] Start time: {datetime.now().strftime('%H:%M:%S')}")
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(scan_port, ip, port, timeout): port 
            for port in ports
        }
        
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            if completed % 100 == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                print(f"    Progress: {completed}/{len(ports)} ({rate:.1f} ports/sec)")
            
            port, state, service = future.result()
            if state == "open":
                open_ports.append({"port": port, "service": service})
                print(f"    [+] {port}/tcp open {service}")
            elif state == "filtered":
                filtered_count += 1
    
    elapsed = time.time() - start_time
    print(f"[*] Completed in {elapsed:.1f}s")
    
    return open_ports, filtered_count

def generate_report(ip, open_ports, filtered_count, scan_range):
    """Generate MITRE ATT&CK formatted report"""
    
    if not open_ports:
        risk = "Low"
        summary = "No open ports found."
    elif len([p for p in open_ports if p['port'] in [445, 135, 3389, 5985]]) > 0:
        risk = "High"
        summary = f"Critical lateral movement services exposed ({len(open_ports)} open ports)"
    else:
        risk = "Medium"
        summary = f"Services accessible for potential lateral movement ({len(open_ports)} open ports)"
    
    lateral_ports = {
        135: "RPC - DCOM exploitation, remote method invocation",
        139: "NetBIOS - SMB over NetBIOS, legacy file sharing",
        389: "LDAP - Domain enumeration, password queries",
        445: "SMB - File sharing, PsExec, WMI, credential relay",
        3389: "RDP - Remote desktop access",
        5985: "WinRM - PowerShell remoting, CimSessions",
        5986: "WinRM SSL - Secure PowerShell remoting"
    }
    
    details = []
    for p in open_ports:
        entry = {
            "port": p['port'],
            "service": p['service'],
            "lateral_movement_potential": p['port'] in lateral_ports,
            "notes": lateral_ports.get(p['port'], "Service available")
        }
        details.append(entry)
    
    report = {
        "technique_id": "T1021",
        "technique_name": "Remote Services",
        "risk_level": risk,
        "summary": summary,
        "target": ip,
        "scan_range": scan_range,
        "filtered_ports_detected": filtered_count,
        "details": details,
        "lateral_movement_vectors": [
            lateral_ports[p['port']] 
            for p in open_ports if p['port'] in lateral_ports
        ]
    }
    
    return report

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <IP> <port-range> [threads] [timeout]")
        print(f"Examples:")
        print(f"  {sys.argv[0]} 10.129.39.113 \"1-1000\"")
        print(f"  {sys.argv[0]} 10.129.39.113 \"1-65535\" 50 2")
        print(f"  {sys.argv[0]} 10.129.39.113 \"1-1000,3268,3269")
        sys.exit(1)
    
    ip = sys.argv[1]
    port_range = sys.argv[2]
    threads = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 2.5
    
    ports = parse_port_range(port_range)
    
    max_requested = max(ports) if ports else 0
    if max_requested < 10000:
        print("[*] Auto-adding common high ports (AD/Windows)")
        additional = [p for p in COMMON_HIGH_PORTS if p not in ports]
        ports.extend(additional)
        ports = sorted(set(ports))
        print(f"[*] Added {len(additional)} high ports, total: {len(ports)}")
    
    open_ports, filtered_count = scan_host(ip, ports, threads, timeout)
    
    report = generate_report(ip, open_ports, filtered_count, port_range)
    print("\n" + json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
