import { AgentNameHeader } from '@/app/(app)/(new-agent)/_components/agent-name-header';

import type { FC, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

const NewAgentLayout: FC<Props> = ({ children }) => (
  <>
    <AgentNameHeader />
    <main className="flex-1 flex flex-col">{children}</main>
  </>
);

export default NewAgentLayout;
