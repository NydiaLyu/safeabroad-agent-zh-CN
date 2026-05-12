import re
from typing import Dict, List, Optional

from backend.agents.timeline_agent import TimelineReconstructionAgent
from backend.models.case_state import CaseState, TimelineEvent
from backend.services.llm_service import LLMServiceError, QwenLLMService


UNCERTAIN_MARKERS = ["不确定", "记不清", "不记得", "可能", "大概", "好像"]
UNCERTAINTY_SCOPE_MARKERS = ["先后", "顺序", "这两件", "两件事", "是否", "有没有", "哪件", "具体", "只", "范围"]


class TimelineRefinementAgent:
    def __init__(self, llm: Optional[QwenLLMService] = None):
        self.llm = llm or QwenLLMService()
        self.timeline_agent = TimelineReconstructionAgent(self.llm)

    def refine(self, case: CaseState, fragment: str, current_issue: Optional[Dict] = None) -> Dict:
        if self.llm.enabled:
            try:
                result = self._refine_with_llm(case, fragment, current_issue)
                if result.get("events"):
                    return result
            except LLMServiceError:
                pass
        return self._refine_with_rules(case, fragment, current_issue)

    def _refine_with_llm(self, case: CaseState, fragment: str, current_issue: Optional[Dict]) -> Dict:
        timeline_text = "\n".join(
            f"{event.event_id}. {event.description_zh} ({event.event_type}, {event.certainty})"
            for event in sorted(case.timeline, key=lambda item: item.sequence_index)
        )
        system_prompt = (
            "你是时间线精修 agent。任务：把用户的新补充片段插入现有案发时间线的正确位置。"
            "只使用用户明确说出的事实，不要编造。"
            "如果新片段和现有时间线有逻辑矛盾，必须提出中文澄清问题。"
            "例如现有事件是“对方先拿走了薯条”，新片段是“旁边的人制止对方拿走薯条”，"
            "需要追问：制止发生在已经拿走之后，还是拿走前/没拿成？"
            "如果用户明确说不确定、记不清，可以把 certainty 设为 uncertain，并不再阻塞。"
            "输出 JSON：{"
            "\"events\":[{\"description_zh\":\"...\",\"event_type\":\"...\",\"certainty\":\"confirmed|approximate|uncertain\","
            "\"insert_after_event_id\":\"E1|null\",\"insert_before_event_id\":\"E2|null\"}],"
            "\"logic_issues\":[{\"issue_id\":\"...\",\"question\":\"...\",\"blocking\":true}]}"
        )
        user_prompt = (
            f"现有时间线：\n{timeline_text}\n\n"
            f"当前正在澄清的问题：{current_issue or '无'}\n\n"
            f"用户新补充片段：{fragment}"
        )
        payload = self.llm.chat_json(system_prompt, user_prompt)
        return {
            "events": payload.get("events", []),
            "logic_issues": payload.get("logic_issues", []),
        }

    def _refine_with_rules(self, case: CaseState, fragment: str, current_issue: Optional[Dict]) -> Dict:
        uncertainty_detected = any(marker in fragment for marker in UNCERTAIN_MARKERS)
        certainty = "uncertain" if uncertainty_detected else "confirmed"
        event_type = self._classify_fragment(fragment)
        insert_after, insert_before = self._choose_insert_position(case, fragment, event_type)

        events = [
            {
                "description_zh": self._normalize_description(fragment, event_type),
                "event_type": event_type,
                "certainty": certainty,
                "insert_after_event_id": insert_after,
                "insert_before_event_id": insert_before,
            }
        ]

        logic_issues: List[Dict] = []
        if certainty != "uncertain":
            logic_issues.extend(self._detect_logic_issues(case, fragment, event_type))
        elif current_issue and current_issue.get("issue_id") and not self._has_uncertainty_scope(fragment):
            logic_issues.append(
                {
                    "issue_id": f"{current_issue.get('issue_id')}_uncertainty_scope",
                    "priority": "P0",
                    "blocking": True,
                    "question": (
                        "你说“记不清/不确定”，为了避免材料写得太模糊，请说明记不清的范围："
                        "是只不确定这两件事的先后顺序，还是不确定其中某件事是否真的发生？"
                        "例如可以写：“我只是不确定制止和拿走薯条的先后顺序，但两件事都发生了。”"
                    ),
                }
            )

        return {"events": events, "logic_issues": logic_issues}

    def _classify_fragment(self, fragment: str) -> str:
        if any(marker in fragment for marker in ["挥拳", "恐吓", "威胁"]):
            return "physical_threat"
        if any(marker in fragment for marker in ["推", "打", "扭", "拧", "扭断", "抓住手", "掰", "手腕", "胳膊"]):
            return "physical_contact"
        if "制止" in fragment or "阻止" in fragment:
            return "verbal_intervention"
        if "证人" in fragment or ("旁边" in fragment and "人" in fragment):
            return "witness_presence"
        if "CCTV" in fragment or "监控" in fragment or "摄像" in fragment:
            return "cctv_possibility"
        if "说" in fragment or "骂" in fragment or "问" in fragment:
            return "verbal_exchange"
        if "拿" in fragment or "薯条" in fragment:
            return "property_interference"
        return "follow_up_detail"

    def _normalize_description(self, fragment: str, event_type: str) -> str:
        text = fragment.strip(" ，。,.；;")
        if event_type == "verbal_intervention" and "制止" in text and "用户旁边" not in text and "旁边的人" not in text:
            return f"用户旁边的人{text}"
        return text

    def _choose_insert_position(self, case: CaseState, fragment: str, event_type: str) -> tuple:
        sorted_events = sorted(case.timeline, key=lambda item: item.sequence_index)
        anchored_position = self._choose_anchor_position(sorted_events, fragment)
        if anchored_position != (None, None):
            return anchored_position

        property_event = self._find_event(sorted_events, ["薯条", "拿"])
        verbal_response = self._find_event(sorted_events, ["你想怎样", "回答"])
        physical_contact = self._find_event(sorted_events, ["推", "打"])
        escalation_anchor = self._find_last_event(
            sorted_events,
            ["比我强", "你想怎样", "威胁", "恐吓", "骂", "挑衅"],
        )
        aftermath_event = self._find_first_event_after(
            sorted_events,
            escalation_anchor,
            ["警察", "监控", "笔录", "发现", "扣", "离开", "走了"],
        )

        if event_type == "verbal_intervention" and property_event:
            return property_event.event_id, verbal_response.event_id if verbal_response else None
        if event_type == "witness_presence":
            return property_event.event_id if property_event else None, verbal_response.event_id if verbal_response else None
        if event_type == "cctv_possibility":
            return physical_contact.event_id if physical_contact else (sorted_events[-1].event_id if sorted_events else None), None
        if event_type in ["physical_contact", "physical_threat"] and escalation_anchor:
            return escalation_anchor.event_id, aftermath_event.event_id if aftermath_event else None
        return sorted_events[-1].event_id if sorted_events else None, None

    def _choose_anchor_position(self, events: List[TimelineEvent], fragment: str) -> tuple:
        after_anchor = self._extract_anchor(fragment, ["之后", "以后", "后面", "后"])
        if after_anchor:
            event = self._find_anchor_event(events, after_anchor)
            if event:
                return event.event_id, None

        before_anchor = self._extract_anchor(fragment, ["之前", "以前", "前面", "前"])
        if before_anchor:
            before_event = self._find_anchor_event(events, before_anchor)
            if before_event:
                previous_event = self._previous_event(events, before_event)
                return previous_event.event_id if previous_event else None, before_event.event_id

            escalation_anchor = self._find_last_event(events, ["比我强", "你想怎样", "威胁", "恐吓", "骂", "挑衅"])
            if self._looks_like_hand_twist(before_anchor) and escalation_anchor:
                return escalation_anchor.event_id, None

        return None, None

    def _extract_anchor(self, fragment: str, markers: List[str]) -> Optional[str]:
        escaped = "|".join(re.escape(marker) for marker in markers)
        patterns = [
            rf"在(.+?)({escaped})",
            rf"(.+?)({escaped})",
        ]
        for pattern in patterns:
            match = re.search(pattern, fragment)
            if match:
                anchor = match.group(1).strip(" ，。,.；;：:")
                if anchor:
                    return anchor
        return None

    def _find_anchor_event(self, events: List[TimelineEvent], anchor: str) -> Optional[TimelineEvent]:
        anchor = anchor.strip("“”\"' ，。,.；;：:")
        special_keywords = []
        if "比我强" in anchor:
            special_keywords.append("比我强")
        if "你想怎样" in anchor or "想怎样" in anchor:
            special_keywords.append("你想怎样")
        if self._looks_like_hand_twist(anchor):
            special_keywords.extend(["扭", "拧", "手", "手腕", "胳膊"])
        if special_keywords:
            found = self._find_event(events, special_keywords)
            if found:
                return found

        anchor_keywords = [keyword for keyword in re.split(r"[，。,.；;：:\s]+", anchor) if len(keyword) >= 2]
        if anchor_keywords:
            found = self._find_event(events, anchor_keywords)
            if found:
                return found

        for event in events:
            description = event.description_zh
            shared_chunks = [anchor[index : index + 2] for index in range(max(len(anchor) - 1, 0))]
            if any(chunk and chunk in description for chunk in shared_chunks):
                return event
        return None

    def _looks_like_hand_twist(self, text: str) -> bool:
        return any(marker in text for marker in ["扭", "拧", "扭断", "掰"]) and any(
            body_part in text for body_part in ["手", "手腕", "胳膊"]
        )

    def _detect_logic_issues(self, case: CaseState, fragment: str, event_type: str) -> List[Dict]:
        issues = []
        has_taken_fries = any("薯条" in event.description_zh and "拿" in event.description_zh for event in case.timeline)
        if event_type == "verbal_intervention" and has_taken_fries and ("拿走" in fragment or "拿" in fragment):
            issue_id = "fries_taken_vs_intervention"
            if issue_id not in case.answered_logic_issues:
                issues.append(
                    {
                        "issue_id": issue_id,
                        "priority": "P0",
                        "blocking": True,
                        "question": (
                            "这里有一个时间顺序需要确认：你前面说“对方先拿走了我的薯条”，"
                            "现在又说“旁边的人制止了对方拿走薯条”。请确认："
                            "是对方已经拿走后旁边的人出声制止，还是旁边的人制止时对方还没有拿走/没有拿成？"
                            "如果记不清，可以直接写“记不清”。"
                        ),
                    }
                )
        return issues

    def _has_uncertainty_scope(self, fragment: str) -> bool:
        return any(marker in fragment for marker in UNCERTAINTY_SCOPE_MARKERS)

    def _find_event(self, events: List[TimelineEvent], keywords: List[str]) -> Optional[TimelineEvent]:
        for event in events:
            if any(keyword in event.description_zh for keyword in keywords):
                return event
        return None

    def _find_last_event(self, events: List[TimelineEvent], keywords: List[str]) -> Optional[TimelineEvent]:
        for event in reversed(events):
            if any(keyword in event.description_zh for keyword in keywords):
                return event
        return None

    def _find_first_event_after(
        self,
        events: List[TimelineEvent],
        anchor: Optional[TimelineEvent],
        keywords: List[str],
    ) -> Optional[TimelineEvent]:
        if not anchor:
            return None
        for event in events:
            if event.sequence_index > anchor.sequence_index and any(keyword in event.description_zh for keyword in keywords):
                return event
        return None

    def _previous_event(self, events: List[TimelineEvent], event: TimelineEvent) -> Optional[TimelineEvent]:
        previous = None
        for item in events:
            if item.event_id == event.event_id:
                return previous
            previous = item
        return None
