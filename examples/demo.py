import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.agents.case_intake_agent import CaseIntakeAgent
from backend.models.case_state import PoliceInfo
from backend.services.workflow_service import CaseWorkflowService


case = CaseIntakeAgent().create_case(police=PoliceInfo(reported=True, event_number="E1234567"))
workflow = CaseWorkflowService()

narrative = "我昨晚在悉尼被人打了。对方先拿了我的薯条，我问他干嘛，他说你想怎样，然后站起来骂我，后来推了我。"
workflow.submit_free_narrative(case, narrative)
outputs = workflow.generate_outputs(case)

print(outputs["markdown_bundle"])
