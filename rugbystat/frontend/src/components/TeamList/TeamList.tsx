import React, { Fragment } from 'react';
import { useQuery } from 'react-query';
import { Avatar, Divider, List, Paper } from '@mantine/core';
import { IconPhoto } from '@tabler/icons-react';
import { fetchTeamList } from '@/api/teams';

enum TeamsQueryKey {
  LIST = 'teams/list',
}

export function TeamList() {
  const page = 1;
  const query = useQuery([TeamsQueryKey.LIST, page] as const, () => fetchTeamList(page));

  return (
    <Paper>
      <List withPadding px="lg" py="sm">
        {query.data?.results.map((i, index) => (
          <Fragment key={i.id}>
            {index > 0 && <Divider />}
            <List.Item
              icon={
                <Avatar src={i.documents[0]?.dropbox_thumb} radius="sm">
                  <IconPhoto size={20} />
                </Avatar>
              }
              px="sm"
              py="sm"
            >
              <a href="#">
                {i.name} {i.short_name}
                {i.operational_years.length > 0 && <> ({i.operational_years})</>}
              </a>
            </List.Item>
          </Fragment>
        ))}
      </List>
    </Paper>
  );
}
