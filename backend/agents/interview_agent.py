from typing import Dict, List

from backend.agents.gap_analyzer_agent import QUESTION_BANK


class TraumaInformedInterviewAgent:
    ground_rules = (
        "你不需要一次把所有事情说完整。可以从你最清楚记得的地方开始。"
        "如果时间、顺序或细节不确定，可以直接说“不确定”。"
        "请不要猜测，也不用为了让故事完整而补充你不确定的内容。"
    )

    def next_question(self, gaps: List[Dict]) -> str:
        if gaps:
            return gaps[0]["question"]
        return QUESTION_BANK["next_action"]
