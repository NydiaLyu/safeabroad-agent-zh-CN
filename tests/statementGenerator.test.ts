import { describe, expect, it } from "vitest";
import { generateNeutralPoliceStatement } from "../lib/agent/statementGenerator";

describe("generateNeutralPoliceStatement", () => {
  it("preserves uncertain memory", () => {
    const statement = generateNeutralPoliceStatement(
      {
        incidentType: "physical_assault",
        description: "我不确定顺序。",
        uncertaintyNotes: "I am not sure whether the push happened before or after the verbal threat.",
        injuries: [],
        psychologicalImpact: [],
        propertyLoss: [],
        witnesses: [],
        evidence: []
      },
      [
        {
          eventId: "E1",
          sequenceIndex: 0,
          eventType: "physical_contact",
          descriptionZh: "对方推了我",
          certainty: "uncertain",
          knownFields: {},
          missingFields: []
        }
      ]
    );

    expect(statement).toContain("Some details are uncertain");
    expect(statement).toContain("I am uncertain");
  });

  it("does not fabricate missing location", () => {
    const statement = generateNeutralPoliceStatement(
      {
        incidentType: "physical_assault",
        description: "对方推了我。",
        injuries: [],
        psychologicalImpact: [],
        propertyLoss: [],
        witnesses: [],
        evidence: []
      },
      []
    );

    expect(statement).not.toContain("convenience store");
  });
});
