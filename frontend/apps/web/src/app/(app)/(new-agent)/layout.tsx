import { NewAgentHeader } from '@/app/(app)/(new-agent)/_components/new-agent-header';

import type { FC, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

const NewAgentLayout: FC<Props> = ({ children }) => (
  <>
    <NewAgentHeader />
    <main className="flex-1 p-6">{children}</main>
  </>
);

export default NewAgentLayout;
