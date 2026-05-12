from backend.models.case_state import CaseState, GeneratedDocument


class PoliceFollowUpAgent:
    def generate(self, case: CaseState) -> GeneratedDocument:
        content = f"""Hi Constable [Name],

My name is {case.user_profile.name or "[Name]"}. I am following up regarding Event No. {case.police.event_number or "[number]"}.

Could you please let me know whether there has been any update, whether there are any safety precautions I should take, and whether I should provide any further evidence or statement?

Kind regards,
{case.user_profile.name or "[Name]"}"""
        return GeneratedDocument(document_type="police_followup", language="en", content=content)

