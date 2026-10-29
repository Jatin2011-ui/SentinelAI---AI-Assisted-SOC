
"""Supervisor Agent for SOC orchestration."""
from app.agents.state import SOCState


class SupervisorAgent:
    def __init__(self):
        self.name = "SupervisorAgent"

    def plan_investigation(self, state: SOCState) -> SOCState:
        state.investigation_history.append("Supervisor: start investigation plan")
        # Simple deterministic planning
        if not state.events:
            state.hypotheses.append({"name": "Insufficient data", "confidence": 0.1})
        else:
            state.hypotheses.append({"name": "Potential credential attack", "confidence": 0.6})
        return state

    def coordinate(self, state: SOCState) -> SOCState:
        state.investigation_history.append("Supervisor: coordinate agents")
        # In real implementation, would invoke Investigation, Threat Intel, MITRE agents
        return state
