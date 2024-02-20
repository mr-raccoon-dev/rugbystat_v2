import '@mantine/core/styles.css';
import { AppShell, MantineProvider } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { AppHeader } from '@/components/AppHeader/AppHeader';

function App() {
  const [opened, { toggle }] = useDisclosure();

  return (
    <MantineProvider>
      <AppShell
        header={{ height: 60 }}
        navbar={{ width: 300, breakpoint: 'sm', collapsed: { desktop: true, mobile: !opened } }}
        padding="md"
      >
        <AppHeader opened={opened} toggle={toggle} />
        <AppShell.Main>Content will be here</AppShell.Main>
      </AppShell>
    </MantineProvider>
  );
}

export default App;
