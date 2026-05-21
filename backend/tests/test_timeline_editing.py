from backend.models.case_state import CaseState, TimelineEvent
from backend.services.workflow_service import CaseWorkflowService


def test_update_timeline_reorders_and_edits_events():
    workflow = CaseWorkflowService()
    case = CaseState(
        timeline=[
            TimelineEvent(event_id="E1", event_type="property_interference", description_zh="对方拿走薯条", sequence_index=1),
            TimelineEvent(event_id="E2", event_type="physical_contact", description_zh="对方推了我", sequence_index=2),
        ]
    )

    result = workflow.update_timeline(
        case,
        [
            {"description_zh": "我问对方干嘛", "event_type": "verbal_exchange", "certainty": "confirmed"},
            {"description_zh": "对方拿走薯条", "event_type": "property_interference", "certainty": "uncertain"},
        ],
    )

    assert [event.description_zh for event in result["timeline"]] == ["我问对方干嘛", "对方拿走薯条"]
    assert result["timeline"][1].certainty == "uncertain"
    assert result["timeline"][1].event_id == "E2"


def test_reconstruct_case_story_marks_uncertain_events():
    workflow = CaseWorkflowService()
    case = CaseState(
        timeline=[
            TimelineEvent(event_id="E1", event_type="property_interference", description_zh="对方拿走薯条", sequence_index=1),
            TimelineEvent(event_id="E2", event_type="physical_contact", description_zh="对方推了我", sequence_index=2, certainty="uncertain"),
        ]
    )

    result = workflow.reconstruct_case_story(case)

    assert "我记得：对方拿走薯条" in result["story_zh"]
    assert "我不确定：对方推了我" in result["story_zh"]
    assert result["uncertain_items"][0]["event_id"] == "E2"


def test_finalize_followup_review_marks_selected_events_uncertain():
    workflow = CaseWorkflowService()
    case = CaseState(
        timeline=[
            TimelineEvent(event_id="E1", event_type="property_interference", description_zh="对方拿走薯条", sequence_index=1),
            TimelineEvent(event_id="E2", event_type="physical_contact", description_zh="对方推了我", sequence_index=2),
        ]
    )

    result = workflow.finalize_followup_review(case, ["E1"])

    assert result["followup_finished"] is True
    assert case.timeline[0].certainty == "uncertain"
    assert case.timeline[1].certainty == "confirmed"

