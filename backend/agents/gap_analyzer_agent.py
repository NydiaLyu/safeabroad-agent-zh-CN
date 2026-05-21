from typing import Dict, List

from backend.models.case_state import CaseState


QUESTION_BANK = {
    "next_action": "在这之后，下一件你记得发生的事情是什么？",
    "exact_words_or_meaning": "对方当时有没有说什么？如果记得原话可以写原话；如果不确定，可以写大概意思。",
    "body_part": "第一次身体接触具体是怎么发生的？接触到你身体哪个部位？",
    "force": "你能描述当时的力度或你身体的反应吗？不确定也可以直接说不确定。",
    "immediate_effect": "接触发生后，你马上有什么身体反应或行动？",
    "witnesses": "你记得附近有没有人可能看到或听到这件事？",
    "cctv": "附近是否可能有 CCTV，例如商店、车站、校园、公交或路口？",
    "medical_help": "事件后你是否看过医生、医院或校医？",
}


REQUIRED_FIELDS_BY_EVENT_TYPE = {
    "physical_contact": ["body_part", "force", "immediate_effect"],
    "verbal_exchange": ["exact_words_or_meaning", "next_action"],
    "property_interference": ["next_action"],
    "injury": ["body_part", "medical_help"],
}


class DetailGapAnalyzerAgent:
    def analyze(self, case: CaseState) -> List[Dict]:
        gaps: List[Dict] = []
        for event in case.timeline:
            required_fields = REQUIRED_FIELDS_BY_EVENT_TYPE.get(event.event_type, [])
            for field in required_fields:
                if field not in event.known_fields:
                    answered_key = f"{event.event_id}:{field}"
                    if answered_key in case.answered_gaps:
                        continue
                    priority = "P1" if event.event_type in {"physical_contact", "verbal_exchange"} else "P2"
                    gaps.append(
                        {
                            "event_id": event.event_id,
                            "gap_id": field,
                            "priority": priority,
                            "reason": f"{event.event_type} is missing {field}.",
                            "question": QUESTION_BANK.get(field, "你能补充这个细节吗？"),
                        }
                    )

        if "global:witnesses" not in case.answered_gaps and not any(gap["gap_id"] == "witnesses" for gap in gaps):
            gaps.append({"event_id": None, "gap_id": "witnesses", "priority": "P2", "reason": "Witness details are useful evidence.", "question": QUESTION_BANK["witnesses"]})
        if "global:cctv" not in case.answered_gaps and not any(gap["gap_id"] == "cctv" for gap in gaps):
            gaps.append({"event_id": None, "gap_id": "cctv", "priority": "P2", "reason": "CCTV may be time-sensitive.", "question": QUESTION_BANK["cctv"]})

        return sorted(gaps, key=lambda item: item["priority"])
