import { describe, expect, it } from "vitest";
import { IncidentSchema } from "../lib/schemas/incident";

describe("IncidentSchema", () => {
  it("rejects an empty incident description", () => {
    const result = IncidentSchema.safeParse({
      incidentType: "physical_assault",
      description: ""
    });

    expect(result.success).toBe(false);
  });

  it("accepts uncertainty notes", () => {
    const result = IncidentSchema.parse({
      incidentType: "physical_assault",
      description: "我记得被推了，但不确定具体顺序。",
      uncertaintyNotes: "The sequence is uncertain."
    });

    expect(result.uncertaintyNotes).toContain("uncertain");
  });
});
