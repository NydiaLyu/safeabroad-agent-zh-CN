from backend.agents.evidence_agent import EvidenceManagerAgent
from backend.agents.export_privacy_agent import DocumentExportPrivacyAgent
from backend.agents.followup_agent import PoliceFollowUpAgent
from backend.agents.gap_analyzer_agent import DetailGapAnalyzerAgent
from backend.agents.interview_agent import TraumaInformedInterviewAgent
from backend.agents.claims_agent import ClaimsSupportNavigatorAgent
from backend.agents.safety_triage_agent import SafetyTriageAgent
from backend.agents.statement_agent import PoliceStatementGeneratorAgent
from backend.agents.timeline_agent import TimelineReconstructionAgent
from backend.agents.timeline_refinement_agent import UNCERTAIN_MARKERS, TimelineRefinementAgent
from backend.models.case_state import CaseState, TimelineEvent


class CaseWorkflowService:
    def __init__(self):
        self.timeline_agent = TimelineReconstructionAgent()
        self.triage_agent = SafetyTriageAgent()
        self.refinement_agent = TimelineRefinementAgent()
        self.gap_agent = DetailGapAnalyzerAgent()
        self.interview_agent = TraumaInformedInterviewAgent()
        self.evidence_agent = EvidenceManagerAgent()
        self.statement_agent = PoliceStatementGeneratorAgent()
        self.followup_agent = PoliceFollowUpAgent()
        self.claims_agent = ClaimsSupportNavigatorAgent()
        self.export_agent = DocumentExportPrivacyAgent()

    def submit_free_narrative(self, case: CaseState, narrative: str) -> dict:
        case.free_narrative_zh = narrative
        triage_result = self.triage_agent.classify_narrative(narrative, case.jurisdiction.jurisdiction_id or "AU-NSW")
        case.current_risk_level = triage_result["risk_level"]
        case.timeline = self.timeline_agent.extract(narrative)
        case.answered_gaps = []
        case.answered_logic_issues = []
        case.followup_finished = False
        case.logic_issues = []
        case.missing_details = self.gap_agent.analyze(case)
        response = self._interview_response(case)
        response["narrative_triage"] = triage_result
        return response

    def submit_interview_answer(self, case: CaseState, answer: str) -> dict:
        current_item = self._current_followup_item(case)
        if current_item:
            self._mark_answered(case, current_item, answer)

        refinement = self.refinement_agent.refine(case, answer, current_item)
        self._insert_refined_events(case, refinement.get("events", []), current_item)
        case.logic_issues = self._merge_logic_issues(case, refinement.get("logic_issues", []))
        case.missing_details = self.gap_agent.analyze(case)
        return self._interview_response(case)

    def finish_followup(self, case: CaseState) -> dict:
        case.followup_finished = True
        return self._interview_response(case)

    def update_timeline(self, case: CaseState, events: list) -> dict:
        updated = []
        for index, item in enumerate(events, start=1):
            description = str(item.get("description_zh", "")).strip()
            if not description:
                continue
            updated.append(
                TimelineEvent(
                    event_id=f"E{index}",
                    event_type=item.get("event_type") or "follow_up_detail",
                    description_zh=description,
                    sequence_index=index,
                    certainty=item.get("certainty") or "uncertain",
                    known_fields=item.get("known_fields") or {},
                    missing_fields=item.get("missing_fields") or [],
                )
            )
        case.timeline = updated
        case.logic_issues = []
        case.missing_details = self.gap_agent.analyze(case)
        return self._interview_response(case)

    def reconstruct_case_story(self, case: CaseState) -> dict:
        parts = []
        uncertain_items = []
        for event in sorted(case.timeline, key=lambda item: item.sequence_index):
            prefix = "我记得"
            if event.certainty == "approximate":
                prefix = "我大概记得"
            if event.certainty == "uncertain":
                prefix = "我不确定"
                uncertain_items.append(
                    {
                        "event_id": event.event_id,
                        "description_zh": event.description_zh,
                        "certainty": event.certainty,
                    }
                )
            parts.append(f"{prefix}：{event.description_zh}")
        story = "。".join(parts)
        if story and not story.endswith("。"):
            story += "。"
        return {
            "story_zh": story or "暂无可还原的案发经过。",
            "events": case.timeline,
            "uncertain_items": uncertain_items,
        }

    def finalize_followup_review(self, case: CaseState, uncertain_event_ids: list) -> dict:
        uncertain_set = set(uncertain_event_ids)
        for event in case.timeline:
            if event.event_id in uncertain_set:
                event.certainty = "uncertain"
        case.followup_finished = True
        return self._interview_response(case)

    def evaluate_evidence(self, case: CaseState, user_note: str = "") -> dict:
        return self.evidence_agent.evaluate(case, user_note)

    def support_guidance(self, case: CaseState) -> dict:
        return self.claims_agent.generate_support_guidance(case)

    def _current_followup_item(self, case: CaseState) -> dict:
        if case.followup_finished:
            return None
        scoped_uncertainty_issues = [issue for issue in case.logic_issues if str(issue.get("issue_id", "")).endswith("_uncertainty_scope")]
        if scoped_uncertainty_issues:
            return scoped_uncertainty_issues[0]
        if case.logic_issues:
            return case.logic_issues[0]
        return case.missing_details[0] if case.missing_details else None

    def _interview_response(self, case: CaseState) -> dict:
        current_item = self._current_followup_item(case)
        if case.followup_finished:
            next_question = "用户已结束案发经过追问。你仍然可以生成英文材料，生成前请确认时间线内容。"
        elif current_item:
            next_question = current_item.get("question", self.interview_agent.next_question(case.missing_details))
        else:
            next_question = "案发经过暂时没有明显逻辑矛盾或关键缺口。你可以生成英文材料，或继续补充更多细节。"
        return {
            "case": case,
            "timeline": case.timeline,
            "logic_issues": case.logic_issues,
            "missing_details": case.missing_details,
            "next_question": next_question,
            "current_gap": current_item,
            "followup_finished": case.followup_finished,
        }

    def _mark_answered(self, case: CaseState, item: dict, answer: str) -> None:
        issue_id = item.get("issue_id")
        if issue_id:
            if issue_id.endswith("_uncertainty_scope"):
                parent_issue_id = issue_id.replace("_uncertainty_scope", "")
                if parent_issue_id not in case.answered_logic_issues:
                    case.answered_logic_issues.append(parent_issue_id)
                case.logic_issues = [
                    issue
                    for issue in case.logic_issues
                    if issue.get("issue_id") not in {issue_id, parent_issue_id}
                ]
                return
            if issue_id not in case.answered_logic_issues and not self._is_vague_uncertainty(answer):
                case.answered_logic_issues.append(issue_id)
                case.logic_issues = [issue for issue in case.logic_issues if issue.get("issue_id") != issue_id]
            return

        event_id = item.get("event_id")
        gap_id = item.get("gap_id")
        if not gap_id:
            return
        if not self._answer_matches_gap(gap_id, answer):
            return
        answered_key = f"{event_id or 'global'}:{gap_id}"
        if answered_key not in case.answered_gaps:
            case.answered_gaps.append(answered_key)
        for event in case.timeline:
            if event.event_id == event_id:
                event.known_fields[gap_id] = answer

    def _answer_matches_gap(self, gap_id: str, answer: str) -> bool:
        if any(marker in answer for marker in UNCERTAIN_MARKERS):
            return True
        matchers = {
            "cctv": ["CCTV", "监控", "摄像", "店", "车站", "路口", "公交", "校园"],
            "witnesses": ["证人", "旁边", "有人", "两个人", "看到", "听到", "路人"],
            "body_part": ["肩", "手", "胳膊", "背", "胸", "头", "脸", "腿", "身体", "部位"],
            "force": ["用力", "力度", "很重", "轻", "往后", "摔", "退"],
            "immediate_effect": ["之后", "马上", "然后", "后退", "摔", "疼", "离开"],
            "exact_words_or_meaning": ["说", "骂", "喊", "原话", "意思", "你想怎样"],
            "next_action": ["之后", "然后", "接着", "后来", "下一"],
            "medical_help": ["医生", "医院", "诊所", "校医", "GP", "medical"],
        }
        keywords = matchers.get(gap_id)
        return True if keywords is None else any(keyword in answer for keyword in keywords)

    def _is_vague_uncertainty(self, answer: str) -> bool:
        if not any(marker in answer for marker in UNCERTAIN_MARKERS):
            return False
        scope_markers = ["先后", "顺序", "这两件", "两件事", "是否", "有没有", "哪件", "具体", "只", "范围"]
        return not any(marker in answer for marker in scope_markers)

    def _insert_refined_events(self, case: CaseState, refined_events: list, current_item: dict) -> None:
        for refined in refined_events:
            description = refined.get("description_zh", "").strip()
            if not description:
                continue
            insert_at = self._resolve_insert_index(case, refined)
            from backend.models.case_state import TimelineEvent

            event = TimelineEvent(
                event_id="TEMP",
                event_type=refined.get("event_type", "follow_up_detail"),
                description_zh=description,
                sequence_index=insert_at + 1,
                certainty=refined.get("certainty", "uncertain"),
                known_fields={
                    "source_question": current_item.get("question", "") if current_item else "",
                    "source_gap_id": current_item.get("gap_id", current_item.get("issue_id", "")) if current_item else "",
                },
            )
            case.timeline.insert(insert_at, event)
            self._renumber_timeline(case)

    def _resolve_insert_index(self, case: CaseState, refined: dict) -> int:
        before_id = refined.get("insert_before_event_id")
        after_id = refined.get("insert_after_event_id")
        if before_id:
            for index, event in enumerate(case.timeline):
                if event.event_id == before_id:
                    return index
        if after_id:
            for index, event in enumerate(case.timeline):
                if event.event_id == after_id:
                    return index + 1
        return len(case.timeline)

    def _renumber_timeline(self, case: CaseState) -> None:
        for index, event in enumerate(case.timeline, start=1):
            event.sequence_index = index
            event.event_id = f"E{index}"

    def _merge_logic_issues(self, case: CaseState, new_issues: list) -> list:
        by_id = {issue.get("issue_id"): issue for issue in case.logic_issues if issue.get("issue_id")}
        for issue in new_issues:
            issue_id = issue.get("issue_id")
            if not issue_id or issue_id in case.answered_logic_issues:
                continue
            by_id[issue_id] = issue
        return sorted(by_id.values(), key=lambda item: item.get("priority", "P1"))

    def generate_outputs(self, case: CaseState) -> dict:
        statement = self.statement_agent.generate(case)
        followup = self.followup_agent.generate(case)
        medical_summary = self.claims_agent.generate_medical_summary(case)
        university_email = self.claims_agent.generate_university_support_email(case)
        case.generated_documents = [
            document
            for document in case.generated_documents
            if document.document_type
            not in {"police_statement", "police_followup", "medical_summary", "university_support_email"}
        ]
        case.generated_documents.extend([statement, followup, medical_summary, university_email])
        return {
            "evidence": self.evidence_agent.build_checklist(case),
            "police_statement": statement,
            "police_followup": followup,
            "medical_summary": medical_summary,
            "university_support_email": university_email,
            "markdown_bundle": self.export_agent.export_markdown(case),
        }
