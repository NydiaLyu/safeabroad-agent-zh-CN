from backend.agents.statement_agent import PoliceStatementGeneratorAgent
from backend.models.case_state import CaseState, Jurisdiction, PoliceInfo, UserProfile


def test_statement_does_not_invent_charges():
    case = CaseState(
        user_profile=UserProfile(name="Test User"),
        jurisdiction=Jurisdiction(country="Australia", state="NSW"),
        police=PoliceInfo(event_number="E123"),
    )

    statement = PoliceStatementGeneratorAgent().generate(case).content

    assert "charged" not in statement.lower()
    assert "sentenced" not in statement.lower()
    assert "convicted" not in statement.lower()

