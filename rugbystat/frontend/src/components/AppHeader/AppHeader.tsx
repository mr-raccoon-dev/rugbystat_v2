import { AppShell, Burger, Group, Title, UnstyledButton } from '@mantine/core';
import { IconBallAmericanFootball } from '@tabler/icons-react';
import classes from './AppHeader.module.css';

interface AppHeaderProps {
  opened?: boolean;
  toggle?: () => void;
}

export function AppHeader(props: AppHeaderProps) {
  const { opened, toggle } = props;

  const buttons = (
    <>
      <UnstyledButton className={classes.control}>Турниры</UnstyledButton>
      <UnstyledButton className={classes.control}>Команды</UnstyledButton>
      <UnstyledButton className={classes.control}>Персоны</UnstyledButton>
      <UnstyledButton className={classes.control}>Документы</UnstyledButton>
      <UnstyledButton className={classes.control}>Контакты</UnstyledButton>
    </>
  );

  return (
    <>
      <AppShell.Header>
        <Group h="100%" px="md">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          <Group justify="space-between" style={{ flex: 1 }}>
            <Group>
              <IconBallAmericanFootball size={30} />
              <Title size="1.2rem">Регбийный архив</Title>
            </Group>

            <Group ml="xl" gap={0} visibleFrom="sm">
              {buttons}
            </Group>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar py="md" px={4}>
        {buttons}
      </AppShell.Navbar>
    </>
  );
}
