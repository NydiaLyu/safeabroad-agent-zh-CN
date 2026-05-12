from pydantic import BaseModel


class TriagePayload(BaseModel):
    current_danger: bool = False
    serious_injury: bool = False
    offender_nearby: bool = False
    needs_ambulance: bool = False
    injured: bool = False
    jurisdiction_id: str = "AU-NSW"


class SafetyTriageAgent:
    emergency_numbers = {
        "AU-NSW": "000",
        "AU-VIC": "000",
        "UK": "999",
        "US-CA": "911",
    }

    def classify(self, payload: TriagePayload) -> dict:
        if payload.current_danger or payload.serious_injury or payload.offender_nearby:
            risk_level = "RED"
        elif payload.needs_ambulance or payload.injured:
            risk_level = "YELLOW"
        else:
            risk_level = "GREEN"

        emergency_number = self.emergency_numbers.get(payload.jurisdiction_id, "local emergency services")
        action = "Call emergency services immediately" if risk_level == "RED" else "Continue organising the case file"

        return {
            "risk_level": risk_level,
            "action": action,
            "emergency_number": emergency_number,
            "script": "I am an international student. I was assaulted at [location]. I need help and I am currently at [current location].",
        }

    def classify_narrative(self, narrative: str, jurisdiction_id: str = "AU-NSW") -> dict:
        text = narrative or ""
        red_keywords = [
            "现在还在",
            "还在门口",
            "还在附近",
            "跟着我",
            "追我",
            "威胁我现在",
            "流很多血",
            "大量流血",
            "不能呼吸",
            "昏迷",
            "刀",
            "枪",
            "武器",
            "不敢回家",
            "回不了家",
        ]
        yellow_keywords = [
            "流血",
            "头晕",
            "疼",
            "肿",
            "受伤",
            "被打",
            "被推",
            "睡不着",
            "害怕",
            "不敢出门",
            "需要看医生",
            "想去医院",
        ]
        matched_red = [keyword for keyword in red_keywords if keyword in text]
        matched_yellow = [keyword for keyword in yellow_keywords if keyword in text]
        payload = TriagePayload(
            current_danger=bool(matched_red),
            serious_injury=any(keyword in text for keyword in ["流很多血", "大量流血", "不能呼吸", "昏迷", "武器", "刀", "枪"]),
            offender_nearby=any(keyword in text for keyword in ["现在还在", "还在门口", "还在附近", "跟着我", "追我"]),
            needs_ambulance=any(keyword in text for keyword in ["需要救护车", "不能呼吸", "昏迷", "大量流血"]),
            injured=bool(matched_yellow),
            jurisdiction_id=jurisdiction_id,
        )
        result = self.classify(payload)
        result.update(
            {
                "source": "narrative",
                "matched_red_flags": matched_red,
                "matched_yellow_flags": matched_yellow,
                "message_zh": self._message_zh(result["risk_level"], matched_red, matched_yellow),
            }
        )
        return result

    def _message_zh(self, risk_level: str, red_flags: list, yellow_flags: list) -> str:
        if risk_level == "RED":
            return "中文讲述中出现可能的当前危险或严重伤情信号，请优先确认安全并联系当地紧急服务。触发词：" + "、".join(red_flags)
        if risk_level == "YELLOW":
            return "中文讲述中出现受伤、恐惧或后续影响信号，建议尽快考虑就医、报备或联系学校支持。触发词：" + "、".join(yellow_flags)
        return "中文讲述未发现明显当前危险信号，可继续整理材料。"
