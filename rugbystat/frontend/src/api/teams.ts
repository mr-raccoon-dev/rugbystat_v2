import ky from 'ky';
import { z } from 'zod';
import { D, G, pipe } from '@mobily/ts-belt';
import { TeamSchema } from '@/api/data-contracts';

const fetchTeamListParamsSchema = z.object({
  page: z.number().optional(),
  search: z.string().nullish(),
  year: z.number().optional(),
  short_name: z.string().optional(),
});

type FetchTeamListParams = z.infer<typeof fetchTeamListParamsSchema>;

export async function fetchTeamList(params: FetchTeamListParams) {
  const response = await ky.get('/api/v1/teams/', {
    searchParams: pipe(
      fetchTeamListParamsSchema.parse(params),
      D.map((v) => (G.isNull(v) ? undefined : v)),
      D.filter(G.isNotNullable)
    ),
  });

  const data = await response.json();

  return z
    .object({
      count: z.number(),
      next: z.nullable(z.string()),
      previous: z.nullable(z.string()),
      results: TeamSchema.array(),
    })
    .parse(data);
}
