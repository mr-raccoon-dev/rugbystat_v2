import ky from 'ky';
import { z } from 'zod';
import { TeamSchema } from '@/api/data-contracts';

const prefixUrl = 'http://rugbystat.pythonanywhere.com/';

export async function fetchTeamList(page = 1) {
  const response = await ky.get('api/v1/teams/', {
    searchParams: { page },
    prefixUrl,
  });

  return z
    .object({
      count: z.number(),
      next: z.nullable(z.string()),
      prev: z.nullable(z.string()),
      results: TeamSchema.array(),
    })
    .parse(response);
}
