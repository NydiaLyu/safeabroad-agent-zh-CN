import type { Incident } from "../schemas/incident";
import type { TimelineEvent } from "../schemas/timeline";

export function generateNeutralPoliceStatement(incident: Incident, timeline: TimelineEvent[]): string {
  const lines = [
    `I am reporting an incident described as ${incident.incidentType.replaceAll("_", " ")}.`,
    incident.location ? `The location I remember is ${incident.location}.` : undefined,
    incident.uncertaintyNotes ? `Some details are uncertain: ${incident.uncertaintyNotes}.` : undefined,
    "The events I currently remember are:"
  ].filter(Boolean);

  for (const event of timeline) {
    const certainty = event.certainty === "confirmed" ? "I remember" : `I am ${event.certainty}`;
    lines.push(`- ${certainty}: ${event.descriptionEn ?? event.descriptionZh}`);
  }

  return lines.join("\n");
}
