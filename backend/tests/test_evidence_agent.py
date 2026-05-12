from backend.agents.evidence_agent import EvidenceManagerAgent
from backend.models.case_state import CaseState, TimelineEvent


def test_mcdonalds_cctv_note_generates_high_value_collection_guidance():
    agent = EvidenceManagerAgent()
    agent.llm.api_key = ""
    case = CaseState(
        timeline=[
            TimelineEvent(event_id="E1", event_type="property_interference", description_zh="对方拿走了我的薯条", sequence_index=1),
            TimelineEvent(event_id="E2", event_type="physical_contact", description_zh="对方推了我", sequence_index=2),
        ]
    )

    result = agent.evaluate(case, "我们在麦当劳监控底下")
    cctv_items = [item for item in result["recommended_evidence"] if item["evidence_type"] == "cctv"]

    assert cctv_items
    assert cctv_items[0]["usefulness"] == "high"
    assert "manager" in cctv_items[0]["how_to_collect"]
    assert "保留" in cctv_items[0]["how_to_collect"]

