import re
from typing import List

from backend.models.case_state import TimelineEvent
from backend.services.llm_service import LLMServiceError, QwenLLMService


class TimelineReconstructionAgent:
    event_rules = [
        ("property_interference", ["拿", "抢", "拽", "夺", "bag", "phone", "fries"]),
        ("verbal_exchange", ["问", "说", "骂", "威胁", "shout", "said"]),
        ("physical_contact", ["推", "打", "踢", "撞", "抓", "pushed", "hit"]),
        ("injury", ["疼", "流血", "肿", "受伤", "injury", "pain"]),
    ]

    def __init__(self, llm: QwenLLMService = None):
        self.llm = llm or QwenLLMService()

    def extract(self, narrative: str) -> List[TimelineEvent]:
        if self.llm.enabled:
            try:
                return self._extract_with_llm(narrative)
            except LLMServiceError:
                pass
        return self._extract_with_rules(narrative)

    def _extract_with_llm(self, narrative: str) -> List[TimelineEvent]:
        system_prompt = (
            "你负责把用户的中文叙述拆解成按时间顺序排列的事件节点。"
            "只提取用户已经说出的事实，不要补充、推断或编造。"
            "输出 JSON 对象，格式为 {\"events\": [...] }。"
            "每个事件包含 event_type, description_zh, sequence_index, certainty。"
            "certainty 只能是 confirmed, approximate, uncertain。"
        )
        payload = self.llm.chat_json(system_prompt, narrative)
        events = payload.get("events", payload if isinstance(payload, list) else [])
        timeline = [
            TimelineEvent(
                event_id=f"E{index}",
                event_type=item.get("event_type", "context"),
                description_zh=item.get("description_zh", ""),
                sequence_index=item.get("sequence_index", index),
                certainty=item.get("certainty", "uncertain"),
            )
            for index, item in enumerate(events, start=1)
            if item.get("description_zh")
        ]
        if not timeline:
            raise LLMServiceError("Qwen returned an empty timeline.")
        return timeline

    def _extract_with_rules(self, narrative: str) -> List[TimelineEvent]:
        parts = [
            part.strip(" ，。,.；;")
            for part in re.split(r"(?:然后|后来|之后|接着|,|，|。|；|;)", narrative)
            if part.strip(" ，。,.；;")
        ]
        events: List[TimelineEvent] = []
        for index, part in enumerate(parts, start=1):
            events.append(
                TimelineEvent(
                    event_id=f"E{index}",
                    event_type=self._classify_event(part),
                    description_zh=part,
                    sequence_index=index,
                    certainty="approximate" if "大概" in part or "可能" in part else "confirmed",
                )
            )
        return events

    def _classify_event(self, text: str) -> str:
        lower = text.lower()
        for event_type, keywords in self.event_rules:
            if any(keyword in lower for keyword in keywords):
                return event_type
        return "context"
