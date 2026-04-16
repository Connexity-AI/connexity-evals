'use client';

import { Skeleton } from '@workspace/ui/components/ui/skeleton';
import { cn } from '@workspace/ui/lib/utils';

// Silhouette of the chat message list: alternating assistant (left, muted) and
// user (right, blue-tinted) bubbles. Matches the bubble shapes in ChatMessages.

export function ChatMessagesAreaSkeleton() {
  return (
    <div className="flex-1 overflow-hidden p-6 space-y-4">
      <AssistantBubble lineWidths={['w-52', 'w-44']} />
      <UserBubble widthClass="w-40" heightClass="h-9" />
      <AssistantBubble lineWidths={['w-60', 'w-56', 'w-40']} />
      <UserBubble widthClass="w-28" heightClass="h-7" />
    </div>
  );
}

function AssistantBubble({ lineWidths }: { lineWidths: string[] }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[82%] rounded-2xl rounded-bl-sm bg-muted/60 px-4 py-3 space-y-2">
        {lineWidths.map((width, index) => (
          <Skeleton key={index} className={cn('h-3', width)} />
        ))}
      </div>
    </div>
  );
}

function UserBubble({ widthClass, heightClass }: { widthClass: string; heightClass: string }) {
  return (
    <div className="flex justify-end">
      <Skeleton
        className={cn(heightClass, widthClass, 'rounded-2xl rounded-br-sm bg-blue-500/25')}
      />
    </div>
  );
}
