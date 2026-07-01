class PlannerAgent:
    def __init__(self):
        # Maps current phase to the logical next phase
        self.logical_flow = {
            "recon": "vuln_scan",
            "vuln_scan": "initial_access",
            "initial_access": "execution",
            "execution": "persistence",
            "persistence": "privilege_escalation",
            "privilege_escalation": "defense_evasion",
            "defense_evasion": "credentials",
            "credentials": "lateral_movement",
            "lateral_movement": "exfiltration",
            "exfiltration": "impact",
            "impact": "complete"
        }

    def suggest_next_action(self, current_phase: str, last_result_success: bool) -> dict:
        """
        Suggests the next module to run based on the campaign state.
        """
        if not last_result_success:
            return {
                "action": "halt",
                "reason": f"Phase '{current_phase}' failed to find actionable vectors. Halting campaign path.",
                "next_module": None
            }
            
        next_phase = self.logical_flow.get(current_phase.lower(), "complete")
        
        if next_phase == "complete":
            return {
                "action": "complete",
                "reason": "All tactical phases completed successfully.",
                "next_module": None
            }
            
        # Hardcoded suggestions for the lab flow
        module_map = {
            "vuln_scan": "vuln_scan.nuclei_scan",
            "initial_access": "initial_access.exposed_admin_check",
            "execution": "execution.command_test",
            "persistence": "persistence.cron_test",
            "privilege_escalation": "privilege_escalation.sudo_check",
            "defense_evasion": "defense_evasion.detection_check",
            "credentials": "credentials.env_secret_scan",
            "lateral_movement": "lateral_movement.network_reachability",
            "exfiltration": "exfiltration.dummy_file_create",
            "impact": "impact.file_rename_test"
        }
        
        return {
            "action": "continue",
            "reason": f"Phase '{current_phase}' successful. Progressing to '{next_phase}'.",
            "next_module": module_map.get(next_phase)
        }
