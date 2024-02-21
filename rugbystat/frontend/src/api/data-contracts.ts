import { z } from 'zod';

const CitySchema = z.object({
  id: z.number(),
  name: z.string(),
  short_name: z.string(),
});

export type City = z.infer<typeof CitySchema>;

const DocumentVersionSchema = z.object({
  title: z.string(),
  dropbox_path: z.string().nullable(),
  dropbox_thumb: z.string().nullable(),
  year: z.number().nullable(),
  month: z.number().nullable(),
  date: z.string().nullable(),
  is_image: z.boolean(),
});

export type DocumentVersion = z.infer<typeof DocumentVersionSchema>;

const DocumentSchema = z.object({
  id: z.number(),
  title: z.string(),
  description: z.string().nullable(),
  dropbox_path: z.string().nullable(),
  kind: z.string(),
  dropbox_thumb: z.string().nullable(),
  year: z.number().nullable(),
  month: z.number().nullable(),
  date: z.string().nullable(),
  is_image: z.boolean(),
  source_title: z.string(),
  versions: DocumentVersionSchema.array(),
});

export type Document = z.infer<typeof DocumentSchema>;

const BaseTeamSchema = z.object({
  url: z.string().url(),
  id: z.number(),
  name: z.string(),
  short_name: z.string(),
  story: z.string(),
  city: CitySchema,
  year: z.number().nullable(),
  disband_year: z.union([z.number(), z.string()]).nullable(),
  operational_years: z.string(),
  documents: DocumentSchema.array(),
});

type Team = z.infer<typeof BaseTeamSchema> & {
  parent: Team | null;
};

export const TeamSchema: z.ZodType<Team> = BaseTeamSchema.extend({
  parent: z.lazy(() => TeamSchema).nullable(),
});
