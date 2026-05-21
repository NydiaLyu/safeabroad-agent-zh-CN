import { z } from "zod";

export const UserProfileSchema = z.object({
  preferredLanguage: z.enum(["zh", "en"]).default("zh"),
  studentStatus: z.enum(["international_student", "exchange_student", "visitor", "migrant", "other"]).optional(),
  university: z.string().optional(),
  contactEmail: z.string().email().optional(),
  phone: z.string().optional(),
  emergencyContactKnown: z.boolean().optional()
});

export type UserProfile = z.infer<typeof UserProfileSchema>;
