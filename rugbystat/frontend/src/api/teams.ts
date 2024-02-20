import ky from 'ky';
import { z } from 'zod';
import { TeamSchema } from '@/api/data-contracts';

export async function fetchTeamList(page = 1) {
  const response = await ky.get('/api/v1/teams/', {
    searchParams: { page },
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
