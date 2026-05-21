from datetime import datetime
from typing import Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


Certainty = Literal["confirmed", "approximate", "uncertain"]
RiskLevel = Literal["RED", "YELLOW", "GREEN"]


class UserProfile(BaseModel):
    name: Optional[str] = None
    preferred_language: str = "zh"
    student_status: Optional[str] = "international_student"
    university: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None


class Jurisdiction(BaseModel):
    country: str = "Australia"
    state: Optional[str] = "NSW"
    city: Optional[str] = "Sydney"
    jurisdiction_id: Optional[str] = "AU-NSW"


class PoliceInfo(BaseModel):
    reported: bool = False
    event_number: Optional[str] = None
    officer_name: Optional[str] = None
    police_station: Optional[str] = None
    police_unit: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class TimelineEvent(BaseModel):
    event_id: str
    event_type: str
    description_zh: str
    description_en: Optional[str] = None
    sequence_index: int
    certainty: Certainty = "uncertain"
    known_fields: Dict[str, str] = Field(default_factory=dict)
    missing_fields: List[str] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid4()))
    evidence_type: str
    description: str
    exists: bool = False
    file_path: Optional[str] = None
    redacted: bool = False
    notes: Optional[str] = None


class GeneratedDocument(BaseModel):
    document_type: str
    language: str = "en"
    content: str
    reviewed_by_user: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CaseState(BaseModel):
    case_id: str = Field(default_factory=lambda: str(uuid4()))
    user_profile: UserProfile = Field(default_factory=UserProfile)
    jurisdiction: Jurisdiction = Field(default_factory=Jurisdiction)
    police: PoliceInfo = Field(default_factory=PoliceInfo)
    incident_type: str = "assault"
    current_risk_level: Optional[RiskLevel] = None

    free_narrative_zh: Optional[str] = None
    timeline: List[TimelineEvent] = Field(default_factory=list)
    injuries: List[str] = Field(default_factory=list)
    psychological_impact: List[str] = Field(default_factory=list)
    property_loss: List[Dict] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    evidence_notes: List[str] = Field(default_factory=list)
    evidence_recommendations: List[Dict] = Field(default_factory=list)

    missing_details: List[Dict] = Field(default_factory=list)
    answered_gaps: List[str] = Field(default_factory=list)
    logic_issues: List[Dict] = Field(default_factory=list)
    answered_logic_issues: List[str] = Field(default_factory=list)
    followup_finished: bool = False
    generated_documents: List[GeneratedDocument] = Field(default_factory=list)
    reviewed_by_user: bool = False
