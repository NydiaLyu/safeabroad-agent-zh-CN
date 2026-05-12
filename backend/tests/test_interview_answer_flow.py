from backend.services.workflow_service import CaseWorkflowService
from backend.models.case_state import CaseState, TimelineEvent


def test_answer_appends_to_timeline_and_marks_gap_answered():
    workflow = CaseWorkflowService()
    workflow.timeline_agent.llm.api_key = ""
    workflow.refinement_agent.llm.api_key = ""
    case = CaseState(
        timeline=[
            TimelineEvent(
                event_id="E1",
                event_type="physical_contact",
                description_zh="他推了我",
                sequence_index=1,
            )
        ]
    )
    case.missing_details = workflow.gap_agent.analyze(case)

    result = workflow.submit_interview_answer(case, "他推到我的肩膀，我往后退了一步。")

    assert len(result["timeline"]) > 1
    assert "E1:body_part" in case.answered_gaps
    assert case.timeline[0].known_fields["body_part"] == "他推到我的肩膀，我往后退了一步。"


def test_intervention_inserted_between_taken_fries_and_response_with_conflict_question():
    workflow = CaseWorkflowService()
    workflow.timeline_agent.llm.api_key = ""
    workflow.refinement_agent.llm.api_key = ""
    case = CaseState(
        timeline=[
            TimelineEvent(event_id="E1", event_type="property_interference", description_zh="对方先拿走了我的薯条", sequence_index=1),
            TimelineEvent(event_id="E2", event_type="verbal_exchange", description_zh="我问对方干嘛", sequence_index=2),
            TimelineEvent(event_id="E3", event_type="verbal_exchange", description_zh="对方回答你想怎样", sequence_index=3),
            TimelineEvent(event_id="E4", event_type="physical_contact", description_zh="对方推了我", sequence_index=4),
        ]
    )

    result = workflow.submit_interview_answer(case, "旁边的人出声制止了对方拿走薯条的行为")
    descriptions = [event.description_zh for event in result["timeline"]]

    assert descriptions.index("旁边的人出声制止了对方拿走薯条的行为") < descriptions.index("对方回答你想怎样")
    assert result["logic_issues"]
    assert "请确认" in result["next_question"]


def test_unrelated_supplement_does_not_mark_current_cctv_gap_answered():
    workflow = CaseWorkflowService()
    workflow.timeline_agent.llm.api_key = ""
    workflow.refinement_agent.llm.api_key = ""
    case = CaseState(
        timeline=[
            TimelineEvent(event_id="E1", event_type="property_interference", description_zh="对方先拿走了我的薯条", sequence_index=1),
            TimelineEvent(event_id="E2", event_type="verbal_exchange", description_zh="对方回答你想怎样", sequence_index=2),
        ],
        missing_details=[
            {
                "event_id": None,
                "gap_id": "cctv",
                "priority": "P2",
                "question": "附近是否可能有 CCTV？",
            }
        ],
    )

    workflow.submit_interview_answer(case, "旁边的人出声制止了对方拿走薯条的行为")

    assert "global:cctv" not in case.answered_gaps


def test_vague_uncertainty_requires_scope_before_resolving_logic_issue():
    workflow = CaseWorkflowService()
    workflow.timeline_agent.llm.api_key = ""
    workflow.refinement_agent.llm.api_key = ""
    case = CaseState(
        timeline=[
            TimelineEvent(event_id="E1", event_type="property_interference", description_zh="对方先拿走了我的薯条", sequence_index=1),
            TimelineEvent(event_id="E2", event_type="verbal_exchange", description_zh="对方回答你想怎样", sequence_index=2),
        ]
    )
    first = workflow.submit_interview_answer(case, "旁边的人出声制止了对方拿走薯条的行为")
    assert first["logic_issues"]

    second = workflow.submit_interview_answer(case, "我记不清了")

    assert second["logic_issues"]
    assert "记不清的范围" in second["next_question"]


def test_scoped_uncertainty_resolves_logic_issue():
    workflow = CaseWorkflowService()
    workflow.timeline_agent.llm.api_key = ""
    workflow.refinement_agent.llm.api_key = ""
    case = CaseState(
        timeline=[
            TimelineEvent(event_id="E1", event_type="property_interference", description_zh="对方先拿走了我的薯条", sequence_index=1),
            TimelineEvent(event_id="E2", event_type="verbal_exchange", description_zh="对方回答你想怎样", sequence_index=2),
        ]
    )
    workflow.submit_interview_answer(case, "旁边的人出声制止了对方拿走薯条的行为")
    result = workflow.submit_interview_answer(case, "我只是不确定制止和拿走薯条的先后顺序，但两件事都发生了。")

    assert not result["logic_issues"]


def test_threat_before_hand_twist_inserts_after_strength_question_not_at_end():
    workflow = CaseWorkflowService()
    workflow.timeline_agent.llm.api_key = ""
    workflow.refinement_agent.llm.api_key = ""
    case = CaseState(
        timeline=[
            TimelineEvent(event_id="E1", event_type="property_interference", description_zh="对方拿了我的薯条", sequence_index=1),
            TimelineEvent(event_id="E2", event_type="verbal_exchange", description_zh="对方问我你觉得你比我强吗", sequence_index=2),
            TimelineEvent(event_id="E3", event_type="physical_contact", description_zh="对方扭我的手", sequence_index=3),
            TimelineEvent(event_id="E4", event_type="authority_response", description_zh="警察直接来了", sequence_index=4),
        ]
    )

    result = workflow.submit_interview_answer(case, "他还挥拳恐吓我，在扭我的手之前")
    descriptions = [event.description_zh for event in result["timeline"]]

    added_index = descriptions.index("他还挥拳恐吓我，在扭我的手之前")
    assert descriptions.index("对方问我你觉得你比我强吗") < added_index
    assert added_index < descriptions.index("对方扭我的手")


def test_hand_twist_inserts_after_strength_question_before_police():
    workflow = CaseWorkflowService()
    workflow.timeline_agent.llm.api_key = ""
    workflow.refinement_agent.llm.api_key = ""
    case = CaseState(
        timeline=[
            TimelineEvent(event_id="E1", event_type="property_interference", description_zh="对方拿了我的薯条", sequence_index=1),
            TimelineEvent(event_id="E2", event_type="verbal_exchange", description_zh="对方问我你觉得你比我强吗", sequence_index=2),
            TimelineEvent(event_id="E3", event_type="authority_response", description_zh="警察直接来了", sequence_index=3),
        ]
    )

    result = workflow.submit_interview_answer(case, "他扭断了我的手")
    descriptions = [event.description_zh for event in result["timeline"]]
    added = next(event for event in result["timeline"] if event.description_zh == "他扭断了我的手")

    added_index = descriptions.index("他扭断了我的手")
    assert added.event_type == "physical_contact"
    assert descriptions.index("对方问我你觉得你比我强吗") < added_index
    assert added_index < descriptions.index("警察直接来了")
