import logging

logger = logging.getLogger("agent.credentials")

class CredentialVault:
    """Secure in-memory credential storage for the agent."""
    def __init__(self):
        self._vault = {}
        
    def store(self, key: str, value: str):
        self._vault[key] = value
        
    def retrieve(self, key: str) -> str:
        return self._vault.get(key)
        
    def clear(self):
        self._vault.clear()
        logger.info("Credential vault cleared.")
