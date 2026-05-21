from backend.services.llm_service import LLMServiceError, QwenLLMService
from backend.models.case_state import CaseState, GeneratedDocument


class PoliceStatementGeneratorAgent:
    def __init__(self, llm: QwenLLMService = None):
        self.llm = llm or QwenLLMService()

    def generate(self, case: CaseState) -> GeneratedDocument:
        if self.llm.enabled:
            try:
                return GeneratedDocument(
                    document_type="police_statement",
                    language="en",
                    content=self._generate_with_llm(case),
                )
            except LLMServiceError:
                pass
        return self._generate_with_rules(case)

    def _generate_with_llm(self, case: CaseState) -> str:
        system_prompt = (
            "You are drafting a factual police statement in English. "
            "Only use facts from the provided case file. Do not invent details. "
            "Do not make legal conclusions. Do not diagnose medical or psychological conditions. "
            "Mark uncertainty clearly. Use chronological order if possible. Use plain formal English. "
            "Do not add next steps, links, legal rights explanations, support service referrals, police contact numbers, "
            "or jurisdiction-specific advice unless those facts are explicitly provided in the case file. "
            "Do not say that the document is official or suitable for filing. "
            "Output only the statement draft for user review."
        )
        user_prompt = case.model_dump_json() if hasattr(case, "model_dump_json") else case.json()
        return self.llm.chat(system_prompt, user_prompt)

    def _generate_with_rules(self, case: CaseState) -> GeneratedDocument:
        lines = [
            "Police Statement Draft",
            "",
            "1. Identity and context",
            f"My name is {case.user_profile.name or '[Name]'}. I am an international student.",
            "",
            "2. Location and jurisdiction",
            f"The incident occurred in {case.jurisdiction.city or '[city]'}, {case.jurisdiction.state or ''}, {case.jurisdiction.country}.",
            "",
            "3. Chronology",
        ]

        if not case.timeline:
            lines.append("No confirmed timeline has been provided yet.")
        for event in sorted(case.timeline, key=lambda item: item.sequence_index):
            certainty = "I am not certain" if event.certainty == "uncertain" else event.certainty
            lines.append(f"- {event.description_zh} ({certainty}).")

        if case.injuries:
            lines.extend(["", "4. Injuries", *[f"- {injury}" for injury in case.injuries]])

        if case.psychological_impact:
            lines.extend(["", "5. Ongoing impact", *[f"- {impact}" for impact in case.psychological_impact]])

        lines.extend(
            [
                "",
                "6. Police report",
                f"Event number: {case.police.event_number or '[unknown]'}",
                "",
                "Uncertainty notes",
                "This draft only includes information provided in the case file. Unknown details should be reviewed before use.",
            ]
        )
        return GeneratedDocument(document_type="police_statement", language="en", content="\n".join(lines))
