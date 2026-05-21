from backend.agents.safety_triage_agent import SafetyTriageAgent, TriagePayload


def test_red_risk_when_current_danger():
    result = SafetyTriageAgent().classify(TriagePayload(current_danger=True))
    assert result["risk_level"] == "RED"
    assert result["emergency_number"] == "000"


def test_green_risk_when_no_flags():
    result = SafetyTriageAgent().classify(TriagePayload())
    assert result["risk_level"] == "GREEN"

