import type { FC } from 'react';

interface Props {
  params: Promise<{ agentId: string }>;
}

const AgentPage: FC<Props> = async ({ params }) => {
  const { agentId } = await params;

  return (
    <div className="flex-1 p-6">
      <h1 className="text-2xl font-bold">Agent: {agentId}</h1>
    </div>
  );
};

export default AgentPage;
