import { describe, expect, it } from "vitest";
import { nextNonLeadingQuestion } from "../lib/agent/interviewEngine";

describe("nextNonLeadingQuestion", () => {
  it("asks a non-leading location question", () => {
    const question = nextNonLeadingQuestion([]);

    expect(question).toContain("大概在哪里");
    expect(question).not.toContain("是不是");
  });

  it("allows uncertainty", () => {
    const question = nextNonLeadingQuestion([
      {
        eventId: "E1",
        sequenceIndex: 0,
        eventType: "location",
        descriptionZh: "我在麦当劳门口",
        certainty: "confirmed",
        knownFields: {},
        missingFields: []
      }
    ]);

    expect(question).toContain("不确定");
  });
});
