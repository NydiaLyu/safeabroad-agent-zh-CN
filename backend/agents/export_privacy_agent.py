from backend.models.case_state import CaseState
from backend.services.redaction_service import redact_text


class DocumentExportPrivacyAgent:
    def export_markdown(self, case: CaseState, redact: bool = True) -> str:
        sections = [
            "# SafeAbroad Case Bundle",
            "",
            "## Safety Disclaimer",
            "This tool organises information and drafts documents. It is not legal, medical, psychological, immigration, or emergency advice.",
            "",
            "## Case Summary",
            f"- Case ID: {case.case_id}",
            f"- Jurisdiction: {case.jurisdiction.jurisdiction_id}",
            f"- Police Event Number: {case.police.event_number or '[unknown]'}",
            "",
            "## Timeline",
        ]
        for event in case.timeline:
            sections.append(f"{event.sequence_index}. {event.description_zh} [{event.certainty}]")

        sections.extend(["", "## Generated Documents"])
        for document in case.generated_documents:
            sections.extend([f"### {document.document_type}", document.content, ""])

        text = "\n".join(sections)
        return redact_text(text) if redact else text

