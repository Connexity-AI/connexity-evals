'use client';

import { cn } from '@workspace/ui/lib/utils';

import { AgentEditActions } from '@/app/(app)/(agent)/_components/header/agent-edit-actions';
import { AgentEditBreadcrumb } from '@/app/(app)/(agent)/_components/header/agent-edit-breadcrumb';
import { AgentModeTabs } from '@/app/(app)/(agent)/_components/header/agent-mode-tabs';
import { useVersions } from '@/app/(app)/(agent)/_context/versions-context';

const HEADER_CLASSNAME = cn(
  'relative h-16 border-b border-border flex items-center sticky top-0 z-10',
  'bg-card dark:bg-zinc-900 px-6'
);

export function AgentEditHeader() {
  const { isReadOnly } = useVersions();
  const isChatClosed = isReadOnly;

  return (
    <header className={HEADER_CLASSNAME}>
      <div className="absolute inset-y-0 left-6 flex items-center">
        <AgentEditBreadcrumb />
      </div>

      <div className="absolute inset-y-0 right-6 flex items-center">
        <AgentEditActions />
      </div>

      <div className="flex flex-1 items-center">
        <div
          aria-hidden
          className={cn(
            'shrink-0 transition-[width] duration-300 ease-in-out',
            isChatClosed ? 'w-0' : 'w-1/3'
          )}
        />
        <div className="flex flex-1 justify-center">
          <AgentModeTabs />
        </div>
      </div>
    </header>
  );
}
