import logging
from sqlalchemy.orm import Session
from database.db import CredentialStore

logger = logging.getLogger("memory.credential")

def add_credential(db: Session, campaign_id: str, username: str, password: str = None, cred_type: str = "password", source: str = "discovered"):
    """Adds a new credential to the store if it doesn't exist."""
    existing = db.query(CredentialStore).filter(
        CredentialStore.campaign_id == campaign_id,
        CredentialStore.username == username,
        CredentialStore.password == password
    ).first()
    
    if existing:
        return existing
        
    cred = CredentialStore(
        campaign_id=campaign_id,
        username=username,
        password=password,
        cred_type=cred_type,
        source=source
    )
    db.add(cred)
    db.commit()
    db.refresh(cred)
    return cred

def get_untested_credentials_for_target(db: Session, campaign_id: str, target: str) -> list:
    """Returns credentials that haven't been tested on the specific target yet."""
    creds = db.query(CredentialStore).filter(CredentialStore.campaign_id == campaign_id).all()
    untested = []
    
    for c in creds:
        tested_on = c.tested_on or []
        if target not in tested_on:
            untested.append(c)
            
    return untested

def mark_credential_tested(db: Session, cred_id: str, target: str, is_valid: bool = False):
    cred = db.query(CredentialStore).filter(CredentialStore.id == cred_id).first()
    if not cred:
        return
        
    tested = set(cred.tested_on or [])
    tested.add(target)
    cred.tested_on = list(tested)
    
    if is_valid:
        valid = set(cred.valid_on or [])
        valid.add(target)
        cred.valid_on = list(valid)
        
    db.commit()
