from backend.services.redaction_service import redact_text


def test_redacts_email_phone_and_event_number():
    text = "Email me at test@example.com, phone +61 400 123 456, event E1234567."
    redacted = redact_text(text)
    assert "test@example.com" not in redacted
    assert "+61 400 123 456" not in redacted
    assert "E1234567" not in redacted


def test_does_not_mangle_uuid_case_id():
    case_id = "fa712595-1c9c-409f-ae7f-2d30e9ea36ef"
    assert case_id in redact_text(f"Case ID: {case_id}")
