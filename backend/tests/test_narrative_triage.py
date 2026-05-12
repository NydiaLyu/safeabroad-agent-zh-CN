from backend.agents.safety_triage_agent import SafetyTriageAgent
from backend.models.case_state import CaseState
from backend.services.workflow_service import CaseWorkflowService


def test_narrative_triage_red_when_offender_nearby():
    result = SafetyTriageAgent().classify_narrative("对方现在还在门口，我不敢回家。")

    assert result["risk_level"] == "RED"
    assert "还在门口" in result["matched_red_flags"]


def test_submit_narrative_updates_case_risk_level():
    workflow = CaseWorkflowService()
    workflow.timeline_agent.llm.api_key = ""
    workflow.refinement_agent.llm.api_key = ""
    case = CaseState()

    result = workflow.submit_free_narrative(case, "我被推了，现在睡不着，不敢出门。")

    assert result["narrative_triage"]["risk_level"] == "YELLOW"
    assert case.current_risk_level == "YELLOW"
