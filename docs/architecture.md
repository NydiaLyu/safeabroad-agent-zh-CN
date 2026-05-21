# Architecture

SafeAbroad MVP uses service orchestration around a shared `CaseState`.

`CaseWorkflowService` coordinates deterministic agent classes:

1. `SafetyTriageAgent`
2. `CaseIntakeAgent`
3. `TimelineReconstructionAgent`
4. `DetailGapAnalyzerAgent`
5. `TraumaInformedInterviewAgent`
6. `EvidenceManagerAgent`
7. `PoliceStatementGeneratorAgent`
8. `PoliceFollowUpAgent`
9. `ClaimsSupportNavigatorAgent`
10. `DocumentExportPrivacyAgent`

The first version deliberately avoids a complex multi-agent runtime. LangGraph can be added later once workflow transitions are stable.

