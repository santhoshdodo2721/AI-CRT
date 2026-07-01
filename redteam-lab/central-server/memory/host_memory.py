import logging
from sqlalchemy.orm import Session
from database.db import HostMemory

logger = logging.getLogger("memory.host")

def get_host(db: Session, campaign_id: str, ip_address: str) -> dict:
    host = db.query(HostMemory).filter(
        HostMemory.campaign_id == campaign_id,
        HostMemory.ip_address == ip_address
    ).first()
    
    if not host:
        return None
        
    return {
        "ip": host.ip_address,
        "hostname": host.hostname,
        "os_info": host.os_info,
        "open_ports": host.open_ports,
        "services": host.services,
        "vulns": host.vulns,
        "state": host.state
    }

def get_all_hosts(db: Session, campaign_id: str) -> list:
    hosts = db.query(HostMemory).filter(HostMemory.campaign_id == campaign_id).all()
    return [
        {
            "ip": host.ip_address,
            "open_ports": host.open_ports,
            "services": host.services
        }
        for host in hosts
    ]
