import '@mantine/core/styles.css';
import { AppShell, MantineProvider } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { QueryClient, QueryClientProvider } from 'react-query';
import { AppHeader } from '@/components/AppHeader/AppHeader';
import { TeamList } from '@/components/TeamList/TeamList';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity,
      refetchOnReconnect: false,
      refetchIntervalInBackground: false,
    },
  },
});

function App() {
  const [opened, { toggle }] = useDisclosure();

  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider>
        <AppShell
          w="100%"
          header={{ height: 60 }}
          navbar={{ width: 300, breakpoint: 'sm', collapsed: { desktop: true, mobile: !opened } }}
          padding="md"
        >
          <AppHeader opened={opened} toggle={toggle} />
          <AppShell.Main bg="var(--mantine-color-gray-2)">
            <TeamList />
          </AppShell.Main>
        </AppShell>
      </MantineProvider>
    </QueryClientProvider>
  );
}

export default App;
