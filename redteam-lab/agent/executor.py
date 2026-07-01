import subprocess
import logging

logger = logging.getLogger("agent.executor")

class SandboxedExecutor:
    @staticmethod
    def run_command(command: str, timeout: int = 600) -> dict:
        """Runs a tool safely with a timeout and captures output."""
        try:
            logger.info(f"Executing command: {command}")
            # Security Note: shell=True is dangerous in production, 
            # but used here for red teaming tool chaining
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            return {
                "status": "completed" if result.returncode == 0 else "failed",
                "exit_code": result.returncode,
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "exit_code": 124,
                "output": "",
                "error": f"Execution timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "status": "failed",
                "exit_code": 1,
                "output": "",
                "error": str(e)
            }
