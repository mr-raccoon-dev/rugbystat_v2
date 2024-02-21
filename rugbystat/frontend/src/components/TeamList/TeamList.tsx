import React, { Fragment, useState } from 'react';
import { useQuery } from 'react-query';
import {
  ActionIcon,
  Avatar,
  Center,
  Divider,
  List,
  LoadingOverlay,
  Pagination,
  Paper,
  rem,
  Stack,
  Text,
  TextInput,
} from '@mantine/core';
import { IconArchive, IconArrowRight, IconPhoto, IconSearch } from '@tabler/icons-react';
import { getHotkeyHandler } from '@mantine/hooks';
import { N } from '@mobily/ts-belt';
import { fetchTeamList } from '@/api/teams';

enum TeamsQueryKey {
  LIST = 'teams/list',
}

export function TeamList() {
  const [search, setSearch] = useState<string>('');
  const [submittedSearch, setSubmittedSearch] = useState<string | null>(null);
  const [page, setPage] = useState<number>(1);

  const query = useQuery(
    [TeamsQueryKey.LIST, { page, search: submittedSearch }] as const,
    ({ queryKey }) => fetchTeamList(queryKey[1]),
    { keepPreviousData: true }
  );

  const handleSearchSubmit = () => {
    setPage(1);
    setSubmittedSearch(search || null);
  };

  const total = Math.ceil(N.divide(query.data?.count ?? 0, 10));

  return (
    <Stack flex="1 1 auto">
      <Paper mb="md">
        <TextInput
          size="md"
          placeholder="Поиск команд"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={getHotkeyHandler([['Enter', handleSearchSubmit]])}
          leftSection={<IconSearch style={{ width: rem(18), height: rem(18) }} stroke={1.5} />}
          rightSectionWidth={42}
          rightSection={
            <ActionIcon onClick={handleSearchSubmit} size={32}>
              <IconArrowRight style={{ width: rem(18), height: rem(18) }} stroke={1.5} />
            </ActionIcon>
          }
        />
      </Paper>
      <Stack flex="1 1 auto" pos="relative">
        <LoadingOverlay
          visible={query.isFetching}
          zIndex={1000}
          overlayProps={{
            radius: 'sm',
            blur: 2,
            color: query.data?.results.length ? undefined : 'var(--mantine-color-gray-2)',
          }}
        />

        {query.data?.results.length ? (
          <Paper px="md" py="md">
            <Stack>
              <List>
                {query.data?.results.map((i, index) => (
                  <Fragment key={i.id}>
                    {index > 0 && <Divider />}
                    <List.Item
                      icon={
                        <Avatar src={i.documents[0]?.dropbox_thumb} radius="sm">
                          <IconPhoto size={20} />
                        </Avatar>
                      }
                      py="sm"
                    >
                      <a href="#">
                        {i.short_name}
                        {i.operational_years.length > 0 && <> ({i.operational_years})</>}
                      </a>
                    </List.Item>
                  </Fragment>
                ))}
              </List>
              <Pagination
                ml="auto"
                total={total}
                value={page}
                onChange={setPage}
                getControlProps={() => ({
                  disabled: total === 1,
                })}
              />
            </Stack>
          </Paper>
        ) : (
          query.data != null && (
            <Center flex="1 1 auto">
              <Stack align="center" justify="center">
                {submittedSearch ? <IconSearch size={36} /> : <IconArchive size={36} />}
                <Text>{submittedSearch ? 'Команды не найдены' : 'Список команд пуст'}</Text>
              </Stack>
            </Center>
          )
        )}
      </Stack>
    </Stack>
  );
}
