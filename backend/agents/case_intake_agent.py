from typing import Optional

from backend.models.case_state import CaseState, Jurisdiction, PoliceInfo, UserProfile


class CaseIntakeAgent:
    def create_case(
        self,
        user_profile: Optional[UserProfile] = None,
        jurisdiction: Optional[Jurisdiction] = None,
        police: Optional[PoliceInfo] = None,
        incident_type: str = "assault",
    ) -> CaseState:
        return CaseState(
            user_profile=user_profile or UserProfile(),
            jurisdiction=jurisdiction or Jurisdiction(),
            police=police or PoliceInfo(),
            incident_type=incident_type,
        )
