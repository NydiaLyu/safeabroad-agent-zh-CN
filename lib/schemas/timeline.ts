import { z } from "zod";

export const CertaintySchema = z.enum(["confirmed", "approximate", "uncertain"]);

export const TimelineEventSchema = z.object({
  eventId: z.string().min(1),
  sequenceIndex: z.number().int().nonnegative(),
  eventType: z.string().min(1),
  descriptionZh: z.string().min(1),
  descriptionEn: z.string().optional(),
  certainty: CertaintySchema,
  knownFields: z.record(z.string()).default({}),
  missingFields: z.array(z.string()).default([])
});

export const TimelineSchema = z.array(TimelineEventSchema);

export type Certainty = z.infer<typeof CertaintySchema>;
export type TimelineEvent = z.infer<typeof TimelineEventSchema>;
export type Timeline = z.infer<typeof TimelineSchema>;
