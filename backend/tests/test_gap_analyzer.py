from backend.agents.gap_analyzer_agent import DetailGapAnalyzerAgent
from backend.models.case_state import CaseState, TimelineEvent


def test_physical_contact_generates_p1_gap():
    case = CaseState(
        timeline=[
            TimelineEvent(event_id="E1", event_type="physical_contact", description_zh="他推了我", sequence_index=1)
        ]
    )
    gaps = DetailGapAnalyzerAgent().analyze(case)
    assert any(gap["priority"] == "P1" and gap["gap_id"] == "body_part" for gap in gaps)

