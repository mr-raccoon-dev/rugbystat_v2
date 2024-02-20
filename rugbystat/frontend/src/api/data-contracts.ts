import { z } from 'zod';

const CitySchema = z.object({
  id: z.number(),
  name: z.string(),
  short_name: z.string(),
});

export type City = z.infer<typeof CitySchema>;

const BaseDocumentSchema = z.object({
  id: z.number(),
  title: z.string(),
  description: z.nullable(z.string()),
  dropbox_path: z.nullable(z.string().url()),
  kind: z.string(),
  dropbox_thumb: z.nullable(z.string().url()),
  year: z.nullable(z.number()),
  month: z.nullable(z.number()),
  date: z.nullable(z.string()),
  is_image: z.boolean(),
  source_title: z.string(),
});

type Document = z.infer<typeof BaseDocumentSchema> & {
  versions: Document[];
};

const DocumentSchema: z.ZodType<Document> = BaseDocumentSchema.extend({
  versions: z.lazy(() => DocumentSchema.array()),
});

const BaseTeamSchema = z.object({
  url: z.string().url(),
  id: z.number(),
  name: z.string(),
  short_name: z.string(),
  story: z.string(),
  city: CitySchema,
  year: z.nullable(z.number()),
  disband_year: z.nullable(z.union([z.number(), z.string()])),
  operational_years: z.string(),
  documents: DocumentSchema.array(),
});

type Team = z.infer<typeof BaseTeamSchema> & {
  parent: Team | null;
};

export const TeamSchema: z.ZodType<Team> = BaseTeamSchema.extend({
  parent: z.nullable(z.lazy(() => TeamSchema)),
});
