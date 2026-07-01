import logging
import json

logger = logging.getLogger("ai_engine.validator")

async def validate_tool_output(tool_name: str, raw_output: str) -> bool:
    """Simple heuristic to check if the tool output is valid and not just an error."""
    if not raw_output or raw_output.strip() == "":
        return False
        
    lower_out = raw_output.lower()
    
    # Common error signatures
    error_sigs = [
        "command not found",
        "segmentation fault",
        "no such file or directory",
        "permission denied",
        "traceback (most recent call last)"
    ]
    
    for sig in error_sigs:
        if sig in lower_out:
            logger.warning(f"Validation failed: detected error signature '{sig}' in output of {tool_name}")
            return False
            
    return True
