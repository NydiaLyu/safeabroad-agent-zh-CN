from backend.agents.claims_agent import ClaimsSupportNavigatorAgent
from backend.models.case_state import CaseState, Jurisdiction, TimelineEvent


def test_nsw_support_guidance_includes_boundaries_and_official_links():
    case = CaseState(
        jurisdiction=Jurisdiction(country="Australia", state="NSW", city="Sydney", jurisdiction_id="AU-NSW"),
        timeline=[
            TimelineEvent(event_id="E1", event_type="physical_contact", description_zh="对方推了我", sequence_index=1)
        ],
    )

    result = ClaimsSupportNavigatorAgent().generate_support_guidance(case)

    assert "不提供法律意见" in result["disclaimer"]
    assert any("不估计" in item for item in result["cannot_provide"])
    assert any("Victims Support" in link["label"] for link in result["official_links"])
    assert any("Legal Aid" in link["label"] for link in result["official_links"])

