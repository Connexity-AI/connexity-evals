import { SidebarTrigger } from '@workspace/ui/components/ui/sidebar';

import type { FC, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

const AgentLayout: FC<Props> = ({ children }) => (
  <>
    <header className="flex h-16 items-center border-b bg-card dark:bg-zinc-900 px-6">
      <SidebarTrigger />
    </header>
    <main className="flex-1 p-6">{children}</main>
  </>
);

export default AgentLayout;
