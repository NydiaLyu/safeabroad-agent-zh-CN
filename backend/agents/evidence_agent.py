from typing import Dict, List, Optional

from backend.models.case_state import CaseState
from backend.services.llm_service import LLMServiceError, QwenLLMService


class EvidenceManagerAgent:
    def __init__(self, llm: Optional[QwenLLMService] = None):
        self.llm = llm or QwenLLMService()

    def evaluate(self, case: CaseState, user_note: str = "") -> dict:
        if user_note.strip():
            case.evidence_notes.append(user_note.strip())

        recommendations = self._rule_based_recommendations(case)
        if self.llm.enabled:
            try:
                recommendations = self._merge_recommendations(
                    recommendations,
                    self._llm_recommendations(case),
                )
            except LLMServiceError:
                pass

        case.evidence_recommendations = recommendations
        return {
            "evidence_notes": case.evidence_notes,
            "recommended_evidence": recommendations,
            "summary": self._summary(recommendations),
        }

    def build_checklist(self, case: CaseState) -> dict:
        recommendations = case.evidence_recommendations or self.evaluate(case)["recommended_evidence"]
        return {
            "existing_evidence": [
                item["title"] for item in recommendations if item.get("status") == "already_available"
            ],
            "missing_evidence": [
                item["title"] for item in recommendations if item.get("status") != "already_available"
            ],
            "recommended_actions": [item["how_to_collect"] for item in recommendations],
            "recommended_evidence": recommendations,
        }

    def _rule_based_recommendations(self, case: CaseState) -> List[Dict]:
        text = "\n".join([case.free_narrative_zh or ""] + [event.description_zh for event in case.timeline] + case.evidence_notes)
        items: List[Dict] = []

        if any(keyword in text for keyword in ["监控", "CCTV", "摄像", "麦当劳", "商店", "店里", "餐厅"]):
            location = "麦当劳" if "麦当劳" in text else "案发地点附近商家/公共区域"
            items.append(
                {
                    "evidence_type": "cctv",
                    "title": "案发地点监控录像",
                    "usefulness": "high",
                    "status": "needs_collection",
                    "why_useful": f"用户提到案发地点可能在{location}监控覆盖范围内，监控可能证明时间、地点、双方动作和周围人员。",
                    "how_to_collect": (
                        f"尽快联系{location}的 manager 或值班负责人，说明你是事件当事人，需要他们保留案发时间段的 CCTV。"
                        "可以请他们不要删除/覆盖，并询问警方是否需要正式调取。记录对方姓名、联系方式、沟通时间。"
                    ),
                }
            )

        if any(keyword in text for keyword in ["旁边的人", "两个人", "路人", "证人", "有人", "制止"]):
            items.append(
                {
                    "evidence_type": "witness",
                    "title": "目击者信息",
                    "usefulness": "high",
                    "status": "needs_collection",
                    "why_useful": "时间线中出现旁边的人或路人，他们可能证明对方拿走物品、言语冲突或推搡过程。",
                    "how_to_collect": "回忆目击者外貌、座位/站位、同行人数、是否有联系方式。不要诱导对方作证，只记录你能确认的信息。",
                }
            )

        if any(keyword in text for keyword in ["推", "打", "疼", "伤", "肿", "流血"]):
            items.append(
                {
                    "evidence_type": "injury_photo_or_medical",
                    "title": "伤情照片和医疗记录",
                    "usefulness": "high",
                    "status": "needs_collection",
                    "why_useful": "如存在身体接触或伤痛，照片和医疗记录可帮助说明身体影响和时间连续性。",
                    "how_to_collect": "拍摄清晰照片，保留原图时间信息；如有疼痛、肿胀、失眠或不适，尽快就医并请医生记录症状。",
                }
            )

        if any(keyword in text for keyword in ["薯条", "麦当劳", "付款", "订单", "收据"]):
            items.append(
                {
                    "evidence_type": "receipt_or_payment",
                    "title": "消费记录或订单记录",
                    "usefulness": "medium",
                    "status": "needs_collection",
                    "why_useful": "消费记录可辅助证明你在案发地点和大致时间。",
                    "how_to_collect": "保存麦当劳订单、付款记录、银行交易截图或电子收据，保留原始时间和商户名称。",
                }
            )

        if case.police.event_number:
            items.append(
                {
                    "evidence_type": "police_event_number",
                    "title": "Police Event Number",
                    "usefulness": "high",
                    "status": "already_available",
                    "why_useful": "可用于后续向警方、学校或支持服务说明案件已报备。",
                    "how_to_collect": "保存警方提供的 Event Number、短信、邮件或纸质记录。",
                }
            )

        if not items:
            items.append(
                {
                    "evidence_type": "basic_case_notes",
                    "title": "个人案发记录",
                    "usefulness": "medium",
                    "status": "needs_collection",
                    "why_useful": "在没有明确外部证据时，及时记录可帮助保持时间线一致。",
                    "how_to_collect": "尽快写下日期、时间、地点、人物、原话、动作和不确定点；不要补充自己不确定的事实。",
                }
            )

        return self._dedupe(items)

    def _llm_recommendations(self, case: CaseState) -> List[Dict]:
        timeline = "\n".join(f"{event.sequence_index}. {event.description_zh} ({event.event_type}, {event.certainty})" for event in case.timeline)
        notes = "\n".join(case.evidence_notes)
        system_prompt = (
            "你是证据整理 agent，面向中国留学生在海外遭遇事件后的材料整理。"
            "根据案发时间线和用户补充，判断可能有用的证据、用途、收集方式。"
            "不要提供法律意见，不要承诺警方/学校/保险结果。"
            "输出 JSON：{\"recommended_evidence\":[{\"evidence_type\":\"...\",\"title\":\"...\","
            "\"usefulness\":\"high|medium|low\",\"status\":\"needs_collection|already_available|unknown\","
            "\"why_useful\":\"...\",\"how_to_collect\":\"...\"}]}"
        )
        payload = self.llm.chat_json(system_prompt, f"时间线：\n{timeline}\n\n用户认为可用的证据：\n{notes}")
        return payload.get("recommended_evidence", [])

    def _merge_recommendations(self, base: List[Dict], extra: List[Dict]) -> List[Dict]:
        return self._dedupe(base + extra)

    def _dedupe(self, items: List[Dict]) -> List[Dict]:
        result: List[Dict] = []
        seen = set()
        priority = {"high": 0, "medium": 1, "low": 2}
        for item in sorted(items, key=lambda item: priority.get(item.get("usefulness", "medium"), 1)):
            key = item.get("evidence_type") or item.get("title")
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result

    def _summary(self, recommendations: List[Dict]) -> str:
        high = [item["title"] for item in recommendations if item.get("usefulness") == "high"]
        if high:
            return "优先收集：" + "、".join(high)
        return "暂未发现高优先级外部证据，请先保留个人案发记录。"

