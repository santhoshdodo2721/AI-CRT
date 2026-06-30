# RedTeam Lab Platform

A self-hosted, AI-assisted red-team automation platform for your **own lab network**.

> ⚠️ **For authorized lab/internal use only.** Only run against systems you own or have explicit written permission to test.

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│            Your Lab Network             │
│                                         │
│  ┌──────────────┐   ┌────────────────┐  │
│  │ Central      │   │ Ollama (local  │  │
│  │ Server       │◄──│ LLM - llama3)  │  │
│  │ (FastAPI +   │   └────────────────┘  │
│  │  PostgreSQL) │                        │
│  └──────┬───────┘                        │
│         │  REST API                      │
│  ┌──────▼───────┐   ┌────────────────┐  │
│  │  Agent(s)    │   │  Dashboard     │  │
│  │  on targets  │   │  (React UI)    │  │
│  └──────────────┘   └────────────────┘  │
└─────────────────────────────────────────┘
```

---

## Quick Start

### 1. Prerequisites

```bash
# Docker + Docker Compose
sudo apt install docker.io docker-compose-plugin

# Go tools (on agent machines)
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
nuclei -update-templates

# Nmap (on agent machines)
sudo apt install nmap
```

### 2. Clone and configure

```bash
git clone <your-repo> redteam-lab
cd redteam-lab

# Edit the central server IP in agent/config.yaml
nano agent/config.yaml
# → server_url: "http://<YOUR_SERVER_IP>:8000"
```

### 3. Start the stack

```bash
docker compose up -d
```

### 4. Pull the AI model (first time only)

```bash
docker exec redteam-ollama ollama pull llama3
# Or use a smaller model:
docker exec redteam-ollama ollama pull mistral
```

### 5. Create admin user

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@lab.local","password":"changeme","role":"admin"}'
```

### 6. Install agent on target machines

```bash
# On each target machine in your lab:
cd agent/
pip install -r requirements.txt
python agent.py
```

---

## Usage Workflow

### Create a campaign and start scanning

```bash
# 1. Login and get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -F "username=admin" -F "password=changeme" | jq -r .access_token)

# 2. Create a campaign
CAMPAIGN=$(curl -s -X POST http://localhost:8000/api/campaigns/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Lab Scan 1","target":"192.168.1.0/24"}' | jq -r .id)

# 3. Start the campaign (auto-queues recon + vuln scan tasks)
curl -X POST http://localhost:8000/api/campaigns/$CAMPAIGN/start \
  -H "Authorization: Bearer $TOKEN"

# 4. Check results
curl http://localhost:8000/api/reports/$CAMPAIGN \
  -H "Authorization: Bearer $TOKEN"

# 5. Ask AI to analyze a task
curl -X POST http://localhost:8000/api/ai/analyze-task/<TASK_ID> \
  -H "Authorization: Bearer $TOKEN"

# 6. Generate full report
curl -X POST http://localhost:8000/api/ai/generate-report/$CAMPAIGN \
  -H "Authorization: Bearer $TOKEN"
```

---

## Module Reference

| Module | MITRE ID | Description |
|--------|----------|-------------|
| `recon.nmap_scan` | T1046 | Port scan + service detection |
| `recon.subdomain_scan` | T1595 | Subdomain enumeration |
| `recon.http_probe` | T1190 | Web app detection |
| `vuln_scan.nuclei_scan` | T1190 | Template-based vuln scan |
| `privilege_escalation.sudo_check` | T1548 | Sudo misconfig check |
| `credentials.env_secret_scan` | T1552 | Secret detection in env/files |
| `lateral_movement.network_reachability` | T1021 | Reachability + attack paths |

---

## MITRE ATT&CK Data

```bash
# Download and store ATT&CK techniques locally
cd mitre/
pip install requests
python sync_mitre.py
```

---

## Directory Structure

```
redteam-lab/
├── central-server/        # FastAPI backend
│   ├── api/               # Route handlers
│   ├── database/          # SQLAlchemy models
│   └── main.py
├── agent/                 # Agent binary
│   ├── agent.py           # Main loop
│   └── config.yaml        # Server URL + allowlist
├── modules/               # Execution modules
│   ├── recon/
│   ├── vuln_scan/
│   ├── privilege_escalation/
│   ├── credentials/
│   ├── lateral_movement/
│   └── ...
├── mitre/                 # ATT&CK data + mapping
├── frontend/              # React dashboard
├── docker/                # Dockerfiles
└── docker-compose.yml
```

---

## Security Considerations

- **Never run against systems you don't own** – all modules include safety checks.
- Change `SECRET_KEY` in docker-compose.yml before production use.
- Agent allowlist (`config.yaml`) controls exactly which modules run on each host.
- All simulations are non-destructive by default (dummy files are cleaned up, real exploitation is blocked).
- Network is isolated to lab VLAN recommended.

---

## Adding New Modules

1. Create `modules/<category>/<name>.py` with a `run(params: dict) -> dict` function.
2. Add the module name to `ALLOWED_MODULES` in `central-server/api/tasks/routes.py`.
3. Add the MITRE mapping in `mitre/sync_mitre.py`.
4. Add to agent `config.yaml` allowlist.
