import { z } from "zod";

export const EvidenceItemSchema = z.object({
  evidenceId: z.string().min(1),
  evidenceType: z.enum([
    "cctv",
    "photo",
    "video",
    "medical_record",
    "witness",
    "receipt",
    "message",
    "location_data",
    "police_record",
    "other"
  ]),
  description: z.string().min(1),
  exists: z.boolean().default(false),
  usefulness: z.enum(["high", "medium", "low", "unknown"]).default("unknown"),
  collectionGuidance: z.string().optional(),
  redacted: z.boolean().default(false),
  notes: z.string().optional()
});

export const EvidenceChecklistSchema = z.array(EvidenceItemSchema);

export type EvidenceItem = z.infer<typeof EvidenceItemSchema>;
export type EvidenceChecklist = z.infer<typeof EvidenceChecklistSchema>;
