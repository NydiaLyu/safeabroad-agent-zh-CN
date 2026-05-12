from backend.models.case_state import CaseState, GeneratedDocument
from backend.services.llm_service import LLMServiceError, QwenLLMService


class ClaimsSupportNavigatorAgent:
    def __init__(self, llm: QwenLLMService = None):
        self.llm = llm or QwenLLMService()

    def generate_medical_summary(self, case: CaseState) -> GeneratedDocument:
        if self.llm.enabled:
            try:
                return GeneratedDocument(
                    document_type="medical_summary",
                    language="en",
                    content=self._generate_medical_summary_with_llm(case),
                )
            except LLMServiceError:
                pass

        timeline_lines = "\n".join(
            f"- {event.description_zh} ({event.certainty})"
            for event in sorted(case.timeline, key=lambda item: item.sequence_index)
        )
        injuries = "\n".join(f"- {item}" for item in case.injuries) or "- [Describe pain, bruising, bleeding, swelling, sleep issues, or other symptoms]"
        impacts = "\n".join(f"- {item}" for item in case.psychological_impact) or "- [Describe sleep, anxiety, fear going outside, study impact, or other effects]"
        content = f"""Medical Visit Summary Draft

Purpose:
I am seeking medical assessment after an incident. This summary is for discussion with a doctor or clinic. It is not a diagnosis.

Incident summary:
{timeline_lines or "- [No timeline confirmed yet]"}

Current physical symptoms:
{injuries}

Current emotional or daily-life impact:
{impacts}

Police report:
Event number: {case.police.event_number or "[unknown]"}

Questions for the doctor:
- Could you please assess and document any injuries or symptoms?
- Could you please advise whether follow-up care is needed?
- Could you provide a medical certificate or clinical note if appropriate?
"""
        return GeneratedDocument(document_type="medical_summary", language="en", content=content)

    def generate_university_support_email(self, case: CaseState) -> GeneratedDocument:
        content = f"""Subject: Request for student support after an incident

Dear Student Support Team,

My name is {case.user_profile.name or "[Name]"}. I am an international student at {case.user_profile.university or "[University]"}.

I am requesting support after an incident that occurred in {case.jurisdiction.city or "[city]"}. I have prepared a case summary and can provide the police event number if required.

Could you please advise what support, academic consideration, or safety arrangements may be available?

Kind regards,
{case.user_profile.name or "[Name]"}"""
        return GeneratedDocument(document_type="university_support_email", language="en", content=content)

    def generate_support_guidance(self, case: CaseState) -> dict:
        jurisdiction_id = case.jurisdiction.jurisdiction_id or "AU-NSW"
        if jurisdiction_id == "AU-NSW":
            return self._nsw_support_guidance(case)
        return {
            "jurisdiction": jurisdiction_id,
            "disclaimer": self._legal_boundary(),
            "cannot_provide": self._prohibited_predictions(),
            "pathways": [
                {
                    "title": "Contact local victim support or legal aid",
                    "purpose": "Get jurisdiction-specific information and referrals.",
                    "what_to_prepare": ["Police event/reference number if available", "Timeline", "Evidence checklist", "Medical or counselling records if relevant"],
                    "questions_to_ask": ["What victim support services may be available?", "What documents should I keep?", "Who can explain court or witness steps?"],
                }
            ],
            "official_links": [],
        }

    def _nsw_support_guidance(self, case: CaseState) -> dict:
        has_event_number = bool(case.police.event_number)
        has_injury_or_impact = bool(case.injuries or case.psychological_impact or any("推" in event.description_zh or "打" in event.description_zh for event in case.timeline))
        return {
            "jurisdiction": "AU-NSW",
            "disclaimer": self._legal_boundary(),
            "cannot_provide": self._prohibited_predictions(),
            "pathways": [
                {
                    "title": "NSW Victims Support Scheme",
                    "purpose": "了解是否可申请 counselling、immediate needs、economic loss 或 recognition payment。",
                    "fit": "可能相关" if has_injury_or_impact else "需要更多伤情/影响信息判断",
                    "what_to_prepare": [
                        "警方 Event Number 或报案信息" if has_event_number else "如已报案，记录警方 Event Number；如未报案，保留其他客观报告材料",
                        "客观、具体的案发经过时间线",
                        "医疗、牙科、心理咨询或政府/政府资助机构出具的报告（如有）",
                        "申请费用相关的 itemised tax invoices、receipts、treatment plans",
                        "身份证明文件，例如 passport 或其他 government-issued ID",
                    ],
                    "questions_to_ask": [
                        "我这种情况是否可能属于 primary victim？",
                        "我需要哪一种 report 支持申请？",
                        "如果已经向 NSW Police 报案，申请表里需要怎样填写报案信息？",
                        "哪些费用需要收据、治疗计划或保险/Medicare rebate 证明？",
                    ],
                },
                {
                    "title": "Victims Access Line / Victims Services",
                    "purpose": "获取免费、保密的信息、转介和支持服务。",
                    "fit": "建议联系",
                    "what_to_prepare": ["所在州 NSW", "案发日期/地点", "简短时间线", "当前安全和健康影响", "是否已有 Event Number"],
                    "questions_to_ask": [
                        "我可以获得哪些 victim support referral？",
                        "是否可以申请 Approved Counselling Scheme？",
                        "如果英文沟通困难，是否可请求 interpreter 或中文支持？",
                    ],
                },
                {
                    "title": "Legal Aid NSW / LawAccess NSW",
                    "purpose": "获取法律信息、转介，符合条件时获得免费法律建议。",
                    "fit": "需要具体法律问题时联系",
                    "what_to_prepare": ["时间线", "警方沟通记录", "任何 court/witness 文件", "你想问的问题列表"],
                    "questions_to_ask": [
                        "我作为受害者/证人可能需要了解哪些流程？",
                        "如果收到警方或法院联系，我应该如何准备？",
                        "我是否需要单独的法律建议？",
                    ],
                },
                {
                    "title": "出庭准备信息",
                    "purpose": "只整理可能需要准备的材料，不预测是否出庭。",
                    "fit": "仅当警方或法院通知你时适用",
                    "what_to_prepare": ["警方 Event Number", "证据清单", "英文 statement 草稿", "学校/医疗影响记录", "可用日期和联系方式"],
                    "questions_to_ask": [
                        "我是否需要提供正式 statement？",
                        "如果需要出庭，是否有 witness support 或 interpreter？",
                        "是否可以获得关于 court process 的书面信息？",
                    ],
                },
            ],
            "official_links": [
                {"label": "NSW Police Victim Support and Referral", "url": "https://www.police.nsw.gov.au/safety_and_prevention/victims_of_crime/victim_support_and_referral"},
                {"label": "NSW Victims Support Scheme", "url": "https://www.nsw.gov.au/legal-and-justice/information-for-victims-of-crime/victims-support-scheme"},
                {"label": "Supporting documents for Victims Support Scheme applications", "url": "https://www.nsw.gov.au/legal-and-justice/information-for-victims-of-crime/victims-support-scheme/supporting-documents"},
                {"label": "Legal Aid NSW legal advice", "url": "https://www.legalaid.nsw.gov.au/ways-to-get-help/legal-advice"},
                {"label": "NSW going to court as a victim or witness", "url": "https://www.nsw.gov.au/legal-and-justice/victim-of-crime"},
            ],
        }

    def _legal_boundary(self) -> str:
        return "本模块只提供一般信息整理和官方路径导航，不提供法律意见、胜诉/起诉/出庭概率、定罪概率或判刑估计。具体法律问题请联系律师、Legal Aid 或当地官方服务。"

    def _prohibited_predictions(self) -> list:
        return [
            "不估计对方是否会被 charge、convict 或 sentence",
            "不估计出庭概率或案件成功率",
            "不预测赔偿、保险或政府支持申请一定成功",
            "不替代律师、警方、法院或 Victims Services 的判断",
        ]

    def _case_json(self, case: CaseState) -> str:
        return case.model_dump_json() if hasattr(case, "model_dump_json") else case.json()

    def _generate_medical_summary_with_llm(self, case: CaseState) -> str:
        system_prompt = (
            "Draft a concise English medical visit summary for the user's review. "
            "Use only the provided case file. Translate relevant Chinese facts into plain English. "
            "Do not diagnose, do not infer injuries, and do not provide medical advice. "
            "If symptoms or injuries are not provided, use placeholders for the user to complete. "
            "Do not mention CCTV, police investigation steps, external support services, legal options, or emergency instructions. "
            "Make clear that this is for discussion with a doctor or clinic and is not a diagnosis."
        )
        return self.llm.chat(system_prompt, self._case_json(case))
