import { z } from "zod";

export const IncidentSchema = z.object({
  date: z.string().optional(),
  time: z.string().optional(),
  location: z.string().optional(),
  jurisdiction: z.string().optional(),
  incidentType: z.enum([
    "physical_assault",
    "verbal_threat",
    "robbery",
    "harassment",
    "property_damage",
    "medical_emergency",
    "other"
  ]),
  description: z.string().min(1),
  injuries: z.array(z.string()).default([]),
  psychologicalImpact: z.array(z.string()).default([]),
  propertyLoss: z.array(z.string()).default([]),
  witnesses: z.array(z.string()).default([]),
  suspectDescription: z.string().optional(),
  evidence: z.array(z.string()).default([]),
  policeEventNumber: z.string().optional(),
  uncertaintyNotes: z.string().optional()
});

export type Incident = z.infer<typeof IncidentSchema>;
